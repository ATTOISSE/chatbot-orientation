"""
COMMIT 8: RAG Preparation Pipeline
Pipeline d'indexation complète des formations pour RAG

Processus:
1. Charger les formations de la BD
2. Nettoyer et découper le texte
3. Générer les embeddings
4. Stocker pour retrieval
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path
import json
import pickle

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.formation import Formation, Etablissement, Domaine
from app.rag.chunking import DocumentChunker, Chunk, TextPreprocessor
from app.rag.embeddings import (
    EmbeddingModel,
    HuggingFaceEmbeddingModel,
    MockEmbeddingModel,
    EmbeddingStore
)

logger = logging.getLogger(__name__)


class RAGPreparationPipeline:
    """Pipeline pour préparer les données RAG"""
    
    def __init__(
        self,
        embedding_model: Optional[EmbeddingModel] = None,
        chunking_strategy: str = "semantic",
        chunk_size: int = 512,
        use_mock_embeddings: bool = True,
        cache_dir: Optional[Path] = None
    ):
        """
        Initialiser le pipeline
        
        Args:
            embedding_model: Modèle d'embeddings (ou None pour mock)
            chunking_strategy: 'semantic', 'paragraph', 'sentence', 'sliding_window'
            chunk_size: Taille des chunks
            use_mock_embeddings: Utiliser mock embeddings pour dev
            cache_dir: Répertoire pour cacher les résultats
        """
        
        self.chunking_strategy = chunking_strategy
        self.chunk_size = chunk_size
        self.cache_dir = cache_dir
        
        # Initialiser le modèle d'embeddings
        if embedding_model is not None:
            self.embedding_model = embedding_model
        elif use_mock_embeddings:
            logger.info("Using mock embedding model for development")
            self.embedding_model = MockEmbeddingModel(dimension=384)
        else:
            logger.info("Loading HuggingFace embedding model")
            self.embedding_model = HuggingFaceEmbeddingModel()
        
        # Initialiser les autres composants
        self.chunker = DocumentChunker(chunk_size=chunk_size)
        self.preprocessor = TextPreprocessor()
        self.embedding_store = EmbeddingStore()
        
        # Métriques
        self.stats = {
            "formations_processed": 0,
            "total_chunks": 0,
            "total_embeddings_generated": 0,
            "processing_time_seconds": 0,
            "errors": []
        }
    
    def prepare_from_database(
        self,
        db: Session,
        batch_size: int = 50,
        max_formations: Optional[int] = None
    ) -> EmbeddingStore:
        """
        Préparer les embeddings à partir de la base de données
        
        Args:
            db: Session SQLAlchemy
            batch_size: Nombre de formations par batch
            max_formations: Limiter le nombre de formations (pour test)
        
        Returns:
            EmbeddingStore avec tous les embeddings
        """
        
        import time
        start_time = time.time()
        
        logger.info("Starting RAG preparation pipeline")
        
        # Récupérer les formations
        query = db.query(Formation)
        
        if max_formations:
            query = query.limit(max_formations)
        
        total_formations = query.count()
        logger.info(f"Processing {total_formations} formations")
        
        # Traiter par batches
        for offset in range(0, total_formations, batch_size):
            batch = query.offset(offset).limit(batch_size).all()
            
            logger.info(f"Processing batch {offset // batch_size + 1}")
            
            for formation in batch:
                try:
                    self._process_formation(formation, db)
                    self.stats["formations_processed"] += 1
                except Exception as e:
                    logger.error(f"Error processing formation {formation.id}: {e}")
                    self.stats["errors"].append({
                        "formation_id": formation.id,
                        "error": str(e)
                    })
        
        # Calculer le temps écoulé
        self.stats["processing_time_seconds"] = time.time() - start_time
        
        logger.info(f"RAG preparation complete. Stats: {self.stats}")
        
        return self.embedding_store
    
    def _process_formation(self, formation: Formation, db: Session):
        """
        Traiter une formation complète
        
        1. Récupérer les données
        2. Découper en chunks
        3. Générer les embeddings
        4. Stocker
        """
        
        # Récupérer les données liées
        etablissement = formation.etablissement
        domaines = formation.domaines
        
        formation_data = {
            "id": formation.id,
            "intitule": formation.intitule,
            "diplome": formation.diplome,
            "niveau": formation.niveau,
            "duree": formation.duree,
            "conditions_admission": formation.conditions_admission,
            "objectifs": formation.objectifs,
            "debouches": formation.debouches,
            "description": formation.conditions_admission,  # Utiliser comme description
            "etablissement": etablissement.nom if etablissement else None,
            "ville": etablissement.ville if etablissement else None,
            "domaine": domaines[0].nom if domaines else None,
        }
        
        # Découper la formation
        chunks = self.chunker.chunk_formation(
            formation_data,
            strategy=self.chunking_strategy
        )
        
        # Générer les embeddings pour chaque chunk
        for chunk in chunks:
            # Prétraiter le texte
            clean_content = self.preprocessor.clean_text(chunk.content)
            
            if len(clean_content) < 10:  # Ignorer les chunks trop courts
                continue
            
            # Générer l'embedding
            embedding = self.embedding_model.embed(clean_content)
            
            # Enrichir les métadonnées
            chunk.metadata["model"] = self.embedding_model.get_model_name()
            chunk.metadata["strategy"] = self.chunking_strategy
            chunk.metadata["clean_length"] = len(clean_content)
            
            # Extraire les keywords
            keywords = self.preprocessor.extract_keywords(clean_content, n=5)
            chunk.metadata["keywords"] = keywords
            
            # Stocker dans le store
            self.embedding_store.add(
                chunk.chunk_id,
                embedding,
                chunk.metadata
            )
            
            self.stats["total_chunks"] += 1
            self.stats["total_embeddings_generated"] += 1
    
    def save(self, path: Path):
        """Sauvegarder l'embedding store"""
        
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder les embeddings et métadonnées
        embeddings_path = path / "embeddings.pkl"
        metadata_path = path / "metadata.json"
        stats_path = path / "stats.json"
        
        # Embeddings (binary)
        with open(embeddings_path, 'wb') as f:
            pickle.dump({
                "embeddings": self.embedding_store.embeddings,
                "corpus": self.embedding_store.corpus,
                "corpus_embeddings": self.embedding_store.corpus_embeddings
            }, f)
        
        # Métadonnées (JSON)
        metadata_json = {}
        for chunk_id, meta in self.embedding_store.metadata.items():
            # Convertir les types non sérialisables
            meta_copy = meta.copy()
            metadata_json[chunk_id] = meta_copy
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_json, f, ensure_ascii=False, indent=2)
        
        # Statistiques
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"RAG data saved to {path}")
        logger.info(f"  - embeddings.pkl: {embeddings_path}")
        logger.info(f"  - metadata.json: {metadata_path}")
        logger.info(f"  - stats.json: {stats_path}")
    
    def load(self, path: Path) -> EmbeddingStore:
        """Charger l'embedding store"""
        
        path = Path(path)
        embeddings_path = path / "embeddings.pkl"
        metadata_path = path / "metadata.json"
        
        # Charger les embeddings
        with open(embeddings_path, 'rb') as f:
            data = pickle.load(f)
        
        self.embedding_store.embeddings = data["embeddings"]
        self.embedding_store.corpus = data["corpus"]
        self.embedding_store.corpus_embeddings = data["corpus_embeddings"]
        
        # Charger les métadonnées
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata_json = json.load(f)
        
        self.embedding_store.metadata = metadata_json
        
        logger.info(f"RAG data loaded from {path}")
        logger.info(f"  - Loaded {len(self.embedding_store.corpus)} chunks")
        
        return self.embedding_store
    
    def get_stats(self) -> Dict:
        """Retourner les statistiques"""
        return self.stats


class FormationRAGIndexer:
    """Index RAG pour les formations"""
    
    def __init__(self, embedding_store: EmbeddingStore):
        self.store = embedding_store
    
    def search(
        self,
        query: str,
        embedding_model: EmbeddingModel,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Rechercher les formations pertinentes
        
        Returns:
            List de dicts avec chunk_id, score, metadata, contenu
        """
        
        # Générer l'embedding de la requête
        query_embedding = embedding_model.embed(query)
        
        # Rechercher les chunks similaires
        results = self.store.search(query_embedding, top_k=top_k, metric="cosine")
        
        # Formater les résultats
        formatted_results = []
        for chunk_id, score, metadata in results:
            formatted_results.append({
                "chunk_id": chunk_id,
                "similarity_score": score,
                "metadata": metadata,
                "formation_id": metadata.get("formation_id"),
                "intitule": metadata.get("intitule"),
                "domaine": metadata.get("domaine"),
                "etablissement": metadata.get("etablissement"),
                "keywords": metadata.get("keywords", [])
            })
        
        return formatted_results
    
    def get_formation_chunks(self, formation_id: int) -> List[Dict]:
        """Récupérer tous les chunks d'une formation"""
        
        chunks = []
        for chunk_id, metadata in self.store.metadata.items():
            if metadata.get("formation_id") == formation_id:
                chunks.append({
                    "chunk_id": chunk_id,
                    "metadata": metadata,
                    "size": metadata.get("chunk_size", 0)
                })
        
        return sorted(chunks, key=lambda x: x["metadata"].get("chunk_size", 0), reverse=True)

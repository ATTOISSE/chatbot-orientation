"""
COMMIT 9: ChromaDB Vector Store Integration
Service pour gérer les embeddings avec ChromaDB

Fonctionnalités:
1. Initialisation et gestion du vectorstore
2. Indexation des formations
3. Recherche sémantique
4. Gestion des collections
"""

import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class ChromaDBVectorStore:
    """Service ChromaDB pour stockage et recherche vectorielle"""
    
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        embedding_function=None,
        collection_name: str = "formations"
    ):
        """
        Initialiser ChromaDB
        
        Args:
            persist_directory: Chemin pour persistance (None = in-memory)
            embedding_function: Fonction d'embeddings (None = utiliser défaut)
            collection_name: Nom de la collection
        """
        
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            logger.warning("chromadb not installed. Install with: pip install chromadb")
            self.client = None
            self.collection = None
            return
        
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialiser le client Chroma
        if persist_directory:
            settings = Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_directory,
                anonymized_telemetry=False
            )
            self.client = chromadb.Client(settings)
            logger.info(f"ChromaDB initialized with persistence: {persist_directory}")
        else:
            settings = Settings(
                chroma_db_impl="duckdb",
                anonymized_telemetry=False
            )
            self.client = chromadb.Client(settings)
            logger.info("ChromaDB initialized in-memory")
        
        # Créer ou récupérer la collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Collection '{collection_name}' ready")
    
    def add_formation_chunks(
        self,
        chunk_ids: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
        documents: List[str]
    ) -> bool:
        """
        Ajouter des chunks de formations à la collection
        
        Args:
            chunk_ids: IDs uniques des chunks
            embeddings: Embeddings vectoriels
            metadatas: Métadonnées de chaque chunk
            documents: Contenu texte des chunks
        
        Returns:
            True si succès
        """
        
        if self.collection is None:
            logger.error("ChromaDB not initialized")
            return False
        
        try:
            self.collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            logger.info(f"Added {len(chunk_ids)} chunks to ChromaDB")
            return True
        except Exception as e:
            logger.error(f"Error adding chunks: {e}")
            return False
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        where: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Rechercher les chunks similaires
        
        Args:
            query_embedding: Vecteur de la requête
            top_k: Nombre de résultats
            where: Filtre métadonnées (Chroma where clause)
        
        Returns:
            Liste de résultats avec scores
        """
        
        if self.collection is None:
            logger.error("ChromaDB not initialized")
            return []
        
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where
            )
            
            # Formater les résultats
            formatted = []
            if results["ids"] and len(results["ids"]) > 0:
                for idx, (chunk_id, distance, metadata, document) in enumerate(zip(
                    results["ids"][0],
                    results["distances"][0],
                    results["metadatas"][0],
                    results["documents"][0]
                )):
                    # Distance en cosine = 1 - similarity
                    similarity = 1 - distance if distance is not None else 0
                    
                    formatted.append({
                        "chunk_id": chunk_id,
                        "similarity_score": float(similarity),
                        "distance": float(distance) if distance is not None else 0,
                        "metadata": metadata,
                        "content": document
                    })
            
            return formatted
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []
    
    def search_by_text(
        self,
        query_text: str,
        embedding_function,
        top_k: int = 5,
        where: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Rechercher en utilisant du texte (génère embedding automatiquement)
        
        Args:
            query_text: Texte de la requête
            embedding_function: Fonction pour générer l'embedding
            top_k: Nombre de résultats
            where: Filtre métadonnées
        
        Returns:
            Liste de résultats
        """
        
        try:
            # Générer l'embedding
            query_embedding = embedding_function.embed(query_text)
            
            # Convertir en liste si nécessaire
            if hasattr(query_embedding, 'tolist'):
                query_embedding = query_embedding.tolist()
            elif not isinstance(query_embedding, list):
                query_embedding = list(query_embedding)
            
            return self.search(query_embedding, top_k=top_k, where=where)
        except Exception as e:
            logger.error(f"Error in text search: {e}")
            return []
    
    def get_collection_count(self) -> int:
        """Nombre de chunks dans la collection"""
        if self.collection is None:
            return 0
        return self.collection.count()
    
    def delete_collection(self) -> bool:
        """Supprimer la collection"""
        if self.client is None:
            return False
        
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection '{self.collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False
    
    def persist(self) -> bool:
        """Sauvegarder les données persistantes"""
        if self.client is None:
            return False
        
        try:
            self.client.persist()
            logger.info("ChromaDB data persisted")
            return True
        except Exception as e:
            logger.error(f"Error persisting: {e}")
            return False
    
    def reset(self) -> bool:
        """Réinitialiser la collection"""
        if not self.delete_collection():
            return False
        
        # Recréer la collection vide
        try:
            import chromadb
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Collection reset successfully")
            return True
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            return False


class FormationVectorIndexer:
    """Service pour indexer les formations dans ChromaDB"""
    
    def __init__(
        self,
        vectorstore: ChromaDBVectorStore,
        embedding_model
    ):
        """
        Initialiser l'indexeur
        
        Args:
            vectorstore: Instance ChromaDBVectorStore
            embedding_model: Modèle d'embeddings
        """
        
        self.vectorstore = vectorstore
        self.embedding_model = embedding_model
    
    def index_chunks(
        self,
        chunks: List[Dict],
        batch_size: int = 100
    ) -> Dict:
        """
        Indexer une batch de chunks
        
        Args:
            chunks: List de dicts {chunk_id, content, metadata}
            batch_size: Taille des batches pour embeddings
        
        Returns:
            Stats {indexed, errors, etc.}
        """
        
        stats = {
            "total_chunks": len(chunks),
            "indexed": 0,
            "errors": []
        }
        
        if len(chunks) == 0:
            return stats
        
        try:
            # Extraire les composants
            chunk_ids = [c["chunk_id"] for c in chunks]
            documents = [c["content"] for c in chunks]
            metadatas = [c["metadata"] for c in chunks]
            
            # Générer les embeddings en batch
            logger.info(f"Generating {len(documents)} embeddings...")
            embeddings = self.embedding_model.embed_batch(documents, batch_size=batch_size)
            
            # Convertir les embeddings en listes si nécessaire
            embeddings_list = []
            for emb in embeddings:
                if hasattr(emb, 'tolist'):
                    embeddings_list.append(emb.tolist())
                elif not isinstance(emb, list):
                    embeddings_list.append(list(emb))
                else:
                    embeddings_list.append(emb)
            
            # Ajouter à ChromaDB
            success = self.vectorstore.add_formation_chunks(
                chunk_ids=chunk_ids,
                embeddings=embeddings_list,
                metadatas=metadatas,
                documents=documents
            )
            
            if success:
                stats["indexed"] = len(chunks)
                logger.info(f"Successfully indexed {len(chunks)} chunks")
            
        except Exception as e:
            stats["errors"].append(str(e))
            logger.error(f"Error indexing chunks: {e}")
        
        return stats
    
    def search_formations(
        self,
        query: str,
        top_k: int = 5,
        filter_by_domain: Optional[str] = None,
        filter_by_city: Optional[str] = None
    ) -> List[Dict]:
        """
        Rechercher les formations pertinentes
        
        Args:
            query: Texte de la requête
            top_k: Nombre de résultats
            filter_by_domain: Filtrer par domaine
            filter_by_city: Filtrer par ville
        
        Returns:
            Liste de résultats formatés
        """
        
        # Construire le filtre where (Chroma syntax)
        where = None
        if filter_by_domain or filter_by_city:
            where = {}
            if filter_by_domain:
                where["domaine"] = filter_by_domain
            if filter_by_city:
                where["ville"] = filter_by_city
        
        # Rechercher
        results = self.vectorstore.search_by_text(
            query,
            self.embedding_model,
            top_k=top_k,
            where=where
        )
        
        # Enrichir les résultats avec des informations de formation
        enriched = []
        for result in results:
            meta = result["metadata"]
            enriched.append({
                "chunk_id": result["chunk_id"],
                "similarity": result["similarity_score"],
                "formation_id": meta.get("formation_id"),
                "intitule": meta.get("intitule"),
                "etablissement": meta.get("etablissement"),
                "ville": meta.get("ville"),
                "domaine": meta.get("domaine"),
                "field": meta.get("field"),
                "keywords": meta.get("keywords", []),
                "section": meta.get("section"),
                "content_snippet": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"]
            })
        
        return enriched
    
    def get_formation_context(
        self,
        formation_id: int,
        top_k: int = 10
    ) -> Dict:
        """
        Récupérer le contexte complet d'une formation
        
        Args:
            formation_id: ID de la formation
            top_k: Nombre de chunks à récupérer
        
        Returns:
            Dict avec tous les chunks et métadonnées
        """
        
        where = {"formation_id": {"$eq": formation_id}}
        
        try:
            results = self.vectorstore.collection.get(
                where=where,
                limit=top_k
            )
            
            if not results or not results["ids"]:
                return None
            
            # Grouper par field
            context = {}
            for chunk_id, metadata, document in zip(
                results["ids"],
                results["metadatas"],
                results["documents"]
            ):
                field = metadata.get("field", "unknown")
                if field not in context:
                    context[field] = []
                
                context[field].append({
                    "chunk_id": chunk_id,
                    "content": document,
                    "section": metadata.get("section")
                })
            
            return context
        except Exception as e:
            logger.error(f"Error getting formation context: {e}")
            return None
    
    def get_stats(self) -> Dict:
        """Obtenir les statistiques de l'index"""
        
        try:
            count = self.vectorstore.get_collection_count()
            
            # Essayer de compter les formations uniques
            results = self.vectorstore.collection.get()
            formation_ids = set()
            if results["metadatas"]:
                for metadata in results["metadatas"]:
                    formation_ids.add(metadata.get("formation_id"))
            
            return {
                "total_chunks": count,
                "unique_formations": len(formation_ids),
                "embedding_model": self.embedding_model.get_model_name(),
                "vector_dimension": self.embedding_model.get_dimension()
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "total_chunks": 0,
                "unique_formations": 0,
                "error": str(e)
            }

"""
COMMIT 8: Vector Embeddings for RAG
Modèles d'embeddings pour la recherche sémantique

Implémente:
1. HuggingFace embeddings (sentence-transformers)
2. Embedding caching pour performance
3. Similarity search utilities
4. Batch processing pour large datasets
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
from abc import ABC, abstractmethod
import logging
from functools import lru_cache
import json

logger = logging.getLogger(__name__)


class EmbeddingModel(ABC):
    """Interface abstraite pour les modèles d'embeddings"""
    
    @abstractmethod
    def embed(self, text: str) -> np.ndarray:
        """Embedding d'un texte unique"""
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Embeddings d'une batch de textes"""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Dimension des embeddings"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Nom du modèle"""
        pass


class MockEmbeddingModel(EmbeddingModel):
    """
    Mock embedding model pour développement/test
    Génère des embeddings déterministes basés sur le hash du texte
    """
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.model_name = f"mock-embedding-{dimension}d"
        logger.info(f"Initializing {self.model_name}")
    
    def embed(self, text: str) -> np.ndarray:
        """Générer un embedding mock"""
        
        # Utiliser le hash du texte pour reproductibilité
        hash_value = hash(text)
        np.random.seed(abs(hash_value) % (2**31))
        
        embedding = np.random.randn(self.dimension).astype(np.float32)
        # Normaliser
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Embeddings en batch"""
        return [self.embed(text) for text in texts]
    
    def get_dimension(self) -> int:
        return self.dimension
    
    def get_model_name(self) -> str:
        return self.model_name


class HuggingFaceEmbeddingModel(EmbeddingModel):
    """
    Modèle d'embeddings HuggingFace (sentence-transformers)
    Compatible avec Multilingual models pour le français
    """
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        device: str = "cpu",
        cache_enabled: bool = True
    ):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            logger.warning("sentence-transformers not installed, falling back to mock")
            self.model = None
            self.dimension = 384
            self.model_name = model_name
            return
        
        self.model_name = model_name
        self.cache_enabled = cache_enabled
        self.model = None
        self.device = device
        
        try:
            logger.info(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name, device=device)
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded. Dimension: {self.dimension}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}. Using mock model.")
            self.model = None
            self.dimension = 384
    
    def embed(self, text: str) -> np.ndarray:
        """Embedding d'un texte"""
        
        if self.model is None:
            # Fallback à mock
            return self._mock_embed(text)
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.astype(np.float32)
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            return self._mock_embed(text)
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[np.ndarray]:
        """Embeddings en batch avec optimisation"""
        
        if self.model is None:
            return [self._mock_embed(text) for text in texts]
        
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            return [e.astype(np.float32) for e in embeddings]
        except Exception as e:
            logger.error(f"Error in batch embedding: {e}")
            return [self._mock_embed(text) for text in texts]
    
    def get_dimension(self) -> int:
        return self.dimension
    
    def get_model_name(self) -> str:
        return self.model_name
    
    @staticmethod
    def _mock_embed(text: str, dimension: int = 384) -> np.ndarray:
        """Embedding mock pour fallback"""
        hash_value = hash(text)
        np.random.seed(abs(hash_value) % (2**31))
        embedding = np.random.randn(dimension).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)
        return embedding


class EmbeddingCache:
    """Cache pour les embeddings"""
    
    def __init__(self, max_size: int = 10000):
        self.cache: Dict[str, np.ndarray] = {}
        self.max_size = max_size
    
    def get(self, text: str) -> Optional[np.ndarray]:
        """Récupérer un embedding du cache"""
        return self.cache.get(text)
    
    def set(self, text: str, embedding: np.ndarray):
        """Stocker un embedding dans le cache"""
        if len(self.cache) < self.max_size:
            self.cache[text] = embedding
        else:
            # Simple FIFO si cache plein
            if len(self.cache) > 0:
                first_key = next(iter(self.cache))
                del self.cache[first_key]
            self.cache[text] = embedding
    
    def clear(self):
        """Vider le cache"""
        self.cache.clear()
    
    def size(self) -> int:
        """Taille du cache"""
        return len(self.cache)


class SimilaritySearch:
    """Utilitaires pour la recherche de similarité"""
    
    @staticmethod
    def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calcul de similarité cosinus"""
        
        # Normaliser les vecteurs
        vec1_norm = vec1 / np.linalg.norm(vec1)
        vec2_norm = vec2 / np.linalg.norm(vec2)
        
        # Similarité cosinus
        return float(np.dot(vec1_norm, vec2_norm))
    
    @staticmethod
    def euclidean_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Distance euclidienne"""
        return float(np.linalg.norm(vec1 - vec2))
    
    @staticmethod
    def find_similar(
        query_embedding: np.ndarray,
        candidate_embeddings: List[np.ndarray],
        top_k: int = 5,
        metric: str = "cosine"
    ) -> List[Tuple[int, float]]:
        """
        Trouver les top-k embeddings similaires
        
        Returns:
            List of (index, score) tuples
        """
        
        scores = []
        
        for idx, candidate in enumerate(candidate_embeddings):
            if metric == "cosine":
                score = SimilaritySearch.cosine_similarity(query_embedding, candidate)
            elif metric == "euclidean":
                score = -SimilaritySearch.euclidean_distance(query_embedding, candidate)
            else:
                raise ValueError(f"Unknown metric: {metric}")
            
            scores.append((idx, score))
        
        # Trier par score (descending)
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores[:top_k]
    
    @staticmethod
    def batch_similarity(
        query_embedding: np.ndarray,
        corpus_embeddings: np.ndarray,  # (N, D) matrix
        metric: str = "cosine"
    ) -> np.ndarray:
        """
        Calcul de similarité en batch (vectorisé)
        
        Args:
            query_embedding: (D,) vector
            corpus_embeddings: (N, D) matrix
            metric: "cosine" ou "euclidean"
        
        Returns:
            (N,) array de scores
        """
        
        if metric == "cosine":
            # Normaliser
            query_norm = query_embedding / np.linalg.norm(query_embedding)
            corpus_norm = corpus_embeddings / np.linalg.norm(corpus_embeddings, axis=1, keepdims=True)
            
            # Produit scalaire
            return np.dot(corpus_norm, query_norm)
        
        elif metric == "euclidean":
            # Distance euclidienne vectorisée
            distances = np.linalg.norm(corpus_embeddings - query_embedding, axis=1)
            return -distances
        
        else:
            raise ValueError(f"Unknown metric: {metric}")


class EmbeddingStore:
    """Stockage des embeddings (in-memory pour RAG)"""
    
    def __init__(self):
        self.embeddings: Dict[str, np.ndarray] = {}  # chunk_id -> embedding
        self.metadata: Dict[str, Dict] = {}  # chunk_id -> metadata
        self.corpus: List[str] = []  # chunk_ids in order
        self.corpus_embeddings: Optional[np.ndarray] = None  # (N, D) matrix
    
    def add(self, chunk_id: str, embedding: np.ndarray, metadata: Dict):
        """Ajouter un embedding"""
        self.embeddings[chunk_id] = embedding
        self.metadata[chunk_id] = metadata
        self.corpus.append(chunk_id)
        
        # Rebuild corpus matrix
        self._rebuild_corpus_matrix()
    
    def add_batch(
        self,
        chunk_ids: List[str],
        embeddings: List[np.ndarray],
        metadatas: List[Dict]
    ):
        """Ajouter plusieurs embeddings"""
        for chunk_id, embedding, metadata in zip(chunk_ids, embeddings, metadatas):
            self.embeddings[chunk_id] = embedding
            self.metadata[chunk_id] = metadata
            self.corpus.append(chunk_id)
        
        self._rebuild_corpus_matrix()
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        metric: str = "cosine"
    ) -> List[Tuple[str, float, Dict]]:
        """
        Rechercher les top-k chunks similaires
        
        Returns:
            List of (chunk_id, score, metadata) tuples
        """
        
        if self.corpus_embeddings is None or len(self.corpus) == 0:
            return []
        
        # Recherche vectorisée
        scores = SimilaritySearch.batch_similarity(
            query_embedding,
            self.corpus_embeddings,
            metric=metric
        )
        
        # Top-k indices
        top_indices = np.argsort(-scores)[:top_k]
        
        results = []
        for idx in top_indices:
            chunk_id = self.corpus[idx]
            score = float(scores[idx])
            metadata = self.metadata[chunk_id]
            results.append((chunk_id, score, metadata))
        
        return results
    
    def _rebuild_corpus_matrix(self):
        """Reconstruire la matrice corpus"""
        if len(self.corpus) == 0:
            self.corpus_embeddings = None
        else:
            embeddings = [self.embeddings[cid] for cid in self.corpus]
            self.corpus_embeddings = np.stack(embeddings)
    
    def clear(self):
        """Vider le store"""
        self.embeddings.clear()
        self.metadata.clear()
        self.corpus.clear()
        self.corpus_embeddings = None
    
    def size(self) -> int:
        """Nombre de chunks stockés"""
        return len(self.corpus)

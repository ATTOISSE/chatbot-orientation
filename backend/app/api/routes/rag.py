"""
COMMIT 9: RAG Endpoints API
Endpoints pour indexation vectorielle et recherche sémantique
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.core.auth import get_current_user
from app.models import User, Formation
from app.ml.vectorstore import ChromaDBVectorStore, FormationVectorIndexer
from app.rag.embeddings import HuggingFaceEmbeddingModel, MockEmbeddingModel
from app.rag.chunking import DocumentChunker
from app.rag.pipeline import FormationRAGIndexer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/rag", tags=["RAG"])

# Global instances
_vectorstore = None
_indexer = None
_embedding_model = None
_rag_indexer = None


def get_vectorstore() -> ChromaDBVectorStore:
    """Récupérer l'instance ChromaDB"""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = ChromaDBVectorStore(
            persist_directory="./data/chromadb",
            collection_name="formations"
        )
    return _vectorstore


def get_embedding_model():
    """Récupérer le modèle d'embeddings"""
    global _embedding_model
    if _embedding_model is None:
        try:
            _embedding_model = HuggingFaceEmbeddingModel()
        except Exception as e:
            logger.warning(f"HuggingFace model failed: {e}, using mock")
            _embedding_model = MockEmbeddingModel()
    return _embedding_model


def get_indexer() -> FormationVectorIndexer:
    """Récupérer l'indexeur de formations"""
    global _indexer
    if _indexer is None:
        vectorstore = get_vectorstore()
        embedding_model = get_embedding_model()
        _indexer = FormationVectorIndexer(vectorstore, embedding_model)
    return _indexer


def get_rag_indexer(db: Session):
    """Récupérer l'indexeur RAG complet"""
    global _rag_indexer
    if _rag_indexer is None:
        embedding_model = get_embedding_model()
        _rag_indexer = FormationRAGIndexer(
            embedding_model=embedding_model,
            db_session=db
        )
    return _rag_indexer


# Schemas
class IndexStatusResponse(BaseModel):
    status: str
    total_chunks: int
    unique_formations: int
    embedding_model: str
    vector_dimension: int


class SearchResultChunk(BaseModel):
    formation_id: int
    intitule: str
    etablissement: str
    ville: str
    domaine: str
    field: str
    keywords: List[str]
    similarity: float
    content_snippet: str


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    top_k: int = Field(5, ge=1, le=20)
    filter_domain: Optional[str] = None
    filter_city: Optional[str] = None


class SemanticSearchResponse(BaseModel):
    query: str
    results_count: int
    results: List[SearchResultChunk]


class IndexFormationsRequest(BaseModel):
    force_reindex: bool = False
    batch_size: int = Field(50, ge=10, le=200)


class IndexFormationsResponse(BaseModel):
    status: str
    indexed_formations: int
    total_chunks: int
    duration_seconds: float


# Endpoints

@router.get("/status", response_model=IndexStatusResponse)
async def get_index_status():
    """
    Récupérer le statut de l'index vectoriel
    
    Returns:
        Statistiques de l'index
    """
    indexer = get_indexer()
    stats = indexer.get_stats()
    
    return IndexStatusResponse(
        status="ready" if stats["total_chunks"] > 0 else "empty",
        total_chunks=stats["total_chunks"],
        unique_formations=stats["unique_formations"],
        embedding_model=stats["embedding_model"],
        vector_dimension=stats["vector_dimension"]
    )


@router.post("/search", response_model=SemanticSearchResponse)
async def semantic_search(request: SemanticSearchRequest):
    """
    Recherche sémantique des formations
    
    Utilise les embeddings pour trouver les formations similaires à la requête.
    
    Args:
        query: Texte de recherche (ex: "formation en informatique")
        top_k: Nombre de résultats (1-20)
        filter_domain: Domaine optionnel (ex: "Informatique")
        filter_city: Ville optionnelle (ex: "Dakar")
    
    Returns:
        Formations les plus pertinentes avec scores de similarité
    """
    
    try:
        indexer = get_indexer()
        
        results = indexer.search_formations(
            query=request.query,
            top_k=request.top_k,
            filter_by_domain=request.filter_domain,
            filter_by_city=request.filter_city
        )
        
        return SemanticSearchResponse(
            query=request.query,
            results_count=len(results),
            results=[SearchResultChunk(**r) for r in results]
        )
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/index-formations", response_model=IndexFormationsResponse)
async def index_formations(
    request: IndexFormationsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Indexer les formations dans ChromaDB
    
    Route admin seulement. Indexe toutes les formations de la base de données.
    
    Args:
        force_reindex: Réinitialiser l'index existant
        batch_size: Taille des batches pour embeddings
    
    Returns:
        Résumé de l'indexation
    """
    
    # Vérifier les permissions
    if not hasattr(current_user, 'role') or current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        import time
        start_time = time.time()
        
        # Réinitialiser si demandé
        if request.force_reindex:
            vectorstore = get_vectorstore()
            vectorstore.reset()
            logger.info("Vector index reset")
        
        # Récupérer l'indexeur RAG
        rag_indexer = get_rag_indexer(db)
        
        # Indexer les formations
        logger.info("Starting formation indexing...")
        indexed_count = rag_indexer.index_all_formations(
            batch_size=request.batch_size
        )
        
        # Récupérer les stats finales
        indexer = get_indexer()
        stats = indexer.get_stats()
        
        duration = time.time() - start_time
        
        return IndexFormationsResponse(
            status="success",
            indexed_formations=indexed_count,
            total_chunks=stats["total_chunks"],
            duration_seconds=round(duration, 2)
        )
    
    except Exception as e:
        logger.error(f"Indexing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Indexing failed: {str(e)}"
        )


@router.post("/chat")
async def rag_chat(
    query: str,
    top_k: int = 3,
    db: Session = Depends(get_db)
):
    """
    Chat avec contexte RAG
    
    Utilise le contexte des formations pour répondre aux questions.
    
    Args:
        query: Question de l'utilisateur
        top_k: Nombre de formations contextuelles
    
    Returns:
        Réponse avec contexte
    """
    
    try:
        indexer = get_indexer()
        
        # Chercher les formations pertinentes
        results = indexer.search_formations(query, top_k=top_k)
        
        if not results:
            return {
                "query": query,
                "response": "Je n'ai pas trouvé de formations pertinentes pour votre question.",
                "context": []
            }
        
        # Construire le contexte
        context = []
        for result in results:
            context.append({
                "formation": result["intitule"],
                "etablissement": result["etablissement"],
                "ville": result["ville"],
                "domaine": result["domaine"],
                "relevance": f"{result['similarity']*100:.1f}%"
            })
        
        # Simple response generation (peut être amélioré avec LLM)
        response = f"Basé sur {len(results)} formations pertinentes, je vous recommande: "
        response += ", ".join([f"{r['formation']} ({r['etablissement']})" for r in context[:2]])
        
        return {
            "query": query,
            "response": response,
            "context_count": len(context),
            "context": context
        }
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )


@router.get("/formation/{formation_id}/context")
async def get_formation_context(
    formation_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupérer le contexte complet d'une formation
    
    Args:
        formation_id: ID de la formation
    
    Returns:
        Tous les chunks indexés pour la formation
    """
    
    try:
        # Vérifier que la formation existe
        formation = db.query(Formation).filter(Formation.id == formation_id).first()
        if not formation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Formation not found"
            )
        
        # Récupérer le contexte
        indexer = get_indexer()
        context = indexer.get_formation_context(formation_id, top_k=20)
        
        if not context:
            return {
                "formation_id": formation_id,
                "intitule": formation.intitule,
                "context": {}
            }
        
        return {
            "formation_id": formation_id,
            "intitule": formation.intitule,
            "context": context
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Context retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve context: {str(e)}"
        )

"""
COMMIT 12: LLM Chat Endpoints
Routes pour les réponses améliorées avec LLM local
"""

import logging
import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.core.auth import get_current_user
from app.models import User
from app.ml.llm_service import LLMService, LLMConfig, PromptBuilder
from app.services.chatbot_service import ChatbotService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/llm", tags=["LLM Chat"])

# Global LLM service instance
_llm_service = None


def get_llm_service() -> LLMService:
    """Récupérer l'instance LLM service"""
    global _llm_service
    if _llm_service is None:
        config = LLMConfig(
            model_name="llama2",
            api_url="http://localhost:11434",
            temperature=0.7,
            max_tokens=512
        )
        _llm_service = LLMService(config)
    return _llm_service


# Schemas
class LLMGenerateRequest(BaseModel):
    """Requête de génération de texte"""
    prompt: str = Field(..., min_length=1, max_length=2000)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=2048)


class LLMChatRequest(BaseModel):
    """Requête pour chat avec LLM"""
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[int] = None
    context: Optional[str] = None
    use_formations: bool = Field(True, description="Include formation search context")


class LLMStatusResponse(BaseModel):
    """Status du service LLM"""
    available: bool
    model: str
    type: str
    message: str


class LLMGenerateResponse(BaseModel):
    """Réponse de génération"""
    generated_text: str
    model: str
    tokens_used: int


# Endpoints

@router.get("/status")
async def llm_status(llm: LLMService = Depends(get_llm_service)) -> LLMStatusResponse:
    """
    Vérifier le statut du service LLM
    
    Returns:
        Status du LLM (disponibilité, modèle utilisé)
    """
    
    info = llm.get_info()
    available = llm.is_available()
    
    return LLMStatusResponse(
        available=available,
        model=llm.get_model_name(),
        type=info.get("type", "unknown"),
        message="LLM available" if available else "Using mock LLM"
    )


@router.post("/generate")
async def generate_text(
    request: LLMGenerateRequest,
    current_user: User = Depends(get_current_user),
    llm: LLMService = Depends(get_llm_service)
) -> LLMGenerateResponse:
    """
    Générer du texte avec le LLM
    
    Args:
        prompt: Texte d'entrée
        temperature: Paramètre de température (0-2)
        max_tokens: Nombre max de tokens
    
    Returns:
        Texte généré
    """
    
    try:
        # Générer le texte
        generated = llm.generate_response(
            request.prompt,
            temperature=request.temperature,
            num_predict=request.max_tokens
        )
        
        if not generated:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="LLM generation failed"
            )
        
        return LLMGenerateResponse(
            generated_text=generated,
            model=llm.get_model_name(),
            tokens_used=len(generated.split())
        )
    
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )


@router.post("/generate/stream")
async def generate_text_stream(
    request: LLMGenerateRequest,
    current_user: User = Depends(get_current_user),
    llm: LLMService = Depends(get_llm_service)
):
    """
    Générer du texte en streaming avec le LLM
    
    Args:
        prompt: Texte d'entrée
        temperature: Paramètre de température
        max_tokens: Nombre max de tokens
    
    Returns:
        StreamingResponse avec chunks de texte
    """
    
    async def text_generator():
        """Générateur de texte en streaming"""
        try:
            async for chunk in llm.stream_response(
                request.prompt,
                temperature=request.temperature,
                num_predict=request.max_tokens
            ):
                yield chunk
        
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"Error: {str(e)}"
    
    return StreamingResponse(
        text_generator(),
        media_type="text/plain"
    )


@router.post("/chat")
async def llm_chat(
    request: LLMChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service)
):
    """
    Chat avec réponses générées par LLM
    
    Combine:
    1. Recherche de formations (RAG)
    2. Génération de réponse avec LLM
    3. Stockage en base de données
    
    Args:
        message: Message de l'utilisateur
        conversation_id: ID de conversation existante
        context: Contexte additionnel
        use_formations: Inclure les résultats de recherche
    
    Returns:
        Réponse générée par LLM
    """
    
    try:
        chatbot_service = ChatbotService(db)
        
        # Créer ou récupérer la conversation
        if request.conversation_id is None:
            conversation = chatbot_service.create_conversation(
                current_user.id,
                context=request.context
            )
        else:
            conversation = chatbot_service.get_conversation(
                request.conversation_id,
                current_user.id
            )
            if not conversation:
                raise ValueError("Conversation not found")
        
        # Ajouter le message utilisateur
        from app.models.conversation import MessageRole
        chatbot_service.add_message(
            conversation.id,
            MessageRole.USER,
            request.message
        )
        
        # Construire le prompt
        if request.use_formations:
            formations = chatbot_service.search_formations_by_query(
                request.message,
                top_k=5
            )
            prompt = PromptBuilder.build_context_prompt(formations, request.message)
        else:
            prompt = PromptBuilder.build_chat_prompt(request.message)
        
        # Générer la réponse
        llm_response = llm.generate_response(prompt)
        
        if not llm_response:
            llm_response = (
                "Je suis désolé, je n'ai pas pu générer une réponse. "
                "Veuillez réessayer."
            )
        
        # Ajouter la réponse à la base de données
        assistant_message = chatbot_service.add_message(
            conversation.id,
            MessageRole.ASSISTANT,
            llm_response
        )
        
        return {
            "conversation_id": conversation.id,
            "message": llm_response,
            "model": llm.get_model_name(),
            "message_id": assistant_message.id
        }
    
    except Exception as e:
        logger.error(f"LLM chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )


@router.post("/chat/stream")
async def llm_chat_stream(
    request: LLMChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    llm: LLMService = Depends(get_llm_service)
):
    """
    Chat avec réponses en streaming du LLM
    
    Combine RAG + LLM streaming pour l'expérience optimale.
    
    Args:
        message: Message de l'utilisateur
        conversation_id: ID de conversation existante
        context: Contexte additionnel
        use_formations: Inclure les résultats de recherche
    
    Returns:
        StreamingResponse avec chunks de réponse
    """
    
    async def chat_generator():
        """Générateur de réponse en streaming"""
        try:
            chatbot_service = ChatbotService(db)
            
            # Créer ou récupérer la conversation
            if request.conversation_id is None:
                conversation = chatbot_service.create_conversation(
                    current_user.id,
                    context=request.context
                )
            else:
                conversation = chatbot_service.get_conversation(
                    request.conversation_id,
                    current_user.id
                )
                if not conversation:
                    raise ValueError("Conversation not found")
            
            # Ajouter le message utilisateur
            from app.models.conversation import MessageRole
            chatbot_service.add_message(
                conversation.id,
                MessageRole.USER,
                request.message
            )
            
            # Construire le prompt
            if request.use_formations:
                formations = chatbot_service.search_formations_by_query(
                    request.message,
                    top_k=5
                )
                prompt = PromptBuilder.build_context_prompt(formations, request.message)
            else:
                prompt = PromptBuilder.build_chat_prompt(request.message)
            
            # Générer et envoyer en streaming
            full_response = ""
            async for chunk in llm.stream_response(prompt):
                full_response += chunk
                yield chunk
                await asyncio.sleep(0.01)
            
            # Sauvegarder la réponse complète
            if full_response:
                chatbot_service.add_message(
                    conversation.id,
                    MessageRole.ASSISTANT,
                    full_response
                )
        
        except Exception as e:
            logger.error(f"Stream chat error: {e}")
            yield f"Error: {str(e)}"
    
    return StreamingResponse(
        chat_generator(),
        media_type="text/plain"
    )


@router.get("/info")
async def llm_info(llm: LLMService = Depends(get_llm_service)):
    """
    Obtenir les infos détaillées du service LLM
    
    Returns:
        Information sur le modèle et sa configuration
    """
    
    return llm.get_info()


@router.post("/health")
async def llm_health(llm: LLMService = Depends(get_llm_service)):
    """
    Health check pour le service LLM
    
    Returns:
        Status du service
    """
    
    available = llm.is_available()
    
    return {
        "status": "healthy" if available else "degraded",
        "llm_available": available,
        "model": llm.get_model_name(),
        "fallback": "mock" if not available else "none"
    }

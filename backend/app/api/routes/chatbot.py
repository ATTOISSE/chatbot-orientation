"""
COMMIT 10: Chatbot API Endpoints
Routes pour les conversations et le chat avec RAG
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user
from app.models import User
from app.schemas.chatbot import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationDetailResponse,
    ConversationListResponse,
    MessageCreate,
    MessageResponse
)
from app.services.chatbot_service import ChatbotService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chatbot", tags=["Chatbot"])


# Dependencies
def get_chatbot_service(db: Session = Depends(get_db)) -> ChatbotService:
    """Récupérer l'instance du service chatbot"""
    return ChatbotService(db)


# Endpoints

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Envoyer un message au chatbot
    
    Crée une nouvelle conversation si conversation_id est None,
    ou ajoute le message à une conversation existante.
    
    Args:
        message: Texte du message (3-5000 caractères)
        conversation_id: ID de conversation existante (optionnel)
        context: Contexte pour nouvelle conversation (optionnel)
    
    Returns:
        Réponse du chatbot avec sources RAG
    """
    
    try:
        result = service.process_chat_message(
            user_message=request.message,
            user_id=current_user.id,
            conversation_id=request.conversation_id,
            context=request.context
        )
        
        return ChatResponse(
            conversation_id=result["conversation_id"],
            user_message=result["user_message"],
            assistant_message=result["assistant_message"],
            sources=result["sources"],
            confidence=result["confidence"],
            tokens_used=0  # À implémenter avec tokenizer
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}"
        )


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate,
    current_user: User = Depends(get_current_user),
    service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Créer une nouvelle conversation
    
    Args:
        title: Titre optionnel
        context: Contexte optionnel
    
    Returns:
        Conversation créée
    """
    
    try:
        conversation = service.create_conversation(
            user_id=current_user.id,
            title=request.title,
            context=request.context
        )
        
        return ConversationResponse.from_orm(conversation)
    
    except Exception as e:
        logger.error(f"Create conversation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create conversation: {str(e)}"
        )


@router.get("/conversations", response_model=List[ConversationListResponse])
async def list_conversations(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Lister les conversations de l'utilisateur
    
    Args:
        limit: Nombre max de conversations (1-100)
    
    Returns:
        Liste des conversations avec métadonnées
    """
    
    try:
        limit = min(limit, 100)
        conversations = service.list_conversations(current_user.id, limit=limit)
        
        result = []
        for conv in conversations:
            result.append(
                ConversationListResponse(
                    id=conv.id,
                    title=conv.title,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    message_count=len(conv.messages)
                )
            )
        
        return result
    
    except Exception as e:
        logger.error(f"List conversations error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list conversations: {str(e)}"
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Récupérer une conversation avec tous ses messages
    
    Args:
        conversation_id: ID de la conversation
    
    Returns:
        Conversation détaillée avec messages
    """
    
    try:
        conversation = service.get_conversation(conversation_id, current_user.id)
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        messages = [MessageResponse.from_orm(m) for m in conversation.messages]
        
        return ConversationDetailResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            context=conversation.context,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=messages
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get conversation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversation: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Supprimer une conversation
    
    Args:
        conversation_id: ID de la conversation
    
    Returns:
        Message de confirmation
    """
    
    try:
        success = service.delete_conversation(conversation_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        return {
            "status": "success",
            "message": f"Conversation {conversation_id} deleted"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete conversation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete conversation: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/summary")
async def get_conversation_summary(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Obtenir un résumé d'une conversation
    
    Args:
        conversation_id: ID de la conversation
    
    Returns:
        Résumé avec statistiques
    """
    
    try:
        conversation = service.get_conversation(conversation_id, current_user.id)
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        summary = service.get_conversation_summary(conversation_id)
        return summary
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve summary: {str(e)}"
        )


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def add_message_to_conversation(
    conversation_id: int,
    request: MessageCreate,
    current_user: User = Depends(get_current_user),
    service: ChatbotService = Depends(get_chatbot_service)
):
    """
    Ajouter un message utilisateur à une conversation
    
    Principalement pour les corrections ou ajouts manuels.
    Le endpoint /chat est recommandé pour le flux normal.
    
    Args:
        conversation_id: ID de la conversation
        content: Contenu du message
    
    Returns:
        Message créé
    """
    
    try:
        conversation = service.get_conversation(conversation_id, current_user.id)
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        from app.models.conversation import MessageRole
        message = service.add_message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=request.content
        )
        
        return MessageResponse.from_orm(message)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add message error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add message: {str(e)}"
        )

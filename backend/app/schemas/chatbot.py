"""
COMMIT 10: Chatbot Conversation Schemas
Pydantic models pour les requêtes/réponses du chatbot
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class MessageRoleEnum(str, Enum):
    """Rôles possibles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageCreate(BaseModel):
    """Créer un message"""
    content: str = Field(..., min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    """Réponse pour un message"""
    id: int
    conversation_id: int
    role: str
    content: str
    rag_sources: Optional[str] = None
    confidence_score: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Créer une conversation"""
    title: Optional[str] = Field(None, max_length=255)
    context: Optional[str] = Field(None, max_length=1000)


class ConversationResponse(BaseModel):
    """Réponse pour une conversation"""
    id: int
    user_id: int
    title: Optional[str]
    context: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConversationDetailResponse(ConversationResponse):
    """Réponse détaillée avec messages"""
    messages: List[MessageResponse] = []


class ChatRequest(BaseModel):
    """Requête de chat"""
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[int] = None  # None = nouvelle conversation
    context: Optional[str] = None  # Contexte pour nouvelle conversation


class ChatResponse(BaseModel):
    """Réponse du chatbot"""
    conversation_id: int
    user_message: str
    assistant_message: str
    sources: List[dict] = []  # Formations référencées
    confidence: float = 0.0
    tokens_used: int = 0


class ConversationListResponse(BaseModel):
    """Liste des conversations"""
    id: int
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    
    class Config:
        from_attributes = True

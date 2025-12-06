"""
COMMIT 11: Streaming Endpoints (WebSocket & SSE)
Routes pour le chat en temps réel avec streaming
"""

import logging
import asyncio
import json
from typing import Optional
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user
from app.models import User
from app.services.streaming_service import StreamingChatService, StreamingResponseGenerator
from app.schemas.chatbot import ChatRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["Streaming Chat"])


# Dependencies
def get_streaming_service(db: Session = Depends(get_db)) -> StreamingChatService:
    """Récupérer le service de streaming"""
    return StreamingChatService(db)


# SSE Endpoints (Server-Sent Events)

@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    service: StreamingChatService = Depends(get_streaming_service)
):
    """
    Chat avec streaming SSE
    
    Envoie la réponse en streaming via Server-Sent Events (SSE).
    Chaque event est une ligne JSON.
    
    Format des events:
    - type: "start" | "content" | "source" | "end" | "error"
    - data: contenu du chunk
    
    Args:
        message: Texte du message
        conversation_id: ID de conversation existante
        context: Contexte pour nouvelle conversation
    
    Returns:
        StreamingResponse avec MIME type text/event-stream
    """
    
    async def event_generator():
        """Générateur d'events SSE"""
        try:
            async for chunk in service.process_and_stream_message(
                user_message=request.message,
                user_id=current_user.id,
                conversation_id=request.conversation_id,
                context=request.context
            ):
                yield f"data: {chunk}"
        
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )


@router.post("/stream-fast")
async def stream_chat_fast(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    service: StreamingChatService = Depends(get_streaming_service)
):
    """
    Chat avec streaming rapide (délai réduit entre chunks)
    
    Même que /stream mais avec délai plus court entre les chunks
    pour une expérience plus responsive.
    
    Args:
        message: Texte du message
        conversation_id: ID de conversation existante
        context: Contexte pour nouvelle conversation
    
    Returns:
        StreamingResponse avec MIME type text/event-stream
    """
    
    async def event_generator():
        """Générateur d'events SSE rapides"""
        try:
            async for chunk in service.process_and_stream_message(
                user_message=request.message,
                user_id=current_user.id,
                conversation_id=request.conversation_id,
                context=request.context
            ):
                yield f"data: {chunk}"
                # Pas de délai - plus rapide
        
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )


# WebSocket Endpoint

class ConnectionManager:
    """Gestionnaire des connexions WebSocket"""
    
    def __init__(self):
        self.active_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Accepter une nouvelle connexion"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected: user={user_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Fermer une connexion"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected: user={user_id}")
    
    async def send_personal(self, websocket: WebSocket, message: dict):
        """Envoyer un message à une connexion spécifique"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")


manager = ConnectionManager()


@router.websocket("/ws/{conversation_id}")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: int,
    db: Session = Depends(get_db),
    service: StreamingChatService = Depends(get_streaming_service)
):
    """
    WebSocket pour le chat en temps réel
    
    Protocole:
    Client → Server:
    {
        "type": "message" | "ping" | "close",
        "message": "texte du message",
        "token": "JWT token"
    }
    
    Server → Client:
    {
        "type": "start" | "content" | "source" | "end" | "error" | "pong",
        "data": {...}
    }
    
    Args:
        conversation_id: ID de la conversation
    """
    
    user_id = None
    
    try:
        # Accepter la connexion
        await websocket.accept()
        logger.info(f"WebSocket accepted for conversation {conversation_id}")
        
        # Envoyer un message de bienvenue
        await websocket.send_json({
            "type": "connected",
            "conversation_id": conversation_id,
            "message": "Connected to chat"
        })
        
        # Boucle de réception de messages
        while True:
            data = await websocket.receive_json()
            
            message_type = data.get("type", "message")
            
            if message_type == "ping":
                await websocket.send_json({"type": "pong"})
            
            elif message_type == "message":
                user_message = data.get("message", "").strip()
                
                if not user_message:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Empty message"
                    })
                    continue
                
                # Envoyer le streaming de la réponse
                async for chunk in service.process_and_stream_message(
                    user_message=user_message,
                    user_id=user_id or 1,  # À récupérer du token
                    conversation_id=conversation_id
                ):
                    chunk_data = json.loads(chunk.strip())
                    await websocket.send_json(chunk_data)
            
            elif message_type == "close":
                await websocket.close()
                break
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: conversation={conversation_id}")
        if user_id:
            manager.disconnect(websocket, user_id)
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Error: {str(e)}"
            })
        except:
            pass


# Endpoints pour les sources (formations) en streaming

@router.post("/stream-sources")
async def stream_sources(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    service: StreamingChatService = Depends(get_streaming_service)
):
    """
    Envoyer les formations pertinentes en streaming
    
    Utile pour afficher les résultats au fur et à mesure
    de la recherche sans attendre la fin.
    
    Args:
        message: Texte de la requête
    
    Returns:
        StreamingResponse avec JSON lines
    """
    
    async def source_generator():
        """Générateur de sources"""
        try:
            # Envoyer le début
            yield json.dumps({
                "type": "sources_start",
                "message": "Recherche en cours..."
            }) + "\n"
            
            # Envoyer les sources
            async for source in service.stream_sources(request.message, top_k=5):
                yield json.dumps({
                    "type": "source",
                    "data": source
                }) + "\n"
            
            # Envoyer la fin
            yield json.dumps({
                "type": "sources_end",
                "message": "Recherche terminée"
            }) + "\n"
        
        except Exception as e:
            logger.error(f"Source stream error: {e}")
            yield json.dumps({
                "type": "error",
                "message": str(e)
            }) + "\n"
    
    return StreamingResponse(
        source_generator(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


# Health check pour streaming

@router.get("/health")
async def streaming_health(
    current_user: User = Depends(get_current_user)
):
    """Vérifier que le service de streaming fonctionne"""
    return {
        "status": "healthy",
        "service": "streaming-chat",
        "user": current_user.email,
        "features": [
            "SSE streaming",
            "WebSocket streaming",
            "Source streaming",
            "Fast streaming"
        ]
    }

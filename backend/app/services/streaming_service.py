"""
COMMIT 11: Streaming Service for Chat
Service pour générer des réponses en streaming (SSE et WebSocket)
"""

import logging
import asyncio
import json
from typing import AsyncGenerator, List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.services.chatbot_service import ChatbotService

logger = logging.getLogger(__name__)


class StreamingChatService:
    """Service pour le chat avec streaming des réponses"""
    
    def __init__(self, db: Session):
        self.db = db
        self.chatbot_service = ChatbotService(db)
    
    async def stream_chat_response(
        self,
        user_message: str,
        user_id: int,
        conversation_id: Optional[int] = None,
        context: Optional[str] = None,
        chunk_delay: float = 0.05
    ) -> AsyncGenerator[str, None]:
        """
        Générer une réponse de chat en streaming
        
        Yields des chunks JSON avec:
        - type: "start" | "content" | "source" | "end"
        - data: contenu du chunk
        
        Args:
            user_message: Message de l'utilisateur
            user_id: ID de l'utilisateur
            conversation_id: ID de conversation existante
            context: Contexte pour nouvelle conversation
            chunk_delay: Délai entre les chunks (en secondes)
        
        Yields:
            JSON strings avec les chunks de réponse
        """
        
        try:
            # Signaler le début
            yield json.dumps({
                "type": "start",
                "message": "Initializing response...",
                "timestamp": None
            }) + "\n"
            
            await asyncio.sleep(chunk_delay)
            
            # Rechercher les formations
            results = self.chatbot_service.search_formations_by_query(
                user_message,
                top_k=5
            )
            
            if not results:
                yield json.dumps({
                    "type": "content",
                    "data": "Je n'ai trouvé aucune formation correspondant à votre requête. "
                           "Pouvez-vous préciser votre recherche?",
                    "is_final": True
                }) + "\n"
                
                yield json.dumps({
                    "type": "end",
                    "sources_count": 0,
                    "confidence": 0.0
                }) + "\n"
                
                return
            
            # Générer la réponse avec les sources
            response_parts = ["Basé sur votre recherche, voici mes recommandations:\n\n"]
            sources = []
            max_confidence = 0.0
            
            # Envoyer le message d'introduction
            yield json.dumps({
                "type": "content",
                "data": response_parts[0],
                "is_final": False
            }) + "\n"
            
            await asyncio.sleep(chunk_delay)
            
            # Envoyer chaque formation trouvée
            for idx, result in enumerate(results[:5], 1):
                formation_name = result.get("intitule", "Formation")
                etablissement = result.get("etablissement", "")
                ville = result.get("ville", "")
                domaine = result.get("domaine", "")
                similarity = result.get("similarity", 0.0)
                
                # Construire le texte de la formation
                formation_text = (
                    f"{idx}. **{formation_name}**\n"
                    f"   Établissement: {etablissement}\n"
                    f"   Ville: {ville}\n"
                    f"   Domaine: {domaine}\n"
                    f"   Pertinence: {similarity*100:.1f}%\n\n"
                )
                
                # Envoyer le chunk de formation
                yield json.dumps({
                    "type": "content",
                    "data": formation_text,
                    "is_final": False
                }) + "\n"
                
                # Envoyer la source
                source_data = {
                    "index": idx,
                    "intitule": formation_name,
                    "etablissement": etablissement,
                    "ville": ville,
                    "domaine": domaine,
                    "similarity": similarity,
                    "formation_id": result.get("formation_id")
                }
                
                yield json.dumps({
                    "type": "source",
                    "data": source_data
                }) + "\n"
                
                sources.append(source_data)
                max_confidence = max(max_confidence, similarity)
                
                await asyncio.sleep(chunk_delay)
            
            # Envoyer le message de conclusion
            conclusion = (
                "\nPour plus de détails sur une formation, "
                "vous pouvez consulter notre catalogue complet ou poser une autre question."
            )
            
            yield json.dumps({
                "type": "content",
                "data": conclusion,
                "is_final": True
            }) + "\n"
            
            await asyncio.sleep(chunk_delay)
            
            # Signaler la fin
            yield json.dumps({
                "type": "end",
                "sources_count": len(sources),
                "confidence": max_confidence
            }) + "\n"
        
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            yield json.dumps({
                "type": "error",
                "message": f"Error: {str(e)}"
            }) + "\n"
    
    async def process_and_stream_message(
        self,
        user_message: str,
        user_id: int,
        conversation_id: Optional[int] = None,
        context: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Traiter un message et envoyer la réponse en streaming
        
        1. Ajoute le message utilisateur à la conversation
        2. Génère la réponse en streaming
        3. Ajoute la réponse complète à la conversation
        
        Args:
            user_message: Message de l'utilisateur
            user_id: ID de l'utilisateur
            conversation_id: ID de conversation existante
            context: Contexte pour nouvelle conversation
        
        Yields:
            JSON strings avec streaming events
        """
        
        try:
            # Créer ou récupérer la conversation
            if conversation_id is None:
                conversation = self.chatbot_service.create_conversation(
                    user_id,
                    context=context
                )
            else:
                conversation = self.chatbot_service.get_conversation(
                    conversation_id,
                    user_id
                )
                if not conversation:
                    raise ValueError(f"Conversation {conversation_id} not found")
            
            # Ajouter le message utilisateur
            from app.models.conversation import MessageRole
            self.chatbot_service.add_message(
                conversation.id,
                MessageRole.USER,
                user_message
            )
            
            # Variables pour collecter la réponse complète
            full_response = ""
            all_sources = []
            max_confidence = 0.0
            
            # Envoyer les chunks de la réponse
            async for chunk in self.stream_chat_response(
                user_message,
                user_id,
                conversation.id,
                context
            ):
                yield chunk
                
                # Parser le chunk pour construire la réponse complète
                try:
                    chunk_data = json.loads(chunk.strip())
                    
                    if chunk_data["type"] == "content":
                        full_response += chunk_data.get("data", "")
                    
                    elif chunk_data["type"] == "source":
                        source = chunk_data.get("data", {})
                        all_sources.append(source)
                        max_confidence = max(max_confidence, source.get("similarity", 0))
                    
                except json.JSONDecodeError:
                    pass
            
            # Ajouter la réponse complète à la conversation
            if full_response:
                rag_sources_json = json.dumps(all_sources) if all_sources else None
                self.chatbot_service.add_message(
                    conversation.id,
                    MessageRole.ASSISTANT,
                    full_response,
                    rag_sources=rag_sources_json,
                    confidence_score=max_confidence
                )
                
                logger.info(
                    f"Chat processed: user={user_id}, "
                    f"conversation={conversation.id}, "
                    f"sources={len(all_sources)}"
                )
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            yield json.dumps({
                "type": "error",
                "message": f"Error: {str(e)}"
            }) + "\n"
    
    async def stream_sources(
        self,
        user_message: str,
        top_k: int = 5
    ) -> AsyncGenerator[Dict, None]:
        """
        Envoyer les sources (formations) en streaming
        
        Args:
            user_message: Message de l'utilisateur
            top_k: Nombre de résultats
        
        Yields:
            Dicts avec les formations trouvées
        """
        
        try:
            results = self.chatbot_service.search_formations_by_query(
                user_message,
                top_k=top_k
            )
            
            for idx, result in enumerate(results, 1):
                yield {
                    "index": idx,
                    "intitule": result.get("intitule"),
                    "etablissement": result.get("etablissement"),
                    "ville": result.get("ville"),
                    "domaine": result.get("domaine"),
                    "similarity": result.get("similarity"),
                    "formation_id": result.get("formation_id"),
                    "keywords": result.get("keywords", [])
                }
                
                await asyncio.sleep(0.01)
        
        except Exception as e:
            logger.error(f"Error streaming sources: {e}")
            raise


class StreamingResponseGenerator:
    """Générateur de réponses en streaming avec formatage"""
    
    def __init__(self, chunk_size: int = 50):
        self.chunk_size = chunk_size
    
    async def stream_text(
        self,
        text: str,
        delay: float = 0.01
    ) -> AsyncGenerator[str, None]:
        """
        Envoyer du texte en streaming par chunks
        
        Args:
            text: Texte à envoyer
            delay: Délai entre les chunks
        
        Yields:
            Chunks de texte
        """
        
        for i in range(0, len(text), self.chunk_size):
            chunk = text[i:i + self.chunk_size]
            yield chunk
            await asyncio.sleep(delay)
    
    async def format_and_stream(
        self,
        content: str,
        sources: List[Dict],
        confidence: float
    ) -> AsyncGenerator[str, None]:
        """
        Formatter la réponse et l'envoyer en streaming
        
        Args:
            content: Contenu de la réponse
            sources: Formations référencées
            confidence: Score de confiance
        
        Yields:
            JSON lines avec chunks formatés
        """
        
        # Envoyer le contenu principal
        async for chunk in self.stream_text(content, delay=0.01):
            yield json.dumps({
                "type": "content",
                "chunk": chunk,
                "position": None
            }) + "\n"
        
        # Envoyer les sources
        for source in sources:
            yield json.dumps({
                "type": "source",
                "data": source
            }) + "\n"
        
        # Envoyer les métadonnées finales
        yield json.dumps({
            "type": "metadata",
            "confidence": confidence,
            "sources_count": len(sources)
        }) + "\n"

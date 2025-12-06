"""
COMMIT 10: Chatbot Service
Service pour gérer la logique du chatbot avec RAG
"""

import logging
import json
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.models import Conversation, Message, Formation, User
from app.models.conversation import MessageRole
from app.api.routes.rag import get_indexer, get_embedding_model

logger = logging.getLogger(__name__)


class ChatbotService:
    """Service pour gérer le chatbot et les conversations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.indexer = get_indexer()
        self.embedding_model = get_embedding_model()
    
    def create_conversation(
        self,
        user_id: int,
        title: Optional[str] = None,
        context: Optional[str] = None
    ) -> Conversation:
        """
        Créer une nouvelle conversation
        
        Args:
            user_id: ID de l'utilisateur
            title: Titre optionnel
            context: Contexte optionnel
        
        Returns:
            Nouvelle conversation créée
        """
        
        conversation = Conversation(
            user_id=user_id,
            title=title,
            context=context
        )
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        logger.info(f"Created conversation {conversation.id} for user {user_id}")
        return conversation
    
    def get_conversation(self, conversation_id: int, user_id: int) -> Optional[Conversation]:
        """
        Récupérer une conversation (vérifier ownership)
        
        Args:
            conversation_id: ID de la conversation
            user_id: ID de l'utilisateur
        
        Returns:
            Conversation ou None
        """
        
        return self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
    
    def list_conversations(self, user_id: int, limit: int = 20) -> List[Conversation]:
        """
        Lister les conversations d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            limit: Nombre max de résultats
        
        Returns:
            Liste des conversations
        """
        
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(
            Conversation.updated_at.desc()
        ).limit(limit).all()
    
    def add_message(
        self,
        conversation_id: int,
        role: MessageRole,
        content: str,
        rag_sources: Optional[str] = None,
        confidence_score: Optional[float] = None
    ) -> Message:
        """
        Ajouter un message à une conversation
        
        Args:
            conversation_id: ID de la conversation
            role: Rôle (user/assistant)
            content: Contenu du message
            rag_sources: Sources RAG (JSON string)
            confidence_score: Score de confiance
        
        Returns:
            Message créé
        """
        
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            rag_sources=rag_sources,
            confidence_score=confidence_score
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        # Mettre à jour updated_at de la conversation
        conversation = self.get_conversation(conversation_id, -1)  # Dummy user_id
        if conversation:
            conversation.updated_at = message.created_at
            self.db.commit()
        
        logger.info(f"Added {role} message to conversation {conversation_id}")
        return message
    
    def search_formations_by_query(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Rechercher les formations pertinentes pour une requête
        
        Args:
            query: Texte de la requête
            top_k: Nombre de résultats
        
        Returns:
            Liste des formations pertinentes
        """
        
        try:
            results = self.indexer.search_formations(query, top_k=top_k)
            return results
        except Exception as e:
            logger.error(f"Error searching formations: {e}")
            return []
    
    def generate_response(
        self,
        user_message: str,
        conversation_id: int
    ) -> Tuple[str, List[Dict], float]:
        """
        Générer une réponse du chatbot
        
        Args:
            user_message: Message de l'utilisateur
            conversation_id: ID de la conversation
        
        Returns:
            Tuple (response_text, sources, confidence)
        """
        
        try:
            # Chercher les formations pertinentes
            results = self.search_formations_by_query(user_message, top_k=5)
            
            if not results:
                return (
                    "Je n'ai trouvé aucune formation correspondant à votre requête. "
                    "Pouvez-vous préciser votre recherche?",
                    [],
                    0.0
                )
            
            # Construire la réponse avec contexte
            response_parts = ["Basé sur votre recherche, voici mes recommandations:\n"]
            sources = []
            confidence = 0.0
            
            for idx, result in enumerate(results[:3], 1):
                formation_name = result.get("intitule", "Formation")
                etablissement = result.get("etablissement", "")
                ville = result.get("ville", "")
                domaine = result.get("domaine", "")
                similarity = result.get("similarity", 0.0)
                
                response_parts.append(
                    f"{idx}. **{formation_name}**\n"
                    f"   Établissement: {etablissement}\n"
                    f"   Ville: {ville}\n"
                    f"   Domaine: {domaine}\n"
                )
                
                sources.append({
                    "intitule": formation_name,
                    "etablissement": etablissement,
                    "ville": ville,
                    "domaine": domaine,
                    "similarity": similarity
                })
                
                confidence = max(confidence, similarity)
            
            response_parts.append(
                "\nPour plus de détails sur une formation, "
                "vous pouvez consulter notre catalogue complet ou poser une autre question."
            )
            
            response_text = "\n".join(response_parts)
            
            return response_text, sources, confidence
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return (
                f"Désolé, une erreur s'est produite lors de la génération de la réponse. "
                f"Veuillez réessayer.",
                [],
                0.0
            )
    
    def process_chat_message(
        self,
        user_message: str,
        user_id: int,
        conversation_id: Optional[int] = None,
        context: Optional[str] = None
    ) -> Dict:
        """
        Traiter un message de chat complètement
        
        Args:
            user_message: Message de l'utilisateur
            user_id: ID de l'utilisateur
            conversation_id: ID de conversation existante (ou None pour nouvelle)
            context: Contexte optionnel pour nouvelle conversation
        
        Returns:
            Dict avec les détails de la réponse
        """
        
        # Créer ou récupérer la conversation
        if conversation_id is None:
            conversation = self.create_conversation(user_id, context=context)
        else:
            conversation = self.get_conversation(conversation_id, user_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")
        
        # Ajouter le message utilisateur
        self.add_message(
            conversation.id,
            MessageRole.USER,
            user_message
        )
        
        # Générer la réponse
        response_text, sources, confidence = self.generate_response(
            user_message,
            conversation.id
        )
        
        # Ajouter la réponse assistant
        rag_sources_json = json.dumps(sources) if sources else None
        assistant_message = self.add_message(
            conversation.id,
            MessageRole.ASSISTANT,
            response_text,
            rag_sources=rag_sources_json,
            confidence_score=confidence
        )
        
        return {
            "conversation_id": conversation.id,
            "user_message": user_message,
            "assistant_message": response_text,
            "sources": sources,
            "confidence": confidence,
            "message_id": assistant_message.id
        }
    
    def get_conversation_summary(self, conversation_id: int) -> Dict:
        """
        Obtenir un résumé de conversation
        
        Args:
            conversation_id: ID de la conversation
        
        Returns:
            Dict avec résumé
        """
        
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        
        if not conversation:
            return None
        
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).all()
        
        return {
            "id": conversation.id,
            "title": conversation.title,
            "context": conversation.context,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "message_count": len(messages),
            "user_messages": sum(1 for m in messages if m.role == MessageRole.USER),
            "assistant_messages": sum(1 for m in messages if m.role == MessageRole.ASSISTANT)
        }
    
    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        """
        Supprimer une conversation (vérifier ownership)
        
        Args:
            conversation_id: ID de la conversation
            user_id: ID de l'utilisateur
        
        Returns:
            True si suppression réussie
        """
        
        conversation = self.get_conversation(conversation_id, user_id)
        
        if not conversation:
            return False
        
        self.db.delete(conversation)
        self.db.commit()
        
        logger.info(f"Deleted conversation {conversation_id} for user {user_id}")
        return True

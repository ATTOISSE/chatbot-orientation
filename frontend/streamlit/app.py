"""
COMMIT 13: Streamlit Frontend - Main App
Interface utilisateur pour EduGuide Chatbot avec Streamlit
"""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Optional, List, Dict

# Configuration Streamlit
st.set_page_config(
    page_title="EduGuide - Chatbot Orientation",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stChatMessage--user {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
    }
    .stChatMessage--assistant {
        background-color: #f5f5f5;
        border-left: 4px solid #4CAF50;
    }
    .source-card {
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }
    .confidence-score {
        color: #666;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = st.secrets.get("api_url", "http://localhost:8000")
API_ENDPOINTS = {
    "login": f"{API_BASE_URL}/api/v1/auth/login",
    "chat": f"{API_BASE_URL}/api/v1/chatbot/chat",
    "stream": f"{API_BASE_URL}/api/v1/chat/stream",
    "conversations": f"{API_BASE_URL}/api/v1/chatbot/conversations",
    "get_conversation": f"{API_BASE_URL}/api/v1/chatbot/conversations/",
}

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.user_email = None
    st.session_state.conversations = []
    st.session_state.current_conversation_id = None
    st.session_state.messages = []


def login(email: str, password: str) -> bool:
    """Authentifier l'utilisateur"""
    try:
        response = requests.post(
            API_ENDPOINTS["login"],
            json={"email": email, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.user_email = email
            st.session_state.authenticated = True
            return True
        else:
            st.error(f"Login failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Connection error: {e}")
        return False


def logout():
    """Déconnexion"""
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.user_email = None
    st.session_state.conversations = []
    st.session_state.current_conversation_id = None
    st.session_state.messages = []
    st.rerun()


def get_headers() -> Dict:
    """Récupérer les headers avec token"""
    return {
        "Authorization": f"Bearer {st.session_state.token}",
        "Content-Type": "application/json"
    }


def load_conversations():
    """Charger les conversations de l'utilisateur"""
    try:
        response = requests.get(
            API_ENDPOINTS["conversations"],
            headers=get_headers()
        )
        
        if response.status_code == 200:
            st.session_state.conversations = response.json()
        else:
            st.warning("Failed to load conversations")
    except Exception as e:
        st.error(f"Error loading conversations: {e}")


def load_conversation(conversation_id: int):
    """Charger une conversation spécifique"""
    try:
        response = requests.get(
            f"{API_ENDPOINTS['get_conversation']}{conversation_id}",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.current_conversation_id = conversation_id
            st.session_state.messages = data.get("messages", [])
        else:
            st.warning(f"Failed to load conversation {conversation_id}")
    except Exception as e:
        st.error(f"Error loading conversation: {e}")


def create_conversation(title: Optional[str] = None, context: Optional[str] = None) -> Optional[int]:
    """Créer une nouvelle conversation"""
    try:
        response = requests.post(
            API_ENDPOINTS["conversations"],
            headers=get_headers(),
            json={"title": title, "context": context}
        )
        
        if response.status_code == 200:
            data = response.json()
            conversation_id = data["id"]
            st.session_state.current_conversation_id = conversation_id
            st.session_state.messages = []
            load_conversations()
            return conversation_id
        else:
            st.error("Failed to create conversation")
            return None
    except Exception as e:
        st.error(f"Error creating conversation: {e}")
        return None


def send_message(message: str, use_streaming: bool = True) -> bool:
    """Envoyer un message"""
    try:
        # Créer une conversation si nécessaire
        if st.session_state.current_conversation_id is None:
            conv_id = create_conversation()
            if not conv_id:
                return False
        
        if use_streaming:
            return stream_message(message)
        else:
            return regular_message(message)
    
    except Exception as e:
        st.error(f"Error sending message: {e}")
        return False


def stream_message(message: str) -> bool:
    """Envoyer un message avec streaming SSE"""
    try:
        response = requests.post(
            API_ENDPOINTS["stream"],
            headers=get_headers(),
            json={
                "message": message,
                "conversation_id": st.session_state.current_conversation_id
            },
            stream=True
        )
        
        if response.status_code == 200:
            # Créer un placeholder pour la réponse
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                full_response = ""
                sources = []
                
                # Traiter le streaming
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.replace("data: ", ""))
                            
                            if chunk["type"] == "content":
                                full_response += chunk.get("data", "")
                                response_placeholder.markdown(full_response)
                            
                            elif chunk["type"] == "source":
                                sources.append(chunk.get("data", {}))
                        
                        except json.JSONDecodeError:
                            pass
                
                # Afficher les sources
                if sources:
                    st.markdown("### 📚 Sources référencées")
                    for source in sources:
                        with st.expander(f"📖 {source.get('intitule', 'Formation')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Établissement:** {source.get('etablissement')}")
                                st.write(f"**Ville:** {source.get('ville')}")
                            with col2:
                                st.write(f"**Domaine:** {source.get('domaine')}")
                                st.write(f"**Pertinence:** {source.get('similarity', 0)*100:.1f}%")
            
            return True
        else:
            st.error(f"Error: {response.status_code}")
            return False
    
    except Exception as e:
        st.error(f"Streaming error: {e}")
        return False


def regular_message(message: str) -> bool:
    """Envoyer un message sans streaming"""
    try:
        response = requests.post(
            API_ENDPOINTS["chat"],
            headers=get_headers(),
            json={
                "message": message,
                "conversation_id": st.session_state.current_conversation_id
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            
            with st.chat_message("assistant"):
                st.markdown(data["assistant_message"])
                
                if data["sources"]:
                    st.markdown("### 📚 Sources référencées")
                    for idx, source in enumerate(data["sources"], 1):
                        with st.expander(f"📖 {source.get('intitule')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Établissement:** {source.get('etablissement')}")
                                st.write(f"**Ville:** {source.get('ville')}")
                            with col2:
                                st.write(f"**Domaine:** {source.get('domaine')}")
                                st.write(f"**Pertinence:** {source.get('similarity', 0)*100:.1f}%")
            
            return True
        else:
            st.error(f"Error: {response.status_code}")
            return False
    
    except Exception as e:
        st.error(f"Error sending message: {e}")
        return False


# ============================================================================
# SIDEBAR - Authentication & Settings
# ============================================================================

with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    if not st.session_state.authenticated:
        st.markdown("### 🔐 Authentification")
        
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_button"):
            if login(email, password):
                st.success("Connected!")
                st.rerun()
    
    else:
        st.markdown(f"### 👤 Connecté")
        st.write(f"Email: {st.session_state.user_email}")
        
        if st.button("Logout"):
            logout()
        
        st.divider()
        
        st.markdown("### 📋 Conversations")
        
        if st.button("➕ New Conversation"):
            conv_id = create_conversation(title="New Chat")
            if conv_id:
                st.rerun()
        
        load_conversations()
        
        if st.session_state.conversations:
            for conv in st.session_state.conversations:
                conv_title = conv.get("title", f"Chat {conv['id']}")
                
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    if st.button(
                        f"💬 {conv_title}",
                        key=f"conv_{conv['id']}",
                        use_container_width=True
                    ):
                        load_conversation(conv["id"])
                        st.rerun()
        
        st.divider()
        
        st.markdown("### ⚡ Options")
        
        st.session_state.use_streaming = st.checkbox(
            "Use Streaming",
            value=True,
            help="Stream responses in real-time"
        )
        
        st.session_state.api_url = st.text_input(
            "API URL",
            value=API_BASE_URL,
            help="Backend API URL"
        )


# ============================================================================
# MAIN CONTENT
# ============================================================================

if not st.session_state.authenticated:
    st.markdown("# 🎓 EduGuide - Chatbot Orientation")
    st.markdown("### Bienvenue!")
    
    st.markdown("""
    **EduGuide** est votre assistant d'orientation éducative basé sur l'IA.
    
    Connectez-vous pour:
    - 💬 Discuter avec notre chatbot
    - 📚 Découvrir des formations adaptées
    - 🎯 Recevoir des recommandations personnalisées
    - 📊 Gérer votre historique de conversations
    
    Veuillez vous connecter avec vos identifiants.
    """)

else:
    st.markdown("# 🎓 EduGuide - Chatbot Orientation")
    
    # Afficher la conversation actuelle
    if st.session_state.current_conversation_id:
        st.markdown(f"### Conversation #{st.session_state.current_conversation_id}")
        
        # Afficher les messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.markdown(message["content"])
        
        # Input pour nouveau message
        st.divider()
        
        user_input = st.chat_input("Posez votre question...")
        
        if user_input:
            # Afficher le message utilisateur
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Envoyer et traiter la réponse
            if send_message(user_input, use_streaming=st.session_state.use_streaming):
                # Recharger la conversation
                load_conversation(st.session_state.current_conversation_id)
                st.rerun()
    
    else:
        st.info("👈 Sélectionnez une conversation ou créez-en une nouvelle")


def main():
    """Point d'entrée principal de l'application"""
    # L'application s'exécute automatiquement avec Streamlit
    pass


# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.85rem;'>
    EduGuide Chatbot • Powered by FastAPI + Streamlit • 🚀
    </div>
""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()

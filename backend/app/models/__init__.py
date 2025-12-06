"""
Imports centralisés de tous les modèles SQLAlchemy
Pour faciliter les migrations Alembic
"""
from app.database.base import Base
from app.models.user import User
from app.models.conversation import Conversation, Message, MessageRole
from app.models.formation import Formation, Etablissement, Domaine, DataSource, formation_domaine
from app.models.student_profile import StudentProfile

# Export explicite pour imports faciles
__all__ = [
    "Base",
    "User",
    "Conversation",
    "Message",
    "MessageRole",
    "Formation",
    "Etablissement",
    "Domaine",
    "DataSource",
    "StudentProfile",
    "formation_domaine"
]

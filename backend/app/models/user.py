"""
Modèle User - Gestion des utilisateurs
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class User(Base):
    """Modèle utilisateur pour l'authentification et les profils"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    
    # Profil étudiant
    niveau_etude = Column(String(100), nullable=True)  # Bac, Licence, Master, etc.
    domaine_interet = Column(String(255), nullable=True)  # Domaines d'intérêt
    region_preference = Column(String(100), nullable=True)  # Dakar, Thiès, etc.
    
    # Statut et métadonnées
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

"""
Service d'authentification
Logique métier pour la gestion des utilisateurs et de l'authentification
"""
from typing import Optional
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token, create_refresh_token, verify_token
from app.auth.schemas import UserCreate, Token
from app.config import get_settings

settings = get_settings()


class AuthService:
    """Service pour la gestion de l'authentification"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Crée un nouvel utilisateur
        
        Args:
            db: Session de base de données
            user_data: Données de l'utilisateur à créer
            
        Returns:
            User créé
            
        Raises:
            HTTPException: Si l'email ou le username existe déjà
        """
        # Vérifier si l'email existe
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Vérifier si le username existe
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Hasher le mot de passe
        hashed_password = hash_password(user_data.password)
        
        # Créer l'utilisateur
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            niveau_etude=user_data.niveau_etude,
            domaine_interet=user_data.domaine_interet,
            region_preference=user_data.region_preference,
            is_active=True,
            is_superuser=False
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """
        Authentifie un utilisateur
        
        Args:
            db: Session de base de données
            username: Username ou email
            password: Mot de passe en clair
            
        Returns:
            User si authentification réussie, None sinon
        """
        # Chercher par username ou email
        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            return None
        
        # Vérifier le mot de passe
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    @staticmethod
    def create_tokens(user: User) -> Token:
        """
        Crée les tokens d'accès et de rafraîchissement pour un utilisateur
        
        Args:
            user: Utilisateur
            
        Returns:
            Token contenant access_token et refresh_token
        """
        # Données à encoder dans le token
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email
        }
        
        # Créer les tokens
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        refresh_token = create_refresh_token(
            data=token_data,
            expires_delta=timedelta(days=7)
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        """
        Rafraîchit un access token à partir d'un refresh token
        
        Args:
            refresh_token: Refresh token valide
            
        Returns:
            Nouveau access token
            
        Raises:
            HTTPException: Si le refresh token est invalide
        """
        # Vérifier le refresh token
        payload = verify_token(refresh_token, expected_type="refresh")
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Extraire les données
        user_id = payload.get("user_id")
        username = payload.get("username")
        email = payload.get("email")
        
        if not user_id or not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Créer un nouveau access token
        token_data = {
            "user_id": user_id,
            "username": username,
            "email": email
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return access_token
    
    @staticmethod
    def change_password(db: Session, user: User, old_password: str, new_password: str) -> bool:
        """
        Change le mot de passe d'un utilisateur
        
        Args:
            db: Session de base de données
            user: Utilisateur
            old_password: Ancien mot de passe
            new_password: Nouveau mot de passe
            
        Returns:
            True si le changement a réussi
            
        Raises:
            HTTPException: Si l'ancien mot de passe est incorrect
        """
        # Vérifier l'ancien mot de passe
        if not verify_password(old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )
        
        # Hasher et enregistrer le nouveau mot de passe
        user.hashed_password = hash_password(new_password)
        db.commit()
        
        return True
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Récupère un utilisateur par son ID
        
        Args:
            db: Session de base de données
            user_id: ID de l'utilisateur
            
        Returns:
            User ou None
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Récupère un utilisateur par son email
        
        Args:
            db: Session de base de données
            email: Email de l'utilisateur
            
        Returns:
            User ou None
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Récupère un utilisateur par son username
        
        Args:
            db: Session de base de données
            username: Username de l'utilisateur
            
        Returns:
            User ou None
        """
        return db.query(User).filter(User.username == username).first()

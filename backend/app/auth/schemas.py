"""
Schémas Pydantic pour l'authentification
Validation des requêtes et réponses
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class UserCreate(BaseModel):
    """Schéma pour la création d'un utilisateur"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    niveau_etude: Optional[str] = None
    domaine_interet: Optional[str] = None
    region_preference: Optional[str] = None
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """Valider que le username est alphanumérique"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (with _ or - allowed)')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        """Valider la force du mot de passe"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v


class UserLogin(BaseModel):
    """Schéma pour la connexion"""
    username: str
    password: str


class UserResponse(BaseModel):
    """Schéma pour la réponse utilisateur (sans mot de passe)"""
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    niveau_etude: Optional[str] = None
    domaine_interet: Optional[str] = None
    region_preference: Optional[str] = None
    is_active: bool
    is_superuser: bool
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schéma pour la réponse de token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schéma pour les données extraites du token"""
    user_id: Optional[int] = None
    username: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Schéma pour la requête de rafraîchissement de token"""
    refresh_token: str


class PasswordChange(BaseModel):
    """Schéma pour le changement de mot de passe"""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def password_strength(cls, v):
        """Valider la force du nouveau mot de passe"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v


class PasswordReset(BaseModel):
    """Schéma pour la réinitialisation de mot de passe"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schéma pour confirmer la réinitialisation de mot de passe"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def password_strength(cls, v):
        """Valider la force du nouveau mot de passe"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v

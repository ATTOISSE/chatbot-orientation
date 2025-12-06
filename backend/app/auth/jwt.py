"""
Utilitaires pour la gestion des tokens JWT
Création, validation et décodage des tokens d'authentification
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.config import get_settings

settings = get_settings()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT d'accès
    
    Args:
        data: Données à encoder dans le token (généralement user_id, username)
        expires_delta: Durée de validité du token (optionnel)
        
    Returns:
        Token JWT encodé
    """
    to_encode = data.copy()
    
    # Définir l'expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Ajouter les claims standards
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    # Encoder le token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crée un token JWT de rafraîchissement
    
    Args:
        data: Données à encoder dans le token
        expires_delta: Durée de validité du token (optionnel)
        
    Returns:
        Token JWT encodé
    """
    to_encode = data.copy()
    
    # Durée de vie plus longue pour le refresh token (7 jours par défaut)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Décode et valide un token JWT
    
    Args:
        token: Token JWT à décoder
        
    Returns:
        Payload du token si valide, None sinon
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_token(token: str, expected_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Vérifie qu'un token est valide et du bon type
    
    Args:
        token: Token JWT à vérifier
        expected_type: Type de token attendu ("access" ou "refresh")
        
    Returns:
        Payload du token si valide et du bon type, None sinon
    """
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    # Vérifier le type de token
    token_type = payload.get("type")
    if token_type != expected_type:
        return None
    
    return payload


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Récupère la date d'expiration d'un token
    
    Args:
        token: Token JWT
        
    Returns:
        Date d'expiration ou None si le token est invalide
    """
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    exp_timestamp = payload.get("exp")
    if exp_timestamp:
        return datetime.fromtimestamp(exp_timestamp)
    
    return None


def is_token_expired(token: str) -> bool:
    """
    Vérifie si un token est expiré
    
    Args:
        token: Token JWT
        
    Returns:
        True si expiré, False sinon
    """
    expiration = get_token_expiration(token)
    
    if expiration is None:
        return True
    
    return datetime.utcnow() > expiration

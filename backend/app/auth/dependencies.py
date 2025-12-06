"""
Dépendances FastAPI pour l'authentification
OAuth2, récupération de l'utilisateur courant, vérification des permissions
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.models.user import User
from app.auth.jwt import verify_token

# Schéma OAuth2 avec endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Récupère l'utilisateur courant à partir du token JWT
    
    Args:
        token: Token JWT d'authentification
        db: Session de base de données
        
    Returns:
        User: Utilisateur authentifié
        
    Raises:
        HTTPException: Si le token est invalide ou l'utilisateur n'existe pas
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Décoder et valider le token
    payload = verify_token(token, expected_type="access")
    
    if payload is None:
        raise credentials_exception
    
    # Extraire l'ID utilisateur
    user_id: Optional[int] = payload.get("user_id")
    if user_id is None:
        raise credentials_exception
    
    # Récupérer l'utilisateur depuis la base de données
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise credentials_exception
    
    # Vérifier que l'utilisateur est actif
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Récupère l'utilisateur courant et vérifie qu'il est actif
    (Alias pour get_current_user, déjà vérifié)
    
    Args:
        current_user: Utilisateur courant
        
    Returns:
        User: Utilisateur actif
    """
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Vérifie que l'utilisateur courant est un superuser
    
    Args:
        current_user: Utilisateur courant
        
    Returns:
        User: Superuser
        
    Raises:
        HTTPException: Si l'utilisateur n'est pas superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return current_user


async def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Récupère l'utilisateur courant si authentifié, None sinon
    Permet des endpoints accessibles avec ou sans authentification
    
    Args:
        token: Token JWT (optionnel)
        db: Session de base de données
        
    Returns:
        User ou None
    """
    if token is None:
        return None
    
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None

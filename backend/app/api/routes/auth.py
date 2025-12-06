"""
Routes d'authentification FastAPI
Endpoints pour registration, login, refresh token, etc.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.auth import (
    AuthService,
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    RefreshTokenRequest,
    PasswordChange,
    get_current_user,
    get_current_active_user
)
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Créer un nouveau compte utilisateur
    
    - **email**: Email unique
    - **username**: Nom d'utilisateur unique (alphanumérique)
    - **password**: Mot de passe (min 8 chars, 1 chiffre, 1 lettre)
    - **full_name**: Nom complet (optionnel)
    - **niveau_etude**: Niveau d'études (optionnel)
    - **domaine_interet**: Domaine d'intérêt (optionnel)
    - **region_preference**: Région préférée (optionnel)
    """
    user = AuthService.create_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authentification et obtention des tokens
    
    - **username**: Username ou email
    - **password**: Mot de passe
    
    Retourne access_token et refresh_token
    """
    # Authentifier l'utilisateur
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Vérifier que l'utilisateur est actif
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Créer les tokens
    tokens = AuthService.create_tokens(user)
    return tokens


@router.post("/refresh", response_model=dict)
async def refresh_token(
    refresh_request: RefreshTokenRequest
):
    """
    Rafraîchir l'access token avec un refresh token
    
    - **refresh_token**: Refresh token valide
    
    Retourne un nouveau access_token
    """
    try:
        new_access_token = AuthService.refresh_access_token(refresh_request.refresh_token)
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtenir les informations de l'utilisateur courant
    
    Nécessite un token d'authentification valide
    """
    return current_user


@router.post("/change-password", response_model=dict)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Changer le mot de passe de l'utilisateur courant
    
    - **old_password**: Ancien mot de passe
    - **new_password**: Nouveau mot de passe (min 8 chars, 1 chiffre, 1 lettre)
    """
    success = AuthService.change_password(
        db,
        current_user,
        password_data.old_password,
        password_data.new_password
    )
    
    if success:
        return {"message": "Password changed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password"
        )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtenir les informations d'un utilisateur par son ID
    
    Nécessite authentification
    """
    user = AuthService.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.delete("/me", response_model=dict)
async def delete_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Supprimer le compte de l'utilisateur courant
    
    Action irréversible - supprime toutes les données associées
    """
    try:
        db.delete(current_user)
        db.commit()
        return {"message": "Account deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )

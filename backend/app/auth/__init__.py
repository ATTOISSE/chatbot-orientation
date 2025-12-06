"""
Exports centralisés du module auth
"""
from app.auth.password import hash_password, verify_password
from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token,
    get_token_expiration,
    is_token_expired
)
from app.auth.dependencies import (
    oauth2_scheme,
    get_current_user,
    get_current_active_user,
    get_current_superuser,
    get_optional_current_user
)
from app.auth.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    TokenData,
    RefreshTokenRequest,
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm
)
from app.auth.service import AuthService

__all__ = [
    # Password utilities
    "hash_password",
    "verify_password",
    
    # JWT utilities
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "verify_token",
    "get_token_expiration",
    "is_token_expired",
    
    # Dependencies
    "oauth2_scheme",
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    "get_optional_current_user",
    
    # Schemas
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenData",
    "RefreshTokenRequest",
    "PasswordChange",
    "PasswordReset",
    "PasswordResetConfirm",
    
    # Service
    "AuthService"
]

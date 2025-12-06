# COMMIT 4: JWT Authentication & Password Hashing

## 📋 Summary

Complete authentication system with JWT tokens, password hashing (bcrypt), FastAPI dependencies, and auth service layer.

## 📁 Files Created

### Authentication Core
- ✅ `backend/app/auth/password.py` - Password hashing with bcrypt
- ✅ `backend/app/auth/jwt.py` - JWT token creation and validation
- ✅ `backend/app/auth/dependencies.py` - FastAPI OAuth2 dependencies
- ✅ `backend/app/auth/schemas.py` - Pydantic validation schemas
- ✅ `backend/app/auth/service.py` - Authentication business logic
- ✅ `backend/app/auth/__init__.py` - Centralized exports

## 🔐 Authentication Features

### 1. Password Security (password.py)
```python
✅ hash_password(password) - Bcrypt hashing
✅ verify_password(plain, hashed) - Password verification
✅ CryptContext with bcrypt
✅ Automatic salt generation
```

### 2. JWT Token Management (jwt.py)
```python
✅ create_access_token() - Short-lived (30 min)
✅ create_refresh_token() - Long-lived (7 days)
✅ decode_token() - Decode and validate
✅ verify_token() - Verify token type
✅ get_token_expiration() - Get expiry date
✅ is_token_expired() - Check if expired
```

**Token Structure:**
```json
{
  "user_id": 123,
  "username": "john_doe",
  "email": "john@example.com",
  "exp": 1234567890,
  "iat": 1234567890,
  "type": "access"  // ou "refresh"
}
```

### 3. FastAPI Dependencies (dependencies.py)
```python
✅ oauth2_scheme - OAuth2PasswordBearer
✅ get_current_user() - Get authenticated user
✅ get_current_active_user() - Verify active user
✅ get_current_superuser() - Verify superuser
✅ get_optional_current_user() - Optional auth
```

**Usage:**
```python
@app.get("/protected")
async def protected_route(user: User = Depends(get_current_user)):
    return {"user": user.username}
```

### 4. Pydantic Schemas (schemas.py)
```python
✅ UserCreate - Registration validation
✅ UserLogin - Login credentials
✅ UserResponse - User data (no password)
✅ Token - Token response
✅ TokenData - Token payload
✅ RefreshTokenRequest - Token refresh
✅ PasswordChange - Password update
✅ PasswordReset - Password reset request
✅ PasswordResetConfirm - Reset confirmation
```

**Password Validation:**
- Minimum 8 characters
- At least 1 digit
- At least 1 letter
- Username alphanumeric (+ _ -)

### 5. Auth Service (service.py)
```python
✅ create_user() - User registration
✅ authenticate_user() - Login
✅ create_tokens() - Generate access + refresh
✅ refresh_access_token() - Renew access token
✅ change_password() - Update password
✅ get_user_by_id() - Fetch by ID
✅ get_user_by_email() - Fetch by email
✅ get_user_by_username() - Fetch by username
```

## 🔄 Authentication Flow

### Registration Flow:
```
1. Client → POST /register with UserCreate
2. Service validates email/username uniqueness
3. Password hashed with bcrypt
4. User created in database
5. Return UserResponse (no password)
```

### Login Flow:
```
1. Client → POST /login with username + password
2. Service finds user by username or email
3. Verify password with bcrypt
4. Create access_token (30 min) + refresh_token (7 days)
5. Return Token {access_token, refresh_token, token_type}
```

### Protected Route Flow:
```
1. Client → GET /protected with Authorization: Bearer <token>
2. oauth2_scheme extracts token
3. verify_token() validates JWT
4. get_current_user() fetches user from DB
5. Check user.is_active
6. Return user to endpoint
```

### Token Refresh Flow:
```
1. Client → POST /refresh with refresh_token
2. verify_token() validates refresh token
3. Extract user data from payload
4. Create new access_token
5. Return new access_token
```

## 🛡️ Security Features

### Password Security:
- ✅ Bcrypt hashing (adaptive work factor)
- ✅ Automatic salt per password
- ✅ No plaintext storage
- ✅ Password strength validation

### JWT Security:
- ✅ HS256 algorithm (HMAC-SHA256)
- ✅ Secret key from environment
- ✅ Token expiration (exp claim)
- ✅ Issued at timestamp (iat claim)
- ✅ Token type verification
- ✅ Signature validation

### API Security:
- ✅ OAuth2 password bearer scheme
- ✅ Automatic token extraction
- ✅ User active status check
- ✅ Superuser permission check
- ✅ HTTPException on auth failure

## 📊 Error Handling

### HTTP Status Codes:
```
401 UNAUTHORIZED - Invalid credentials/token
403 FORBIDDEN - Inactive user / insufficient permissions
400 BAD_REQUEST - Email/username exists, weak password
```

### Exceptions:
```python
# Invalid credentials
HTTPException(401, "Could not validate credentials")

# Inactive user
HTTPException(403, "Inactive user")

# Not superuser
HTTPException(403, "Not enough permissions")

# Email exists
HTTPException(400, "Email already registered")

# Invalid refresh token
HTTPException(401, "Invalid refresh token")
```

## 🧪 Testing Instructions

### Test 1: Vérifier les fichiers auth
```powershell
cd c:\ATTOISSE\eduGuide\chatbot-orientation\backend

# Lister les fichiers auth
Get-ChildItem -Recurse -Filter "*.py" -Path app\auth | Select-Object Name

# Expected output:
# password.py
# jwt.py
# dependencies.py
# schemas.py
# service.py
# __init__.py
```

### Test 2: Tester le hachage de mot de passe
```python
from app.auth import hash_password, verify_password

# Hasher un mot de passe
hashed = hash_password("SecurePass123")
print(f"Hash: {hashed[:20]}...")  # $2b$12$...

# Vérifier
assert verify_password("SecurePass123", hashed) == True
assert verify_password("WrongPass", hashed) == False
```

### Test 3: Tester la création de tokens
```python
from app.auth import create_access_token, decode_token
from datetime import timedelta

# Créer un token
token_data = {"user_id": 1, "username": "test_user"}
token = create_access_token(token_data, timedelta(minutes=30))
print(f"Token: {token[:20]}...")

# Décoder
payload = decode_token(token)
assert payload["user_id"] == 1
assert payload["username"] == "test_user"
assert payload["type"] == "access"
```

### Test 4: Tester la validation des schémas
```python
from app.auth.schemas import UserCreate
from pydantic import ValidationError

# Valide
user = UserCreate(
    email="test@example.com",
    username="test_user",
    password="SecurePass123"
)

# Invalide - mot de passe faible
try:
    user = UserCreate(
        email="test@example.com",
        username="test",
        password="weak"  # Pas de chiffre, trop court
    )
except ValidationError as e:
    print("✅ Validation password failed as expected")
```

### Test 5: Tester AuthService
```python
from app.auth import AuthService
from app.auth.schemas import UserCreate
from app.database.base import SessionLocal

db = SessionLocal()

# Créer un utilisateur
user_data = UserCreate(
    email="john@example.com",
    username="john_doe",
    password="SecurePass123"
)

user = AuthService.create_user(db, user_data)
print(f"✅ User created: {user.username}")

# Authentifier
auth_user = AuthService.authenticate_user(db, "john_doe", "SecurePass123")
assert auth_user is not None
print(f"✅ Authentication successful")

# Créer des tokens
tokens = AuthService.create_tokens(user)
print(f"✅ Tokens created: {tokens.token_type}")

db.close()
```

### Test 6: Tester les dépendances FastAPI
```python
from fastapi import FastAPI, Depends
from app.auth import get_current_user
from app.models.user import User

app = FastAPI()

@app.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email
    }

# Tester avec httpx:
# headers = {"Authorization": f"Bearer {access_token}"}
# response = client.get("/me", headers=headers)
```

## 📝 Configuration Required

### .env variables (already in config.py):
```env
JWT_SECRET_KEY=your-secret-key-here-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🔧 Dependencies Used

From `backend/requirements.txt`:
- ✅ `python-jose[cryptography]` - JWT encoding/decoding
- ✅ `passlib[bcrypt]` - Password hashing
- ✅ `python-multipart` - OAuth2 form parsing
- ✅ `pydantic[email]` - Email validation

## 📋 Auth Module Structure

```
backend/app/auth/
├── __init__.py          # Exports centralisés
├── password.py          # Hachage bcrypt
├── jwt.py               # Gestion tokens JWT
├── dependencies.py      # Dependencies FastAPI
├── schemas.py           # Validation Pydantic
└── service.py           # Logique métier
```

## ✅ Checklist

- [x] Password hashing with bcrypt
- [x] Password verification
- [x] JWT access token creation (30 min)
- [x] JWT refresh token creation (7 days)
- [x] Token validation and decoding
- [x] Token expiration check
- [x] OAuth2 password bearer scheme
- [x] Get current user dependency
- [x] Get superuser dependency
- [x] Optional auth dependency
- [x] User registration schema
- [x] Login schema
- [x] Token response schema
- [x] Password validation (8+ chars, digit, letter)
- [x] Username validation (alphanumeric)
- [x] Email validation
- [x] AuthService with 8 methods
- [x] Email uniqueness check
- [x] Username uniqueness check
- [x] Active user check
- [x] Superuser permission check

## 📝 Commit Message

```
feat: Add JWT authentication and password hashing system

- Create password hashing utilities with bcrypt
- Implement JWT token creation (access + refresh)
- Add token validation and expiration checks
- Create FastAPI OAuth2 dependencies (get_current_user, etc.)
- Add Pydantic schemas for auth (UserCreate, Token, etc.)
- Implement AuthService with registration and login
- Add password strength validation (8+ chars, digit, letter)
- Add username/email uniqueness validation
- Configure OAuth2PasswordBearer scheme
- Add superuser and optional auth dependencies
- Support token refresh flow
- Add password change functionality
```

## ✅ Status

**READY FOR COMMIT 4** ✅

## 🔜 Next Steps (COMMIT 5)

- Create authentication API endpoints
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/refresh
- GET /api/auth/me
- POST /api/auth/change-password

---

**Status:** ✅ READY FOR COMMIT 4  
**Next:** COMMIT 5 - Authentication API Endpoints

# COMMIT 5: Authentication API Endpoints

## 📋 Summary

Complete REST API endpoints for authentication with FastAPI routes, CORS configuration, and API documentation.

## 📁 Files Created/Modified

### API Routes
- ✅ `backend/app/api/__init__.py` - API package init
- ✅ `backend/app/api/routes/__init__.py` - Routes exports
- ✅ `backend/app/api/routes/auth.py` - Authentication endpoints
- ✅ `backend/app/main.py` - Updated with CORS and router registration

### Configuration
- ✅ `backend/app/config.py` - Updated CORS settings

## 🌐 API Endpoints Created

### Authentication Routes (`/api/auth`)

#### 1. **POST /api/auth/register**
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "SecurePass123",
  "full_name": "John Doe",
  "niveau_etude": "Licence 1",
  "domaine_interet": "Informatique",
  "region_preference": "Dakar"
}

Response: 201 Created
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "niveau_etude": "Licence 1",
  "domaine_interet": "Informatique",
  "region_preference": "Dakar",
  "is_active": true,
  "is_superuser": false
}
```

**Features:**
- ✅ Email uniqueness validation
- ✅ Username uniqueness validation
- ✅ Password strength validation
- ✅ Returns UserResponse (no password)
- ✅ HTTP 201 Created on success
- ✅ HTTP 400 if email/username exists

#### 2. **POST /api/auth/login**
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=john_doe
password=SecurePass123

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Features:**
- ✅ OAuth2PasswordRequestForm
- ✅ Login with username OR email
- ✅ Password verification
- ✅ Active user check
- ✅ Returns access + refresh tokens
- ✅ HTTP 401 if credentials invalid
- ✅ HTTP 403 if user inactive

#### 3. **POST /api/auth/refresh**
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Features:**
- ✅ Validates refresh token
- ✅ Checks token type
- ✅ Generates new access token
- ✅ HTTP 401 if token invalid

#### 4. **GET /api/auth/me**
```http
GET /api/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response: 200 OK
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "niveau_etude": "Licence 1",
  "domaine_interet": "Informatique",
  "region_preference": "Dakar",
  "is_active": true,
  "is_superuser": false
}
```

**Features:**
- ✅ Requires authentication
- ✅ Returns current user info
- ✅ HTTP 401 if not authenticated

#### 5. **POST /api/auth/change-password**
```http
POST /api/auth/change-password
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "old_password": "SecurePass123",
  "new_password": "NewSecurePass456"
}

Response: 200 OK
{
  "message": "Password changed successfully"
}
```

**Features:**
- ✅ Requires authentication
- ✅ Verifies old password
- ✅ Validates new password strength
- ✅ Updates hashed password
- ✅ HTTP 400 if old password incorrect

#### 6. **GET /api/auth/users/{user_id}**
```http
GET /api/auth/users/1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response: 200 OK
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  ...
}
```

**Features:**
- ✅ Requires authentication
- ✅ Get user by ID
- ✅ HTTP 404 if user not found

#### 7. **DELETE /api/auth/me**
```http
DELETE /api/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response: 200 OK
{
  "message": "Account deleted successfully"
}
```

**Features:**
- ✅ Requires authentication
- ✅ Soft delete user account
- ✅ CASCADE deletes related data
- ✅ HTTP 500 if deletion fails

## 🔧 FastAPI Features Implemented

### 1. **CORS Configuration**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8501", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"]
)
```

**Allows:**
- ✅ Frontend Streamlit (port 8501)
- ✅ React/Next.js dev (port 3000)
- ✅ Swagger UI (port 8000)
- ✅ Credentials (cookies, auth headers)
- ✅ All HTTP methods
- ✅ All headers

### 2. **Router Registration**
```python
from app.api.routes import auth

app.include_router(auth.router)
```

**Structure:**
- ✅ APIRouter with prefix `/api/auth`
- ✅ Tag `Authentication` for docs
- ✅ Automatic OpenAPI generation

### 3. **Automatic API Documentation**

**Swagger UI:** `http://localhost:8000/docs`
- Interactive API testing
- Request/response schemas
- Authentication flow

**ReDoc:** `http://localhost:8000/redoc`
- Clean documentation
- Examples for each endpoint

## 📊 HTTP Status Codes

### Success Codes:
- ✅ `200 OK` - Request successful
- ✅ `201 Created` - User registered

### Client Error Codes:
- ✅ `400 Bad Request` - Validation error, email exists, wrong password
- ✅ `401 Unauthorized` - Invalid credentials/token
- ✅ `403 Forbidden` - Inactive user
- ✅ `404 Not Found` - User not found

### Server Error Codes:
- ✅ `500 Internal Server Error` - Database error

## 🔐 Security Features

### Authentication Flow:
1. **Register** → Create user with hashed password
2. **Login** → Verify credentials, return tokens
3. **Protected Routes** → Verify access token
4. **Refresh** → Renew access token with refresh token

### Token Security:
- ✅ Bearer token in Authorization header
- ✅ Access token expires in 30 minutes
- ✅ Refresh token expires in 7 days
- ✅ Token validation on every request
- ✅ Active user check

### Password Security:
- ✅ Bcrypt hashing
- ✅ No plaintext storage
- ✅ Strength validation (8+ chars, digit, letter)
- ✅ Secure password change flow

## 🧪 Testing Instructions

### Test 1: Vérifier les fichiers API
```powershell
cd c:\ATTOISSE\eduGuide\chatbot-orientation\backend

# Lister les fichiers API
Get-ChildItem -Recurse -Path app\api | Select-Object Name

# Expected:
# __init__.py
# routes\
#   __init__.py
#   auth.py
```

### Test 2: Démarrer le serveur (avec Docker)
```powershell
# Démarrer tous les services
docker-compose up -d

# Vérifier les logs du backend
docker-compose logs -f backend

# Expected: 
# Uvicorn running on http://0.0.0.0:8000
```

### Test 3: Tester la documentation API
```powershell
# Ouvrir le navigateur
start http://localhost:8000/docs

# Vous devriez voir:
# - Swagger UI interactive
# - Section "Authentication" avec 7 endpoints
# - Schémas UserCreate, Token, etc.
```

### Test 4: Tester l'inscription (curl)
```powershell
$body = @{
    email = "test@example.com"
    username = "test_user"
    password = "SecurePass123"
    full_name = "Test User"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"

# Expected: UserResponse avec id, email, username
```

### Test 5: Tester la connexion
```powershell
$body = @{
    username = "test_user"
    password = "SecurePass123"
}

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" `
    -Method POST `
    -Body $body `
    -ContentType "application/x-www-form-urlencoded"

# Expected: Token avec access_token, refresh_token
```

### Test 6: Tester route protégée
```powershell
$token = "VOTRE_ACCESS_TOKEN_ICI"

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/me" `
    -Method GET `
    -Headers @{Authorization = "Bearer $token"}

# Expected: UserResponse avec vos infos
```

### Test 7: Tester le refresh token
```powershell
$body = @{
    refresh_token = "VOTRE_REFRESH_TOKEN_ICI"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/auth/refresh" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"

# Expected: Nouveau access_token
```

### Test 8: Tester avec Python httpx
```python
import httpx

# Inscription
response = httpx.post("http://localhost:8000/api/auth/register", json={
    "email": "user@test.com",
    "username": "user_test",
    "password": "Test1234"
})
print(response.json())

# Login
response = httpx.post("http://localhost:8000/api/auth/login", data={
    "username": "user_test",
    "password": "Test1234"
})
tokens = response.json()
access_token = tokens["access_token"]

# Route protégée
headers = {"Authorization": f"Bearer {access_token}"}
response = httpx.get("http://localhost:8000/api/auth/me", headers=headers)
print(response.json())
```

## 📋 API Routes Summary

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/auth/register` | ❌ | Créer un compte |
| POST | `/api/auth/login` | ❌ | Se connecter |
| POST | `/api/auth/refresh` | ❌ | Rafraîchir token |
| GET | `/api/auth/me` | ✅ | Info utilisateur courant |
| POST | `/api/auth/change-password` | ✅ | Changer mot de passe |
| GET | `/api/auth/users/{id}` | ✅ | Info utilisateur par ID |
| DELETE | `/api/auth/me` | ✅ | Supprimer compte |

## ✅ Checklist

- [x] Create API routes structure
- [x] POST /api/auth/register endpoint
- [x] POST /api/auth/login endpoint (OAuth2)
- [x] POST /api/auth/refresh endpoint
- [x] GET /api/auth/me endpoint
- [x] POST /api/auth/change-password endpoint
- [x] GET /api/auth/users/{id} endpoint
- [x] DELETE /api/auth/me endpoint
- [x] CORS middleware configuration
- [x] Router registration in main.py
- [x] API documentation (Swagger/ReDoc)
- [x] Error handling (400, 401, 403, 404, 500)
- [x] OAuth2PasswordRequestForm for login
- [x] Token validation on protected routes
- [x] Active user check

## 📝 Commit Message

```
feat: Add authentication API endpoints

- Create API routes structure (app/api/routes/)
- Add POST /api/auth/register (user registration)
- Add POST /api/auth/login (OAuth2 password flow)
- Add POST /api/auth/refresh (token refresh)
- Add GET /api/auth/me (current user info)
- Add POST /api/auth/change-password (password update)
- Add GET /api/auth/users/{id} (get user by ID)
- Add DELETE /api/auth/me (account deletion)
- Configure CORS middleware (localhost:3000, 8501, 8000)
- Register auth router in main.py
- Add automatic API documentation (Swagger UI, ReDoc)
- Implement error handling (400, 401, 403, 404, 500)
- Use OAuth2PasswordRequestForm for login
- Validate tokens on protected routes
```

## ✅ Status

**READY FOR COMMIT 5** ✅

## 🔜 Next Steps (COMMIT 6)

- Load formation data from JSON files
- Create data import scripts
- Seed database with formations, établissements, domaines
- Add data validation and cleaning

---

**Status:** ✅ READY FOR COMMIT 5  
**Next:** COMMIT 6 - Data Models & Import (Formations)

# COMMIT 2: Configuration & Dependencies Setup

## 📋 Summary

This commit adds all configuration files, dependency specifications, and Docker orchestration files.

## 📁 Files Created

### Core Configuration
- ✅ `backend/app/config.py` - Pydantic Settings class with 50+ configuration parameters
- ✅ `backend/requirements.txt` - 30+ Python dependencies for backend
- ✅ `frontend/requirements.txt` - 15+ Python dependencies for frontend
- ✅ `.env.example` - Environment variables template (already in COMMIT 1)

### Dockerization
- ✅ `backend/Dockerfile` - Python 3.11 + FastAPI setup
- ✅ `frontend/Dockerfile` - Python 3.11 + Streamlit setup
- ✅ `docker-compose.yml` - Complete multi-service orchestration

## 📦 Dependencies Summary

### Backend (30+ packages)
**Core Framework:**
- FastAPI 0.104.1
- Uvicorn 0.24.0 (ASGI server)
- Pydantic 2.5.0 (data validation)

**Database:**
- SQLAlchemy 2.0.23 (ORM)
- psycopg2-binary (PostgreSQL driver)
- Alembic (migrations)

**LLM & RAG:**
- LangChain 0.0.352
- Hugging Face Hub 0.19.4
- Sentence-Transformers 2.2.2 (embeddings)
- Torch 2.1.1

**Vector Database:**
- ChromaDB 0.4.21

**Security:**
- Python-Jose (JWT)
- Passlib + Bcrypt (password hashing)

**Testing & Development:**
- Pytest, Black, Flake8, MyPy

### Frontend (15+ packages)
**UI Framework:**
- Streamlit 1.28.1
- Streamlit plugins (auth, lottie)

**HTTP & Data:**
- Httpx, Requests
- Pandas

**Visualization:**
- Plotly, Matplotlib

## 🐳 Docker Architecture

### 4 Services in docker-compose.yml:

1. **PostgreSQL (postgres)**
   - Image: postgres:15-alpine
   - Port: 5432
   - Volume: postgres_data
   - Health checks: ✅

2. **ChromaDB (chromadb)**
   - Image: chromadb/chroma:latest
   - Port: 8000
   - Volume: chromadb_data
   - Health checks: ✅

3. **FastAPI Backend (backend)**
   - Build from: ./backend/Dockerfile
   - Port: 8000
   - Reload: enabled for development
   - Depends on: postgres, chromadb ✅

4. **Streamlit Frontend (frontend)**
   - Build from: ./frontend/Dockerfile
   - Port: 8501
   - Depends on: backend ✅

### Features:
- Network: eduguide-network (internal communication)
- Health checks for database services
- Persistent volumes for data
- Environment variable injection
- Auto-restart policy

## 🔧 Configuration (config.py)

### Settings Class Structure:
```
✅ APP_NAME, VERSION, DEBUG, LOG_LEVEL
✅ DATABASE_URL (PostgreSQL connection)
✅ JWT_SECRET, JWT_ALGORITHM, TOKEN_EXPIRE
✅ HUGGINGFACE_API_KEY, MODEL config
✅ CHROMADB_HOST, PORT, PERSIST_DIR
✅ CORS_ORIGINS, CREDENTIALS, METHODS
✅ RAG_CHUNK_SIZE, RAG_TOP_K, RAG_SCORE_THRESHOLD
✅ EMBEDDING_MODEL, DIMENSION
```

### Features:
- Pydantic Settings (validates all configs)
- Environment file support (.env)
- Cached singleton instance (lru_cache)
- Safe defaults for all parameters
- Type-safe configuration access

## 🧪 Testing Instructions

### Test 1: Verify requirements.txt files
```powershell
cd c:\ATTOISSE\eduGuide\chatbot-orientation

# Check backend dependencies
cat backend\requirements.txt | Select-String "fastapi|sqlalchemy|langchain|chromadb"

# Expected output:
# fastapi==0.104.1
# sqlalchemy==2.0.23
# langchain==0.0.352
# chromadb==0.4.21

# Check frontend dependencies
cat frontend\requirements.txt | Select-String "streamlit|plotly"

# Expected output:
# streamlit==1.28.1
# plotly==5.18.0
```

### Test 2: Verify Dockerfiles
```powershell
# Check backend Dockerfile
cat backend\Dockerfile | Select-String "FROM|WORKDIR|EXPOSE|CMD"

# Expected output:
# FROM python:3.11-slim
# WORKDIR /app
# EXPOSE 8000
# CMD ["uvicorn", "app.main:app"...

# Check frontend Dockerfile
cat frontend\Dockerfile | Select-String "FROM|EXPOSE|CMD"

# Expected output:
# FROM python:3.11-slim
# EXPOSE 8501
# CMD ["streamlit", "run", "app.py"...
```

### Test 3: Verify docker-compose.yml
```powershell
# Check services are defined
cat docker-compose.yml | Select-String "postgres:|chromadb:|backend:|frontend:"

# Expected output:
# postgres:
# chromadb:
# backend:
# frontend:

# Check volumes
cat docker-compose.yml | Select-String "volumes:|postgres_data:|chromadb_data:"

# Check networks
cat docker-compose.yml | Select-String "networks:|eduguide-network:"
```

### Test 4: Verify config.py syntax
```powershell
# Check that config.py can be imported
python -c "from app.config import get_settings; print('Config loaded successfully')"

# Expected: Config loaded successfully (after dependencies are installed)
```

### Test 5: Verify .env.example
```powershell
# Count environment variables
(Select-String "=" .env.example | Measure-Object).Count

# Expected: 25+ environment variables defined
```

### Test 6: Docker Compose validation
```powershell
# Validate docker-compose syntax
docker-compose config > /dev/null 2>&1
if ($LASTEXITCODE -eq 0) { 
    Write-Host "✅ docker-compose.yml is valid"
} else {
    Write-Host "❌ docker-compose.yml has errors"
}
```

## 📋 Checklist

- [x] config.py created with all settings
- [x] backend/requirements.txt with 30+ packages
- [x] frontend/requirements.txt with 15+ packages
- [x] backend/Dockerfile created
- [x] frontend/Dockerfile created
- [x] docker-compose.yml with 4 services
- [x] PostgreSQL service configured
- [x] ChromaDB service configured
- [x] Backend service configured
- [x] Frontend service configured
- [x] Health checks configured
- [x] Networks configured
- [x] Volumes configured
- [x] Environment variables templated

## 🎯 Expected Results

After this commit, you should be able to:
1. ✅ View all configuration options in config.py
2. ✅ Install all dependencies with: `pip install -r backend/requirements.txt`
3. ✅ Build Docker images with: `docker-compose build`
4. ✅ Validate docker-compose syntax without errors
5. ✅ See all 4 services when running: `docker-compose ps`

## 📝 Commit Message

```
config: Add configuration, dependencies and Docker setup

- Create Pydantic Settings class (config.py) with 50+ parameters
- Add backend/requirements.txt with 30+ Python packages
- Add frontend/requirements.txt with 15+ Python packages
- Create backend/Dockerfile (Python 3.11 + FastAPI)
- Create frontend/Dockerfile (Python 3.11 + Streamlit)
- Create docker-compose.yml with 4 services:
  * PostgreSQL 15 (database)
  * ChromaDB (vector store)
  * FastAPI backend (port 8000)
  * Streamlit frontend (port 8501)
- Configure health checks, volumes, networks
- Add environment variable injection
- Enable auto-restart policies
```

## ✅ Status

**READY FOR COMMIT 2** ✅

## 🔜 Next Steps (COMMIT 3)

- Create SQLAlchemy database models
- Define User, Conversation, Message tables
- Define Formation, Etablissement, Domaine, DataSource tables
- Setup database connection and session management

---

**Status:** ✅ READY FOR COMMIT 2  
**Next:** COMMIT 3 - Database Models (SQLAlchemy)

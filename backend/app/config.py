"""
Configuration settings for EduGuide backend using Pydantic
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # ==================== APP CONFIG ====================
    APP_NAME: str = "EduGuide Sénégal"
    APP_DESCRIPTION: str = "Plateforme d'orientation pour études supérieures"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # ==================== SERVER CONFIG ====================
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    
    # ==================== DATABASE ====================
    DATABASE_URL: str = "postgresql://eduguide:eduguide2024@localhost:5432/eduguide_db"
    POSTGRES_USER: str = "eduguide"
    POSTGRES_PASSWORD: str = "eduguide2024"
    POSTGRES_DB: str = "eduguide_db"
    
    # ==================== JWT & SECURITY ====================
    JWT_SECRET: str = "your-super-secret-key-change-this-in-production-min-32-chars-!!!"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ==================== HUGGING FACE & LLM ====================
    HUGGINGFACE_API_KEY: str = ""
    HUGGINGFACE_MODEL: str = "meta-llama/Llama-2-7b-chat-hf"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 512
    LLM_TOP_P: float = 0.95
    LLM_TOP_K: int = 50
    
    # ==================== CHROMADB ====================
    CHROMADB_HOST: str = "localhost"
    CHROMADB_PORT: int = 8000
    CHROMADB_PERSIST_DIR: str = "./chroma_data"
    
    # ==================== FRONTEND ====================
    FRONTEND_URL: str = "http://localhost:8501"
    BACKEND_API_URL: str = "http://backend:8000"
    
    # ==================== CORS ====================
    CORS_ORIGINS: List[str] = [
        "http://localhost:8501",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://frontend:8501",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # ==================== RAG CONFIG ====================
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200
    RAG_TOP_K: int = 5
    RAG_SCORE_THRESHOLD: float = 0.6
    
    # ==================== EMBEDDING CONFIG ====================
    EMBEDDING_MODEL: str = "sentence-transformers/xlm-r-base-multilingual"
    EMBEDDING_DIMENSION: int = 768
    
    class Config:
        """Pydantic config"""
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()

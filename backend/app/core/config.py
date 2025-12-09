from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path

class Settings(BaseSettings):
    # API Keys
    GOOGLE_API_KEY: str
    PINECONE_API_KEY: str
    
    # Pinecone Configuration
    PINECONE_ENVIRONMENT: str = "gcp-starter"
    PINECONE_INDEX_NAME: str = "documind-index"
    
    # Application Configuration
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    
    # Model Configuration - Using Gemini 2.5 Pro (separate quota from Flash)
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    LLM_MODEL: str = "models/gemini-2.5-pro"  # Switched to Pro for separate quota
    CHUNK_SIZE: int = 1024
    CHUNK_OVERLAP: int = 200
    TOP_K: int = 8
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

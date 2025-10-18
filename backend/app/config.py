from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # API Keys
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # LLM Configuration
    DEFAULT_LLM_MODEL: str = "gpt-4o"  # ← CHANGED THIS LINE
    DEFAULT_TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 4000
    
    # Application
    APP_NAME: str = "Multi-Agent AI Assistant"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    
    # CORS - use string that we'll split
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # File Upload
    UPLOAD_DIR: str = "data/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    @property
    def allowed_extensions(self) -> set:
        """Return allowed file extensions as a set"""
        return {".pdf", ".txt", ".docx", ".csv", ".xlsx"}
    
    # Vector Store
    VECTOR_STORE_DIR: str = "data/vector_db"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Agent Configuration
    MAX_ITERATIONS: int = 10
    AGENT_TIMEOUT: int = 300  # seconds
    
    # Redis (optional)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Initialize settings instance OUTSIDE the class
settings = Settings()
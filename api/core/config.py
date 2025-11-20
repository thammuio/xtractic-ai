"""
Configuration management for the API
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Supabase Settings
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # Cloudera AI Agent Studio Settings
    CLOUDERA_API_URL: str = os.getenv("CLOUDERA_API_URL", "")
    CLOUDERA_API_KEY: str = os.getenv("CLOUDERA_API_KEY", "")
    CLOUDERA_WORKSPACE_ID: str = os.getenv("CLOUDERA_WORKSPACE_ID", "")
    
    # Deployed Workflow Settings
    DEPLOYED_WORKFLOW_URL: str = os.getenv(
        "DEPLOYED_WORKFLOW_URL",
        "https://workflow-0421b0de-eec0-4dab-9a72-00e31453cf14.ml-d248e68a-04a.se-sandb.a465-9q4k.cloudera.site"
    )
    CDSW_APIV2_KEY: str = os.getenv("CDSW_APIV2_KEY", "")
    CDSW_PROJECT_ID: str = os.getenv("CDSW_PROJECT_ID", "")
    CDSW_DOMAIN: str = os.getenv("CDSW_DOMAIN", "")
    CDSW_APP_PORT: int = int(os.getenv("CDSW_APP_PORT", "9000"))
    
    # MCP Server Settings
    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://localhost:3001")
    MCP_API_KEY: str = os.getenv("MCP_API_KEY", "")
    
    # RAG Database Settings
    RAG_DB_HOST: str = os.getenv("RAG_DB_HOST", "localhost")
    RAG_DB_PORT: int = int(os.getenv("RAG_DB_PORT", "5432"))
    RAG_DB_NAME: str = os.getenv("RAG_DB_NAME", "rag_db")
    RAG_DB_USER: str = os.getenv("RAG_DB_USER", "postgres")
    RAG_DB_PASSWORD: str = os.getenv("RAG_DB_PASSWORD", "")
    
    # Vector Database Settings (for RAG)
    VECTOR_DB_TYPE: str = os.getenv("VECTOR_DB_TYPE", "pgvector")  # pgvector, pinecone, weaviate
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "")
    
    # OpenAI/LLM Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Redis Settings (for caching and task queue)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()

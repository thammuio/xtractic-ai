"""
Configuration management for the API
"""
from pydantic_settings import BaseSettings
import os
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Backend Database Settings
    BACKEND_DATABASE_URL: str = os.getenv(
        "BACKEND_DATABASE_URL",
        ""
    )
    
    # Cloudera AI Agent Studio Settings
    CLOUDERA_API_URL: str = os.getenv("CLOUDERA_API_URL", "")
    CLOUDERA_API_KEY: str = os.getenv("CLOUDERA_API_KEY", "")
    CLOUDERA_WORKSPACE_ID: str = os.getenv("CLOUDERA_WORKSPACE_ID", "")
    
    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Deployed Workflow Settings
    DEPLOYED_WORKFLOW_URL: str = os.getenv(
        "DEPLOYED_WORKFLOW_URL",
        ""
    )
    CDSW_APIV2_KEY: str = os.getenv("CDSW_APIV2_KEY", "")
    CDSW_PROJECT_ID: str = os.getenv("CDSW_PROJECT_ID", "")
    CDSW_DOMAIN: str = os.getenv("CDSW_DOMAIN", "")
    CDSW_APP_PORT: int = int(os.getenv("CDSW_APP_PORT", "9000"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
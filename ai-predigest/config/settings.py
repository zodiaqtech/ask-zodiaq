"""
Configuration settings for the MyZodiaq Marriage API
"""
from pydantic_settings import BaseSettings
from typing import Optional, Literal
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Settings
    APP_NAME: str = "MyZodiaq Marriage API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database Configuration
    DATABASE_URL: Optional[str] = None  # postgresql+asyncpg://user:pass@host:port/db
    
    # External API Keys - Support both naming conventions
    VEDIC_ASTRO_API_KEY: str = "dcdb25dd-081c-5ee7-bfec-a986788bc4d2"
    
    # KP API - Support both old (DIVINE_*) and new (KP_*) names
    KP_API_KEY: Optional[str] = None
    KP_AUTH_TOKEN: Optional[str] = None
    DIVINE_API_KEY: Optional[str] = None  # Alias for KP_API_KEY
    DIVINE_API_TOKEN: Optional[str] = None  # Alias for KP_AUTH_TOKEN
    
    # AstrologyAPI.com credentials (for Lal Kitab remedies)
    ASTROLOGY_API_USER_ID: Optional[str] = None
    ASTROLOGY_API_KEY: Optional[str] = None
    
    # LLM Provider Configuration
    LLM_PROVIDER: Literal["groq", "openai", "azure_openai", "anthropic", "gemini"] = "groq"
    
    # Groq Configuration
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o"
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = None
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    
    # Anthropic Configuration
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    
    # Gemini Configuration
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-pro"
    
    # LLM Settings
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 4096
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra env vars
    
    @property
    def kp_api_key(self) -> str:
        """Get KP API key (supports both naming conventions)"""
        return self.KP_API_KEY or self.DIVINE_API_KEY or "ad76edaf6e76e7d7fa1cbf3e72ccc3ef"
    
    @property
    def kp_auth_token(self) -> str:
        """Get KP Auth token (supports both naming conventions)"""
        return self.KP_AUTH_TOKEN or self.DIVINE_API_TOKEN or ""


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
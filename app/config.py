"""Application configuration using Pydantic settings."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_title: str = "FastAPI Agent Backend"
    api_version: str = "1.0.0"
    api_description: str = "Production-ready FastAPI backend with AI agent orchestration"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=False, env="RELOAD")
    
    # Authentication (Clerk)
    clerk_secret_key: str = Field(default="demo-secret-key", env="CLERK_SECRET_KEY")
    clerk_publishable_key: str = Field(default="demo-publishable-key", env="CLERK_PUBLISHABLE_KEY")
    jwt_algorithm: str = Field(default="RS256", env="JWT_ALGORITHM")
    
    # Database (Supabase)
    supabase_url: str = Field(default="https://demo.supabase.co", env="SUPABASE_URL")
    supabase_anon_key: str = Field(default="demo-anon-key", env="SUPABASE_ANON_KEY")
    supabase_service_role_key: str = Field(default="demo-service-role-key", env="SUPABASE_SERVICE_ROLE_KEY")
    database_url: str = Field(default="postgresql+asyncpg://demo:demo@localhost:5432/demo", env="DATABASE_URL")
    
    # AI Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # CORS Configuration
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:19006"],
        env="CORS_ORIGINS"
    )
    
    # Observability
    prometheus_port: int = Field(default=8001, env="PROMETHEUS_PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings() 
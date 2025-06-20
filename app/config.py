"""Application configuration using Pydantic settings."""

from typing import Optional, List
from pydantic import Field, field_validator
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
    supabase_direct_url: Optional[str] = Field(default=None, env="SUPABASE_DIRECT_URL")
    supabase_connection_pooling: bool = Field(default=True, env="SUPABASE_CONNECTION_POOLING")

    # AI Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")

    # MindsDB Configuration
    mindsdb_enabled: bool = Field(default=False, env="MINDSDB_ENABLED")
    mindsdb_host: Optional[str] = Field(default=None, env="MINDSDB_HOST")
    mindsdb_port: int = Field(default=47334, env="MINDSDB_PORT")
    mindsdb_user: Optional[str] = Field(default=None, env="MINDSDB_USER")
    mindsdb_password: Optional[str] = Field(default=None, env="MINDSDB_PASSWORD")
    mindsdb_use_https: bool = Field(default=True, env="MINDSDB_USE_HTTPS")

    # Gmail Configuration
    gmail_enabled: bool = Field(default=False, env="GMAIL_ENABLED")
    gmail_client_id: Optional[str] = Field(default=None, env="GMAIL_CLIENT_ID")
    gmail_client_secret: Optional[str] = Field(default=None, env="GMAIL_CLIENT_SECRET")
    gmail_refresh_token: Optional[str] = Field(default=None, env="GMAIL_REFRESH_TOKEN")

    # CORS Configuration - More robust parsing
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:19006", "tauri://localhost", "tauri://*"],
        env="CORS_ORIGINS",
        description="CORS origins as JSON array string, e.g., '[\"*\"]' or '[\"https://example.com\"]'"
    )

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            try:
                import json
                return json.loads(v)
            except json.JSONDecodeError:
                # If JSON parsing fails, treat as single origin
                return [v] if v else ["*"]
        return v if isinstance(v, list) else ["*"]

    # Tauri Configuration
    tauri_enabled: bool = Field(default=False, env="TAURI_ENABLED")
    tauri_allowed_origins: List[str] = Field(
        default=["tauri://localhost", "tauri://*"],
        env="TAURI_ALLOWED_ORIGINS"
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

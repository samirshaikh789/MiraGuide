"""MiraGuide Backend Configuration"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "MiraGuide"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8787

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./miraguide.db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # AI Providers
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_VISION_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"
    GEMINI_VISION_MODEL: str = "gemini-1.5-pro"

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    DEFAULT_VISION_PROVIDER: str = "demo"
    DEFAULT_TEXT_PROVIDER: str = "demo"
    DEFAULT_OCR_PROVIDER: str = "demo"
    DEFAULT_STT_PROVIDER: str = "demo"
    DEFAULT_TTS_PROVIDER: str = "demo"

    # Demo Mode
    DEMO_MODE: bool = True

    # File Upload
    MAX_FILE_SIZE_MB: int = 8
    ALLOWED_MIME_TYPES: List[str] = Field(
        default=["image/jpeg", "image/png", "image/webp", "image/gif", "application/pdf"]
    )
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".webp", ".gif", ".pdf"]
    )

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"]
    )
    CORS_ALLOW_CREDENTIALS: bool = True

    # Security
    SECRET_KEY: str = "change-me-in-production"
    API_KEY_HEADER: str = "X-API-Key"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Request ID
    REQUEST_ID_HEADER: str = "X-Request-ID"

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def has_real_ai_provider(self) -> bool:
        return bool(
            self.OPENAI_API_KEY or self.GEMINI_API_KEY or self.ANTHROPIC_API_KEY
        )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
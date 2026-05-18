"""
Application configuration loaded from environment variables.
Uses pydantic-settings for validation and .env file support.
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central configuration for the application.
    All values are loaded from environment variables or .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "ClearView API"
    debug: bool = False

    # Database - async connection string (asyncpg driver for PostgreSQL)
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/clearview"

    # External APIs (optional - for future use)
    openai_api_key: str | None = None

    # Semantic retrieval
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    faiss_index_dir: str = "data/faiss_indexes"

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value: object) -> object:
        """Handle shells that set DEBUG to environment names like 'release'."""
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production"}:
                return False
            if normalized in {"dev", "development"}:
                return True
        return value


# Singleton instance - import this for config access
settings = Settings()

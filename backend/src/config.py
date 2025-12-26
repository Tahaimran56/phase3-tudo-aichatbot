"""Application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = "postgresql://localhost/todoapp"

    # Authentication
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    frontend_url: str = "http://localhost:3000"

    # Environment
    environment: str = "development"

    # Phase 3: OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_timeout: int = 60

    # Phase 3: Chat Configuration
    max_conversation_messages: int = 20
    chat_rate_limit_per_minute: int = 60

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

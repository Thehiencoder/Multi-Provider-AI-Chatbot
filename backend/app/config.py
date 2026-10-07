from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # LLM API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # Redis Config
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TTL_HOURS: int = 24
    SLIDING_WINDOW_SIZE: int = 20

    # Default Models
    DEFAULT_OPENAI_MODEL: str = "gpt-4o-mini"
    DEFAULT_CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    DEFAULT_GEMINI_MODEL: str = "gemini-3.8-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

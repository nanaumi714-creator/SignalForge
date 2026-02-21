"""Application settings management for SCOUT SYSTEM."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed environment settings loaded from .env and process env."""

    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_key: str = Field(..., alias="SUPABASE_KEY")

    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", alias="OPENAI_MODEL")

    youtube_api_key: str = Field(..., alias="YOUTUBE_API_KEY")
    discord_webhook_url: str = Field(..., alias="DISCORD_WEBHOOK_URL")
    
    scout_api_key: str = Field(..., alias="SCOUT_API_KEY")

    hot_threshold: int = Field(85, alias="HOT_THRESHOLD")
    batch_size: int = Field(5, alias="BATCH_SIZE")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()

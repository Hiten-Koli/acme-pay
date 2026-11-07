"""Application settings, loaded from environment variables (and `.env` locally)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed runtime configuration.

    Attributes:
        database_url: PostgreSQL connection URL. Any `postgresql://` URL works,
            including Neon's, and is adapted for the async driver at startup.
        gemini_api_key: Enables the AI pay analyst when set (Google AI Studio, free tier).
        gemini_model: Gemini model id. Default: a free-tier model that passes all
            golden evals and stays responsive when larger free models are overloaded.
    """

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    # Local-development default matching docker-compose.yml; never used in production.
    database_url: str = "postgresql://acme:acme@localhost:5432/acme_pay"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.5-flash-lite"


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings, read once."""
    return Settings()

"""
config/settings.py
Centralised settings loaded from environment variables.
All services import from here — never read os.environ directly.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ───────────────────────────────────────────────────
    debug: bool = False
    log_level: str = "INFO"
    environment: str = "production"

    # ── Auth ──────────────────────────────────────────────────
    api_secret_key: str = "change_this_to_a_random_32_char_string"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # ── LLM ───────────────────────────────────────────────────
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-70b-versatile"

    # ── Database ──────────────────────────────────────────────
    database_url: str = "postgresql://autopilot:autopilot@localhost:5432/autopilot"
    postgres_user: str = "autopilot"
    postgres_password: str = "autopilot"
    postgres_db: str = "autopilot"
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    # ── Redis ─────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── ChromaDB ──────────────────────────────────────────────
    chroma_host: str = "localhost"
    chroma_port: int = 8000

    # ── LangSmith ─────────────────────────────────────────────
    langchain_tracing_v2: bool = True
    langchain_endpoint: str = "https://api.smith.langchain.com"
    langchain_api_key: str = ""
    langchain_project: str = "auto-pilot"

    # ── Telegram ──────────────────────────────────────────────
    telegram_bot_token: str = ""
    telegram_webhook_url: str = ""

    # ── Discord ───────────────────────────────────────────────
    discord_bot_token: str = ""
    discord_guild_id: str = ""

    # ── Gmail ─────────────────────────────────────────────────
    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    gmail_redirect_uri: str = "http://localhost:8000/auth/gmail/callback"
    gmail_user_email: str = ""

    # ── Notion ────────────────────────────────────────────────
    notion_api_key: str = ""
    notion_database_id: str = ""

    # ── Slack ─────────────────────────────────────────────────
    slack_bot_token: str = ""
    slack_app_token: str = ""
    slack_signing_secret: str = ""
    slack_channel_id: str = ""

    # ── Service URLs ──────────────────────────────────────────
    gateway_url: str = "http://localhost:8000"
    agents_url: str = "http://localhost:8001"
    memory_url: str = "http://localhost:8002"


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()


settings = get_settings()

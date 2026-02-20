"""
Updated configuration with LangSmith, Qdrant, and multi-agent settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List


class Settings(BaseSettings):

    # LLM
    groq_api_key: str = Field(default="")
    fast_model: str = Field(default="llama-3.1-8b-instant")
    smart_model: str = Field(default="llama-3.1-70b-versatile")

    # LangSmith Monitoring
    langchain_tracing_v2: str = Field(default="true")
    langchain_endpoint: str = Field(default="https://api.smith.langchain.com")
    langchain_api_key: str = Field(default="")
    langchain_project: str = Field(default="deep-research-agent")

    # Source APIs
    github_token: str = Field(default="")

    # Qdrant Vector DB
    qdrant_host: str = Field(default="localhost")
    qdrant_port: int = Field(default=6333)
    qdrant_collection_name: str = Field(default="research_cache")
    embedding_model: str = Field(default="all-MiniLM-L6-v2")
    semantic_cache_threshold: float = Field(default=0.85)

    # Supabase
    supabase_url: Optional[str] = Field(default=None)
    supabase_key: Optional[str] = Field(default=None)

    # App
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    enable_streaming: bool = Field(default=True)
    max_results_per_source: int = Field(default=10)
    quality_threshold: float = Field(default=0.70)
    supervisor_recursion_limit: int = Field(default=25)

    # MCP
    mcp_server_name: str = Field(default="deep-research-agent")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8501"]
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()


def get_settings() -> Settings:
    return settings


def validate_required_settings():
    errors = []
    if not settings.groq_api_key:
        errors.append("GROQ_API_KEY is required")
    if not settings.github_token:
        print("⚠️  GitHub token not set - GitHub search limited to 60 req/hr")
    if not settings.langchain_api_key:
        print("⚠️  LangSmith not configured - tracing disabled")
    if errors:
        raise ValueError("\n".join(errors))
    print("✅ Configuration validated")

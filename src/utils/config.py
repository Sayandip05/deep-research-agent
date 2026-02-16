"""
Configuration management for Deep Research Agent.
Loads settings from environment variables with validation.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # =============================================================================
    # LLM Configuration
    # =============================================================================
    groq_api_key: str = Field(default="", description="Groq API key")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    
    # Model selection
    fast_model: str = Field(default="llama-3.1-8b-instant", description="Fast model for simple tasks")
    smart_model: str = Field(default="llama-3.1-70b-versatile", description="Smart model for complex synthesis")
    
    # =============================================================================
    # Source API Keys
    # =============================================================================
    github_token: str = Field(default="", description="GitHub personal access token")
    reddit_client_id: str = Field(default="", description="Reddit client ID")
    reddit_client_secret: str = Field(default="", description="Reddit client secret")
    reddit_user_agent: str = Field(default="deep-research-agent/1.0", description="Reddit user agent")
    
    # =============================================================================
    # Database (Optional)
    # =============================================================================
    supabase_url: Optional[str] = Field(default=None, description="Supabase project URL")
    supabase_key: Optional[str] = Field(default=None, description="Supabase anon key")
    
    # =============================================================================
    # Application Settings
    # =============================================================================
    environment: str = Field(default="development", description="Environment (development/production)")
    debug: bool = Field(default=True, description="Debug mode")
    
    # API
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    
    # Cache
    cache_type: str = Field(default="memory", description="Cache type (memory/redis)")
    cache_ttl: int = Field(default=3600, description="Cache TTL in seconds")
    
    # Rate Limits
    rate_limit_requests: int = Field(default=30, description="Rate limit requests")
    rate_limit_period: int = Field(default=60, description="Rate limit period in seconds")
    
    # =============================================================================
    # Model Configuration
    # =============================================================================
    enable_streaming: bool = Field(default=True, description="Enable streaming responses")
    
    # =============================================================================
    # Search Configuration
    # =============================================================================
    max_results_per_source: int = Field(default=10, description="Max results per source")
    semantic_cache_threshold: float = Field(default=0.85, description="Semantic cache similarity threshold")
    quality_threshold: float = Field(default=0.70, description="Quality score threshold for refinement")
    
    # =============================================================================
    # Security (Optional)
    # =============================================================================
    secret_key: Optional[str] = Field(default=None, description="JWT secret key")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8501"],
        description="CORS allowed origins"
    )
    
    # =============================================================================
    # Monitoring (Optional)
    # =============================================================================
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN")
    logtail_source_token: Optional[str] = Field(default=None, description="Logtail source token")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def validate_required_settings():
    """
    Validate that required settings are configured.
    Raises ValueError if critical settings are missing.
    """
    errors = []
    
    # Check LLM configuration
    if not settings.groq_api_key and not settings.openai_api_key and not settings.anthropic_api_key:
        errors.append("At least one LLM API key must be configured (Groq/OpenAI/Anthropic)")
    
    # Check source APIs (at least one should be configured)
    if not settings.github_token:
        print("⚠️  Warning: GitHub token not configured. GitHub search will be limited.")
    
    if not settings.reddit_client_id or not settings.reddit_client_secret:
        print("⚠️  Warning: Reddit credentials not configured. Reddit search will be disabled.")
    
    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    print("✅ Configuration validated successfully")


if __name__ == "__main__":
    # Test configuration loading
    validate_required_settings()
    print(f"\n📋 Current Configuration:")
    print(f"  Environment: {settings.environment}")
    print(f"  Debug Mode: {settings.debug}")
    print(f"  Fast Model: {settings.fast_model}")
    print(f"  Smart Model: {settings.smart_model}")
    print(f"  API Host: {settings.api_host}:{settings.api_port}")
    print(f"  Streaming: {settings.enable_streaming}")
    print(f"  Cache Type: {settings.cache_type}")
    print(f"  Cache TTL: {settings.cache_ttl}s")

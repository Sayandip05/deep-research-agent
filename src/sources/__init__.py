"""Sources package - search adapters for different platforms."""

from .base import BaseSource, SearchResult, SourceRegistry, source_registry
from .github import GitHubSource
from .hackernews import HackerNewsSource

# Initialize and register sources
def initialize_sources():
    """Initialize and register all source adapters."""
    github = GitHubSource()
    hackernews = HackerNewsSource()
    
    source_registry.register(github)
    source_registry.register(hackernews)
    
    print("✅ Initialized sources:")
    print(f"   - GitHub")
    print(f"   - Hacker News")


__all__ = [
    "BaseSource",
    "SearchResult",
    "SourceRegistry",
    "source_registry",
    "GitHubSource",
    "HackerNewsSource",
    "initialize_sources",
]

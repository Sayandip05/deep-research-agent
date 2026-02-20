"""Sources package - GitHub, Hacker News, Stack Overflow adapters."""

from .base import BaseSource, SearchResult, SourceRegistry, source_registry
from .github import GitHubSource
from .hackernews import HackerNewsSource
from .stackoverflow import StackOverflowSource


def initialize_sources():
    source_registry.register(GitHubSource())
    source_registry.register(HackerNewsSource())
    source_registry.register(StackOverflowSource())
    print("✅ Sources initialized: GitHub | Hacker News | Stack Overflow")


__all__ = [
    "BaseSource", "SearchResult", "SourceRegistry", "source_registry",
    "GitHubSource", "HackerNewsSource", "StackOverflowSource",
    "initialize_sources",
]

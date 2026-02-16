"""
Base source adapter abstract class.
All source implementations (GitHub, Reddit, etc.) inherit from this.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SearchResult:
    """Standardized search result format across all sources."""
    
    source: str  # e.g., "github", "reddit", "hackernews"
    title: str
    url: str
    content: str
    author: Optional[str] = None
    score: Optional[int] = None  # upvotes, stars, etc.
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source": self.source,
            "title": self.title,
            "url": self.url,
            "content": self.content,
            "author": self.author,
            "score": self.score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata or {},
        }


class BaseSource(ABC):
    """
    Abstract base class for all source adapters.
    
    Each source (GitHub, Reddit, etc.) implements this interface
    to provide consistent search functionality.
    """
    
    def __init__(self):
        """Initialize the source adapter."""
        self.source_name = self.__class__.__name__.replace("Source", "").lower()
    
    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """
        Search the source for relevant results.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the source is properly configured and available.
        
        Returns:
            True if source can be used, False otherwise
        """
        pass
    
    def get_name(self) -> str:
        """Get the source name."""
        return self.source_name
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test the source connection and return status.
        
        Returns:
            Dictionary with connection status and details
        """
        try:
            available = await self.is_available()
            return {
                "source": self.source_name,
                "available": available,
                "status": "ok" if available else "unavailable",
            }
        except Exception as e:
            return {
                "source": self.source_name,
                "available": False,
                "status": "error",
                "error": str(e),
            }


class SourceRegistry:
    """
    Registry to manage all available sources.
    Allows dynamic enabling/disabling of sources.
    """
    
    def __init__(self):
        self._sources: Dict[str, BaseSource] = {}
    
    def register(self, source: BaseSource):
        """Register a new source."""
        self._sources[source.get_name()] = source
    
    def get_source(self, name: str) -> Optional[BaseSource]:
        """Get a source by name."""
        return self._sources.get(name)
    
    async def get_available_sources(self) -> List[BaseSource]:
        """Get all available (configured) sources."""
        available = []
        for source in self._sources.values():
            if await source.is_available():
                available.append(source)
        return available
    
    async def search_all(self, query: str, max_results_per_source: int = 10) -> Dict[str, List[SearchResult]]:
        """
        Search all available sources in parallel.
        
        Args:
            query: Search query
            max_results_per_source: Max results per source
            
        Returns:
            Dictionary mapping source names to their results
        """
        import asyncio
        
        available_sources = await self.get_available_sources()
        
        # Search all sources in parallel
        tasks = [
            source.search(query, max_results_per_source)
            for source in available_sources
        ]
        
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Map results to source names
        results = {}
        for source, result in zip(available_sources, results_list):
            if isinstance(result, Exception):
                print(f"⚠️  Error searching {source.get_name()}: {result}")
                results[source.get_name()] = []
            else:
                results[source.get_name()] = result
        
        return results


# Global source registry instance
source_registry = SourceRegistry()

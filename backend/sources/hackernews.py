"""
Hacker News source adapter using Algolia API.
Completely free, no authentication required.
"""

from typing import List
from datetime import datetime
import httpx
from .base import BaseSource, SearchResult


class HackerNewsSource(BaseSource):
    """
    Hacker News source adapter using Algolia search API.
    No authentication required - completely free.
    """
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://hn.algolia.com/api/v1"
    
    async def is_available(self) -> bool:
        """HN API is always available (no auth required)."""
        return True
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """
        Search Hacker News stories and comments.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of SearchResult objects
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/search",
                    params={
                        "query": query,
                        "tags": "story",  # Search stories only (not comments)
                        "hitsPerPage": min(max_results, 50),
                    },
                )
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("hits", [])[:max_results]:
                    # Get title
                    title = item.get("title", "No title")
                    
                    # Get URL (prefer story_url, fallback to HN discussion)
                    url = item.get("url") or f"https://news.ycombinator.com/item?id={item['objectID']}"
                    
                    # Get content (story text or first comment)
                    content = item.get("story_text") or item.get("title", "")
                    
                    result = SearchResult(
                        source="hackernews",
                        title=title,
                        url=url,
                        content=content,
                        author=item.get("author"),
                        score=item.get("points", 0),
                        created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                        metadata={
                            "num_comments": item.get("num_comments", 0),
                            "story_id": item["objectID"],
                        },
                    )
                    results.append(result)
                
                return results
                
        except Exception as e:
            print(f"⚠️  Error searching Hacker News: {e}")
            return []

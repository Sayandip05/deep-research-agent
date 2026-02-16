"""
GitHub source adapter for searching repositories, issues, and code.
"""

from typing import List, Optional
from datetime import datetime
import httpx
from .base import BaseSource, SearchResult
from ..utils.config import settings


class GitHubSource(BaseSource):
    """
    GitHub source adapter using REST API.
    Searches repositories by default (can be extended for issues, code).
    """
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.github.com"
        self.token = settings.github_token
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    async def is_available(self) -> bool:
        """Check if GitHub token is configured."""
        return bool(self.token)
    
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """
        Search GitHub repositories.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of SearchResult objects
        """
        if not await self.is_available():
            print("⚠️  GitHub token not configured, skipping search")
            return []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Search repositories
                response = await client.get(
                    f"{self.base_url}/search/repositories",
                    params={
                        "q": query,
                        "sort": "stars",
                        "order": "desc",
                        "per_page": min(max_results, 30),
                    },
                    headers=self.headers,
                )
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("items", [])[:max_results]:
                    result = SearchResult(
                        source="github",
                        title=item["full_name"],
                        url=item["html_url"],
                        content=item.get("description", "No description"),
                        author=item["owner"]["login"],
                        score=item["stargazers_count"],
                        created_at=datetime.fromisoformat(item["created_at"].replace("Z", "+00:00")),
                        metadata={
                            "language": item.get("language"),
                            "forks": item["forks_count"],
                            "open_issues": item["open_issues_count"],
                            "topics": item.get("topics", []),
                        },
                    )
                    results.append(result)
                
                return results
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                print("⚠️  GitHub API rate limit exceeded")
            else:
                print(f"⚠️  GitHub API error: {e}")
            return []
        except Exception as e:
            print(f"⚠️  Error searching GitHub: {e}")
            return []

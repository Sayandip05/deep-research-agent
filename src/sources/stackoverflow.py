"""
Stack Overflow source adapter - FREE API, no key needed.
"""

from typing import List
from datetime import datetime
import httpx
from .base import BaseSource, SearchResult


class StackOverflowSource(BaseSource):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.stackexchange.com/2.3"

    async def is_available(self) -> bool:
        return True  # Always available, no auth needed

    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/search/advanced",
                    params={
                        "order": "desc",
                        "sort": "relevance",
                        "q": query,
                        "site": "stackoverflow",
                        "pagesize": min(max_results, 30),
                        "filter": "withbody",
                    }
                )
                response.raise_for_status()
                data = response.json()

                results = []
                for item in data.get("items", [])[:max_results]:
                    content = item.get("body", "")[:500] if item.get("body") else item.get("title", "")
                    # Strip HTML tags simply
                    import re
                    content = re.sub(r'<[^>]+>', '', content).strip()

                    result = SearchResult(
                        source="stackoverflow",
                        title=item["title"],
                        url=item["link"],
                        content=content,
                        author=item.get("owner", {}).get("display_name"),
                        score=item.get("score", 0),
                        created_at=datetime.fromtimestamp(item["creation_date"]),
                        metadata={
                            "answer_count": item.get("answer_count", 0),
                            "is_answered": item.get("is_answered", False),
                            "accepted_answer_id": item.get("accepted_answer_id"),
                            "tags": item.get("tags", []),
                        }
                    )
                    results.append(result)
                return results

        except Exception as e:
            print(f"⚠️  Stack Overflow search error: {e}")
            return []

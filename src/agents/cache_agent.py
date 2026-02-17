"""
Cache Agent - Semantic caching with Qdrant vector database.
"""

import hashlib
from typing import Dict, Any, Optional
from langchain_core.messages import AIMessage
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from .state import AgentState, AgentNames
from ..utils.config import settings


class CacheAgent:
    def __init__(self):
        self.name = AgentNames.CACHE
        self.threshold = settings.semantic_cache_threshold
        self.encoder = SentenceTransformer(settings.embedding_model)
        self.vector_size = self.encoder.get_sentence_embedding_dimension()
        self.collection = settings.qdrant_collection_name

        try:
            self.client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
            self._ensure_collection()
            self.available = True
            print(f"✅ Qdrant connected at {settings.qdrant_host}:{settings.qdrant_port}")
        except Exception as e:
            print(f"⚠️  Qdrant unavailable: {e} - cache disabled")
            self.client = None
            self.available = False

    def _ensure_collection(self):
        cols = [c.name for c in self.client.get_collections().collections]
        if self.collection not in cols:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
            )

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        if not self.available:
            return {
                "cache_hit": False,
                "messages": [AIMessage(content="⚠️  Cache offline, proceeding fresh", name=self.name)],
                "next_agent": AgentNames.SEARCH,
            }

        query = state["query"]
        cached = self._get(query)

        if cached:
            return {
                "cache_hit": True,
                "cached_result": cached["payload"],
                "synthesis": cached["payload"].get("synthesis"),
                "citations": cached["payload"].get("citations"),
                "quality_score": cached["payload"].get("quality_score", 1.0),
                "messages": [AIMessage(content=f"💾 Cache HIT (similarity: {cached['score']:.2f}) - returning cached result", name=self.name)],
                "next_agent": AgentNames.MEMORY,
            }

        return {
            "cache_hit": False,
            "messages": [AIMessage(content="💾 Cache MISS - starting fresh research", name=self.name)],
            "next_agent": AgentNames.SEARCH,
        }

    def _get(self, query: str) -> Optional[Dict]:
        try:
            vec = self.encoder.encode(query).tolist()
            results = self.client.search(
                collection_name=self.collection,
                query_vector=vec,
                limit=1,
                score_threshold=self.threshold
            )
            if results:
                return {"payload": results[0].payload, "score": results[0].score}
        except Exception as e:
            print(f"⚠️  Cache lookup error: {e}")
        return None

    def store(self, state: AgentState) -> bool:
        if not self.available:
            return False
        try:
            query = state["query"]
            payload = {
                "query": query,
                "synthesis": state.get("synthesis"),
                "citations": state.get("citations"),
                "quality_score": state.get("quality_score"),
            }
            vec = self.encoder.encode(query).tolist()
            point_id = int(hashlib.md5(query.encode()).hexdigest()[:8], 16)
            self.client.upsert(
                collection_name=self.collection,
                points=[PointStruct(id=point_id, vector=vec, payload=payload)]
            )
            print(f"✅ Cached: {query[:50]}...")
            return True
        except Exception as e:
            print(f"⚠️  Cache store error: {e}")
            return False

    def stats(self) -> Dict:
        if not self.available:
            return {"status": "offline"}
        try:
            info = self.client.get_collection(self.collection)
            return {"total_cached": info.points_count, "threshold": self.threshold, "status": "online"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

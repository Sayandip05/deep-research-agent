"""
FastAPI application - REST API + SSE streaming for Deep Research Agent.
"""

import asyncio
import json
import uuid
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

from backend.agents import SupervisorAgent
from backend.sources import initialize_sources
from config.settings import settings, validate_required_settings


# ─── Models ───────────────────────────────────────────────────────────────────

class ResearchRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    max_results_per_source: Optional[int] = 5


class ResearchResponse(BaseModel):
    query: str
    synthesis: str
    citations: list
    key_insights: list
    quality_score: float
    cache_hit: bool
    sources_used: list
    session_id: Optional[str]


# ─── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Deep Research Agent API",
    description="Multi-agent research system with semantic caching and streaming",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supervisor: Optional[SupervisorAgent] = None


@app.on_event("startup")
async def startup():
    global supervisor
    print("🚀 Starting Deep Research Agent API v2...")
    validate_required_settings()
    initialize_sources()
    supervisor = SupervisorAgent()
    print("✅ API ready → http://localhost:8000")
    print("📚 Docs    → http://localhost:8000/docs")


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "name": "Deep Research Agent API",
        "version": "2.0.0",
        "agents": 7,
        "features": ["multi-agent", "semantic-cache", "streaming", "mcp"],
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "supervisor": supervisor is not None}


@app.get("/cache/stats")
async def cache_stats():
    """Get Qdrant cache statistics."""
    if not supervisor:
        raise HTTPException(503, "Agent not initialized")
    return supervisor.cache_agent.stats()


@app.post("/research", response_model=ResearchResponse)
async def research(req: ResearchRequest):
    """Full multi-agent research - returns complete report."""
    if not supervisor:
        raise HTTPException(503, "Agent not initialized")
    try:
        result = await supervisor.research(req.query, session_id=req.session_id)
        return ResearchResponse(**result)
    except Exception as e:
        raise HTTPException(500, f"Research failed: {e}")


@app.post("/research/stream")
async def research_stream(req: ResearchRequest):
    """
    Stream research progress via Server-Sent Events.
    Connect with EventSource in JS or text/event-stream in Python.
    """
    if not supervisor:
        raise HTTPException(503, "Agent not initialized")

    async def generate():
        try:
            async for update in supervisor.stream_research(req.query, session_id=req.session_id):
                yield {
                    "event": update.get("agent", "update"),
                    "data": json.dumps(update),
                }
        except Exception as e:
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return EventSourceResponse(generate())


@app.get("/sources")
async def list_sources():
    """List all sources and their availability."""
    from backend.sources import source_registry
    sources = []
    for source in source_registry._sources.values():
        status = await source.test_connection()
        sources.append(status)
    return {
        "sources": sources,
        "total": len(sources),
        "available": sum(1 for s in sources if s["available"]),
    }


@app.get("/history/{session_id}")
async def get_history(session_id: str):
    """Get research history for a session."""
    if not supervisor:
        raise HTTPException(503, "Agent not initialized")
    history = supervisor.memory_agent.get_history(session_id)
    return {"session_id": session_id, "history": history or []}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.main:app", host=settings.api_host, port=settings.api_port, reload=settings.debug)

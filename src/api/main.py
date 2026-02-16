"""
FastAPI application for Deep Research Agent.
Provides REST API endpoints for research queries.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio

from ..agent import ResearchAgent
from ..sources import initialize_sources
from ..utils.config import settings, validate_required_settings


# Request/Response Models
class ResearchRequest(BaseModel):
    """Research query request."""
    query: str
    max_results_per_source: Optional[int] = 5


class ResearchResponse(BaseModel):
    """Research query response."""
    query: str
    report: str
    metadata: Dict[str, Any]


# Initialize FastAPI app
app = FastAPI(
    title="Deep Research Agent API",
    description="AI-powered research assistant that searches multiple sources and synthesizes findings",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
research_agent: Optional[ResearchAgent] = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global research_agent
    
    print("🚀 Starting Deep Research Agent API...")
    
    # Validate configuration
    try:
        validate_required_settings()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        raise
    
    # Initialize sources
    initialize_sources()
    
    # Initialize agent
    research_agent = ResearchAgent()
    
    print("✅ API ready at http://localhost:8000")
    print("📚 Docs available at http://localhost:8000/docs")


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "Deep Research Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """
    Conduct research on a query.
    
    Returns a synthesized report with citations.
    """
    if not research_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Conduct research
        report = await research_agent.research(request.query)
        
        return ResearchResponse(
            query=request.query,
            report=report,
            metadata={
                "sources_used": ["github", "hackernews"],
                "max_results_per_source": request.max_results_per_source,
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")


@app.post("/research/quick")
async def quick_research(request: ResearchRequest):
    """
    Quick research that returns raw results without synthesis.
    Faster but less processed.
    """
    if not research_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        results = await research_agent.quick_research(request.query)
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick research failed: {str(e)}")


@app.get("/sources")
async def list_sources():
    """
    List all available sources and their status.
    """
    from ..sources import source_registry
    
    sources = []
    for source in source_registry._sources.values():
        status = await source.test_connection()
        sources.append(status)
    
    return {
        "sources": sources,
        "total": len(sources),
        "available": len([s for s in sources if s["available"]]),
    }


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle all unhandled exceptions."""
    return {
        "error": "Internal server error",
        "detail": str(exc) if settings.debug else "An error occurred",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )

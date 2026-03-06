"""
agents/main.py
Agent Engine FastAPI app — receives tasks from the Gateway, runs them through
the LangGraph supervisor, and returns results.
"""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from supervisor.supervisor_agent import SupervisorAgent

logger = structlog.get_logger()
supervisor: SupervisorAgent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global supervisor
    logger.info("agents.startup")
    supervisor = SupervisorAgent()
    await supervisor.initialize()
    app.state.supervisor = supervisor
    yield
    logger.info("agents.shutdown")


app = FastAPI(title="Auto-Pilot Agent Engine", version="1.0.0", lifespan=lifespan)

from routers import tasks_router   # noqa: E402 (import after app created)
app.include_router(tasks_router.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "agents"}

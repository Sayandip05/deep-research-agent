"""
agents/a2a/server.py
A2A JSON-RPC server — each specialist agent mounts this to expose its skills.
"""

from __future__ import annotations
import structlog
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any

logger = structlog.get_logger()


class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: str
    method: str
    params: dict = {}


def create_a2a_router(agent_name: str, skill_handlers: dict) -> APIRouter:
    """
    Factory that creates a JSON-RPC router for a specialist agent.

    skill_handlers: {"skill_name": async_function(params) -> result}
    """
    router = APIRouter()

    @router.post(f"/a2a/{agent_name.replace('_agent', '')}")
    async def handle(request: JsonRpcRequest):
        handler = skill_handlers.get(request.method)
        if not handler:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request.id,
                "error": {"code": -32601, "message": f"Skill '{request.method}' not found"},
            })
        try:
            result = await handler(request.params)
            return {"jsonrpc": "2.0", "id": request.id, "result": result}
        except Exception as e:
            logger.error("a2a.skill_error", agent=agent_name, skill=request.method, error=str(e))
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request.id,
                "error": {"code": -32603, "message": str(e)},
            })

    @router.get(f"/.well-known/agent.json")
    async def agent_card():
        import json
        from pathlib import Path
        card_path = Path(__file__).parent / "agent_cards" / f"{agent_name.replace('_agent', '')}.json"
        if card_path.exists():
            return JSONResponse(json.loads(card_path.read_text()))
        return JSONResponse({"name": agent_name, "skills": list(skill_handlers.keys())})

    return router

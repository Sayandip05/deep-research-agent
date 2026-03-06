"""
agents/a2a/client.py
A2A Protocol Client — discovers agents via Agent Cards and sends
JSON-RPC tasks to them.
"""

from __future__ import annotations
import json
import uuid
from pathlib import Path
from typing import Any

import httpx
import structlog

logger = structlog.get_logger()

AGENT_CARDS_DIR = Path(__file__).parent / "agent_cards"

# Map agent names to their base URLs (configurable via env)
import os
AGENT_URLS = {
    "browser_agent":       os.getenv("BROWSER_AGENT_URL",       "http://agents:8001/a2a/browser"),
    "email_agent":         os.getenv("EMAIL_AGENT_URL",         "http://agents:8001/a2a/email"),
    "task_agent":          os.getenv("TASK_AGENT_URL",          "http://agents:8001/a2a/task"),
    "file_agent":          os.getenv("FILE_AGENT_URL",          "http://agents:8001/a2a/file"),
    "memory_agent":        os.getenv("MEMORY_AGENT_URL",        "http://agents:8001/a2a/memory"),
    "notification_agent":  os.getenv("NOTIFICATION_AGENT_URL",  "http://agents:8001/a2a/notification"),
}


class A2AClient:
    """Send tasks to specialist agents using JSON-RPC over HTTP."""

    def load_agent_card(self, agent_name: str) -> dict:
        card_path = AGENT_CARDS_DIR / f"{agent_name.replace('_agent', '')}.json"
        if card_path.exists():
            return json.loads(card_path.read_text())
        return {}

    async def call_agent(
        self,
        agent_name: str,
        skill: str,
        params: dict,
        timeout: int = 60,
    ) -> Any:
        """
        Send a JSON-RPC request to a specialist agent.
        Returns the result or raises on failure.
        """
        url = AGENT_URLS.get(agent_name)
        if not url:
            raise ValueError(f"Unknown agent: {agent_name}")

        request_id = str(uuid.uuid4())
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": skill,
            "params": params,
        }

        logger.info("a2a.call", agent=agent_name, skill=skill, request_id=request_id)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()

            if "error" in data:
                raise RuntimeError(f"Agent error: {data['error']}")

            result = data.get("result")
            logger.info("a2a.success", agent=agent_name, skill=skill)
            return result

        except httpx.RequestError as e:
            logger.error("a2a.connection_failed", agent=agent_name, error=str(e))
            # Return a graceful fallback instead of crashing the whole workflow
            return {"error": f"Agent '{agent_name}' unavailable: {e}", "fallback": True}

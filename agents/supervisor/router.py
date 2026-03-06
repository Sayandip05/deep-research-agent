"""
agents/supervisor/router.py
A2A Agent Discovery Router — maps workflow types to specialist agent calls
and exposes a well-known agent card discovery endpoint.
"""

from __future__ import annotations
import json
from pathlib import Path

import structlog

logger = structlog.get_logger()

AGENT_CARDS_DIR = Path(__file__).parent.parent / "a2a" / "agent_cards"


def discover_agents() -> list[dict]:
    """Load all agent cards from the agent_cards directory."""
    agents = []
    for card_file in AGENT_CARDS_DIR.glob("*.json"):
        try:
            agents.append(json.loads(card_file.read_text()))
        except Exception as e:
            logger.warning("router.card_parse_error", file=str(card_file), error=str(e))
    return agents


def get_agents_for_workflow(workflow_type: str) -> list[str]:
    """Return which specialist agents are needed for a given workflow."""
    WORKFLOW_AGENTS = {
        "price_tracker":       ["browser_agent", "memory_agent", "notification_agent"],
        "price_tracker_check": ["browser_agent", "memory_agent", "notification_agent"],
        "email_to_calendar":   ["email_agent", "memory_agent", "notification_agent"],
        "slack_to_notion":     ["task_agent", "memory_agent", "notification_agent"],
        "file_organizer":      ["file_agent", "memory_agent", "notification_agent"],
        "social_poster":       ["browser_agent", "notification_agent"],
    }
    return WORKFLOW_AGENTS.get(workflow_type, [])


def get_skills_for_workflow(workflow_type: str) -> list[str]:
    """Return which SKILL.md files are relevant for a given workflow."""
    WORKFLOW_SKILLS = {
        "price_tracker":       ["browser", "price_tracker"],
        "price_tracker_check": ["browser", "price_tracker"],
        "email_to_calendar":   ["gmail"],
        "slack_to_notion":     ["slack", "notion"],
        "file_organizer":      [],
        "social_poster":       ["browser"],
    }
    return WORKFLOW_SKILLS.get(workflow_type, [])

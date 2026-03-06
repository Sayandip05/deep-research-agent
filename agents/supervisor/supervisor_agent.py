"""
agents/supervisor/supervisor_agent.py
ReAct Supervisor — the brain. Reasons about tasks, reads SKILL.md files,
delegates to specialist agents via A2A, and synthesises results.
"""

from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Any, TypedDict, Annotated
import operator

import structlog
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "config"))
from settings import settings

logger = structlog.get_logger()

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills"

SYSTEM_PROMPT = """You are Auto-Pilot's Supervisor Agent. You operate in a ReAct loop:
Reason → Act → Observe → Reason → ...

Your job:
1. Understand the user's task.
2. Read the relevant SKILL.md files to understand your capabilities.
3. Create a step-by-step execution plan.
4. Delegate sub-tasks to specialist agents.
5. Synthesise results and report back clearly.

Available specialist agents and their domains:
- browser_agent: web scraping, price extraction, form filling, social posting
- email_agent: read Gmail, draft replies, extract meeting info
- task_agent: create/update Notion and Trello tasks
- file_agent: organise local filesystem
- memory_agent: read/write to vector memory (ChromaDB)
- notification_agent: send Telegram/Discord messages

Always think step by step. If a step fails, adapt your plan.
Be concise in your final response to the user.
"""


class AgentState(TypedDict):
    task_id: str
    workflow_type: str
    input_data: dict
    user_key: str
    messages: Annotated[list, operator.add]
    plan: str
    current_step: int
    results: dict
    final_response: str
    status: str


class SupervisorAgent:
    def __init__(self):
        self.llm = None
        self.graph = None

    async def initialize(self):
        """Initialise LLM and build the LangGraph state machine."""
        if not settings.groq_api_key:
            logger.warning("supervisor.no_groq_key", msg="Set GROQ_API_KEY in .env")

        self.llm = ChatGroq(
            api_key=settings.groq_api_key or "placeholder",
            model=settings.groq_model,
            temperature=0,
        )
        self.graph = self._build_graph()
        logger.info("supervisor.initialized")

    def _read_skill(self, skill_name: str) -> str:
        """Read a SKILL.md file and return its content."""
        path = SKILLS_DIR / skill_name / "SKILL.md"
        if path.exists():
            return path.read_text()
        return f"[SKILL.md for '{skill_name}' not found]"

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        graph.add_node("plan", self._plan_node)
        graph.add_node("execute", self._execute_node)
        graph.add_node("summarise", self._summarise_node)

        graph.set_entry_point("plan")
        graph.add_edge("plan", "execute")
        graph.add_edge("execute", "summarise")
        graph.add_edge("summarise", END)

        return graph.compile()

    async def _plan_node(self, state: AgentState) -> dict:
        """Reason about the task and create an execution plan."""
        workflow = state["workflow_type"]
        input_data = state["input_data"]

        # Read relevant skill docs
        skill_map = {
            "email_to_calendar": ["gmail"],
            "slack_to_notion": ["slack", "notion"],
            "price_tracker": ["browser", "price_tracker"],
            "file_organizer": [],
            "social_poster": ["browser"],
        }
        skills_content = "\n\n".join(
            f"=== {s} ===\n{self._read_skill(s)}"
            for s in skill_map.get(workflow, [])
        )

        prompt = f"""Task: {workflow}
Input: {json.dumps(input_data, indent=2)}

Relevant skills:
{skills_content or '(no specific skills required)'}

Create a numbered execution plan. Be specific about which specialist agent handles each step."""

        response = await self.llm.ainvoke(
            [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]
        )
        plan = response.content
        logger.info("supervisor.plan_created", task_id=state["task_id"])

        return {
            "plan": plan,
            "messages": [AIMessage(content=f"Plan:\n{plan}")],
            "status": "executing",
        }

    async def _execute_node(self, state: AgentState) -> dict:
        """Execute the plan by calling specialist agents."""
        from agents.a2a.client import A2AClient

        results = {}
        workflow = state["workflow_type"]
        input_data = state["input_data"]

        # Dispatch to the right workflow handler
        try:
            client = A2AClient()

            if workflow in ("price_tracker", "price_tracker_check"):
                from workflows.price_tracker import run as pt_run
                pt_result = await pt_run(input_data, user_key=state["user_key"])
                results["price_tracker"] = pt_result

            elif workflow == "email_to_calendar":
                email_result = await client.call_agent(
                    "email_agent",
                    "read_recent_emails",
                    {"max_results": 10},
                )
                results["emails"] = email_result

            elif workflow == "file_organizer":
                file_result = await client.call_agent(
                    "file_agent",
                    "organise_downloads",
                    {},
                )
                results["file_changes"] = file_result

            elif workflow == "slack_to_notion":
                results["status"] = "Slack→Notion workflow triggered"

            elif workflow == "social_poster":
                post_result = await client.call_agent(
                    "browser_agent",
                    "post_to_social",
                    input_data,
                )
                results["post"] = post_result

        except Exception as e:
            logger.error("supervisor.execute_error", error=str(e))
            results["error"] = str(e)

        return {"results": results, "status": "summarising"}

    async def _summarise_node(self, state: AgentState) -> dict:
        """Synthesise results into a user-friendly response."""
        results_str = json.dumps(state["results"], indent=2, default=str)
        prompt = f"""Task '{state["workflow_type"]}' completed.

Results:
{results_str}

Write a concise, friendly summary for the user. Use plain language. Include key numbers or outcomes."""

        response = await self.llm.ainvoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]
        )
        final = response.content
        return {"final_response": final, "status": "completed"}

    async def run(
        self,
        task_id: str,
        workflow_type: str,
        input_data: dict,
        user_key: str = "default",
    ) -> dict:
        """Entry point — run the full ReAct graph for a task."""
        initial_state: AgentState = {
            "task_id": task_id,
            "workflow_type": workflow_type,
            "input_data": input_data,
            "user_key": user_key,
            "messages": [],
            "plan": "",
            "current_step": 0,
            "results": {},
            "final_response": "",
            "status": "pending",
        }

        final_state = await self.graph.ainvoke(initial_state)
        return {
            "task_id": task_id,
            "status": final_state["status"],
            "plan": final_state["plan"],
            "results": final_state["results"],
            "response": final_state["final_response"],
        }

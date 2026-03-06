"""
agents/supervisor/planner_agent.py
Deep Research Planner — drafts, critiques, and revises execution plans
before any action is taken.
"""

from __future__ import annotations
import structlog
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

logger = structlog.get_logger()

PLANNER_SYSTEM = """You are a meticulous planning agent. Your role is to:
1. Receive a high-level task.
2. Draft a detailed step-by-step execution plan.
3. Critique the plan — identify edge cases, missing steps, failure modes.
4. Revise the plan to address the critique.
5. Output the final, revised plan in numbered format.

Each step must specify:
- Which specialist agent executes it
- What input it receives
- What output it produces
- What to do if it fails

Never skip the critique step.
"""


class PlannerAgent:
    def __init__(self, llm: ChatGroq):
        self.llm = llm

    async def create_plan(self, task: str, context: str = "") -> str:
        prompt = f"""Task: {task}

Context:
{context or 'No additional context.'}

Draft a plan, critique it, then output the final revised plan."""

        response = await self.llm.ainvoke(
            [SystemMessage(content=PLANNER_SYSTEM), HumanMessage(content=prompt)]
        )
        plan = response.content
        logger.info("planner.plan_created", task=task[:60])
        return plan

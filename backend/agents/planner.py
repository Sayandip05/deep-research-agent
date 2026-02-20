"""
Planner Agent - Analyzes queries and creates research plans.
"""

import json
from typing import Dict, Any
from langchain_core.messages import AIMessage, HumanMessage
from langchain_groq import ChatGroq
from .state import AgentState, AgentNames


class PlannerAgent:
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        self.name = AgentNames.PLANNER

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        query = state["query"]

        prompt = f"""Analyze this research query and return ONLY valid JSON:

Query: "{query}"

{{
  "complexity": <1-10>,
  "intent": {{
    "type": "<comparison|explanation|trend|best_practices|tutorial>",
    "topics": ["topic1", "topic2"],
    "context": "domain context"
  }},
  "plan": {{
    "strategy": "research approach",
    "key_questions": ["q1", "q2", "q3"],
    "sources_priority": ["github", "stackoverflow", "hackernews"]
  }},
  "subtasks": ["specific search query 1", "specific search query 2"],
  "selected_sources": ["github", "stackoverflow", "hackernews"]
}}"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content.strip()
            if "```" in content:
                content = content.split("```")[1].lstrip("json").strip()
            data = json.loads(content)
        except Exception:
            data = {
                "complexity": 5,
                "intent": {"type": "general", "topics": [query], "context": "technical"},
                "plan": {"strategy": "broad search", "key_questions": [query], "sources_priority": ["github", "hackernews", "stackoverflow"]},
                "subtasks": [query],
                "selected_sources": ["github", "hackernews", "stackoverflow"]
            }

        return {
            "intent": data.get("intent"),
            "complexity": data.get("complexity", 5),
            "plan": data.get("plan"),
            "subtasks": data.get("subtasks", [query]),
            "selected_sources": data.get("selected_sources", ["github", "hackernews"]),
            "messages": [AIMessage(content=f"📋 Plan created | Complexity: {data.get('complexity')}/10 | Sources: {data.get('selected_sources')}", name=self.name)],
            "next_agent": AgentNames.CACHE,
        }

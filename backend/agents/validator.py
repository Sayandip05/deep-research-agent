"""Validator Agent - checks synthesis quality and citation accuracy."""

from typing import Dict, Any
from langchain_core.messages import AIMessage, HumanMessage
from langchain_groq import ChatGroq
from .state import AgentState, AgentNames
import json


class ValidatorAgent:
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        self.name = AgentNames.VALIDATOR

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        query = state["query"]
        synthesis = state.get("synthesis", "")
        raw_results = state.get("raw_results", {})
        retry_count = state.get("retry_count", 0)

        quality_score, issues = self._validate(query, synthesis, raw_results)
        needs_refinement = quality_score < 0.7 and retry_count < 2

        return {
            "quality_score": quality_score,
            "needs_refinement": needs_refinement,
            "retry_count": retry_count + (1 if needs_refinement else 0),
            "messages": [AIMessage(
                content=f"✅ Validation | Score: {quality_score:.2f} | Issues: {issues} | Refine: {needs_refinement}",
                name=self.name
            )],
            "next_agent": AgentNames.SEARCH if needs_refinement else AgentNames.MEMORY,
        }

    def _validate(self, query: str, synthesis: str, raw_results: Dict) -> tuple:
        issues = []
        score = 1.0

        # Check synthesis length (too short = poor quality)
        if len(synthesis) < 200:
            issues.append("synthesis_too_short")
            score -= 0.3

        # Check if query topic appears in synthesis
        query_words = set(query.lower().split())
        synthesis_words = set(synthesis.lower().split())
        overlap = len(query_words & synthesis_words) / max(len(query_words), 1)
        if overlap < 0.3:
            issues.append("low_query_relevance")
            score -= 0.2

        # Check if we have results from multiple sources
        if len(raw_results) < 2:
            issues.append("insufficient_sources")
            score -= 0.1

        # Check total result count
        total = sum(len(v) for v in raw_results.values())
        if total < 3:
            issues.append("too_few_results")
            score -= 0.2

        return max(0.0, score), issues

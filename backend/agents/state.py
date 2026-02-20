"""
Shared state definitions for the 7-agent supervisor system.
"""

from typing import TypedDict, Annotated, Sequence, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    query: str
    session_id: Optional[str]

    # Planner outputs
    intent: Optional[Dict[str, Any]]
    complexity: Optional[int]
    plan: Optional[Dict[str, Any]]
    subtasks: Optional[List[str]]
    selected_sources: Optional[List[str]]

    # Cache
    cache_hit: Optional[bool]
    cached_result: Optional[Dict[str, Any]]

    # Search results
    raw_results: Optional[Dict[str, List[Dict[str, Any]]]]

    # Synthesis
    synthesis: Optional[str]
    key_insights: Optional[List[str]]
    citations: Optional[List[Dict[str, Any]]]

    # Validation
    quality_score: Optional[float]
    needs_refinement: Optional[bool]
    retry_count: Optional[int]

    # Memory
    conversation_history: Optional[List[Dict[str, Any]]]

    # Routing
    next_agent: Optional[str]
    errors: Optional[List[str]]


class AgentNames:
    SUPERVISOR = "supervisor"
    PLANNER = "planner"
    CACHE = "cache_agent"
    SEARCH = "search_coordinator"
    SYNTHESIZER = "synthesizer"
    VALIDATOR = "validator"
    MEMORY = "memory_agent"
    FINISH = "__end__"

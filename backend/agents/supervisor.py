"""
Supervisor Agent - LangGraph StateGraph orchestrating all 7 agents.
Pattern: Supervisor routes between specialized agents based on state.
"""

from typing import Dict, Any, AsyncIterator
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import os

from .state import AgentState, AgentNames
from .planner import PlannerAgent
from database.cache_agent import CacheAgent
from .search_coordinator import SearchCoordinatorAgent
from .synthesizer import SynthesizerAgent
from .validator import ValidatorAgent
from database.memory_agent import MemoryAgent
from config.settings import settings


class SupervisorAgent:
    """
    7-Agent Supervisor System using LangGraph.

    Flow:
    START → Planner → Cache → [HIT: Memory] [MISS: Search → Synthesizer → Validator → Memory] → END
    """

    def __init__(self):
        # Setup LangSmith tracing
        if settings.langchain_api_key:
            os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
            os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
            os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
            print(f"✅ LangSmith tracing enabled → project: {settings.langchain_project}")

        # Initialize LLMs
        fast_llm = ChatGroq(api_key=settings.groq_api_key, model_name=settings.fast_model, temperature=0.3)
        smart_llm = ChatGroq(api_key=settings.groq_api_key, model_name=settings.smart_model, temperature=0.7)

        # Initialize all agents
        self.planner = PlannerAgent(llm=fast_llm)
        self.cache_agent = CacheAgent()
        self.search_coordinator = SearchCoordinatorAgent()
        self.synthesizer = SynthesizerAgent(llm=smart_llm)
        self.validator = ValidatorAgent(llm=fast_llm)
        self.memory_agent = MemoryAgent()

        # Build the graph
        self.graph = self._build_graph()
        print("✅ Multi-agent supervisor initialized with 7 agents")

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)

        # Register all agent nodes
        workflow.add_node(AgentNames.PLANNER, self.planner)
        workflow.add_node(AgentNames.CACHE, self.cache_agent)
        workflow.add_node(AgentNames.SEARCH, self.search_coordinator)
        workflow.add_node(AgentNames.SYNTHESIZER, self.synthesizer)
        workflow.add_node(AgentNames.VALIDATOR, self.validator)
        workflow.add_node(AgentNames.MEMORY, self.memory_agent)

        # Entry point
        workflow.set_entry_point(AgentNames.PLANNER)

        # Fixed edges
        workflow.add_edge(AgentNames.PLANNER, AgentNames.CACHE)
        workflow.add_edge(AgentNames.SEARCH, AgentNames.SYNTHESIZER)
        workflow.add_edge(AgentNames.SYNTHESIZER, AgentNames.VALIDATOR)
        workflow.add_edge(AgentNames.MEMORY, END)

        # Conditional: after cache
        workflow.add_conditional_edges(
            AgentNames.CACHE,
            lambda state: AgentNames.MEMORY if state.get("cache_hit") else AgentNames.SEARCH,
            {AgentNames.MEMORY: AgentNames.MEMORY, AgentNames.SEARCH: AgentNames.SEARCH}
        )

        # Conditional: after validation - refine or finish
        workflow.add_conditional_edges(
            AgentNames.VALIDATOR,
            lambda state: AgentNames.SEARCH if state.get("needs_refinement") else AgentNames.MEMORY,
            {AgentNames.SEARCH: AgentNames.SEARCH, AgentNames.MEMORY: AgentNames.MEMORY}
        )

        # Compile with memory checkpointing
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)

    async def research(self, query: str, session_id: str = None) -> Dict[str, Any]:
        """Run full multi-agent research pipeline."""
        import uuid
        config = {"configurable": {"thread_id": session_id or str(uuid.uuid4())}}

        initial_state: AgentState = {
            "messages": [],
            "query": query,
            "session_id": session_id,
            "retry_count": 0,
        }

        result = await self.graph.ainvoke(initial_state, config=config)

        # Store result in cache for future queries
        if result.get("synthesis") and not result.get("cache_hit"):
            self.cache_agent.store(result)

        return {
            "query": query,
            "synthesis": result.get("synthesis", ""),
            "citations": result.get("citations", []),
            "key_insights": result.get("key_insights", []),
            "quality_score": result.get("quality_score", 0),
            "cache_hit": result.get("cache_hit", False),
            "sources_used": list(result.get("raw_results", {}).keys()),
            "session_id": result.get("session_id"),
            "agent_messages": [m.content for m in result.get("messages", [])],
        }

    async def stream_research(self, query: str, session_id: str = None) -> AsyncIterator[Dict[str, Any]]:
        """Stream research progress event by event."""
        import uuid
        config = {"configurable": {"thread_id": session_id or str(uuid.uuid4())}}

        initial_state: AgentState = {
            "messages": [],
            "query": query,
            "session_id": session_id,
            "retry_count": 0,
        }

        async for event in self.graph.astream(initial_state, config=config, stream_mode="updates"):
            for node_name, node_output in event.items():
                messages = node_output.get("messages", [])
                for msg in messages:
                    yield {
                        "agent": node_name,
                        "message": msg.content if hasattr(msg, "content") else str(msg),
                        "next": node_output.get("next_agent"),
                    }

            # Yield final result when done
            if "__end__" in event or AgentNames.MEMORY in event:
                final = event.get(AgentNames.MEMORY, {})
                if final:
                    yield {"agent": "complete", "message": "✅ Research complete", "final": True}

"""Search Coordinator Agent - manages parallel searches across all sources."""

import asyncio
from typing import Dict, Any, List
from langchain_core.messages import AIMessage
from .state import AgentState, AgentNames
from backend.sources import source_registry


class SearchCoordinatorAgent:
    def __init__(self):
        self.name = AgentNames.SEARCH

    async def __call__(self, state: AgentState) -> Dict[str, Any]:
        query = state["query"]
        subtasks = state.get("subtasks", [query])
        selected_sources = state.get("selected_sources", ["github", "hackernews", "stackoverflow"])

        # Run all subtask searches in parallel across selected sources
        all_results: Dict[str, List[Dict]] = {}
        search_tasks = []

        available = await source_registry.get_available_sources()
        active_sources = [s for s in available if s.get_name() in selected_sources]

        if not active_sources:
            active_sources = available  # fallback to all

        for source in active_sources:
            for subtask in subtasks[:3]:  # cap at 3 subtasks
                search_tasks.append((source.get_name(), source.search(subtask, max_results=5)))

        # Execute in parallel
        task_results = await asyncio.gather(
            *[task for _, task in search_tasks],
            return_exceptions=True
        )

        for (source_name, _), result in zip(search_tasks, task_results):
            if isinstance(result, Exception):
                print(f"⚠️  {source_name} search failed: {result}")
                continue
            if source_name not in all_results:
                all_results[source_name] = []
            for r in result:
                all_results[source_name].append(r.to_dict())

        total = sum(len(v) for v in all_results.values())

        return {
            "raw_results": all_results,
            "messages": [AIMessage(
                content=f"🔍 Search complete | Sources: {list(all_results.keys())} | Total results: {total}",
                name=self.name
            )],
            "next_agent": AgentNames.SYNTHESIZER,
        }

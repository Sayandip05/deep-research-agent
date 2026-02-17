"""Synthesizer Agent - combines research findings into coherent reports."""

import json
from typing import Dict, Any, List
from langchain_core.messages import AIMessage, HumanMessage
from langchain_groq import ChatGroq
from .state import AgentState, AgentNames


class SynthesizerAgent:
    def __init__(self, llm: ChatGroq):
        self.llm = llm
        self.name = AgentNames.SYNTHESIZER

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        query = state["query"]
        raw_results = state.get("raw_results", {})
        plan = state.get("plan", {})

        # Format results for LLM
        formatted = self._format_results(raw_results)

        prompt = f"""You are a research synthesis expert. Create a comprehensive, well-structured report.

Original Query: {query}
Research Strategy: {plan.get('strategy', 'Comprehensive analysis')}
Key Questions to Answer: {plan.get('key_questions', [])}

Research Data:
{formatted}

Write a detailed synthesis report that:
1. Directly answers the query
2. Identifies consensus across sources
3. Highlights contradictions or debates
4. Provides concrete recommendations
5. Uses [Source: platform] citations inline

Format with clear sections using markdown headers.
Be specific, technical, and actionable."""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        synthesis = response.content

        # Extract citations
        citations = self._extract_citations(raw_results)

        # Extract key insights
        insight_prompt = f"""From this research synthesis, extract 5 key insights as a JSON array of strings:

{synthesis[:2000]}

Return ONLY a JSON array: ["insight1", "insight2", ...]"""

        try:
            insight_resp = self.llm.invoke([HumanMessage(content=insight_prompt)])
            content = insight_resp.content.strip()
            if "```" in content:
                content = content.split("```")[1].lstrip("json").strip()
            insights = json.loads(content)
        except Exception:
            insights = ["See full report for detailed insights"]

        return {
            "synthesis": synthesis,
            "citations": citations,
            "key_insights": insights,
            "messages": [AIMessage(
                content=f"✍️  Synthesis complete | {len(synthesis)} chars | {len(citations)} citations",
                name=self.name
            )],
            "next_agent": AgentNames.VALIDATOR,
        }

    def _format_results(self, raw_results: Dict) -> str:
        output = []
        for source, results in raw_results.items():
            output.append(f"\n### {source.upper()} ({len(results)} results)")
            for i, r in enumerate(results[:5], 1):
                output.append(f"{i}. **{r['title']}** (score: {r.get('score', 'N/A')})")
                output.append(f"   URL: {r['url']}")
                output.append(f"   {r['content'][:200]}...")
        return "\n".join(output)

    def _extract_citations(self, raw_results: Dict) -> List[Dict]:
        citations = []
        for source, results in raw_results.items():
            for r in results[:5]:
                citations.append({
                    "source": source,
                    "title": r["title"],
                    "url": r["url"],
                    "score": r.get("score"),
                    "author": r.get("author"),
                })
        return citations

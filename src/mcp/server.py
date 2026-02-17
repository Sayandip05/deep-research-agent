"""
FastMCP Server - 6 research tools for Claude Desktop and AI assistants.

Tools:
1. research_topic         - Full multi-agent research
2. search_github          - GitHub repository search
3. search_hackernews      - Hacker News search
4. search_stackoverflow   - Stack Overflow Q&A search
5. compare_technologies   - Compare X vs Y
6. analyze_trends         - What's trending in topic
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastmcp import FastMCP
from src.agents import SupervisorAgent
from src.sources import source_registry, initialize_sources
from src.utils.config import settings

# Initialize MCP server
mcp = FastMCP(settings.mcp_server_name)

# Initialize sources and agent
initialize_sources()
_supervisor: SupervisorAgent = None


def get_supervisor() -> SupervisorAgent:
    global _supervisor
    if _supervisor is None:
        _supervisor = SupervisorAgent()
    return _supervisor


# ─────────────────────────────────────────────
# Tool 1: Full Research
# ─────────────────────────────────────────────
@mcp.tool()
async def research_topic(query: str) -> str:
    """
    Conduct comprehensive AI-powered research using 7 specialized agents.
    Searches GitHub, Hacker News, and Stack Overflow, then synthesizes findings.

    Args:
        query: The research topic or question

    Returns:
        Detailed research report with citations and key insights
    """
    supervisor = get_supervisor()
    result = await supervisor.research(query)

    output = f"# Research Report: {query}\n\n"
    output += f"**Quality Score:** {result['quality_score']:.0%}\n"
    output += f"**Cache Hit:** {'Yes ⚡' if result['cache_hit'] else 'No (fresh research)'}\n"
    output += f"**Sources Used:** {', '.join(result['sources_used'])}\n\n"

    if result.get("key_insights"):
        output += "## 💡 Key Insights\n"
        for insight in result["key_insights"]:
            output += f"- {insight}\n"
        output += "\n"

    output += "## 📊 Full Analysis\n"
    output += result.get("synthesis", "No synthesis available")
    output += "\n\n## 📚 Citations\n"

    for i, cite in enumerate(result.get("citations", [])[:10], 1):
        output += f"{i}. [{cite['title']}]({cite['url']}) - {cite['source']}\n"

    return output


# ─────────────────────────────────────────────
# Tool 2: GitHub Search
# ─────────────────────────────────────────────
@mcp.tool()
async def search_github(query: str, max_results: int = 10) -> str:
    """
    Search GitHub repositories for code, projects, and implementations.
    Best for: finding libraries, frameworks, code examples, and open-source projects.

    Args:
        query: GitHub search query
        max_results: Number of results (1-30)

    Returns:
        Top GitHub repositories matching the query
    """
    source = source_registry.get_source("github")
    if not source or not await source.is_available():
        return "⚠️ GitHub source not available. Add GITHUB_TOKEN to .env"

    results = await source.search(query, max_results=min(max_results, 30))
    if not results:
        return f"No GitHub results found for: {query}"

    output = f"# GitHub Results: {query}\n\n"
    for i, r in enumerate(results, 1):
        output += f"## {i}. {r.title}\n"
        output += f"⭐ Stars: {r.score:,} | Language: {r.metadata.get('language', 'N/A')}\n"
        output += f"🔗 {r.url}\n"
        output += f"{r.content}\n\n"
    return output


# ─────────────────────────────────────────────
# Tool 3: Hacker News Search
# ─────────────────────────────────────────────
@mcp.tool()
async def search_hackernews(query: str, max_results: int = 10) -> str:
    """
    Search Hacker News for tech discussions, trends, and community opinions.
    Best for: community sentiment, tech news, startup trends, engineering debates.

    Args:
        query: Search query
        max_results: Number of results (1-50)

    Returns:
        Top Hacker News stories matching the query
    """
    source = source_registry.get_source("hackernews")
    if not source:
        return "⚠️ Hacker News source not available"

    results = await source.search(query, max_results=min(max_results, 50))
    if not results:
        return f"No Hacker News results found for: {query}"

    output = f"# Hacker News: {query}\n\n"
    for i, r in enumerate(results, 1):
        output += f"## {i}. {r.title}\n"
        output += f"▲ Points: {r.score} | 💬 Comments: {r.metadata.get('num_comments', 0)}\n"
        output += f"🔗 {r.url}\n\n"
    return output


# ─────────────────────────────────────────────
# Tool 4: Stack Overflow Search
# ─────────────────────────────────────────────
@mcp.tool()
async def search_stackoverflow(query: str, max_results: int = 10) -> str:
    """
    Search Stack Overflow for technical Q&A, solutions, and best practices.
    Best for: debugging, how-to questions, technical implementations.

    Args:
        query: Technical question or topic
        max_results: Number of results (1-30)

    Returns:
        Relevant Stack Overflow questions with answers
    """
    source = source_registry.get_source("stackoverflow")
    if not source:
        return "⚠️ Stack Overflow source not available"

    results = await source.search(query, max_results=min(max_results, 30))
    if not results:
        return f"No Stack Overflow results found for: {query}"

    output = f"# Stack Overflow: {query}\n\n"
    for i, r in enumerate(results, 1):
        answered = "✅" if r.metadata.get("is_answered") else "❓"
        output += f"## {i}. {answered} {r.title}\n"
        output += f"👍 Score: {r.score} | 💬 Answers: {r.metadata.get('answer_count', 0)}\n"
        output += f"🏷️  Tags: {', '.join(r.metadata.get('tags', []))}\n"
        output += f"🔗 {r.url}\n"
        output += f"{r.content[:300]}...\n\n"
    return output


# ─────────────────────────────────────────────
# Tool 5: Compare Technologies
# ─────────────────────────────────────────────
@mcp.tool()
async def compare_technologies(tech1: str, tech2: str, context: str = "") -> str:
    """
    Compare two technologies, frameworks, or tools using multi-source research.
    Provides objective comparison with community consensus.

    Args:
        tech1: First technology (e.g., "Redux")
        tech2: Second technology (e.g., "Zustand")
        context: Optional context (e.g., "for React applications")

    Returns:
        Detailed comparison report with pros/cons and recommendations
    """
    ctx = f" {context}" if context else ""
    query = f"Compare {tech1} vs {tech2}{ctx}"

    supervisor = get_supervisor()
    result = await supervisor.research(query)

    output = f"# {tech1} vs {tech2} Comparison\n\n"
    if context:
        output += f"**Context:** {context}\n\n"
    output += f"**Quality Score:** {result['quality_score']:.0%} | "
    output += f"**Sources:** {', '.join(result['sources_used'])}\n\n"

    if result.get("key_insights"):
        output += "## ⚡ Quick Verdict\n"
        for insight in result["key_insights"][:3]:
            output += f"- {insight}\n"
        output += "\n"

    output += result.get("synthesis", "")
    return output


# ─────────────────────────────────────────────
# Tool 6: Analyze Trends
# ─────────────────────────────────────────────
@mcp.tool()
async def analyze_trends(topic: str, timeframe: str = "2024") -> str:
    """
    Analyze current trends in a technology or domain area.
    Searches recent discussions, GitHub activity, and community sentiment.

    Args:
        topic: Technology or domain to analyze (e.g., "AI agents", "Rust web frameworks")
        timeframe: Time period (e.g., "2024", "recent", "this year")

    Returns:
        Trend analysis report with adoption data and predictions
    """
    query = f"Trends and adoption of {topic} in {timeframe}"
    supervisor = get_supervisor()
    result = await supervisor.research(query)

    output = f"# Trend Analysis: {topic} ({timeframe})\n\n"
    output += f"**Sources:** {', '.join(result['sources_used'])}\n\n"

    if result.get("key_insights"):
        output += "## 📈 Key Trends\n"
        for insight in result["key_insights"]:
            output += f"- {insight}\n"
        output += "\n"

    output += "## 📊 Full Analysis\n"
    output += result.get("synthesis", "")
    return output


if __name__ == "__main__":
    print(f"🚀 Starting MCP Server: {settings.mcp_server_name}")
    print("📋 Tools available:")
    print("   1. research_topic")
    print("   2. search_github")
    print("   3. search_hackernews")
    print("   4. search_stackoverflow")
    print("   5. compare_technologies")
    print("   6. analyze_trends")
    mcp.run()

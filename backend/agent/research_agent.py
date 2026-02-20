"""
Main Research Agent using Deep Agents framework.
Orchestrates multi-source research with intelligent synthesis.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from langchain_groq import ChatGroq
from deepagents import create_deep_agent
from langchain_core.tools import tool
from backend.sources import source_registry, SearchResult
from config.settings import settings


@dataclass
class ResearchResult:
    """Final research result with synthesis and citations."""
    
    query: str
    synthesis: str
    citations: List[Dict[str, Any]]
    raw_results: Dict[str, List[SearchResult]]
    metadata: Dict[str, Any]


class ResearchAgent:
    """
    Deep Research Agent that searches multiple sources and synthesizes findings.
    """
    
    def __init__(self):
        """Initialize the research agent with Deep Agents."""
        
        # Initialize LLM
        self.llm = ChatGroq(
            api_key=settings.groq_api_key,
            model_name=settings.smart_model,
            temperature=0.7,
        )
        
        # Create tools for the agent
        self.tools = self._create_tools()
        
        # Create Deep Agent
        self.agent = create_deep_agent(
            tools=self.tools,
            model=self.llm,
            system_prompt=self._get_system_prompt(),
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the research agent."""
        return """You are an expert research assistant specializing in technical topics.

Your task is to:
1. Understand the user's research query
2. Search relevant sources (GitHub, Hacker News, etc.)
3. Analyze and synthesize the findings
4. Provide a comprehensive report with proper citations

Guidelines:
- Use multiple sources to get diverse perspectives
- Prioritize recent and authoritative sources
- Cite all claims with [Source: name] format
- Identify consensus and contradictions
- Be objective and balanced
- Focus on technical accuracy

When searching:
- Use specific, targeted search queries
- Search sources in parallel when possible
- Validate the quality of results

When synthesizing:
- Organize findings logically
- Highlight key insights
- Compare different approaches
- Provide actionable recommendations
"""
    
    def _create_tools(self) -> List:
        """Create LangChain tools for source searching."""
        
        @tool
        async def search_github(query: str) -> str:
            """
            Search GitHub repositories for relevant code, projects, and discussions.
            Best for: Finding popular libraries, code examples, and active projects.
            
            Args:
                query: Search query for GitHub repositories
            
            Returns:
                Formatted string with search results
            """
            source = source_registry.get_source("github")
            if not source:
                return "GitHub source not available"
            
            results = await source.search(query, max_results=5)
            
            if not results:
                return f"No GitHub results found for: {query}"
            
            output = f"GitHub Search Results for '{query}':\n\n"
            for i, result in enumerate(results, 1):
                output += f"{i}. {result.title}\n"
                output += f"   Stars: {result.score}\n"
                output += f"   URL: {result.url}\n"
                output += f"   Description: {result.content}\n"
                if result.metadata.get("language"):
                    output += f"   Language: {result.metadata['language']}\n"
                output += "\n"
            
            return output
        
        @tool
        async def search_hackernews(query: str) -> str:
            """
            Search Hacker News for discussions, trends, and community opinions.
            Best for: Tech news, startup trends, community sentiment.
            
            Args:
                query: Search query for Hacker News stories
            
            Returns:
                Formatted string with search results
            """
            source = source_registry.get_source("hackernews")
            if not source:
                return "Hacker News source not available"
            
            results = await source.search(query, max_results=5)
            
            if not results:
                return f"No Hacker News results found for: {query}"
            
            output = f"Hacker News Search Results for '{query}':\n\n"
            for i, result in enumerate(results, 1):
                output += f"{i}. {result.title}\n"
                output += f"   Points: {result.score}\n"
                output += f"   URL: {result.url}\n"
                output += f"   Comments: {result.metadata.get('num_comments', 0)}\n"
                output += "\n"
            
            return output
        
        return [search_github, search_hackernews]
    
    async def research(self, query: str) -> str:
        """
        Conduct research on the given query.
        
        Args:
            query: Research question or topic
            
        Returns:
            Synthesized research report
        """
        print(f"🔍 Starting research for: {query}")
        
        # Invoke the Deep Agent
        result = await self.agent.ainvoke({
            "messages": [
                {
                    "role": "user",
                    "content": f"Research this topic thoroughly and provide a comprehensive report: {query}"
                }
            ]
        })
        
        # Extract the final response
        messages = result.get("messages", [])
        if messages:
            final_message = messages[-1]
            return final_message.content
        
        return "No results generated"
    
    async def quick_research(self, query: str) -> Dict[str, Any]:
        """
        Quick research that returns structured data.
        
        Args:
            query: Research query
            
        Returns:
            Dictionary with results and metadata
        """
        # Search all sources in parallel
        all_results = await source_registry.search_all(query, max_results_per_source=5)
        
        # Count total results
        total_results = sum(len(results) for results in all_results.values())
        
        # Format results
        formatted_results = {}
        for source_name, results in all_results.items():
            formatted_results[source_name] = [r.to_dict() for r in results]
        
        return {
            "query": query,
            "total_results": total_results,
            "sources": list(all_results.keys()),
            "results": formatted_results,
        }


# Example usage
async def main():
    """Example usage of the research agent."""
    agent = ResearchAgent()
    
    # Example query
    result = await agent.research("What are the best practices for React hooks?")
    print("\n" + "="*80)
    print("RESEARCH REPORT")
    print("="*80)
    print(result)


if __name__ == "__main__":
    import asyncio
    from backend.sources import initialize_sources
    
    # Initialize sources
    initialize_sources()
    
    # Run research
    asyncio.run(main())

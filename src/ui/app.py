"""
Streamlit UI for Deep Research Agent.
Simple web interface for conducting research queries.
"""

import streamlit as st
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agent import ResearchAgent
from src.sources import initialize_sources
from src.utils.config import settings, validate_required_settings


# Page configuration
st.set_page_config(
    page_title="Deep Research Agent",
    page_icon="🔬",
    layout="wide",
)


@st.cache_resource
def get_agent():
    """Initialize and cache the research agent."""
    try:
        validate_required_settings()
        initialize_sources()
        return ResearchAgent()
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        return None


def main():
    """Main Streamlit app."""
    
    # Header
    st.title("🔬 Deep Research Agent")
    st.markdown("AI-powered research assistant that searches multiple sources and synthesizes findings")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        st.markdown("### Sources")
        st.markdown("✅ GitHub")
        st.markdown("✅ Hacker News")
        st.markdown("🔜 Reddit (coming soon)")
        st.markdown("🔜 Stack Overflow (coming soon)")
        
        st.markdown("---")
        
        st.markdown("### Model")
        st.text(f"Fast: {settings.fast_model}")
        st.text(f"Smart: {settings.smart_model}")
        
        st.markdown("---")
        
        st.markdown("### About")
        st.markdown("""
        This research agent:
        - Searches multiple technical sources
        - Synthesizes findings intelligently
        - Provides proper citations
        - Runs on 100% FREE infrastructure
        """)
    
    # Main content
    agent = get_agent()
    
    if not agent:
        st.error("❌ Agent not initialized. Check your configuration in .env file")
        st.stop()
    
    # Query input
    query = st.text_input(
        "🔍 What would you like to research?",
        placeholder="e.g., What are the best practices for React hooks?",
        help="Enter a technical topic or question"
    )
    
    # Example queries
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📚 React State Management"):
            query = "Compare Redux vs Zustand for React state management"
    with col2:
        if st.button("🦀 Rust for Web"):
            query = "Best Rust frameworks for web development in 2024"
    with col3:
        if st.button("🐍 Python Performance"):
            query = "How to optimize Python performance for data processing"
    
    # Research button
    if st.button("🚀 Start Research", type="primary", disabled=not query):
        if query:
            with st.spinner("🔍 Researching..."):
                # Run async research
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(agent.research(query))
                    loop.close()
                    
                    # Display results
                    st.success("✅ Research complete!")
                    
                    st.markdown("### 📊 Research Report")
                    st.markdown(result)
                    
                    # Display metadata
                    with st.expander("ℹ️ Metadata"):
                        st.json({
                            "query": query,
                            "sources": ["GitHub", "Hacker News"],
                            "model": settings.smart_model,
                        })
                
                except Exception as e:
                    st.error(f"❌ Research failed: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    Built with Deep Agents • Powered by Groq • 100% FREE Infrastructure
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

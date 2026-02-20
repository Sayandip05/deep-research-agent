"""
Streamlit UI v2 - Real-time streaming research with 7-agent progress display.
"""

import streamlit as st
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(page_title="Deep Research Agent", page_icon="🔬", layout="wide")

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.agent-box { padding: 8px 12px; border-radius: 6px; margin: 4px 0; font-size: 13px; }
.agent-planner    { background: #1e3a5f; border-left: 3px solid #4a9eff; }
.agent-cache      { background: #1e4a2e; border-left: 3px solid #4aff7a; }
.agent-search     { background: #4a2e1e; border-left: 3px solid #ff9a4a; }
.agent-synthesizer{ background: #3a1e4a; border-left: 3px solid #c44aff; }
.agent-validator  { background: #4a3a1e; border-left: 3px solid #ffcc4a; }
.agent-memory     { background: #1e3a4a; border-left: 3px solid #4ae0ff; }
.metric-card { background: #1e1e2e; padding: 12px; border-radius: 8px; text-align: center; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_supervisor():
    from backend.agents import SupervisorAgent
    from backend.sources import initialize_sources
    from config.settings import validate_required_settings
    validate_required_settings()
    initialize_sources()
    return SupervisorAgent()


def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


AGENT_COLORS = {
    "planner": "agent-planner",
    "cache_agent": "agent-cache",
    "search_coordinator": "agent-search",
    "synthesizer": "agent-synthesizer",
    "validator": "agent-validator",
    "memory_agent": "agent-memory",
}

AGENT_ICONS = {
    "planner": "📋",
    "cache_agent": "💾",
    "search_coordinator": "🔍",
    "synthesizer": "✍️",
    "validator": "✅",
    "memory_agent": "🧠",
}


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🔬 Deep Research Agent")
    st.caption("v2.0 - Multi-Agent System")
    st.markdown("---")

    st.markdown("### 🤖 Agent System")
    agents = ["📋 Planner", "💾 Cache (Qdrant)", "🔍 Search Coordinator",
              "✍️ Synthesizer", "✅ Validator", "🧠 Memory (Supabase)"]
    for a in agents:
        st.markdown(f"- {a}")

    st.markdown("---")
    st.markdown("### 📡 Sources")
    st.markdown("- ⭐ GitHub API")
    st.markdown("- 🔶 Hacker News")
    st.markdown("- 📚 Stack Overflow")

    st.markdown("---")
    st.markdown("### 🔧 MCP Tools")
    st.code("research_topic()\nsearch_github()\nsearch_hackernews()\nsearch_stackoverflow()\ncompare_technologies()\nanalyze_trends()")

    st.markdown("---")
    from config.settings import settings
    st.markdown("### ⚙️ Config")
    st.text(f"LangSmith: {'✅' if settings.langchain_api_key else '❌'}")
    st.text(f"Qdrant: {settings.qdrant_host}:{settings.qdrant_port}")
    st.text(f"Fast: {settings.fast_model.split('-')[0]}")
    st.text(f"Smart: {settings.smart_model.split('-')[0]}")


# ─── Main UI ──────────────────────────────────────────────────────────────────
st.title("🔬 Deep Research Agent")
st.caption("7 specialized AI agents · Qdrant semantic cache · Real-time streaming")

# Quick example buttons
col1, col2, col3, col4 = st.columns(4)
query = st.session_state.get("query", "")

with col1:
    if st.button("⚡ Redux vs Zustand"):
        query = "Compare Redux vs Zustand for React state management"
        st.session_state["query"] = query
with col2:
    if st.button("🦀 Rust for Web"):
        query = "Is Rust good for web development in 2024?"
        st.session_state["query"] = query
with col3:
    if st.button("🤖 AI Agents Trend"):
        query = "Trends in AI agent frameworks 2024"
        st.session_state["query"] = query
with col4:
    if st.button("🐍 FastAPI vs Flask"):
        query = "Compare FastAPI vs Flask for Python APIs"
        st.session_state["query"] = query

query_input = st.text_input("🔍 Research Query", value=query, placeholder="e.g., Compare Next.js vs Remix for React")

col_btn, col_mode = st.columns([2, 1])
with col_btn:
    run_btn = st.button("🚀 Start Research", type="primary", use_container_width=True, disabled=not query_input)
with col_mode:
    stream_mode = st.toggle("⚡ Stream Progress", value=True)

if run_btn and query_input:
    supervisor = get_supervisor()

    # Agent progress column
    col_agents, col_results = st.columns([1, 2])

    with col_agents:
        st.markdown("### 🤖 Agent Progress")
        progress_placeholder = st.empty()

    with col_results:
        st.markdown("### 📊 Research Report")
        result_placeholder = st.empty()

    agent_logs = []

    if stream_mode:
        # Streaming mode - show real-time progress
        with st.spinner(""):
            async def stream():
                result = None
                async for update in supervisor.stream_research(query_input):
                    agent_logs.append(update)

                    # Update agent progress display
                    with progress_placeholder.container():
                        for log in agent_logs[-10:]:
                            agent = log.get("agent", "")
                            css_class = AGENT_COLORS.get(agent, "agent-box")
                            icon = AGENT_ICONS.get(agent, "⚙️")
                            msg = log.get("message", "")[:80]
                            st.markdown(
                                f'<div class="agent-box {css_class}">{icon} <b>{agent}</b><br>{msg}</div>',
                                unsafe_allow_html=True
                            )

                    if log.get("final"):
                        result = await supervisor.research(query_input)
                        return result

                return await supervisor.research(query_input)

            result = run_async(stream())
    else:
        # Non-streaming mode
        with st.spinner("🔍 Researching... (this may take 10-30s)"):
            result = run_async(supervisor.research(query_input))

    # Display final result
    if result:
        # Metrics row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Quality Score", f"{result['quality_score']:.0%}")
        m2.metric("Cache Hit", "⚡ Yes" if result["cache_hit"] else "🔄 No")
        m3.metric("Sources", len(result["sources_used"]))
        m4.metric("Citations", len(result.get("citations", [])))

        # Key Insights
        if result.get("key_insights"):
            st.markdown("### 💡 Key Insights")
            for insight in result["key_insights"]:
                st.info(f"→ {insight}")

        # Full Report
        st.markdown("### 📝 Full Report")
        st.markdown(result.get("synthesis", "No synthesis available"))

        # Citations
        if result.get("citations"):
            with st.expander(f"📚 {len(result['citations'])} Citations"):
                for i, cite in enumerate(result["citations"], 1):
                    st.markdown(f"{i}. **[{cite['title']}]({cite['url']})** — {cite['source']} ({'⭐ ' + str(cite.get('score', '')) if cite.get('score') else ''})")

        # Session ID
        if result.get("session_id"):
            st.caption(f"Session: `{result['session_id']}`")

# Footer
st.markdown("---")
st.caption("Built with Deep Agents · LangGraph · Qdrant · Groq · FastMCP · LangSmith · 100% FREE")

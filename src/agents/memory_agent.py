"""Memory Agent - stores and retrieves research sessions from Supabase."""

from typing import Dict, Any, Optional
from langchain_core.messages import AIMessage
from .state import AgentState, AgentNames
from ..utils.config import settings
from datetime import datetime
import uuid


class MemoryAgent:
    def __init__(self):
        self.name = AgentNames.MEMORY
        self.client = None

        if settings.supabase_url and settings.supabase_key:
            try:
                from supabase import create_client
                self.client = create_client(settings.supabase_url, settings.supabase_key)
                print("✅ Supabase memory connected")
            except Exception as e:
                print(f"⚠️  Supabase unavailable: {e}")

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        session_id = state.get("session_id") or str(uuid.uuid4())

        # Build history entry
        entry = {
            "session_id": session_id,
            "query": state["query"],
            "synthesis": state.get("synthesis", ""),
            "quality_score": state.get("quality_score", 0),
            "sources_used": list(state.get("raw_results", {}).keys()),
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Store to Supabase if available
        stored = False
        if self.client:
            try:
                self.client.table("research_sessions").insert(entry).execute()
                stored = True
            except Exception as e:
                print(f"⚠️  Memory store error: {e}")

        # Get conversation history (last 5 queries for context)
        history = state.get("conversation_history", [])
        history.append({"query": state["query"], "timestamp": entry["timestamp"]})
        history = history[-5:]  # Keep last 5

        return {
            "session_id": session_id,
            "conversation_history": history,
            "messages": [AIMessage(
                content=f"🧠 Memory {'stored to Supabase' if stored else 'kept in-memory'} | Session: {session_id[:8]}...",
                name=self.name
            )],
            "next_agent": AgentNames.FINISH,
        }

    def get_history(self, session_id: str) -> Optional[list]:
        """Retrieve research history for a session."""
        if not self.client:
            return None
        try:
            result = (
                self.client.table("research_sessions")
                .select("*")
                .eq("session_id", session_id)
                .order("timestamp", desc=True)
                .limit(10)
                .execute()
            )
            return result.data
        except Exception as e:
            print(f"⚠️  History fetch error: {e}")
            return None

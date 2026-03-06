"""
agents/specialists/memory_agent.py
Interface to ChromaDB — three collections: preferences, episodes, skills.
"""

from __future__ import annotations
import os
import structlog
from typing import Any

logger = structlog.get_logger()

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))


def _get_client():
    import chromadb
    return chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)


def _get_embedding_fn():
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    return SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")


async def query_preferences(params: dict) -> dict:
    query = params.get("query", "")
    user_key = params.get("user_key", "default")
    top_k = params.get("top_k", 5)

    try:
        import asyncio
        def _query():
            client = _get_client()
            col = client.get_or_create_collection(
                "user_preferences",
                embedding_function=_get_embedding_fn()
            )
            results = col.query(
                query_texts=[query],
                n_results=top_k,
                where={"user_key": user_key},
            )
            memories = []
            for i, doc in enumerate(results["documents"][0]):
                memories.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                })
            return memories

        memories = await asyncio.get_event_loop().run_in_executor(None, _query)
        return {"memories": memories}

    except Exception as e:
        logger.error("memory.query_preferences_error", error=str(e))
        return {"memories": [], "error": str(e)}


async def store_preference(params: dict) -> dict:
    user_key = params.get("user_key", "default")
    content = params.get("content", "")
    metadata = params.get("metadata", {})

    try:
        import asyncio
        import uuid

        def _store():
            client = _get_client()
            col = client.get_or_create_collection(
                "user_preferences",
                embedding_function=_get_embedding_fn()
            )
            doc_id = str(uuid.uuid4())
            col.add(
                documents=[content],
                metadatas=[{"user_key": user_key, **metadata}],
                ids=[doc_id],
            )
            return doc_id

        doc_id = await asyncio.get_event_loop().run_in_executor(None, _store)
        logger.info("memory.preference_stored", user=user_key)
        return {"stored": True, "id": doc_id}

    except Exception as e:
        logger.error("memory.store_preference_error", error=str(e))
        return {"stored": False, "error": str(e)}


async def store_episode(params: dict) -> dict:
    task_id = params.get("task_id", "")
    workflow = params.get("workflow", "")
    summary = params.get("summary", "")
    outcome = params.get("outcome", "")
    user_key = params.get("user_key", "default")

    content = f"Workflow: {workflow}\nSummary: {summary}\nOutcome: {outcome}"

    try:
        import asyncio
        def _store():
            client = _get_client()
            col = client.get_or_create_collection(
                "task_episodes",
                embedding_function=_get_embedding_fn()
            )
            col.add(
                documents=[content],
                metadatas=[{"task_id": task_id, "workflow": workflow, "user_key": user_key}],
                ids=[task_id or str(__import__("uuid").uuid4())],
            )

        await asyncio.get_event_loop().run_in_executor(None, _store)
        logger.info("memory.episode_stored", task_id=task_id)
        return {"stored": True}

    except Exception as e:
        logger.error("memory.store_episode_error", error=str(e))
        return {"stored": False, "error": str(e)}


async def query_episodes(params: dict) -> dict:
    query = params.get("query", "")
    user_key = params.get("user_key", "default")
    top_k = params.get("top_k", 3)

    try:
        import asyncio
        def _query():
            client = _get_client()
            col = client.get_or_create_collection(
                "task_episodes",
                embedding_function=_get_embedding_fn()
            )
            results = col.query(
                query_texts=[query],
                n_results=top_k,
                where={"user_key": user_key},
            )
            episodes = []
            for i, doc in enumerate(results["documents"][0]):
                episodes.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i],
                })
            return episodes

        episodes = await asyncio.get_event_loop().run_in_executor(None, _query)
        return {"episodes": episodes}

    except Exception as e:
        logger.error("memory.query_episodes_error", error=str(e))
        return {"episodes": [], "error": str(e)}

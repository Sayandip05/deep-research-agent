"""
memory/chroma_client.py
Centralised ChromaDB client factory with connection pooling.
"""

from __future__ import annotations
import os
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))

_client: chromadb.HttpClient | None = None
_embedding_fn: SentenceTransformerEmbeddingFunction | None = None


def get_client() -> chromadb.HttpClient:
    global _client
    if _client is None:
        _client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    return _client


def get_embedding_fn() -> SentenceTransformerEmbeddingFunction:
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
    return _embedding_fn


def get_collection(name: str):
    """Get or create a named collection with the default embedding function."""
    client = get_client()
    return client.get_or_create_collection(name, embedding_function=get_embedding_fn())


def reset_all():
    """Delete all collections — useful for development resets."""
    client = get_client()
    client.reset()

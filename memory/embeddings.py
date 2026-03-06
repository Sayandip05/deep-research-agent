"""
memory/embeddings.py
Local embedding generation using SentenceTransformers.
Avoids external API calls for embedding — fully free and offline.
"""

from __future__ import annotations
from typing import List
from sentence_transformers import SentenceTransformer

_model: SentenceTransformer | None = None
MODEL_NAME = "all-MiniLM-L6-v2"


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts."""
    model = get_model()
    return model.encode(texts, convert_to_numpy=True).tolist()


def embed_one(text: str) -> List[float]:
    """Generate an embedding for a single text string."""
    return embed([text])[0]

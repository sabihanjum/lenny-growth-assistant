"""Embedding generation utility using FastEmbed for high-throughput, zero-cost vectors."""

import logging
from typing import List
import numpy as np
from fastembed import TextEmbedding
from app.config import settings

logger = logging.getLogger("lenny_assistant.embeddings")

_embedding_model = None


def get_embedding_model() -> TextEmbedding:
    global _embedding_model
    if _embedding_model is None:
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL} (dim={settings.EMBEDDING_DIMENSION})")
        _embedding_model = TextEmbedding(model_name=settings.EMBEDDING_MODEL)
    return _embedding_model


def embed_text(text: str) -> List[float]:
    """Generate normalized vector embedding for a single text query."""
    model = get_embedding_model()
    embeddings = list(model.embed([text]))
    vec = embeddings[0]
    # Ensure float list
    return [float(x) for x in vec]


def embed_batch(texts: List[str], batch_size: int = 64) -> List[List[float]]:
    """Generate vector embeddings for a list of texts."""
    model = get_embedding_model()
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        chunk_texts = texts[i : i + batch_size]
        batch_vecs = list(model.embed(chunk_texts))
        for vec in batch_vecs:
            all_embeddings.append([float(x) for x in vec])
    return all_embeddings


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two float vectors."""
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))

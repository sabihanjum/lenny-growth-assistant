"""Automated tests for vector similarity retrieval and grounded refusal thresholds."""

import pytest
from app.rag.embeddings import embed_text, cosine_similarity
from app.rag.retriever import TranscriptRetriever
from app.database import get_session_factory


@pytest.mark.asyncio
async def test_embedding_generation_and_cosine():
    vec1 = embed_text("growth loops and user acquisition")
    vec2 = embed_text("product led growth and retention")
    vec3 = embed_text("astrophysics and black hole quantum mechanics")

    assert len(vec1) == 384
    assert len(vec2) == 384
    assert len(vec3) == 384

    # Related queries should have high similarity
    sim_related = cosine_similarity(vec1, vec2)
    # Unrelated queries should have low similarity
    sim_unrelated = cosine_similarity(vec1, vec3)

    assert sim_related > sim_unrelated
    assert sim_related > 0.50


@pytest.mark.asyncio
async def test_in_domain_retrieval_returns_citations():
    session_factory = get_session_factory()
    async with session_factory() as db:
        retriever = TranscriptRetriever(db)
        chunks = await retriever.retrieve_relevant_chunks(
            query="How do you build a high-performing growth team?",
            top_k=5,
            similarity_threshold=0.55
        )

        assert len(chunks) > 0
        assert len(chunks) <= 5
        top = chunks[0]
        assert "score" in top
        assert top["score"] >= 0.55
        assert top["guest"] in ["Adam Fishman", "Elena Verna", "Hila Qu"]
        assert "episode" in top
        assert "text" in top
        assert len(top["text"]) > 50


@pytest.mark.asyncio
async def test_out_of_domain_retrieval_triggers_refusal():
    session_factory = get_session_factory()
    async with session_factory() as db:
        retriever = TranscriptRetriever(db)
        # Irrelevant query
        chunks = await retriever.retrieve_relevant_chunks(
            query="What is the chemical composition of basaltic rocks on Mars?",
            top_k=5,
            similarity_threshold=0.55
        )

        # Must return empty list to trigger the deterministic refusal response
        assert len(chunks) == 0

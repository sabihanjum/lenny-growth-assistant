"""Transcript retrieval engine using pgvector cosine similarity with local resilience fallback."""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from app.config import settings
from app.database import is_pgvector_active
from app.models.db_models import TranscriptChunk
from app.rag.embeddings import embed_text, cosine_similarity

logger = logging.getLogger("lenny_assistant.retriever")


class TranscriptRetriever:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        k = top_k or settings.RETRIEVAL_TOP_K
        threshold = similarity_threshold if similarity_threshold is not None else settings.SIMILARITY_THRESHOLD

        # 1. Compute embedding vector for query
        query_vector = embed_text(query)

        # 2. If pgvector extension is confirmed active, use native pgvector query
        if is_pgvector_active():
            try:
                query_stmt = text("""
                    SELECT
                        episode_slug,
                        episode_title,
                        guest_name,
                        timestamp_ref,
                        chunk_text,
                        1 - (embedding <=> :vector::vector) AS similarity_score
                    FROM transcript_chunks
                    WHERE 1 - (embedding <=> :vector::vector) >= :threshold
                    ORDER BY similarity_score DESC
                    LIMIT :limit;
                """)

                result = await self.session.execute(
                    query_stmt,
                    {
                        "vector": str(query_vector),
                        "threshold": threshold,
                        "limit": k,
                    }
                )
                rows = result.fetchall()
                if rows:
                    logger.info(f"Retrieved {len(rows)} chunks via native pgvector (top score: {rows[0].similarity_score:.3f})")
                    return [
                        {
                            "slug": r.episode_slug,
                            "episode": r.episode_title,
                            "guest": r.guest_name,
                            "timestamp": r.timestamp_ref,
                            "text": r.chunk_text,
                            "score": float(r.similarity_score),
                        }
                        for r in rows
                    ]
            except Exception as pg_err:
                logger.warning(f"Native pgvector query failed ({pg_err}). Rolling back and using fallback.")
                await self.session.rollback()

        # 3. Fallback: Query chunks and compute cosine similarity
        try:
            stmt = select(TranscriptChunk)
            result = await self.session.execute(stmt)
            all_chunks = result.scalars().all()
        except Exception as e:
            logger.error(f"Error querying transcript chunks: {e}")
            await self.session.rollback()
            return []

        if not all_chunks:
            logger.warning("No transcript chunks found in database.")
            return []

        scored_chunks = []
        for c in all_chunks:
            chunk_vec = c.embedding
            if isinstance(chunk_vec, (list, tuple)):
                score = cosine_similarity(query_vector, chunk_vec)
                if score >= threshold:
                    scored_chunks.append({
                        "slug": c.episode_slug,
                        "episode": c.episode_title,
                        "guest": c.guest_name,
                        "timestamp": c.timestamp_ref,
                        "text": c.chunk_text,
                        "score": score,
                    })

        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        top_results = scored_chunks[:k]
        top_score_str = f"{top_results[0]['score']:.3f}" if top_results else "0.000"
        logger.info(f"Retrieved {len(top_results)} chunks (top score: {top_score_str})")
        return top_results

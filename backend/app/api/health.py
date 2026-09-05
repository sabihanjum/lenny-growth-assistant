"""Health and diagnostics probe endpoint."""

from datetime import datetime, timezone
import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func
from app.config import settings
from app.database import get_db, is_pgvector_active
from app.models.db_models import TranscriptChunk, Session
from app.models.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
async def check_health(db: AsyncSession = Depends(get_db)):
    # 1. Database check
    db_status = "healthy"
    chunks_count = 0
    sessions_count = 0
    try:
        chunks_res = await db.execute(select(func.count(TranscriptChunk.id)))
        chunks_count = chunks_res.scalar() or 0
        sessions_res = await db.execute(select(func.count(Session.id)))
        sessions_count = sessions_res.scalar() or 0
    except Exception as e:
        db_status = f"degraded: {str(e)}"

    # 2. Ollama probe
    ollama_status = "unreachable"
    ollama_models = []
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                ollama_status = "connected"
                data = resp.json()
                ollama_models = [m.get("name") for m in data.get("models", [])]
            else:
                ollama_status = f"error HTTP {resp.status_code}"
    except Exception as e:
        ollama_status = f"disconnected ({type(e).__name__})"

    overall_status = "ok" if (db_status == "healthy" and chunks_count > 0) else "degraded"

    return {
        "status": overall_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {
            "status": db_status,
            "pgvector_active": is_pgvector_active(),
            "indexed_chunks": chunks_count,
            "total_sessions": sessions_count,
        },
        "ollama": {
            "status": ollama_status,
            "base_url": settings.OLLAMA_BASE_URL,
            "available_models": ollama_models,
            "default_model": settings.DEFAULT_OLLAMA_MODEL,
        },
        "retrieval": {
            "model": settings.EMBEDDING_MODEL,
            "dimension": settings.EMBEDDING_DIMENSION,
            "similarity_threshold": settings.SIMILARITY_THRESHOLD,
            "top_k": settings.RETRIEVAL_TOP_K,
        }
    }

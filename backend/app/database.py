"""Database connection, engine configuration, and session management."""

import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.config import settings
from app.models.db_models import Base, set_use_native_vector

logger = logging.getLogger("lenny_assistant.database")

# Primary Async Engine
_engine = None
_session_factory = None
_is_pgvector_active = False


def get_engine():
    global _engine, _session_factory
    if _engine is None:
        db_url = settings.DATABASE_URL
        # Normalize Render/Heroku postgres:// URLs for asyncpg
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("postgresql://") and "+asyncpg" not in db_url:
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        try:
            _engine = create_async_engine(
                db_url,
                echo=settings.DEBUG,
                future=True,
                pool_pre_ping=True,
            )
            _session_factory = async_sessionmaker(
                _engine,
                expire_on_commit=False,
                class_=AsyncSession,
            )
            logger.info(f"Initialized database engine: {db_url.split('@')[-1] if '@' in db_url else db_url}")
        except Exception as e:
            logger.warning(f"Failed to initialize primary database ({e}). Falling back to SQLite.")
            fallback_url = "sqlite+aiosqlite:///./lenny_assistant.db"
            _engine = create_async_engine(
                fallback_url,
                echo=settings.DEBUG,
                future=True,
            )
            _session_factory = async_sessionmaker(
                _engine,
                expire_on_commit=False,
                class_=AsyncSession,
            )
    return _engine


def get_session_factory():
    global _session_factory
    if _session_factory is None:
        get_engine()
    return _session_factory


async def init_db():
    """Initialize database tables and pgvector extension if supported."""
    global _is_pgvector_active
    engine = get_engine()

    # Attempt to enable pgvector extension on PostgreSQL
    if "postgresql" in str(engine.url):
        try:
            async with engine.begin() as conn:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                _is_pgvector_active = True
                set_use_native_vector(True)
                logger.info("Successfully ensured 'vector' extension in PostgreSQL.")
        except Exception as e:
            _is_pgvector_active = False
            set_use_native_vector(False)
            logger.info(f"Native 'vector' extension not installed in current Postgres ({e}). Running in compatible vector mode.")

    # Create all schema tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # If pgvector is active, create HNSW index if not already present
        if _is_pgvector_active:
            try:
                await conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_transcript_chunks_hnsw 
                    ON transcript_chunks 
                    USING hnsw (embedding vector_cosine_ops)
                    WITH (m = 16, ef_construction = 64);
                """))
                logger.info("Created / verified HNSW cosine index on transcript_chunks.")
            except Exception as e:
                logger.warning(f"Could not create HNSW index: {e}")

    logger.info("Database schema initialized successfully.")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for yielding an async database session."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def is_pgvector_active() -> bool:
    return _is_pgvector_active

"""SQLAlchemy database models with pgvector support and fallback."""

import uuid
from datetime import datetime, timezone
import json
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    TypeDecorator,
)
from sqlalchemy.orm import declarative_base, relationship

try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False

Base = declarative_base()

# Global runtime flag set by database.py
USE_NATIVE_VECTOR = False


def set_use_native_vector(val: bool):
    global USE_NATIVE_VECTOR
    USE_NATIVE_VECTOR = val


class CompatibleVector(TypeDecorator):
    """Custom type decorator for 384-dimensional vector embeddings.
    Uses native pgvector Vector(384) on PostgreSQL when pgvector extension is available,
    and seamlessly uses Text (JSON serialized) on environments without the pgvector binary.
    """
    impl = Text
    cache_ok = True

    def __init__(self, dim=384, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dim = dim

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql" and HAS_PGVECTOR and USE_NATIVE_VECTOR:
            return dialect.type_descriptor(Vector(self.dim))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql" and HAS_PGVECTOR and USE_NATIVE_VECTOR:
            return value
        if isinstance(value, (list, tuple)):
            return json.dumps([float(x) for x in value])
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, str):
            try:
                cleaned = value.strip("[] \n")
                if not cleaned:
                    return []
                return [float(x.strip()) for x in cleaned.split(",")]
            except Exception:
                return json.loads(value)
        return list(value)


def gen_uuid_str() -> str:
    return str(uuid.uuid4())


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=gen_uuid_str)
    title = Column(String(255), nullable=False, default="New Growth Conversation")
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)

    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=gen_uuid_str)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(32), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    sources = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)

    session = relationship("Session", back_populates="messages")
    artifacts = relationship("Artifact", back_populates="message", cascade="all, delete-orphan")


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(String(36), primary_key=True, default=gen_uuid_str)
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=True, index=True)
    artifact_type = Column(String(32), nullable=False)  # 'markdown' or 'html'
    identifier = Column(String(128), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=now_utc, nullable=False)

    message = relationship("Message", back_populates="artifacts")


class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"

    id = Column(String(36), primary_key=True, default=gen_uuid_str)
    episode_slug = Column(String(255), nullable=False, index=True)
    episode_title = Column(String(512), nullable=False)
    guest_name = Column(String(255), nullable=False, index=True)
    publish_date = Column(String(64), nullable=True)
    youtube_url = Column(String(512), nullable=True)
    timestamp_ref = Column(String(64), nullable=True)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding = Column(CompatibleVector(384), nullable=False)

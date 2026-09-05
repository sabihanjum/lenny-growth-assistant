"""Pydantic v2 schemas for API validation and serialization."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class Citation(BaseModel):
    episode: str
    guest: str
    timestamp: Optional[str] = None
    score: float = Field(..., description="Cosine similarity score (0.0 - 1.0)")
    text: str


class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, description="UUID of existing session, or None to create new")
    message: str = Field(..., min_length=1, description="User prompt or query")
    mode: Optional[str] = Field(default="default", description="'default', 'ship30', or 'artifact'")
    provider: Optional[str] = Field(default="ollama", description="'ollama', 'claude', or 'openai'")
    model: Optional[str] = Field(default=None, description="Model override (e.g. 'llama3.1:8b', 'gpt-4o')")
    temperature: Optional[float] = Field(default=0.3, ge=0.0, le=1.0)


class SessionCreate(BaseModel):
    title: Optional[str] = Field(default="New Growth Conversation", max_length=255)


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class ArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    message_id: Optional[str] = None
    artifact_type: str
    identifier: str
    title: str
    content: str
    created_at: datetime


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    role: str
    content: str
    sources: List[Dict[str, Any]] = []
    created_at: datetime
    artifacts: List[ArtifactResponse] = []


class SessionDetailResponse(BaseModel):
    session: SessionResponse
    messages: List[MessageResponse]


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    database: Dict[str, Any]
    ollama: Dict[str, Any]
    retrieval: Dict[str, Any]

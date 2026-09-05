"""Session management API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.db_models import Session, Message, Artifact
from app.models.schemas import (
    SessionCreate,
    SessionResponse,
    SessionDetailResponse,
    MessageResponse,
    ArtifactResponse,
)

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: SessionCreate = SessionCreate(),
    db: AsyncSession = Depends(get_db)
):
    new_session = Session(title=payload.title or "New Growth Conversation")
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session


@router.get("", response_model=List[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    stmt = select(Session).order_by(desc(Session.updated_at))
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    return sessions


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Session)
        .where(Session.id == session_id)
        .options(
            selectinload(Session.messages).selectinload(Message.artifacts)
        )
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session '{session_id}' not found")

    messages_out = []
    for m in session.messages:
        art_out = [
            ArtifactResponse(
                id=a.id,
                message_id=a.message_id,
                artifact_type=a.artifact_type,
                identifier=a.identifier,
                title=a.title,
                content=a.content,
                created_at=a.created_at,
            )
            for a in m.artifacts
        ]
        messages_out.append(
            MessageResponse(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                sources=m.sources or [],
                created_at=m.created_at,
                artifacts=art_out,
            )
        )

    return SessionDetailResponse(
        session=SessionResponse.model_validate(session),
        messages=messages_out,
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Session).where(Session.id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session '{session_id}' not found")

    await db.delete(session)
    await db.commit()
    return None

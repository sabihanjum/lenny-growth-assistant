"""Streaming Chat API endpoint with RAG, Ship 30 for 30 Skill, and Artifact extraction."""

import json
import logging
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db, get_session_factory
from app.models.db_models import Session, Message, Artifact
from app.models.schemas import ChatRequest
from app.rag.retriever import TranscriptRetriever
from app.providers.factory import LLMProviderFactory
from app.skills.ship30_writer import SHIP_30_SYSTEM_PROMPT, build_ship30_prompt
from app.skills.artifact_generator import ARTIFACT_SYSTEM_PROMPT, extract_artifacts

logger = logging.getLogger("lenny_assistant.api.chat")

router = APIRouter(prefix="/chat", tags=["Chat"])

GROUNDED_QA_SYSTEM_PROMPT = """You are the Lenny Growth Assistant, an enterprise-grade AI advisor for product managers and growth leaders.
Your knowledge is strictly grounded in the provided transcripts from Lenny's Podcast.

CRITICAL INSTRUCTIONS:
1. Grounding & Attribution:
   - Base your answer STRICTLY upon the provided context chunks.
   - For every substantive claim, tactic, or recommendation, cite the source explicitly using bracketed citation notation:
     `[Guest Name: Episode Title, Timestamp]` (e.g. `[Adam Fishman: How to build a high-performing growth team, 00:12:45]`).
   - If multiple guests discuss the topic, compare and synthesize their perspectives with separate citations.

2. Tone & Depth:
   - Provide direct, executive-ready, highly actionable answers.
   - Avoid generic fluff. Highlight specific metrics, tactical frameworks, and failure modes mentioned by the guests.

3. Refusal Condition:
   - If the provided context does not contain sufficient facts to answer the user query, respond immediately with:
     "I do not have sufficient information in Lenny's podcast archive to answer this."
"""


@router.post("")
async def stream_chat(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    # 1. Resolve or create Session
    session_id = req.session_id
    session = None
    if session_id:
        stmt = select(Session).where(Session.id == session_id)
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

    if not session:
        session = Session(title=req.message[:50] + ("..." if len(req.message) > 50 else ""))
        db.add(session)
        await db.commit()
        await db.refresh(session)
        session_id = session.id

    # 2. Retrieve relevant transcript chunks
    retriever = TranscriptRetriever(db)
    retrieved_chunks = await retriever.retrieve_relevant_chunks(
        query=req.message,
        top_k=5,
        similarity_threshold=0.55
    )

    # 3. Select LLM Provider dynamically
    llm = LLMProviderFactory.get_provider(provider=req.provider, model=req.model)

    # 4. SSE Generator
    async def sse_event_stream() -> AsyncGenerator[str, None]:
        # Yield retrieval status
        yield f"event: status\ndata: {json.dumps({'stage': 'retrieving', 'message': 'Searching podcast transcripts...'})}\n\n"

        # Check refusal condition
        if not retrieved_chunks:
            refusal_text = "I do not have sufficient information in Lenny's podcast archive to answer this."
            yield f"event: token\ndata: {json.dumps({'token': refusal_text})}\n\n"

            # Persist refusal exchange using independent session
            session_factory = get_session_factory()
            async with session_factory() as persist_db:
                u_msg = Message(session_id=session_id, role="user", content=req.message, sources=[])
                a_msg = Message(session_id=session_id, role="assistant", content=refusal_text, sources=[])
                persist_db.add(u_msg)
                persist_db.add(a_msg)
                await persist_db.commit()

            yield f"event: done\ndata: {json.dumps({'session_id': session_id, 'refusal': True})}\n\n"
            return

        # Send retrieved sources to client
        sources_payload = [
            {
                "slug": c["slug"],
                "episode": c["episode"],
                "guest": c["guest"],
                "timestamp": c.get("timestamp"),
                "score": round(c["score"], 3),
                "snippet": c["text"][:300] + "...",
            }
            for c in retrieved_chunks
        ]
        yield f"event: sources\ndata: {json.dumps(sources_payload)}\n\n"
        yield f"event: status\ndata: {json.dumps({'stage': 'generating', 'message': 'Synthesizing grounded response...'})}\n\n"

        # Format prompt according to mode
        mode = (req.mode or "default").lower()
        if mode == "ship30":
            system_prompt = SHIP_30_SYSTEM_PROMPT
            user_content = build_ship30_prompt(req.message, retrieved_chunks)
        elif mode == "artifact":
            system_prompt = f"{GROUNDED_QA_SYSTEM_PROMPT}\n\n{ARTIFACT_SYSTEM_PROMPT}"
            formatted_context = "\n\n".join([
                f"--- Episode: {c['episode']} (Guest: {c['guest']}, Timestamp: {c.get('timestamp')}) ---\n{c['text']}"
                for c in retrieved_chunks
            ])
            user_content = f"Context Material:\n{formatted_context}\n\nUser Request:\n{req.message}\n\nPlease generate the required artifact enclosed in <artifact identifier=... type=... title=...>...</artifact> tags."
        else:
            system_prompt = f"{GROUNDED_QA_SYSTEM_PROMPT}\n\n{ARTIFACT_SYSTEM_PROMPT}"
            formatted_context = "\n\n".join([
                f"--- Episode: {c['episode']} (Guest: {c['guest']}, Timestamp: {c.get('timestamp')}) ---\n{c['text']}"
                for c in retrieved_chunks
            ])
            user_content = f"Context Material:\n{formatted_context}\n\nUser Question:\n{req.message}"

        # Stream tokens from LLM
        accumulated_tokens = []
        messages_payload = [{"role": "user", "content": user_content}]

        try:
            async for token in llm.generate_response(
                messages=messages_payload,
                system_prompt=system_prompt,
                temperature=req.temperature or 0.3
            ):
                accumulated_tokens.append(token)
                yield f"event: token\ndata: {json.dumps({'token': token})}\n\n"
        except Exception as gen_err:
            logger.error(f"Error during token streaming: {gen_err}")
            err_msg = f"\n\n[Streaming Error: {str(gen_err)}]"
            payload_str = json.dumps({"token": err_msg})
            yield f"event: token\ndata: {payload_str}\n\n"

        full_response = "".join(accumulated_tokens)

        # 5. Extract and format any artifacts
        clean_text, artifacts_list = extract_artifacts(full_response)
        if artifacts_list:
            yield f"event: artifact\ndata: {json.dumps(artifacts_list)}\n\n"

        # 6. Persist Messages and Artifacts in DB
        session_factory = get_session_factory()
        async with session_factory() as persist_db:
            u_msg = Message(session_id=session_id, role="user", content=req.message, sources=[])
            a_msg = Message(session_id=session_id, role="assistant", content=full_response, sources=sources_payload)
            persist_db.add(u_msg)
            persist_db.add(a_msg)
            await persist_db.flush()

            for art in artifacts_list:
                art_obj = Artifact(
                    message_id=a_msg.id,
                    artifact_type=art["artifact_type"],
                    identifier=art["identifier"],
                    title=art["title"],
                    content=art["content"]
                )
                persist_db.add(art_obj)

            await persist_db.commit()

        yield f"event: done\ndata: {json.dumps({'session_id': session_id, 'message_id': a_msg.id, 'artifact_count': len(artifacts_list)})}\n\n"

    return StreamingResponse(
        sse_event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

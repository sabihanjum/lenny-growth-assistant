"""Knowledge ingestion script: chunks, embeds, and indexes Lenny's Podcast transcripts into PostgreSQL with pgvector."""

import os
import sys
import re
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any
import yaml
from sqlalchemy import text

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.config import settings
from app.database import init_db, get_session_factory, get_engine
from app.models.db_models import TranscriptChunk
from app.rag.embeddings import embed_batch

TRANSCRIPTS_DIR = settings.TRANSCRIPTS_DIR
CACHE_DIR = settings.CACHE_DIR


def parse_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """Extract YAML frontmatter and transcript body."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if match:
        try:
            metadata = yaml.safe_load(match.group(1)) or {}
            body = match.group(2)
            return metadata, body
        except Exception:
            pass
    return {}, content


def chunk_transcript(
    body: str,
    guest_name: str,
    target_chars: int = 2400,  # ~600 tokens
    overlap_chars: int = 400    # ~100 tokens
) -> List[Dict[str, Any]]:
    """Split transcript into coherent chunks while tracking speaker and timestamps."""
    chunks = []
    
    # Speaker pattern: Name (HH:MM:SS):
    speaker_pattern = re.compile(r"([A-Za-z0-9\s\.\,\'\-]+)\s*\(([0-9]{2}:[0-9]{2}:[0-9]{2})\):")
    
    # Break into natural paragraphs
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    
    current_chunk = []
    current_length = 0
    current_timestamp = "00:00:00"
    
    for p in paragraphs:
        # Check for timestamp
        ts_match = speaker_pattern.search(p)
        if ts_match:
            current_timestamp = ts_match.group(2)

        p_len = len(p)
        if current_length + p_len > target_chars and current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunks.append({
                "timestamp": current_timestamp,
                "text": chunk_text
            })
            
            # Create overlap
            overlap_acc = []
            overlap_len = 0
            for item in reversed(current_chunk):
                if overlap_len + len(item) <= overlap_chars:
                    overlap_acc.insert(0, item)
                    overlap_len += len(item)
                else:
                    break
            current_chunk = overlap_acc
            current_length = overlap_len

        current_chunk.append(p)
        current_length += p_len

    if current_chunk:
        chunks.append({
            "timestamp": current_timestamp,
            "text": "\n\n".join(current_chunk)
        })

    return chunks


async def ingest_transcripts():
    print("=== Ingesting Lenny's Podcast Transcripts into Vector Index ===")
    await init_db()
    session_factory = get_session_factory()

    transcript_files = list(TRANSCRIPTS_DIR.glob("*.md"))
    if not transcript_files:
        print(f"[ERROR] No transcript files found in {TRANSCRIPTS_DIR}.")
        print("Please run: python backend/scripts/download_transcripts.py first.")
        return

    print(f"Found {len(transcript_files)} transcript files to process.")

    total_chunks = 0
    all_chunks_cache = []

    async with session_factory() as db_session:
        # Clear existing chunks
        await db_session.execute(text("DELETE FROM transcript_chunks;"))
        await db_session.commit()

        for filepath in transcript_files:
            slug = filepath.stem
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            metadata, body = parse_frontmatter(content)
            guest = metadata.get("guest") or slug.replace("-", " ").title()
            title = metadata.get("title") or f"Lenny's Podcast: {guest}"
            publish_date = str(metadata.get("publish_date") or "")
            youtube_url = str(metadata.get("youtube_url") or "")

            print(f"\nProcessing [{slug}]: '{title}' (Guest: {guest})")
            raw_chunks = chunk_transcript(body, guest)
            print(f"  Generated {len(raw_chunks)} chunks. Generating embeddings...")

            texts_to_embed = [c["text"] for c in raw_chunks]
            embeddings = embed_batch(texts_to_embed)

            for idx, (raw_c, emb) in enumerate(zip(raw_chunks, embeddings)):
                chunk_obj = TranscriptChunk(
                    episode_slug=slug,
                    episode_title=title,
                    guest_name=guest,
                    publish_date=publish_date,
                    youtube_url=youtube_url,
                    timestamp_ref=raw_c["timestamp"],
                    chunk_text=raw_c["text"],
                    chunk_index=idx,
                    embedding=emb
                )
                db_session.add(chunk_obj)
                
                all_chunks_cache.append({
                    "episode_slug": slug,
                    "episode_title": title,
                    "guest_name": guest,
                    "publish_date": publish_date,
                    "youtube_url": youtube_url,
                    "timestamp_ref": raw_c["timestamp"],
                    "chunk_text": raw_c["text"],
                    "chunk_index": idx,
                    "embedding": emb
                })

            total_chunks += len(raw_chunks)
            await db_session.commit()
            print(f"  [OK] Saved {len(raw_chunks)} chunks for {slug}.")

    # Save JSON backup cache for rapid offline unit testing and resilience
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / "chunks_cache.json"
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks_cache, f)

    print(f"\n==========================================")
    print(f"[COMPLETE] Ingested {total_chunks} chunks across {len(transcript_files)} episodes.")
    print(f"[CACHE] Exported {len(all_chunks_cache)} chunks to {cache_path}")
    print(f"==========================================")


if __name__ == "__main__":
    asyncio.run(ingest_transcripts())

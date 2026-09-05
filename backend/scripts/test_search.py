"""Quick CLI utility to verify transcript vector retrieval and refusal threshold."""

import sys
import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.database import get_session_factory
from app.rag.retriever import TranscriptRetriever


async def test_search(query: str):
    print(f"\n==========================================")
    print(f"Query: \"{query}\"")
    print(f"==========================================")

    session_factory = get_session_factory()
    async with session_factory() as db:
        retriever = TranscriptRetriever(db)
        results = await retriever.retrieve_relevant_chunks(query, top_k=5, similarity_threshold=0.55)

        if not results:
            print("[REFUSAL TRIGGERED] No chunks met the similarity threshold (>= 0.55).")
            print("System Response: \"I do not have sufficient information in Lenny's podcast archive to answer this.\"")
            return

        print(f"Retrieved {len(results)} relevant chunks:")
        for idx, r in enumerate(results, 1):
            print(f"\n[{idx}] Score: {r['score']:.4f} | Guest: {r['guest']} | Timestamp: {r['timestamp']}")
            print(f"    Episode: {r['episode']}")
            snippet = r['text'][:200].replace('\n', ' ')
            print(f"    Snippet: {snippet}...")


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "How do you build a high-performing growth team?"
    asyncio.run(test_search(q))

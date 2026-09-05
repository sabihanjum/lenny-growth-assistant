# Engineering Transcript 01: Initial Scaffolding & Architectural Design

**Phase:** Forward Deployment Discovery & System Setup  
**Focus:** Requirements scoping, technical stack decisions, and foundational structure  

---

## 1. Context & Assignment Discovery

The client brief requested **The Lenny Growth Assistant**—an enterprise RAG application capable of unlocking operational knowledge from *Lenny's Podcast* transcripts for product managers and growth leaders.

### Key Customer Requirements Identified:
1. **Grounded Answers:** Direct attribution to episode transcripts with explicit citations `[Guest Name: Episode Title, Timestamp]`. Deterministic refusal when query context falls outside the podcast archive.
2. **Ship 30 for 30 Content Engine:** Automated transformation of raw insights into structured, 1,250-word high-retention essays following the Ship 30 for 30 heuristics (curiosity hook, short skimmable paragraphs, bold anchor bullets, tactical checklist).
3. **Claude-Style In-App Artifact Viewer:** Rendering Markdown documents and interactive HTML/CSS/JS widgets side-by-side with chat in a secure, sandboxed container.
4. **Dual Model Layer (Local & Cloud):** Seamless runtime switching between a local LLM via Ollama (`llama3.1:8b`) for the required offline evaluation demo, and cloud providers (Anthropic Claude 3.5 Sonnet / OpenAI GPT-4o) without code changes.
5. **Operational Readiness:** Single-command startup (`docker-compose up`), PostgreSQL + pgvector storage, resilience routines, structured logging, and complete Forward Deployment documentation (PRD, Architecture, and Design specs).

---

## 2. Technical Stack Selection & Trade-Offs

| Component | Selected Technology | Rationale & Trade-Offs Considered |
| :--- | :--- | :--- |
| **Backend Framework** | `FastAPI` + `Uvicorn` | Native async support for Server-Sent Events (SSE) streaming; robust Pydantic v2 data validation; clean dependency injection for database sessions. |
| **Relational & Vector DB** | `PostgreSQL 16` + `pgvector` | Standard enterprise database supporting relational tables (`sessions`, `messages`, `artifacts`) and vector embeddings with HNSW indexing in a unified storage engine. Avoids managing a separate vector database cluster. |
| **Embedding Engine** | `FastEmbed` (`BAAI/bge-small-en-v1.5`, 384-dim) | Runs locally via ONNX Runtime with zero PyTorch overhead, under 30MB disk footprint, zero API costs, and sub-15ms embedding latency per chunk on CPU. |
| **Frontend Framework** | `Next.js 14` (App Router) + `Tailwind CSS` | High-performance React framework with TypeScript, server-side rendering capability, clean layout routing, and rapid UI development. |
| **Markdown & Isolation** | `react-markdown` + `remark-gfm` + `DOMPurify` | Rich GitHub-flavored markdown rendering paired with DOMPurify sanitization and iframe sandbox isolation for untrusted AI-generated code. |
| **Local LLM Engine** | `Ollama` (`llama3.1:8b` / `llama3:latest`) | Native support for 8B parameter open weights with local GPU acceleration and standardized OpenAI-compatible/chat endpoints. |

---

## 3. Scaffolding Execution

1. **Discovery Documents:** Authored `docs/PRD.md`, `docs/architecture.md`, and `docs/design.md` detailing personas, success metrics, data contracts, and responsive layout specifications.
2. **Backend Directory Structure:** Established modular application boundaries under `backend/app/` (`api/`, `models/`, `providers/`, `rag/`, `skills/`).
3. **Virtual Environment & Dependencies:** Initialized Python 3.13 virtual environment (`backend/venv`) and locked dependencies in `backend/requirements.txt`.
4. **Frontend Scaffolding:** Configured `frontend/package.json` with Next.js 14, Tailwind CSS, Lucide icons, DOMPurify, and React-Markdown.

---

## 4. Key Takeaways from Scaffolding
- Establishing strict data contracts between the SSE streaming backend and the Next.js client upfront eliminated schema drift.
- Providing fallbacks for local developer environments ensures the system can be developed and evaluated immediately without requiring third-party cloud keys.

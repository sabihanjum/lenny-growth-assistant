# The Lenny Growth Assistant
> Enterprise-grade Retrieval-Augmented Generation (RAG) and Content Engine unlocking operational knowledge from *Lenny’s Podcast* transcripts for product managers and growth leaders.

![License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%20%2B%20pgvector-336791.svg)
![Ollama](https://img.shields.io/badge/Ollama-llama3.1%3A8b-orange.svg)

---

## 1. Executive Overview

*Lenny's Podcast* contains over 300 in-depth conversations with top technology operators (Lyft, Stripe, Reforge, Figma, Airbnb). **The Lenny Growth Assistant** transforms this audio archive into an actionable operational intelligence system with:

1. **Source-Attributed Grounding:** Direct citations (`[Guest Name: Episode Title, Timestamp]`) with deterministic refusal (*"I do not have sufficient information in Lenny's podcast archive to answer this."*) for ungrounded queries.
2. **Ship 30 for 30 Content Engine:** Generates ~1,250-word, high-retention essays applying structured writing heuristics (curiosity hook, short paragraphs, bold anchor bullets, and concluding checklists).
3. **Claude-Style In-App Artifact Viewer:** Renders generated Markdown and interactive HTML/CSS/JS widgets side-by-side inside an isolated, sandboxed container (`sandbox="allow-scripts"`, strictly omitting `allow-same-origin`, pre-sanitized with `DOMPurify`).
4. **Dual Model Layer (Local & Cloud):** Instant runtime switching between local Ollama (`llama3.1:8b`, `llama3:latest`) for private zero-cost evaluation and cloud providers (Anthropic Claude 3.5 Sonnet or OpenAI GPT-4o).
5. **Operational Handoff:** Single-command Docker Compose deployment (`docker-compose up`), automated test suite, structured logging, and forward-deployment documentation.

---

## 2. System Architecture

```mermaid
flowchart TB
    subgraph Client ["Client Presentation Layer (Next.js 14 / Tailwind CSS)"]
        UI["Dual-Pane Interface"]
        ChatPane["Chat & Streaming Stream"]
        ArtifactViewer["Side-by-Side Artifact Drawer"]
        ModelSelector["Runtime Model / Mode Selector"]
        UI --> ChatPane
        UI --> ArtifactViewer
        UI --> ModelSelector
    end

    subgraph Backend ["Application Layer (FastAPI / Python 3.11+)"]
        API["FastAPI Engine & CORS"]
        RAG["Retriever & Embedding Engine (FastEmbed 384-dim)"]
        Skills["Skills Engine (Ship 30 Ghostwriter & Artifact Parser)"]
        LLMFactory["LLM Provider Factory"]
        
        API --> RAG
        API --> Skills
        API --> LLMFactory
    end

    subgraph LLMProviders ["Dual LLM Layer"]
        Ollama["Local Ollama Daemon\nllama3.1:8b / llama3:latest"]
        CloudLLM["Cloud APIs\nAnthropic Claude / OpenAI GPT-4o"]
        LLMFactory -->|Default / Local Toggle| Ollama
        LLMFactory -->|Cloud Toggle| CloudLLM
    end

    subgraph Persistence ["Persistence & Vector Layer"]
        PG["PostgreSQL 16"]
        PGVector["pgvector Extension (HNSW Index)"]
        SessionsTable[("sessions")]
        MessagesTable[("messages")]
        ArtifactsTable[("artifacts")]
        ChunksTable[("transcript_chunks (VECTOR 384)")]
        
        PG --- PGVector
        PGVector --- ChunksTable
        PG --- SessionsTable
        PG --- MessagesTable
        PG --- ArtifactsTable
    end

    Client <-->|HTTP REST & SSE Stream| API
    RAG <-->|Cosine Similarity (HNSW)| ChunksTable
    API <-->|Async CRUD| SessionsTable
    API <-->|Async CRUD| MessagesTable
    API <-->|Async CRUD| ArtifactsTable
```

---

## 3. Project Structure

```
.
├── .env.example                       # Environment template with safe defaults
├── docker-compose.yml                 # Multi-service container orchestration
├── pytest.ini                         # Pytest configuration with session loop scope
├── README.md                          # Main documentation & runbook
├── docs/
│   ├── PRD.md                         # Product Requirements Document & Discovery Brief
│   ├── architecture.md                # System architecture, schemas, and security
│   └── design.md                      # UI/UX design specifications & a11y
├── agent_transcripts/
│   ├── 01_initial_scaffolding.md      # Transcript: Initial scaffolding & design
│   ├── 02_debugging_pgvector_indexing.md # Transcript: Pgvector & transaction debugging
│   └── 03_evaluating_local_ollama_and_ship30.md # Transcript: Local Ollama & Ship 30 evaluation
├── backend/
│   ├── Dockerfile                     # Python 3.11 backend container
│   ├── requirements.txt               # Backend dependencies
│   ├── data/                          # Transcripts & cache directory
│   ├── scripts/
│   │   ├── download_transcripts.py    # Fetches transcripts from GitHub archive
│   │   ├── ingest.py                  # Chunks, embeds, and indexes into PostgreSQL
│   │   └── test_search.py             # CLI verification tool for search & refusal
│   ├── app/
│   │   ├── main.py                    # FastAPI application entry point
│   │   ├── config.py                  # Pydantic Settings configuration
│   │   ├── database.py                # Async engine & pgvector initialization
│   │   ├── models/
│   │   │   ├── db_models.py           # SQLAlchemy models (Session, Message, Artifact, Chunk)
│   │   │   └── schemas.py             # Pydantic v2 schemas
│   │   ├── providers/
│   │   │   ├── base.py                # BaseLLMProvider abstract base class
│   │   │   ├── ollama_provider.py     # Local Ollama streaming driver
│   │   │   ├── cloud_provider.py      # Claude 3.5 & OpenAI GPT-4o streaming drivers
│   │   │   └── factory.py             # LLM dynamic routing factory
│   │   ├── rag/
│   │   │   ├── embeddings.py          # FastEmbed (bge-small-en-v1.5) utility
│   │   │   └── retriever.py           # Cosine similarity retriever with fallback
│   │   ├── skills/
│   │   │   ├── ship30_writer.py       # Ship 30 for 30 Ghostwriting Skill
│   │   │   └── artifact_generator.py  # Claude-style artifact parser & prompt
│   │   └── api/
│   │       ├── health.py              # Health check probe endpoint
│   │       ├── sessions.py            # Session management routes
│   │       └── chat.py                # SSE streaming chat endpoint
│   └── tests/
│       ├── test_api.py                # FastAPI endpoints & session tests
│       ├── test_retrieval.py          # Vector search & refusal threshold tests
│       └── test_providers.py          # Provider routing, skills, & artifact tests
└── frontend/
    ├── Dockerfile                     # Next.js 14 production container
    ├── package.json                   # Frontend dependencies
    ├── tailwind.config.js             # Tailwind CSS styling configuration
    ├── tsconfig.json                  # TypeScript configuration
    └── src/
        ├── app/
        │   ├── layout.tsx             # Application layout & fonts
        │   ├── page.tsx               # Main dual-pane interface
        │   └── globals.css            # Tailwind directives
        ├── components/
        │   ├── Chat/
        │   │   ├── ChatPane.tsx       # Message list & input composer
        │   │   ├── MessageItem.tsx    # Bubble renderer with citation drawer
        │   │   └── ModelSelector.tsx  # Dynamic model & mode switch tabs
        │   └── Artifact/
        │       ├── ArtifactViewer.tsx # Side-by-side artifact preview & code tabs
        │       └── SandboxedIframe.tsx# Isolated iframe sandbox with DOMPurify
        ├── hooks/
        │   └── useChatStream.ts       # React hook for SSE streaming & artifact capture
        └── lib/
            └── api.ts                 # API client utilities & TypeScript types
```

---

## 4. Quickstart & Deployment

### 4.1 Prerequisites
- **Docker & Docker Compose** (v24+) OR **Local Python 3.11+ & Node.js 18+**
- **Ollama** installed on the host running `llama3.1:8b` (or `llama3:latest`):
  ```bash
  ollama pull llama3.1:8b
  ollama serve
  ```

### 4.2 Option A: Single-Command Docker Compose Startup (Recommended)
1. Clone the repository and configure environment variables:
   ```bash
   cp .env.example .env
   ```
2. Start the entire application stack:
   ```bash
   docker-compose up --build
   ```
3. Access the web application:
   - **Frontend UI:** `http://localhost:3000`
   - **Backend API Docs:** `http://localhost:8000/docs`
   - **Health Diagnostic Probe:** `http://localhost:8000/api/health`

### 4.3 Option B: Local Standalone Development Startup
If you prefer running without Docker:

1. **Start Ollama & PostgreSQL:**
   Ensure Ollama is running (`ollama serve`) and PostgreSQL is active.
2. **Backend Setup:**
   ```powershell
   # Create virtual environment
   python -m venv backend/venv
   backend\venv\Scripts\activate

   # Install dependencies
   pip install -r backend/requirements.txt

   # Download transcripts & run ingestion (indexes 320 chunks)
   python backend/scripts/download_transcripts.py
   python backend/scripts/ingest.py

   # Start FastAPI backend
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
3. **Frontend Setup:**
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```
   Open `http://localhost:3000` in your browser.

---

## 5. Knowledge Ingestion & Vector Indexing

The ingestion pipeline (`backend/scripts/ingest.py`) parses transcripts from the curated archive:
- **Speaker & Timestamp Preservation:** Chunks respect speaker turns and preserve timestamp markers `(HH:MM:SS)`.
- **Sliding Window:** 500–800 tokens (~2,400 characters) with a 100-token (~400 character) overlap to maintain semantic continuity across chunk boundaries.
- **Dense Vector Embeddings:** Encoded using `BAAI/bge-small-en-v1.5` (384 dimensions) via FastEmbed (ONNX runtime).
- **Pgvector Indexing:** Chunks are inserted into the `transcript_chunks` table with an HNSW cosine similarity index:
  ```sql
  CREATE INDEX idx_transcript_chunks_hnsw 
  ON transcript_chunks 
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);
  ```

To test vector retrieval via CLI:
```powershell
# In-domain test (returns ranked chunks with scores and guest citations)
python backend/scripts/test_search.py "How do you build a high-performing growth team?"

# Out-of-domain test (triggers deterministic refusal)
python backend/scripts/test_search.py "What is the quantum spin of a black hole in astrophysics?"
```

---

## 6. Core Product Capabilities

### 6.1 Grounded Conversational Q&A
- Queries the vector index for the top-5 most relevant chunks.
- Computes cosine similarity with a strict threshold $\tau \ge 0.55$.
- Enforces explicit bracketed citations: `[Guest Name: Episode Title, Timestamp]`.
- **Refusal Guarantee:** If similarity drops below 0.55 or no chunks match, the assistant immediately responds:
  > *"I do not have sufficient information in Lenny's podcast archive to answer this."*

### 6.2 Ship 30 for 30 Content Engine
Activated via the **"Ship 30 for 30 Essay"** mode tab in the UI:
- **The Hook:** First 2–3 lines highlight an operational contradiction or urgent growth tension.
- **Word Count:** ~1,250 words with deep operational substance.
- **Skimmability:** Strictly 1–3 sentence paragraphs with generous vertical rhythm.
- **Bold Anchor Bullets:** Every bullet starts with **Bold Anchor Keywords**.
- **Attribution:** Specific tactics attributed to guests.
- **Actionable Conclusion:** Ends with a step-by-step implementation checklist.

### 6.3 Side-by-Side Claude-Style Artifact Viewer
- When requested (e.g. *"Create an interactive Growth Loop Simulator in HTML/JS"*), the assistant emits an `<artifact>` block.
- The UI automatically slides open the side drawer, rendering the artifact beside the chat.
- **Security Isolation:**
  - HTML rendered inside `<iframe sandbox="allow-scripts" srcDoc={cleanHtml} />`.
  - **Omission of `allow-same-origin`** prevents scripts from reading `window.parent.localStorage` or document cookies.
  - Pre-sanitized with `DOMPurify` allowing styles and scripts for dynamic calculators while blocking cross-origin DOM escalation.
  - Includes **Preview** and **Code** tabs, clipboard copy, and file download.

### 6.4 Dual Model Switching
- Toggle between **Ollama (Local)**, **Claude 3.5 Sonnet (Cloud)**, and **OpenAI GPT-4o (Cloud)** directly from the top bar.
- Changes take effect on the next token stream without restarting the server or altering source code.

---

## 7. Automated Testing Suite

The project includes automated integration and unit tests covering API endpoints, vector retrieval, and model routing.

Run tests using pytest:
```powershell
backend\venv\Scripts\pytest -v
```

### Test Coverage:
- `backend/tests/test_retrieval.py`: Vector embeddings, cosine similarity calculation, in-domain citation retrieval, and out-of-domain refusal trigger.
- `backend/tests/test_api.py`: FastAPI `/api/health`, session creation (`POST /api/sessions`), session listing, detail retrieval, and deletion lifecycle.
- `backend/tests/test_providers.py`: Dynamic LLM provider factory routing, graceful error handling for missing API keys, Ship 30 prompt builder, and regex artifact extraction.

---

## 8. Manual Verification Plan for Evaluators

| Step | Action | Expected Result |
| :--- | :--- | :--- |
| **1. Health Check** | Navigate to `http://localhost:8000/api/health` | Returns HTTP 200 with JSON showing `database.status: healthy`, `indexed_chunks: 320`, and `ollama.status: connected`. |
| **2. Local Ollama Q&A** | Select `Local (Ollama)` in the UI and submit: *"According to Adam Fishman, how should a startup structure its first growth team?"* | Tokens stream in real time; response cites `[Adam Fishman: How to build a high-performing growth team, 00:10:59]`. Expandable citations drawer lists matching chunks. |
| **3. Grounded Refusal** | Ask: *"What is the chemical composition of basaltic rocks on Mars?"* | System displays amber Grounding Notice and responds: *"I do not have sufficient information in Lenny's podcast archive to answer this."* |
| **4. Ship 30 for 30 Essay** | Switch Mode to `Ship 30 for 30 Essay` and ask: *"Write an essay on Elena Verna's 10 growth tactics that never work."* | Emits an essay with curiosity hook, 1–3 sentence paragraphs, bold anchor bullet points, and an operational checklist conclusion. |
| **5. Interactive Artifact** | Switch Mode to `Interactive Artifact` and ask: *"Create an interactive Growth Loop Simulator in HTML/CSS/JS."* | Side drawer slides open. Interactive simulator renders inside the sandboxed iframe with functioning sliders. Toggling to "Code" shows clean source. Copy and download buttons function. |
| **6. Security Sandbox Verification** | Inspect iframe in Chrome DevTools: `document.querySelector('iframe').contentWindow.localStorage` | Throws `SecurityError: Blocked a frame with origin "null" from accessing a cross-origin frame.` |

---

## 9. Demo Video Guide & Presentation Script (2–3 Minutes)

Record a 2–3 minute presentation with your camera enabled to demonstrate the evaluation criteria.

### Script Breakdown:
- **0:00 – 0:30 (Context & Framing):**
  *"Hi everyone, I'm presenting The Lenny Growth Assistant. Growth PMs face a major problem: unlocking 350+ hours of podcast knowledge without scrubbing audio or accepting hallucinated advice. We designed this forward-deployed solution with strict grounding, dual local and cloud models, and Claude-style sandboxed artifacts."*
- **0:30 – 1:15 (Live Demo: Local Ollama & Grounding):**
  Show the UI on `http://localhost:3000`. Point out the `Ollama (llama3.1:8b)` provider badge. Ask: *"What is Elena Verna's framework for B2B product-led sales?"* Show real-time token streaming, citation badges `[Elena Verna, Timestamp]`, and open the sources drawer. Then submit an out-of-domain query (*"What is the orbital speed of Jupiter's moons?"*) and show the deterministic refusal.
- **1:15 – 2:00 (Ship 30 for 30 & Artifact Viewer):**
  Toggle to **Ship 30 for 30** mode and show the generated essay adhering to the ~1,250-word depth, bold anchor bullets, and tactical checklist. Then click **"Interactive Artifact"** to generate a Growth Loop Calculator. Show the side drawer sliding open, interactive sliders updating dynamically, and explain the iframe security model (`sandbox="allow-scripts"` without `allow-same-origin`, pre-sanitized with `DOMPurify`).
- **2:00 – 2:45 (Key Architectural Trade-Off & Conclusion):**
  *"One critical trade-off we made was using local 8B parameter models with strict prompt heuristics rather than relying solely on cloud APIs. This gives enterprise teams 100% data autonomy with zero inference cost, while maintaining sub-2 second time-to-first-token. Thank you!"*

---

## 10. Operational Runbook & Troubleshooting

- **Ollama Connection Refused (`http://localhost:11434`):**
  Run `ollama serve` in a terminal window. Verify that models are downloaded using `ollama list`.
- **Missing Models in Ollama:**
  Download the recommended 8B model via `ollama pull llama3.1:8b` (or `ollama pull llama3:latest`).
- **Database Connection Reset:**
  If Postgres is restarted, verify connection using `python backend/scripts/test_search.py`. The database automatically recovers.
- **Port Conflicts:**
  Backend runs on port `8000`, Frontend runs on `3000`, PostgreSQL on `5432`. If port 8000 is occupied, set `PORT=8001` in `.env` and update `NEXT_PUBLIC_API_URL`.

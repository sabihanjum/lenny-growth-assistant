# Product Requirements Document (PRD)
## The Lenny Growth Assistant: Enterprise RAG & Content Engine

**Document Version:** 1.0.0  
**Status:** Approved for Implementation  
**Author:** Forward Deployed Engineering Team  
**Target Delivery:** Evaluation Release  

---

## 1. Executive Summary & Discovery Brief

### 1.1 Context & Problem Statement
*Lenny’s Podcast* has become the definitive repository of operational knowledge for technology product management, growth, go-to-market (GTM), and leadership. With over 300 in-depth conversations spanning 350+ hours of audio, the volume of high-leverage frameworks and tactical playbooks is immense. 

However, growth product managers and product leaders face critical barriers:
- **Discovery Bottleneck:** Locating specific operational tactics (e.g., Elena Verna's B2B product-led sales motion or Adam Fishman's growth team org structure) requires scrubbing through hours of audio or static transcripts without context.
- **Synthesization Gap:** Answering complex cross-cutting questions requires collating disparate insights from multiple episodes into a structured, executive-ready format.
- **Actionability Friction:** Turning podcast concepts into tangible assets (e.g., retention calculators, onboarding audit checklists, growth loop diagrams) requires manual creation from scratch.
- **Privacy & Autonomy Requirements:** Enterprise evaluators and security-conscious PMs require the ability to run queries locally on proprietary machines without sending IP or strategic context to third-party cloud APIs.

### 1.2 User Personas & Jobs To Be Done (JTBD)

| Persona | Role & Context | Core Job To Be Done (JTBD) | Pain Points Solved |
| :--- | :--- | :--- | :--- |
| **Alex — Lead Growth PM** | Leading activation & onboarding at a Series B B2B SaaS company. Needs proven frameworks fast. | *"When I am redesigning our onboarding funnel, I want to retrieve proven activation tactics from top practitioners, so that I can de-risk our roadmap without re-inventing the wheel."* | Eliminates 4+ hours of manual research; provides direct attribution and episode timestamps to build stakeholder conviction. |
| **Sarah — Head of Product / Founder** | Pre-PMF to Series A founder establishing growth motions and hiring first growth engineers. | *"When I am crafting our weekly internal product strategy memo, I want to convert podcast insights into high-impact, skimmable Ship 30 for 30 essays, so that my team adopts best practices rapidly."* | Automates structured writing following proven high-retention frameworks; synthesizes multi-guest perspectives. |
| **Marcus — Forward Deployed Evaluator** | Enterprise technical evaluator or engineering lead assessing AI systems. | *"When I am assessing the solution, I want to inspect source citations, toggle seamlessly between local Ollama and cloud LLMs, and verify iframe sandboxing, so that I can trust enterprise operability."* | Single-command deployment (`docker-compose up`); deterministic out-of-domain refusals; complete auditability. |

---

## 2. Product Objectives & Measurable Success Metrics

| Objective | Metric Target | Measurement Methodology | Business Impact |
| :--- | :--- | :--- | :--- |
| **Grounded Retrieval Quality** | $\ge 90\%$ Citation Accuracy | Proportion of generated claims with verifiable `[Episode, Guest, Timestamp]` citations matching retrieved context chunks. | Zero hallucinated playbooks; high stakeholder trust. |
| **Refusal Determinism** | $100\%$ Out-of-Domain Refusal | Queries below cosine similarity threshold ($\tau < 0.55$) return *"I do not have sufficient information in Lenny's podcast archive to answer this."* | Eliminates confabulation on ungrounded topics. |
| **Local Inference Responsiveness** | $< 4.0\text{s}$ Time to First Token (TTFT) | Measured using Ollama `llama3.1:8b` or `llama3:latest` on standard 16GB developer workstations. | Interactive, low-friction conversational experience. |
| **Ship 30 for 30 Adherence** | $\approx 1,250$ words ($\pm 15\%$), 100% heuristic compliance | Validation of Hook (lines 1–3), short paragraphs (1–3 sentences), bold anchor bullets, and terminal operational checklist. | Executive-ready, high-retention strategic communication. |
| **Artifact Security Isolation** | $0$ XSS / DOM Leaks | Sandboxed iframe verification with `sandbox="allow-scripts"` and `DOMPurify` pre-sanitization; 0 access to parent `localStorage` or cookies. | Secure in-app rendering of untrusted AI-generated code. |

---

## 3. Assumptions & Scope Choices

### 3.1 Key Assumptions
1. **Transcript Quality:** Source transcripts from `ChatPRD/lennys-podcast-transcripts` contain reliable speaker annotations and timestamps accurate to within 1–2 minutes.
2. **Local Workstation Hardware:** Evaluator machines possess at least 4 CPU cores, 16 GB RAM, and Ollama installed with 7B/8B class models (`llama3.1:8b`, `llama3:latest`, or `llama3.2:3b`).
3. **Single-Node Deployment:** Evaluation occurs either via unified Docker Compose or directly on localhost with a persistent PostgreSQL database. Multi-tenant distributed clusters are out of scope for this release.
4. **Offline Resilience:** Retrieval and embedding operations should function locally without mandatory internet access once initial models/dependencies are cached.

### 3.2 Scope Inclusions vs. Exclusions

```
+-------------------------------------------------------------------------------+
| IN SCOPE (Delivered)                                                          |
+-------------------------------------------------------------------------------+
| * High-accuracy semantic retrieval with pgvector HNSW indexing               |
| * Dual-provider LLM abstraction (Local Ollama <-> Cloud Anthropic / OpenAI)  |
| * Dedicated "Ship 30 for 30" content engine skill                            |
| * Side-by-side Claude-style Artifact Viewer with live iframe sandboxing       |
| * Session state persistence (Sessions, Messages, Artifacts in PostgreSQL)     |
| * Streaming Server-Sent Events (SSE) for low-latency response rendering       |
| * Single-command Docker Compose orchestration + full automated test suite     |
+-------------------------------------------------------------------------------+
| OUT OF SCOPE (Intentionally Excluded)                                         |
+-------------------------------------------------------------------------------+
| - Real-time YouTube audio stream downloading/Whisper transcribing at runtime  |
| - Complex multi-tenant RBAC / SSO authentication (designed for team/evaluator)|
| - Distributed vector database clusters (pgvector is ideal for ~300 episodes)  |
| - Fine-tuning bespoke base weights (in-context RAG provides superior grounding|
+-------------------------------------------------------------------------------+
```

---

## 4. User Journeys & Functional Requirements

### 4.1 Journey 1: Grounded Conversational Q&A
1. User navigates to the app; the system initializes a session with an active provider badge (e.g. `Ollama (llama3.1:8b)`).
2. User asks: *"What is Elena Verna's framework for B2B product-led sales?"*
3. System computes query embedding, queries PostgreSQL `pgvector`, and retrieves top-5 matching transcript chunks.
4. If chunks exceed similarity threshold ($\ge 0.55$), the model streams an answer with clear inline citations `[Elena Verna: B2B Growth & PLG, 00:24:15]`.
5. If the user asks an irrelevant query (*"What is the airspeed velocity of an unladen swallow?"*), the system immediately refuses with the canonical grounding notice.

### 4.2 Journey 2: Ship 30 for 30 Essay Generation
1. User toggles the **"Ship 30 for 30"** mode in the chat interface.
2. User prompts: *"Write an essay on building high-performing growth teams based on Adam Fishman's episode."*
3. The system retrieves relevant chunks from Adam Fishman's interview and activates the Ship 30 for 30 Ghostwriting Skill.
4. The response streams as a 1,250-word essay featuring:
   - Counterintuitive hook / curiosity gap in the first 2–3 lines.
   - Short 1–3 sentence paragraphs maximizing skimmability.
   - Bold anchor words for each tactical takeaway.
   - Grounded case studies with explicit guest attribution.
   - An operational implementation checklist at the conclusion.

### 4.3 Journey 3: Side-by-Side Artifact Generation & Interactive Viewer
1. User prompts: *"Create an interactive Growth Loop Simulator in HTML/CSS/JS that lets me model acquisition loops."*
2. The agent returns a brief introductory message and emits an `<artifact>` block:
   ```html
   <artifact identifier="growth-loop-sim" type="html" title="Interactive Growth Loop Simulator">
     <!DOCTYPE html>
     ...interactive calculator with styling and JS event handlers...
   </artifact>
   ```
3. The frontend detects the artifact tag in real time. The right drawer slides open automatically.
4. The artifact renders inside a sandboxed `<iframe>` with `sandbox="allow-scripts"` (strictly isolated from parent origin).
5. The user interacts with sliders to model growth retention and can toggle between the rendered preview and raw code.

---

## 5. Technical Acceptance Criteria

1. **API Endpoints:**
   - `POST /api/sessions`: Returns a new session UUID with timestamp.
   - `GET /api/sessions`: Lists all previous sessions ordered by `updated_at`.
   - `GET /api/sessions/{session_id}`: Returns message history and generated artifacts.
   - `POST /api/chat`: Streams SSE events (`status`, `sources`, `token`, `artifact`, `done`).
   - `GET /api/health`: Returns HTTP 200 with JSON payload reporting DB status, vector extension status, Ollama reachability, and ingested chunk count.
2. **Model Switching:**
   - Toggling provider in the UI immediately directs subsequent chat requests to the selected provider without backend restarts or code changes.
3. **Grounding & Refusal:**
   - Every substantive claim must feature a bracketed source reference.
   - Unrelated queries must be deterministically rejected.
4. **Artifact Safety:**
   - Scripts executing within the artifact must fail if attempting to read `window.parent.localStorage` or document cookies.

---

## 6. Risks, Trade-offs & Mitigations

| Risk | Impact | Trade-Off Decision | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Local 8B Model Reasoning Limits** | Medium | Chose `llama3.1:8b` over 70B models to guarantee smooth execution on standard 16GB laptops without external GPU clusters. | Highly structured system prompts with one-shot format constraints; concise retrieval context injection ($K=4\text{--}6$ chunks). |
| **Local Inference Latency** | Medium | Quantized local models (`Q4_K_M`) may produce token generation latency if context windows are overloaded. | Target chunk size of 500–800 tokens; prompt compaction; real-time streaming SSE to reduce perceived TTFT. |
| **Hallucinated Citations** | High | LLMs can confabulate plausible episode titles if context is ambiguous. | System prompt strictly mandates: *"Cite ONLY from the provided Context Chunks using the exact format `[Guest, Episode Title, Timestamp]`. Never invent citations."* |
| **Untrusted Code Execution in UI** | Critical | Generated HTML could execute malicious JavaScript targeting the user's browser session. | Rigid iframe sandboxing (`sandbox="allow-scripts"`, omission of `allow-same-origin`); input sanitized using `DOMPurify`. |
| **Database Dependency** | Low | Evaluating user might not have Docker running immediately. | Primary setup uses Docker Compose pgvector; backend includes local vector search fallback for zero-downtime offline testing. |

---

## 7. Sign-off & Roadmap
- **Sprint 1 (Now):** Core PRD, Architecture, Ingestion, Dual LLM layer, FastAPI streaming backend, Sandboxed Artifact frontend, Automated tests.
- **Sprint 2 (Future):** Dynamic audio playback synced to transcript timestamps; automated weekly transcript syncing via GitHub Actions.

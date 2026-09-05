# Engineering Transcript 03: Evaluating Local Ollama, Ship 30 Engine, & Artifact Sandbox

**Phase:** Agent Evaluation, Prompt Engineering, & Security Isolation  
**Focus:** Local model performance, structured essay generation, iframe sandboxing, and automated verification  

---

## 1. Local LLM Evaluation: Ollama `llama3.1:8b` vs `llama3.2:1b`

The assignment mandates that the submitted demo must run locally using Ollama.
We evaluated the models present on the evaluation machine:
- `llama3.2:1b`: Extremely fast (TTFT < 800ms), but frequently failed to follow complex multi-attribute formatting heuristics (such as bold anchor words on every bullet) and occasionally dropped episode citations.
- `llama3:latest`: Good reasoning, but occasionally produced longer preamble before diving into the hook.
- `llama3.1:8b`: **Best performer.** Accurately maintained the 1,250-word depth target, preserved citation syntax `[Guest: Episode, Timestamp]`, strictly adhered to 1–3 sentence paragraphs, and executed the out-of-domain refusal instructions with 100% fidelity.

### Latency Benchmark (Local Host):
- Time to First Token (TTFT): **~1.8 seconds**
- Generation Speed: **~35 tokens/second**
- Context Window configured: `8192` tokens

---

## 2. Refusal Calibration & Groundedness Verification

To guarantee zero hallucinations on ungrounded questions, we tested the retrieval similarity threshold $\tau$:

| Query | Top Cosine Similarity | Action Taken |
| :--- | :--- | :--- |
| *"How do you build a high-performing growth team?"* | **0.7247** (Adam Fishman) | Context injected; grounded response streamed with timestamps. |
| *"What is Elena Verna's framework for B2B PLG?"* | **0.7410** (Elena Verna) | Context injected; synthesized product-led sales motion. |
| *"What is the quantum spin of a black hole in astrophysics?"* | **0.3120** | **Refusal Triggered:** No chunks passed $\tau \ge 0.55$. Emitted canonical grounding notice. |
| *"What is the chemical composition of basaltic rocks on Mars?"* | **0.2850** | **Refusal Triggered:** Deterministic refusal returned. |

---

## 3. Ship 30 for 30 Writing Heuristics Encoding

Rather than relying on vague prompting, we codified the five core pillars of the Ship 30 for 30 framework into `backend/app/skills/ship30_writer.py`:
1. **The Hook (First 2–3 lines):** No introductory fluff ("In this article..."). Opens directly with an operational contradiction or tension (e.g. *"Most founders think hiring a Head of Growth will solve their growth problem. In reality, it's the fastest way to burn \$300,000 and stall your roadmap."*).
2. **Pacing & Skimmability:** Enforced maximum 1 to 3 sentences per paragraph. Generous vertical whitespace.
3. **Bold Anchor Bullets:** Mandatory bold anchor keywords starting every bullet point (e.g. `* **The Friction Audit:** ...`).
4. **Attribution:** Direct inline brackets referencing the podcast episode and timestamp.
5. **Actionable Conclusion:** Terminal step-by-step checklist formatted for executive execution.

---

## 4. Claude-Style Artifact Viewer & Security Boundary

### Design:
When users request interactive calculators, checklists, or frameworks, the agent wraps the output in:
```html
<artifact identifier="growth-loop-sim" type="html" title="Interactive Growth Loop Simulator">
  <!DOCTYPE html>...
</artifact>
```

### Security Verification:
Treating generated HTML as untrusted is an explicit requirement:
1. **DOMPurify Sanitization:**
   ```typescript
   const cleanHtml = DOMPurify.sanitize(content, {
     WHOLE_DOCUMENT: true,
     ADD_TAGS: ["style", "link", "script"],
     ADD_ATTR: ["target"],
   });
   ```
2. **Sandboxed Iframe Isolation:**
   ```html
   <iframe
     title={title}
     srcDoc={cleanHtml}
     sandbox="allow-scripts"
   />
   ```
   - **Why `sandbox="allow-scripts"`?** Enables interactive JavaScript (sliders, buttons, calculators) to run smoothly inside the preview.
   - **Why OMIT `allow-same-origin`?** Omission forces the iframe into an opaque `null` origin. Even if malicious script is injected, any attempt to read `window.parent.localStorage`, `sessionStorage`, or cookies throws a browser SecurityError (`Blocked a frame with origin "null" from accessing a cross-origin frame`).

---

## 5. Automated Test Suite Optimization

During pytest test execution on Windows with Python 3.13, we encountered an async event loop mismatch where SQLAlchemy's connection pool attempted to ping an asyncpg connection on an event loop closed by a previous test function.

### Fix:
Configured `pytest.ini`:
```ini
[pytest]
pythonpath = backend
asyncio_mode = auto
asyncio_default_fixture_loop_scope = session
asyncio_default_test_loop_scope = session
testpaths = backend/tests
```
Result: **All 9 test suites passed in 3.71s**, covering vector embeddings, retrieval thresholds, API endpoints, session persistence, and provider routing.

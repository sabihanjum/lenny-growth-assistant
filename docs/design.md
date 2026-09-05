# Design Specification & UI/UX Principles
## The Lenny Growth Assistant: Enterprise RAG & Content Engine

**Document Version:** 1.0.0  
**Status:** Approved for Implementation  
**Author:** Forward Deployed Engineering Team  

---

## 1. UI/UX Design Philosophy: "The Impeccable Standard"

The Lenny Growth Assistant is designed for senior product leaders and forward-deployed engineers. The interface emphasizes **editorial precision, cognitive clarity, and low latency**. Rather than treating AI as a generic chatbot, the UI treats it as an interactive knowledge workspace with first-class support for documents and artifacts.

### Core Principles
1. **Source Grounding as First-Class UI:** Every assertion displays accessible, non-obtrusive citation tags `[Guest Name, Timestamp]`. Clicking a citation highlights the exact episode metadata.
2. **Side-by-Side Content Artifacts (Claude-Style):** Complex documents, Ship 30 for 30 essays, and interactive HTML widgets must never be cramped into narrow chat bubbles. They open in a dedicated, high-fidelity side drawer.
3. **Transparent Execution State:** Real-time visibility into retrieval steps, model provider selection, and latency signals eliminates "black-box" anxiety.
4. **Resilient Minimalism:** High contrast, legible typography (Inter/system sans-serif paired with clean monospace code fonts), subtle borders, and zero clutter.

---

## 2. Information Architecture & Layout Anatomy

The interface is organized into a modular **Three-Zone Workspace**:

```
+-----------------------------------------------------------------------------------------+
|                                    APPLICATION HEADER                                   |
| [Logo] The Lenny Growth Assistant    [Provider Badge: Ollama]    [Mode Toggle: Q&A|Ship30|Artifact] |
+------------------+-----------------------------------------+----------------------------+
|  SESSION SIDEBAR |                CHAT PANE                |    ARTIFACT VIEWER DRAWER  |
|                  |                                         |    (Collapsible / 50% split) |
|  [+ New Session] |  Assistant:                             |                            |
|                  |  "According to Adam Fishman, the...     |  +----------------------+  |
|  * Growth Loops  |   [Adam Fishman, 00:04:12]              |  | [Preview] | [Code]   |  |
|  * B2B PLG Sales |                                         |  +----------------------+  |
|  * Org Design    |  User:                                  |  |                      |  |
|                  |  "Generate an interactive calculator"   |  |  Interactive Canvas  |  |
|                  |                                         |  |  (Sandboxed Iframe)  |  |
|                  |  Assistant:                             |  |                      |  |
|                  |  "I've created the artifact for you."   |  |                      |  |
|                  |  [View Artifact: Growth Calculator ->]  |  +----------------------+  |
|                  |                                         |  [Copy Code] [Download]    |
|                  |-----------------------------------------|                            |
|                  | [Input Field: Ask Lenny's transcripts...]                           |
+------------------+-----------------------------------------+----------------------------+
```

### 2.1 Zone 1: Sessions & History Sidebar (Left, 260px)
- **Session List:** Ordered chronologically by last updated.
- **Actions:** Quick "New Chat" button (`Cmd/Ctrl + K`), rename session, delete session.
- **Status Indicator:** System health status dot (Green = DB + Ollama connected; Amber = Local fallback).

### 2.2 Zone 2: Main Conversational Stream (Center, 50%–100%)
- **Top Bar Controls:**
  - **Provider Selector:** Dropdown to switch dynamically between `Ollama (llama3.1:8b)`, `Claude 3.5 Sonnet`, and `OpenAI GPT-4o`.
  - **Mode Selector:** Pill tabs for `Standard Q&A`, `Ship 30 for 30 Essay`, and `Interactive Artifact`.
- **Message List:**
  - Distinct visual styling for user (subtle dark bubble) and assistant (clean editorial left-aligned).
  - Inline collapsible citation badges with direct link to episode and timestamp.
- **Input Composer:**
  - Auto-resizing textarea with keyboard submission (`Enter` to submit, `Shift+Enter` for newline).
  - Quick starter prompt chips (e.g. *"Elena Verna on PLG"*, *"Adam Fishman on growth team hiring"*, *"Brian Balfour growth loops"*).

### 2.3 Zone 3: Side-by-Side Artifact Drawer (Right, Collapsible 50% Split)
- **Header:** Artifact title, type badge (`HTML / CSS` or `Markdown Document`), and window controls (Close, Maximize to Fullscreen).
- **Tab Bar:**
  - **Preview Tab:** Renders either formatted Markdown or the isolated sandboxed iframe.
  - **Code Tab:** Syntax-highlighted raw source code with line numbers.
- **Footer Toolbar:** "Copy to Clipboard" with feedback animation, "Download File" (`.html` or `.md`).

---

## 3. Key Interaction States & Micro-interactions

### 3.1 State 1: Retrieval in Progress
- While vector embeddings and similarity search execute, display an animated pulsing skeleton badge:
  `[Searching Lenny's Podcast Transcripts (top-5 matches)...]`

### 3.2 State 2: Real-Time SSE Token Streaming
- Tokens stream smoothly via Server-Sent Events.
- A subtle blinking cursor marks the active generation point.
- Citations appear in an expandable drawer above the response text.

### 3.3 State 3: Artifact Detection & Automatic Drawer Open
- When the assistant outputs `<artifact ...>`, the client parser automatically captures the tag.
- The right artifact pane slides in smoothly (300ms cubic-bezier transition).
- The chat pane transitions to a 50/50 split on desktop displays.

### 3.4 State 4: Out-of-Domain Refusal
- If the retrieved similarity score is below threshold $\tau < 0.55$, the assistant renders a dedicated amber warning card:
  > *"I do not have sufficient information in Lenny's podcast archive to answer this question. My answers are strictly grounded in guest transcripts."*

---

## 4. Responsive Breakpoints & Adaptive Layout

| Viewport Width | Layout Behavior |
| :--- | :--- |
| **Desktop ($\ge 1280\text{px}$)** | Full three-zone layout. Chat and Artifact drawer side-by-side (50% / 50%). Sidebar visible. |
| **Laptop / Tablet ($768\text{px}\text{--}1279\text{px}$)** | Collapsible sidebar (hamburger toggle). Chat and Artifact split dynamically or toggle via tab. |
| **Mobile ($< 768\text{px}$)** | Single-column view. Artifact drawer opens as a full-screen sliding modal sheet with bottom drag handle. |

---

## 5. Accessibility (a11y) & Usability Standards

1. **WCAG 2.1 AA Compliance:** Color contrast ratio $\ge 4.5:1$ for all body text and $\ge 3:1$ for UI control borders.
2. **Keyboard Navigation:** Full focus trap inside modal dialogs; tab order follows logical DOM flow (`Sidebar` -> `Model Switcher` -> `Chat Stream` -> `Input` -> `Artifact`).
3. **Screen Reader Live Regions:** Streaming tokens announce updates via `aria-live="polite"` to avoid disorienting assistive tech users.
4. **Sandboxed Iframe Isolation:** Iframe contains explicit `title` attributes and cannot capture or trap top-level browser focus involuntarily.

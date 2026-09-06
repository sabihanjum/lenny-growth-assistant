/**
 * API client utilities for communicating with The Lenny Growth Assistant backend.
 */

export const getApiBase = (): string => {
  const url = process.env.NEXT_PUBLIC_API_URL || "";
  if (!url) return "";
  if (url.startsWith("http://") || url.startsWith("https://")) {
    return url.replace(/\/$/, "");
  }
  return `https://${url.replace(/\/$/, "")}`;
};

const API_BASE = getApiBase();

export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Citation {
  slug: string;
  episode: string;
  guest: string;
  timestamp?: string;
  score: number;
  snippet: string;
}

export interface Artifact {
  id?: string;
  message_id?: string;
  identifier: string;
  artifact_type: "html" | "markdown";
  title: string;
  content: string;
  created_at?: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  sources?: Citation[];
  artifacts?: Artifact[];
  created_at: string;
}

export interface SessionDetail {
  session: Session;
  messages: Message[];
}

export interface HealthData {
  status: string;
  timestamp: string;
  database: {
    status: string;
    pgvector_active: boolean;
    indexed_chunks: number;
    total_sessions: number;
  };
  ollama: {
    status: string;
    base_url: string;
    available_models: string[];
    default_model: string;
  };
  retrieval: {
    model: string;
    dimension: number;
    similarity_threshold: number;
    top_k: number;
  };
}

export async function fetchHealth(): Promise<HealthData> {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) throw new Error(`Health check failed: HTTP ${res.status}`);
  return res.json();
}

export async function fetchSessions(): Promise<Session[]> {
  const res = await fetch(`${API_BASE}/api/sessions`);
  if (!res.ok) throw new Error(`Failed to fetch sessions: HTTP ${res.status}`);
  return res.json();
}

export async function createSession(title: string = "New Growth Conversation"): Promise<Session> {
  const res = await fetch(`${API_BASE}/api/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error(`Failed to create session: HTTP ${res.status}`);
  return res.json();
}

export async function fetchSessionDetail(sessionId: string): Promise<SessionDetail> {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}`);
  if (!res.ok) throw new Error(`Failed to fetch session ${sessionId}: HTTP ${res.status}`);
  return res.json();
}

export async function deleteSession(sessionId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error(`Failed to delete session ${sessionId}: HTTP ${res.status}`);
}

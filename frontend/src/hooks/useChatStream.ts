"use client";

import { useState, useRef, useCallback } from "react";
import { Citation, Artifact, getApiBase } from "@/lib/api";

const API_BASE = getApiBase();

interface SendMessageOptions {
  sessionId?: string;
  message: string;
  mode: string;
  provider: string;
  model?: string;
  onDone?: (result: {
    sessionId: string;
    content: string;
    sources: Citation[];
    artifacts: Artifact[];
  }) => void;
  onError?: (err: Error) => void;
}

export function useChatStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [currentCitations, setCurrentCitations] = useState<Citation[]>([]);
  const [currentArtifacts, setCurrentArtifacts] = useState<Artifact[]>([]);
  const [streamingContent, setStreamingContent] = useState<string>("");
  const abortControllerRef = useRef<AbortController | null>(null);

  const cancelStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsStreaming(false);
      setStatusMessage(null);
    }
  }, []);

  const sendMessage = useCallback(
    async ({ sessionId, message, mode, provider, model, onDone, onError }: SendMessageOptions) => {
      setIsStreaming(true);
      setStatusMessage("Connecting to Lenny Growth Assistant...");
      setCurrentCitations([]);
      setCurrentArtifacts([]);
      setStreamingContent("");

      const controller = new AbortController();
      abortControllerRef.current = controller;

      try {
        const response = await fetch(`${API_BASE}/api/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: sessionId || null,
            message,
            mode,
            provider,
            model: model || null,
            temperature: 0.3,
          }),
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`Chat API error: HTTP ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error("No response body reader available.");

        const decoder = new TextDecoder("utf-8");
        let buffer = "";
        let finalContent = "";
        let finalCitations: Citation[] = [];
        let finalArtifacts: Artifact[] = [];
        let finalSessionId = sessionId || "";

        let currentEvent = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed) {
              currentEvent = "";
              continue;
            }

            if (trimmed.startsWith("event: ")) {
              currentEvent = trimmed.slice(7).trim();
            } else if (trimmed.startsWith("data: ")) {
              const rawData = trimmed.slice(6);
              try {
                const data = JSON.parse(rawData);

                if (currentEvent === "status") {
                  setStatusMessage(data.message || null);
                } else if (currentEvent === "sources") {
                  finalCitations = data;
                  setCurrentCitations(data);
                } else if (currentEvent === "token") {
                  finalContent += data.token;
                  setStreamingContent((prev) => prev + data.token);
                } else if (currentEvent === "artifact") {
                  finalArtifacts = data;
                  setCurrentArtifacts(data);
                } else if (currentEvent === "done") {
                  if (data.session_id) finalSessionId = data.session_id;
                  setIsStreaming(false);
                  setStatusMessage(null);
                  if (onDone) {
                    onDone({
                      sessionId: finalSessionId,
                      content: finalContent,
                      sources: finalCitations,
                      artifacts: finalArtifacts,
                    });
                  }
                }
              } catch (parseErr) {
                console.warn("Could not parse SSE JSON line:", trimmed, parseErr);
              }
            }
          }
        }
      } catch (err: any) {
        if (err.name === "AbortError") {
          console.log("Stream aborted by user.");
        } else {
          console.error("Chat streaming error:", err);
          if (onError) onError(err);
        }
      } finally {
        setIsStreaming(false);
        setStatusMessage(null);
        abortControllerRef.current = null;
      }
    },
    []
  );

  return {
    isStreaming,
    statusMessage,
    currentCitations,
    currentArtifacts,
    streamingContent,
    sendMessage,
    cancelStream,
  };
}

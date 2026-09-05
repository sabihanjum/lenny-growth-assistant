"use client";

import React, { useState, useEffect } from "react";
import {
  MessageSquarePlus,
  Trash2,
  Sparkles,
  PanelLeftClose,
  PanelLeft,
  Activity,
  Podcast,
} from "lucide-react";
import {
  Session,
  Message,
  Artifact,
  fetchSessions,
  createSession,
  fetchSessionDetail,
  deleteSession,
  fetchHealth,
} from "@/lib/api";
import { useChatStream } from "@/hooks/useChatStream";
import { ChatPane } from "@/components/Chat/ChatPane";
import { ArtifactViewer } from "@/components/Artifact/ArtifactViewer";

export default function Home() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // Artifact Viewer state
  const [isArtifactOpen, setIsArtifactOpen] = useState(false);
  const [activeArtifacts, setActiveArtifacts] = useState<Artifact[]>([]);
  const [activeArtifactIndex, setActiveArtifactIndex] = useState(0);

  // Model & Mode settings
  const [provider, setProvider] = useState("ollama");
  const [model, setModel] = useState("llama3.1:8b");
  const [mode, setMode] = useState("default");
  const [availableOllamaModels, setAvailableOllamaModels] = useState<string[]>([
    "llama3.1:8b",
    "llama3:latest",
    "llama3.2:1b",
  ]);
  const [healthInfo, setHealthInfo] = useState<{ status: string; chunks: number } | null>(null);

  const {
    isStreaming,
    statusMessage,
    currentCitations,
    currentArtifacts,
    streamingContent,
    sendMessage,
    cancelStream,
  } = useChatStream();

  // Load initial health and sessions
  useEffect(() => {
    async function loadInitData() {
      try {
        const health = await fetchHealth();
        setHealthInfo({
          status: health.status,
          chunks: health.database.indexed_chunks,
        });
        if (health.ollama.available_models && health.ollama.available_models.length > 0) {
          setAvailableOllamaModels(health.ollama.available_models);
          setModel(health.ollama.default_model || health.ollama.available_models[0]);
        }
      } catch (e) {
        console.warn("Could not load health diagnostics:", e);
      }

      try {
        const sessList = await fetchSessions();
        setSessions(sessList);
        if (sessList.length > 0) {
          selectSession(sessList[0].id);
        }
      } catch (e) {
        console.warn("Could not load sessions:", e);
      }
    }
    loadInitData();
  }, []);

  const selectSession = async (sessionId: string) => {
    setCurrentSessionId(sessionId);
    try {
      const detail = await fetchSessionDetail(sessionId);
      setMessages(detail.messages);

      // Collect any artifacts already created in this session
      const existingArtifacts: Artifact[] = [];
      for (const m of detail.messages) {
        if (m.artifacts && m.artifacts.length > 0) {
          existingArtifacts.push(...m.artifacts);
        }
      }
      if (existingArtifacts.length > 0) {
        setActiveArtifacts(existingArtifacts);
        setActiveArtifactIndex(existingArtifacts.length - 1);
      }
    } catch (e) {
      console.error("Failed to load session details:", e);
    }
  };

  const handleNewChat = async () => {
    try {
      const newSess = await createSession("New Growth Conversation");
      setSessions((prev) => [newSess, ...prev]);
      setCurrentSessionId(newSess.id);
      setMessages([]);
      setIsArtifactOpen(false);
      setActiveArtifacts([]);
    } catch (e) {
      console.error("Failed to create new session:", e);
    }
  };

  const handleDeleteSession = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      await deleteSession(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
      if (currentSessionId === id) {
        setCurrentSessionId(null);
        setMessages([]);
        setIsArtifactOpen(false);
      }
    } catch (err) {
      console.error("Failed to delete session:", err);
    }
  };

  const handleSendMessage = (text: string) => {
    const optimisticUserMsg: Message = {
      id: "opt-" + Date.now(),
      session_id: currentSessionId || "",
      role: "user",
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, optimisticUserMsg]);

    sendMessage({
      sessionId: currentSessionId || undefined,
      message: text,
      mode,
      provider,
      model,
      onDone: async ({ sessionId, artifacts }) => {
        setCurrentSessionId(sessionId);
        const sessList = await fetchSessions();
        setSessions(sessList);
        const detail = await fetchSessionDetail(sessionId);
        setMessages(detail.messages);

        if (artifacts && artifacts.length > 0) {
          setActiveArtifacts(artifacts);
          setActiveArtifactIndex(0);
          setIsArtifactOpen(true);
        }
      },
    });
  };

  const handleOpenArtifact = (art: Artifact) => {
    setActiveArtifacts([art]);
    setActiveArtifactIndex(0);
    setIsArtifactOpen(true);
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-100">
      {/* Session Sidebar */}
      <aside
        className={`${
          isSidebarOpen ? "w-64" : "w-0"
        } transition-all duration-200 ease-in-out flex flex-col bg-slate-900 text-slate-200 border-r border-slate-800 overflow-hidden flex-shrink-0`}
      >
        {/* Brand Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center text-white shadow-sm">
              <Podcast className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xs font-bold uppercase tracking-wider text-white">
                Lenny Assistant
              </h1>
              <p className="text-[10px] text-slate-400">Enterprise Growth RAG</p>
            </div>
          </div>
        </div>

        {/* New Chat Button */}
        <div className="p-3">
          <button
            onClick={handleNewChat}
            className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold transition shadow-sm"
          >
            <MessageSquarePlus className="w-4 h-4" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto px-2 space-y-1">
          <div className="px-2 py-1 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
            History
          </div>
          {sessions.map((s) => (
            <div
              key={s.id}
              onClick={() => selectSession(s.id)}
              className={`group flex items-center justify-between px-3 py-2 rounded-lg text-xs cursor-pointer transition ${
                currentSessionId === s.id
                  ? "bg-slate-800 text-white font-medium border border-slate-700"
                  : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
              }`}
            >
              <span className="truncate flex-1 mr-2">{s.title}</span>
              <button
                onClick={(e) => handleDeleteSession(e, s.id)}
                className="opacity-0 group-hover:opacity-100 p-1 text-slate-500 hover:text-red-400 transition"
                title="Delete session"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>

        {/* Operational Health Badge in Footer */}
        <div className="p-3 border-t border-slate-800 bg-slate-950/60">
          <div className="flex items-center space-x-2 text-[11px] text-slate-400">
            <span
              className={`w-2 h-2 rounded-full ${
                healthInfo?.status === "ok" ? "bg-emerald-500 animate-pulse" : "bg-amber-500"
              }`}
            />
            <span className="truncate">
              {healthInfo
                ? `${healthInfo.chunks} chunks indexed`
                : "Checking status..."}
            </span>
          </div>
        </div>
      </aside>

      {/* Main Content Workspace */}
      <main className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        {/* Top Navbar */}
        <div className="h-11 bg-white border-b border-gray-200 flex items-center justify-between px-4 flex-shrink-0">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition"
              title="Toggle sidebar"
            >
              {isSidebarOpen ? (
                <PanelLeftClose className="w-4 h-4" />
              ) : (
                <PanelLeft className="w-4 h-4" />
              )}
            </button>
            <span className="text-xs font-semibold text-gray-700">
              The Lenny Growth Assistant
            </span>
          </div>

          <div className="flex items-center space-x-3 text-xs text-gray-500">
            <span className="hidden sm:inline-block">
              Model: <strong className="text-gray-800">{provider === "ollama" ? `Ollama (${model})` : provider}</strong>
            </span>
            {isArtifactOpen && (
              <span className="text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-200 text-[11px] font-medium">
                Dual-Pane Active
              </span>
            )}
          </div>
        </div>

        {/* Split Screen Container (Chat + Artifact Viewer) */}
        <div className="flex-1 flex min-h-0 overflow-hidden">
          {/* Left Chat Pane (flex-1 or 50% split) */}
          <div
            className={`flex-1 h-full min-w-0 transition-all duration-200 ${
              isArtifactOpen ? "w-full lg:w-1/2" : "w-full"
            }`}
          >
            <ChatPane
              messages={messages}
              isStreaming={isStreaming}
              statusMessage={statusMessage}
              streamingContent={streamingContent}
              streamingCitations={currentCitations}
              onSendMessage={handleSendMessage}
              onCancelStream={cancelStream}
              onOpenArtifact={handleOpenArtifact}
              provider={provider}
              setProvider={setProvider}
              model={model}
              setModel={setModel}
              mode={mode}
              setMode={setMode}
              availableOllamaModels={availableOllamaModels}
            />
          </div>

          {/* Right Artifact Drawer (Claude-style Side-by-Side) */}
          {isArtifactOpen && (
            <div className="w-full lg:w-1/2 h-full border-l border-gray-200 transition-all duration-200">
              <ArtifactViewer
                artifacts={activeArtifacts}
                activeArtifactIndex={activeArtifactIndex}
                onSelectArtifact={(idx) => setActiveArtifactIndex(idx)}
                onClose={() => setIsArtifactOpen(false)}
              />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

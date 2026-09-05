"use client";

import React, { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Send, Square, Sparkles, Compass, Layers, ShieldCheck, ChevronRight } from "lucide-react";
import { Message, Citation, Artifact } from "@/lib/api";
import { ModelSelector } from "./ModelSelector";
import { MessageItem } from "./MessageItem";

interface ChatPaneProps {
  messages: Message[];
  isStreaming: boolean;
  statusMessage: string | null;
  streamingContent: string;
  streamingCitations: Citation[];
  onSendMessage: (text: string) => void;
  onCancelStream: () => void;
  onOpenArtifact: (artifact: Artifact) => void;
  provider: string;
  setProvider: (p: string) => void;
  model: string;
  setModel: (m: string) => void;
  mode: string;
  setMode: (m: string) => void;
  availableOllamaModels: string[];
}

const STARTER_PROMPTS = [
  {
    icon: Compass,
    title: "Elena Verna on PLG",
    query: "What is Elena Verna's framework for B2B product-led sales and why do traditional tactics fail?",
  },
  {
    icon: Sparkles,
    title: "Adam Fishman on Growth Teams",
    query: "According to Adam Fishman, how should a startup structure and hire for its first growth team?",
  },
  {
    icon: Layers,
    title: "Interactive Growth Calculator",
    query: "Create an interactive Growth Loop Simulator in HTML/CSS/JS that lets me model acquisition and retention loops.",
    mode: "artifact",
  },
  {
    icon: ShieldCheck,
    title: "Out-of-Domain Refusal Test",
    query: "What is the orbital speed of Jupiter's moons?",
  },
];

export const ChatPane: React.FC<ChatPaneProps> = ({
  messages,
  isStreaming,
  statusMessage,
  streamingContent,
  streamingCitations,
  onSendMessage,
  onCancelStream,
  onOpenArtifact,
  provider,
  setProvider,
  model,
  setModel,
  mode,
  setMode,
  availableOllamaModels,
}) => {
  const [inputText, setInputText] = useState("");
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent, statusMessage]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputText.trim() || isStreaming) return;
    onSendMessage(inputText.trim());
    setInputText("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = `${Math.min(e.target.scrollHeight, 180)}px`;
  };

  return (
    <div className="flex flex-col h-full bg-white relative">
      {/* Top Controls Bar */}
      <ModelSelector
        provider={provider}
        setProvider={setProvider}
        model={model}
        setModel={setModel}
        mode={mode}
        setMode={setMode}
        availableOllamaModels={availableOllamaModels}
      />

      {/* Message Feed */}
      <div className="flex-1 overflow-y-auto divide-y divide-gray-100">
        {messages.length === 0 && !isStreaming ? (
          <div className="max-w-2xl mx-auto px-4 py-12 text-center">
            <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto mb-4 shadow-sm">
              <Sparkles className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 tracking-tight">
              The Lenny Growth Assistant
            </h2>
            <p className="text-sm text-gray-500 mt-2 max-w-md mx-auto">
              Unlock tactical product and growth playbooks grounded in 300+ transcripts from top technology operators.
            </p>

            {/* Quick Starters Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mt-8 text-left">
              {STARTER_PROMPTS.map((prompt, idx) => {
                const IconComponent = prompt.icon;
                return (
                  <button
                    key={idx}
                    onClick={() => {
                      if (prompt.mode) setMode(prompt.mode);
                      onSendMessage(prompt.query);
                    }}
                    className="p-3 rounded-lg border border-gray-200 bg-white hover:border-emerald-500 hover:bg-emerald-50/30 transition text-left group shadow-xs"
                  >
                    <div className="flex items-center space-x-2 text-xs font-semibold text-gray-800 group-hover:text-emerald-700">
                      <IconComponent className="w-3.5 h-3.5 text-gray-400 group-hover:text-emerald-600" />
                      <span>{prompt.title}</span>
                    </div>
                    <p className="text-[11px] text-gray-500 mt-1 line-clamp-2">
                      {prompt.query}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>
        ) : (
          <div>
            {messages.map((msg) => (
              <MessageItem key={msg.id} message={msg} onOpenArtifact={onOpenArtifact} />
            ))}

            {/* Active Streaming Message */}
            {isStreaming && (
              <div className="py-4 px-4 md:px-6 bg-white">
                <div className="max-w-3xl mx-auto flex items-start space-x-3.5">
                  <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center text-xs font-semibold shadow-sm animate-pulse">
                    <Sparkles className="w-4 h-4" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1.5">
                      <span className="text-xs font-semibold text-gray-800">
                        Lenny Growth Assistant
                      </span>
                      {statusMessage && (
                        <span className="text-[11px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full animate-pulse">
                          {statusMessage}
                        </span>
                      )}
                    </div>

                    {/* Streaming markdown text with cursor */}
                    <div className="prose prose-slate max-w-none text-sm leading-relaxed text-gray-800">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {streamingContent}
                      </ReactMarkdown>
                      <span className="inline-block w-1.5 h-4 bg-emerald-600 ml-0.5 animate-bounce align-middle" />
                    </div>

                    {/* Citations Preview During Streaming */}
                    {streamingCitations.length > 0 && (
                      <div className="mt-2 text-xs text-gray-500">
                        Retrieving from {streamingCitations.length} episodes: {streamingCitations.map(s => s.guest).join(", ")}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Composer */}
      <div className="p-4 bg-white border-t border-gray-200">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative">
          <div className="relative flex items-end rounded-xl border border-gray-300 bg-white shadow-xs focus-within:border-emerald-600 focus-within:ring-1 focus-within:ring-emerald-600">
            <textarea
              ref={textareaRef}
              rows={1}
              value={inputText}
              onChange={handleTextareaChange}
              onKeyDown={handleKeyDown}
              placeholder={
                mode === "ship30"
                  ? "Prompt a Ship 30 for 30 essay topic (e.g. 'How to build high-performing growth teams')..."
                  : mode === "artifact"
                  ? "Describe the interactive artifact or tool to generate..."
                  : "Ask anything about product management, growth, retention, PLG..."
              }
              className="w-full resize-none bg-transparent py-3 pl-4 pr-12 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none max-h-48"
            />

            <div className="absolute right-2 bottom-2">
              {isStreaming ? (
                <button
                  type="button"
                  onClick={onCancelStream}
                  className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition"
                  title="Stop generation"
                >
                  <Square className="w-4 h-4 fill-current" />
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={!inputText.trim()}
                  className={`p-2 rounded-lg transition ${
                    inputText.trim()
                      ? "bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm"
                      : "text-gray-300 cursor-not-allowed"
                  }`}
                  title="Send prompt"
                >
                  <Send className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          <div className="flex items-center justify-between text-[11px] text-gray-400 mt-2 px-1">
            <span>Press Enter to send, Shift+Enter for new line</span>
            <span>Grounding threshold: &ge;0.55 similarity</span>
          </div>
        </form>
      </div>
    </div>
  );
};

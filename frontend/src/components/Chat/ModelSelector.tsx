"use client";

import React from "react";
import { Cpu, Cloud, Sparkles, BookOpen, Layers } from "lucide-react";

interface ModelSelectorProps {
  provider: string;
  setProvider: (p: string) => void;
  model: string;
  setModel: (m: string) => void;
  mode: string;
  setMode: (m: string) => void;
  availableOllamaModels?: string[];
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  provider,
  setProvider,
  model,
  setModel,
  mode,
  setMode,
  availableOllamaModels = ["llama3.1:8b", "llama3:latest", "llama3.2:1b"],
}) => {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 bg-white border-b border-gray-200 px-4 py-2.5 shadow-sm">
      {/* Provider & Model Dropdown */}
      <div className="flex items-center space-x-2">
        <div className="flex items-center space-x-1.5 bg-gray-100 rounded-lg p-1 border border-gray-200">
          <button
            onClick={() => {
              setProvider("ollama");
              if (!model || model.includes("gpt") || model.includes("claude")) {
                setModel(availableOllamaModels[0] || "llama3.1:8b");
              }
            }}
            className={`flex items-center space-x-1.5 text-xs font-medium px-2.5 py-1 rounded-md transition ${
              provider === "ollama"
                ? "bg-white text-emerald-800 shadow-sm border border-gray-200"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            <Cpu className="w-3.5 h-3.5 text-emerald-600" />
            <span>Local (Ollama)</span>
          </button>

          <button
            onClick={() => {
              setProvider("claude");
              setModel("claude-3-5-sonnet-20241022");
            }}
            className={`flex items-center space-x-1.5 text-xs font-medium px-2.5 py-1 rounded-md transition ${
              provider === "claude"
                ? "bg-white text-orange-800 shadow-sm border border-gray-200"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            <Cloud className="w-3.5 h-3.5 text-orange-500" />
            <span>Claude 3.5</span>
          </button>

          <button
            onClick={() => {
              setProvider("openai");
              setModel("gpt-4o");
            }}
            className={`flex items-center space-x-1.5 text-xs font-medium px-2.5 py-1 rounded-md transition ${
              provider === "openai"
                ? "bg-white text-blue-800 shadow-sm border border-gray-200"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-blue-500" />
            <span>OpenAI (GPT-4o)</span>
          </button>

          <button
            onClick={() => {
              setProvider("gemini");
              setModel("gemini-1.5-flash");
            }}
            className={`flex items-center space-x-1.5 text-xs font-medium px-2.5 py-1 rounded-md transition ${
              provider === "gemini"
                ? "bg-white text-indigo-800 shadow-sm border border-gray-200"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            <span>Gemini (Free)</span>
          </button>
        </div>

        {/* Ollama specific model select if provider is Ollama */}
        {provider === "ollama" && (
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="text-xs bg-white border border-gray-200 text-gray-700 rounded-md px-2 py-1 focus:outline-none focus:ring-1 focus:ring-emerald-500"
          >
            {availableOllamaModels.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Mode Selector Tabs */}
      <div className="flex items-center bg-gray-100 rounded-lg p-0.5 border border-gray-200">
        <button
          onClick={() => setMode("default")}
          className={`flex items-center space-x-1.5 text-xs font-medium px-3 py-1 rounded-md transition ${
            mode === "default"
              ? "bg-white text-gray-900 shadow-sm"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          <BookOpen className="w-3.5 h-3.5 text-blue-600" />
          <span>Grounded Q&A</span>
        </button>

        <button
          onClick={() => setMode("ship30")}
          className={`flex items-center space-x-1.5 text-xs font-medium px-3 py-1 rounded-md transition ${
            mode === "ship30"
              ? "bg-white text-purple-900 shadow-sm"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          <Sparkles className="w-3.5 h-3.5 text-purple-600" />
          <span>Ship 30 for 30 Essay</span>
        </button>

        <button
          onClick={() => setMode("artifact")}
          className={`flex items-center space-x-1.5 text-xs font-medium px-3 py-1 rounded-md transition ${
            mode === "artifact"
              ? "bg-white text-emerald-900 shadow-sm"
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          <Layers className="w-3.5 h-3.5 text-emerald-600" />
          <span>Interactive Artifact</span>
        </button>
      </div>
    </div>
  );
};

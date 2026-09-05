"use client";

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { User, Sparkles, ChevronDown, ChevronUp, ExternalLink, PackageOpen, AlertCircle } from "lucide-react";
import { Message, Citation, Artifact } from "@/lib/api";

interface MessageItemProps {
  message: Message;
  onOpenArtifact?: (artifact: Artifact) => void;
}

export const MessageItem: React.FC<MessageItemProps> = ({ message, onOpenArtifact }) => {
  const isUser = message.role === "user";
  const [showSources, setShowSources] = useState(false);

  const isRefusal = message.content.includes("I do not have sufficient information in Lenny's podcast archive");

  return (
    <div className={`py-4 px-4 md:px-6 transition ${isUser ? "bg-slate-50/50" : "bg-white"}`}>
      <div className="max-w-3xl mx-auto flex items-start space-x-3.5">
        {/* Avatar */}
        <div
          className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-xs font-semibold shadow-sm ${
            isUser
              ? "bg-slate-800 text-white"
              : "bg-emerald-600 text-white"
          }`}
        >
          {isUser ? <User className="w-4 h-4" /> : <Sparkles className="w-4 h-4" />}
        </div>

        {/* Content Container */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-1.5">
            <span className="text-xs font-semibold text-gray-800">
              {isUser ? "You" : "Lenny Growth Assistant"}
            </span>
            <span className="text-[11px] text-gray-400">
              {new Date(message.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </span>
          </div>

          {/* Out of domain refusal banner */}
          {isRefusal && (
            <div className="mb-3 p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-start space-x-2 text-amber-900 text-xs">
              <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold">Grounding Notice: </span>
                This assistant only answers queries directly supported by Lenny's Podcast transcripts.
              </div>
            </div>
          )}

          {/* Message Markdown Body */}
          <div className="prose prose-slate max-w-none text-sm leading-relaxed text-gray-800 break-words">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </div>

          {/* Rendered Artifacts Buttons */}
          {message.artifacts && message.artifacts.length > 0 && (
            <div className="mt-3.5 space-y-2">
              {message.artifacts.map((art, idx) => (
                <button
                  key={idx}
                  onClick={() => onOpenArtifact && onOpenArtifact(art)}
                  className="flex items-center justify-between w-full p-2.5 bg-blue-50/80 hover:bg-blue-100/80 border border-blue-200 rounded-lg text-left transition group shadow-xs"
                >
                  <div className="flex items-center space-x-2.5 truncate">
                    <PackageOpen className="w-4 h-4 text-blue-600 group-hover:scale-110 transition" />
                    <span className="text-xs font-semibold text-blue-950 truncate">
                      {art.title}
                    </span>
                    <span className="text-[10px] uppercase font-bold px-1.5 py-0.2 bg-blue-200/70 text-blue-800 rounded">
                      {art.artifact_type}
                    </span>
                  </div>
                  <span className="text-xs text-blue-600 font-medium flex items-center space-x-1">
                    <span>Open in Viewer</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </span>
                </button>
              ))}
            </div>
          )}

          {/* Sources / Citations Drawer */}
          {message.sources && message.sources.length > 0 && (
            <div className="mt-3 pt-2.5 border-t border-gray-100">
              <button
                onClick={() => setShowSources(!showSources)}
                className="flex items-center space-x-1.5 text-xs text-gray-500 hover:text-gray-700 font-medium transition"
              >
                <span>{message.sources.length} Grounded Source Citations</span>
                {showSources ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>

              {showSources && (
                <div className="mt-2.5 grid grid-cols-1 gap-2">
                  {message.sources.map((src: Citation, idx: number) => (
                    <div
                      key={idx}
                      className="p-2.5 bg-gray-50 border border-gray-200 rounded-md text-xs text-gray-700 space-y-1"
                    >
                      <div className="flex items-center justify-between font-medium">
                        <span className="text-emerald-700 truncate max-w-[70%]">
                          {src.guest}: {src.episode}
                        </span>
                        {src.timestamp && (
                          <span className="text-gray-500 bg-gray-200/70 px-1.5 py-0.5 rounded text-[10px]">
                            {src.timestamp}
                          </span>
                        )}
                      </div>
                      <p className="text-gray-600 text-[11px] line-clamp-2 italic">
                        "{src.snippet}"
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

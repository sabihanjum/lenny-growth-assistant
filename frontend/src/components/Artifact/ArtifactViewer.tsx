"use client";

import React, { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Copy, Check, Download, X, Code2, Eye, ExternalLink } from "lucide-react";
import { Artifact } from "@/lib/api";
import { SandboxedIframe } from "./SandboxedIframe";

interface ArtifactViewerProps {
  artifacts: Artifact[];
  activeArtifactIndex?: number;
  onSelectArtifact?: (index: number) => void;
  onClose: () => void;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({
  artifacts,
  activeArtifactIndex = 0,
  onSelectArtifact,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<"preview" | "code">("preview");
  const [copied, setCopied] = useState(false);

  if (!artifacts || artifacts.length === 0) {
    return null;
  }

  const currentArtifact = artifacts[activeArtifactIndex] || artifacts[0];

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(currentArtifact.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (e) {
      console.error("Failed to copy:", e);
    }
  };

  const handleDownload = () => {
    const ext = currentArtifact.artifact_type === "html" ? "html" : "md";
    const blob = new Blob([currentArtifact.content], {
      type: currentArtifact.artifact_type === "html" ? "text/html" : "text/markdown",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${currentArtifact.identifier || "artifact"}.${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col h-full bg-slate-50 border-l border-gray-200 shadow-lg">
      {/* Header Bar */}
      <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-2 truncate max-w-[60%]">
          <span className="font-semibold text-sm text-gray-800 truncate">
            {currentArtifact.title}
          </span>
          <span className="text-[11px] font-medium uppercase px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
            {currentArtifact.artifact_type}
          </span>
        </div>

        {/* Controls */}
        <div className="flex items-center space-x-2">
          {/* Tab Selector */}
          <div className="flex items-center bg-gray-100 rounded-lg p-0.5 border border-gray-200 text-xs">
            <button
              onClick={() => setActiveTab("preview")}
              className={`flex items-center space-x-1 px-2.5 py-1 rounded-md font-medium transition ${
                activeTab === "preview"
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Preview</span>
            </button>
            <button
              onClick={() => setActiveTab("code")}
              className={`flex items-center space-x-1 px-2.5 py-1 rounded-md font-medium transition ${
                activeTab === "code"
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              <Code2 className="w-3.5 h-3.5" />
              <span>Code</span>
            </button>
          </div>

          {/* Copy Button */}
          <button
            onClick={handleCopy}
            title="Copy code"
            className="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
          </button>

          {/* Download Button */}
          <button
            onClick={handleDownload}
            title="Download artifact"
            className="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition"
          >
            <Download className="w-4 h-4" />
          </button>

          {/* Close Drawer Button */}
          <button
            onClick={onClose}
            title="Close artifact viewer"
            className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Multi-Artifact Selector (if > 1) */}
      {artifacts.length > 1 && (
        <div className="bg-gray-100 border-b border-gray-200 px-4 py-1.5 flex items-center space-x-2 overflow-x-auto">
          <span className="text-xs font-medium text-gray-500">Artifacts:</span>
          {artifacts.map((art, idx) => (
            <button
              key={idx}
              onClick={() => onSelectArtifact && onSelectArtifact(idx)}
              className={`text-xs px-2.5 py-0.5 rounded-full border transition whitespace-nowrap ${
                idx === activeArtifactIndex
                  ? "bg-blue-600 text-white border-blue-600 font-medium"
                  : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
              }`}
            >
              {art.title}
            </button>
          ))}
        </div>
      )}

      {/* Main Canvas Area */}
      <div className="flex-1 overflow-auto p-4">
        {activeTab === "preview" ? (
          currentArtifact.artifact_type === "html" ? (
            <SandboxedIframe
              content={currentArtifact.content}
              title={currentArtifact.title}
            />
          ) : (
            <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm prose prose-slate max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {currentArtifact.content}
              </ReactMarkdown>
            </div>
          )
        ) : (
          <div className="bg-gray-900 text-gray-100 rounded-lg p-4 font-mono text-xs overflow-auto h-full border border-gray-800">
            <pre className="whitespace-pre-wrap">{currentArtifact.content}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

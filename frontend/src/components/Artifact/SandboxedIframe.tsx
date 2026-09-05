"use client";

import React, { useMemo } from "react";
import DOMPurify from "dompurify";

interface SandboxedIframeProps {
  content: string;
  title: string;
}

export const SandboxedIframe: React.FC<SandboxedIframeProps> = ({ content, title }) => {
  // Sanitize markup prior to injecting into iframe srcDoc
  const cleanHtml = useMemo(() => {
    // Only run DOMPurify in browser environment
    if (typeof window === "undefined") return content;
    return DOMPurify.sanitize(content, {
      WHOLE_DOCUMENT: true,
      ADD_TAGS: ["style", "link", "script"],
      ADD_ATTR: ["target"],
    });
  }, [content]);

  return (
    <div className="flex flex-col h-full w-full border border-gray-200 rounded-lg overflow-hidden bg-white shadow-sm">
      <div className="bg-gray-50 border-b border-gray-200 px-4 py-2 flex items-center justify-between">
        <span className="text-xs font-semibold text-gray-700 tracking-wide uppercase truncate max-w-[70%]">
          Artifact: {title}
        </span>
        <span className="text-xs text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-medium">
          Sandboxed Preview
        </span>
      </div>
      <iframe
        title={title}
        srcDoc={cleanHtml}
        // Strict security isolation: allow scripts to run for interactivity,
        // but omit allow-same-origin to prevent access to parent cookies, local storage, and DOM.
        sandbox="allow-scripts"
        className="w-full h-full border-none min-h-[500px]"
      />
    </div>
  );
};

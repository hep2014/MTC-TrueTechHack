import { useEffect, useMemo, useRef, useState } from "react";
import Prism from "prismjs";

import "prismjs/components/prism-clike";
import "prismjs/components/prism-lua";
import "prismjs/components/prism-json";
import "prismjs/components/prism-diff";

import "prismjs/themes/prism-tomorrow.css";
import "prismjs/plugins/diff-highlight/prism-diff-highlight";

import { copyText, downloadLuaFile } from "../../utils/file";

interface CodeViewerProps {
  title?: string;
  code: string;
  language?: "lua" | "json" | "text";
  fileName?: string;
}

function resolveLanguage(language: CodeViewerProps["language"]): string {
  if (language === "lua") return "lua";
  if (language === "json") return "json";
  return "clike";
}

export function CodeViewer({
  title = "Результат",
  code,
  language = "text",
  fileName,
}: CodeViewerProps) {
  const [copied, setCopied] = useState(false);
  const codeRef = useRef<HTMLElement | null>(null);

  const prismLanguage = useMemo(() => resolveLanguage(language), [language]);

  useEffect(() => {
    if (codeRef.current) {
      Prism.highlightElement(codeRef.current);
    }
  }, [code, prismLanguage]);

  async function handleCopy() {
    await copyText(code);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  }

  function handleDownload() {
    const inferredName =
      fileName ??
      (language === "json"
        ? "result.json"
        : language === "lua"
        ? "result.lua"
        : "result.txt");

    downloadLuaFile(code, inferredName);
  }

  return (
    <div className="code-viewer code-viewer--prism">
      <div className="code-viewer__top">
        <div className="code-viewer__title">{title}</div>
        <div className="code-viewer__actions">
          <button type="button" className="mini-button" onClick={handleCopy}>
            {copied ? "Скопировано" : "Скопировать"}
          </button>
          <button type="button" className="mini-button" onClick={handleDownload}>
            Скачать
          </button>
        </div>
      </div>

      <div className="code-viewer__body code-viewer__body--single">
        <pre className={`code-viewer__pre prism-pre language-${prismLanguage}`}>
          <code
            ref={codeRef}
            className={`language-${prismLanguage}`}
          >
            {code}
          </code>
        </pre>
      </div>
    </div>
  );
}
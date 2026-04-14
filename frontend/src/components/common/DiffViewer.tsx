import { useEffect, useMemo, useRef, useState } from "react";
import Prism from "prismjs";

import "prismjs/components/prism-clike";
import "prismjs/components/prism-lua";
import "prismjs/components/prism-json";
import "prismjs/components/prism-diff";

import "prismjs/themes/prism-tomorrow.css";
import "prismjs/plugins/diff-highlight/prism-diff-highlight";
import "prismjs/plugins/diff-highlight/prism-diff-highlight.css";

import { copyText, downloadLuaFile } from "../../utils/file";

interface DiffViewerProps {
  title?: string;
  diff: string;
  language?: "lua" | "json" | "text";
  fileName?: string;
}

function resolveDiffLanguage(language: DiffViewerProps["language"]): string {
  if (language === "lua") return "diff-lua";
  if (language === "json") return "diff-json";
  return "diff";
}

export function DiffViewer({
  title = "Diff",
  diff,
  language = "text",
  fileName = "changes.diff",
}: DiffViewerProps) {
  const [copied, setCopied] = useState(false);
  const codeRef = useRef<HTMLElement | null>(null);

  const prismLanguage = useMemo(() => resolveDiffLanguage(language), [language]);

  useEffect(() => {
    if (codeRef.current) {
      Prism.highlightElement(codeRef.current);
    }
  }, [diff, prismLanguage]);

  async function handleCopy() {
    await copyText(diff);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  }

  function handleDownload() {
    downloadLuaFile(diff, fileName);
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
        <pre className={`code-viewer__pre prism-pre diff-highlight language-${prismLanguage}`}>
          <code
            ref={codeRef}
            className={`language-${prismLanguage}`}
          >
            {diff}
          </code>
        </pre>
      </div>
    </div>
  );
}
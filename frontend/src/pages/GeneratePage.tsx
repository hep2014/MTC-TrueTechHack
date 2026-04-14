import { useState } from "react";
import { PageHeader } from "../components/common/PageHeader";
import { CodeViewer } from "../components/common/CodeViewer";
import { ToolResultCard } from "../components/common/ToolResultCard";
import { apiFetch } from "../api/client";
import type { ChatGenerateResponse } from "../types/chat";

type GenerateResponse = ChatGenerateResponse;

export function GeneratePage() {
  const [prompt, setPrompt] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [validateRuntime, setValidateRuntime] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate() {
    if (!prompt.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await apiFetch<GenerateResponse>("/generate", {
        method: "POST",
        body: JSON.stringify({
          prompt,
          session_id: sessionId.trim() || null,
          messages: [],
          validate_runtime: validateRuntime,
        }),
      });

      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось выполнить generate");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="tool-page">
      <PageHeader
        title="Генерация"
        subtitle="Разовая генерация Lua-кода"
      />

      <div className="tool-form">
        <label className="tool-form__field">
          <span>Prompt</span>
          <textarea
            className="chat-input"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Опиши задачу для генерации"
          />
        </label>

        <label className="tool-form__field">
          <span>Session ID (необязательно)</span>
          <input
            className="tool-input"
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            placeholder="session-id"
          />
        </label>

        <label className="tool-checkbox">
          <input
            type="checkbox"
            checked={validateRuntime}
            onChange={(e) => setValidateRuntime(e.target.checked)}
          />
          <span>Включить runtime validation</span>
        </label>

        <button type="button" className="send-button" onClick={handleGenerate} disabled={loading}>
          {loading ? "Генерация..." : "Generate"}
        </button>
      </div>

      {error && <div className="notice notice--error"><div className="notice__text">{error}</div></div>}

      {result && (
        <div className="tool-results">
          {result.code && (
            <CodeViewer title="Lua code" code={result.code} language="lua" fileName="generated.lua" />
          )}

          {result.wrapped_code && (
            <CodeViewer title="Wrapped code" code={result.wrapped_code} language="lua" fileName="wrapped.lua" />
          )}

          {result.json_output && (
            <CodeViewer title="JSON output" code={result.json_output} language="json" fileName="result.json" />
          )}

          <ToolResultCard title="Метаданные">
            <div className="tool-kv-grid">
              <div><strong>Status:</strong> {result.status}</div>
              <div><strong>Provider:</strong> {result.provider}</div>
              <div><strong>Model:</strong> {result.model}</div>
              <div><strong>Attempts:</strong> {result.attempts}</div>
              <div><strong>Confidence:</strong> {result.confidence.score}</div>
              <div><strong>Output mode:</strong> {result.output_mode}</div>
            </div>
          </ToolResultCard>
        </div>
      )}
    </div>
  );
}
import { useState } from "react";
import { evaluateLuaCode } from "../api/tools";
import { PageHeader } from "../components/common/PageHeader";
import { ToolResultCard } from "../components/common/ToolResultCard";
import type { EvaluateCodeResponse } from "../types/tools";

export function EvaluatePage() {
  const [code, setCode] = useState("");
  const [task, setTask] = useState("");
  const [validateRuntime, setValidateRuntime] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<EvaluateCodeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleEvaluate() {
    if (!code.trim() || !task.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await evaluateLuaCode({
        code,
        task,
        validate_runtime: validateRuntime,
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось выполнить evaluate");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="tool-page">
      <PageHeader
        title="Evaluate"
        subtitle="Инженерная оценка Lua-кода по задаче"
      />

      <div className="tool-form">
        <label className="tool-form__field">
          <span>Task</span>
          <textarea
            className="chat-input"
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="Опиши постановку задачи"
          />
        </label>

        <label className="tool-form__field">
          <span>Lua code</span>
          <textarea
            className="tool-textarea tool-textarea--code"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Вставь Lua-код"
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

        <button type="button" className="send-button" onClick={handleEvaluate} disabled={loading}>
          {loading ? "Оценка..." : "Evaluate"}
        </button>
      </div>

      {error && <div className="notice notice--error"><div className="notice__text">{error}</div></div>}

      {result && (
        <div className="tool-results">
          <ToolResultCard title="Confidence">
            <div className="tool-kv-grid">
              <div><strong>Score:</strong> {result.confidence.score}</div>
            </div>
            {result.confidence.reasons?.length > 0 && (
              <pre className="details-block__pre">{result.confidence.reasons.join("\n")}</pre>
            )}
          </ToolResultCard>

          <ToolResultCard title="Validation">
            <div className="tool-kv-grid">
              <div><strong>Итог:</strong> {result.validation.is_valid ? "валидно" : "невалидно"}</div>
              {Object.entries(result.validation.stage_results).map(([key, value]) => (
                <div key={key}>
                  <strong>{key}:</strong> {value ? "ok" : "fail"}
                </div>
              ))}
            </div>
          </ToolResultCard>

          <ToolResultCard title="Evaluation report">
            <div className="tool-kv-grid">
              <div><strong>Context:</strong> {result.evaluation_report.context_mode}</div>
              <div><strong>Profile:</strong> {result.evaluation_report.domain_profile}</div>
              <div><strong>Task type:</strong> {result.evaluation_report.task_type}</div>
              <div><strong>Subtype:</strong> {result.evaluation_report.task_subtype}</div>
              <div><strong>Output mode:</strong> {result.evaluation_report.output_mode}</div>
              <div><strong>Final status:</strong> {result.evaluation_report.final_status}</div>
            </div>
          </ToolResultCard>
        </div>
      )}
    </div>
  );
}
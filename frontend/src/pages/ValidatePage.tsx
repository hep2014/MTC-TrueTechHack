import { useState } from "react";
import { validateLuaCode } from "../api/tools";
import { PageHeader } from "../components/common/PageHeader";
import { ToolResultCard } from "../components/common/ToolResultCard";
import type { ValidateCodeResponse } from "../types/tools";

export function ValidatePage() {
  const [code, setCode] = useState("");
  const [task, setTask] = useState("");
  const [validateRuntime, setValidateRuntime] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ValidateCodeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleValidate() {
    if (!code.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await validateLuaCode({
        code,
        task,
        validate_runtime: validateRuntime,
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось выполнить validate");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="tool-page">
      <PageHeader
        title="Validate"
        subtitle="Ручная проверка Lua-кода"
      />

      <div className="tool-form">
        <label className="tool-form__field">
          <span>Lua code</span>
          <textarea
            className="tool-textarea tool-textarea--code"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Вставь Lua-код"
          />
        </label>

        <label className="tool-form__field">
          <span>Task (необязательно)</span>
          <textarea
            className="chat-input"
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="Постановка задачи для доменной проверки"
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

        <button type="button" className="send-button" onClick={handleValidate} disabled={loading}>
          {loading ? "Проверка..." : "Validate"}
        </button>
      </div>

      {error && <div className="notice notice--error"><div className="notice__text">{error}</div></div>}

      {result && (
        <ToolResultCard title="Результат проверки">
          <div className="tool-kv-grid">
            <div><strong>Итог:</strong> {result.is_valid ? "валидно" : "невалидно"}</div>
            {Object.entries(result.stage_results).map(([key, value]) => (
              <div key={key}>
                <strong>{key}:</strong> {value ? "ok" : "fail"}
              </div>
            ))}
          </div>

          {result.errors.length > 0 && (
            <pre className="details-block__pre">{result.errors.join("\n")}</pre>
          )}

          {result.warnings.length > 0 && (
            <pre className="details-block__pre">{result.warnings.join("\n")}</pre>
          )}
        </ToolResultCard>
      )}
    </div>
  );
}
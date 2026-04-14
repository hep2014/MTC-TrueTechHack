import type { PipelineRunDetailsResponse } from "../../types/chat";

interface RunDetailsProps {
  run: PipelineRunDetailsResponse | null;
  loading: boolean;
  error: string | null;
}

function safeJsonParse(value: string | null): unknown {
  if (!value) return null;

  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}

export function RunDetails({
  run,
  loading,
  error,
}: RunDetailsProps) {
  if (loading) {
    return <div className="runs-state">Загрузка деталей...</div>;
  }

  if (error) {
    return <div className="runs-state runs-state--error">{error}</div>;
  }

  if (!run) {
    return <div className="runs-state">Выбери запуск справа, чтобы посмотреть детали</div>;
  }

  const confidenceReasons = safeJsonParse(run.confidence_reasons_json);
  const taskContract = safeJsonParse(run.task_contract_json);
  const clarificationQuestions = safeJsonParse(run.clarification_questions_json);

  return (
    <div className="run-details">
      <div className="run-details__header">
        <div className="run-details__title">Run #{run.id}</div>
        <div className={`run-details__status run-details__status--${run.status}`}>
          {run.status}
        </div>
      </div>

      <div className="run-details__grid">
        <div><strong>provider:</strong> {run.provider || "—"}</div>
        <div><strong>model:</strong> {run.model || "—"}</div>
        <div><strong>attempts:</strong> {run.attempts}</div>
        <div><strong>confidence:</strong> {run.confidence_score ?? "—"}</div>
        <div><strong>repaired:</strong> {run.repaired ? "yes" : "no"}</div>
        <div><strong>used_history:</strong> {run.used_history ? "yes" : "no"}</div>
      </div>

      <details className="details-block" open>
        <summary className="details-block__summary">Исходный prompt</summary>
        <pre className="details-block__pre">{run.user_prompt}</pre>
      </details>

      {run.final_code && (
        <details className="details-block">
          <summary className="details-block__summary">Итоговый код</summary>
          <pre className="details-block__pre">{run.final_code}</pre>
        </details>
      )}

      <details className="details-block">
        <summary className="details-block__summary">Шаги pipeline</summary>
        <div className="details-block__content">
          {run.steps.map((step) => (
            <div key={step.id} className="pipeline-step">
              <div className="pipeline-step__main">
                <span className="pipeline-step__name">{step.step_name}</span>
                <span className="pipeline-step__status">{step.status}</span>
              </div>
              <div className="pipeline-step__meta">{step.duration_ms} ms</div>
              {step.details_json && (
                <pre className="details-block__pre">{step.details_json}</pre>
              )}
            </div>
          ))}
        </div>
      </details>

      {confidenceReasons && (
        <details className="details-block">
          <summary className="details-block__summary">Почему такой confidence</summary>
          <pre className="details-block__pre">
            {typeof confidenceReasons === "string"
              ? confidenceReasons
              : JSON.stringify(confidenceReasons, null, 2)}
          </pre>
        </details>
      )}

      {taskContract && (
        <details className="details-block">
          <summary className="details-block__summary">Task contract</summary>
          <pre className="details-block__pre">
            {typeof taskContract === "string"
              ? taskContract
              : JSON.stringify(taskContract, null, 2)}
          </pre>
        </details>
      )}

      {clarificationQuestions && (
        <details className="details-block">
          <summary className="details-block__summary">Clarification questions</summary>
          <pre className="details-block__pre">
            {typeof clarificationQuestions === "string"
              ? clarificationQuestions
              : JSON.stringify(clarificationQuestions, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
}
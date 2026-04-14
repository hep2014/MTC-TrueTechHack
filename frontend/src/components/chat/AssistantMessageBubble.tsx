import { useState } from "react";
import type { ChatGenerateResponse } from "../../types/chat";
import type { EvaluateCodeResponse, ValidateCodeResponse } from "../../types/tools";
import { evaluateLuaCode, validateLuaCode } from "../../api/tools";
import { mapValidation } from "../../utils/validation";
import { ConfidenceBar } from "./ConfidenceBar";
import { ResultTabs } from "./ResultTabs";
import { DiffViewer } from "../common/DiffViewer";


interface AssistantMessageBubbleProps {
  content: string;
  isStreaming?: boolean;
  statusText?: string;
  generated?: ChatGenerateResponse | null;
}

function TaskContractBlock({
  contract,
}: {
  contract: ChatGenerateResponse["task_contract"] | null | undefined;
}) {
  if (!contract) return null;

  return (
    <details className="details-block">
      <summary className="details-block__summary">Как система поняла задачу</summary>

      <div className="details-block__content">
        <div><strong>Цель:</strong> {contract.goal || "—"}</div>
        <div><strong>Тип:</strong> {contract.task_type || "—"}</div>
        <div><strong>Подтип:</strong> {contract.task_subtype || "—"}</div>
        <div><strong>Runtime:</strong> {contract.target_runtime || "—"}</div>

        {contract.inputs?.length > 0 && (
          <div><strong>Входы:</strong> {contract.inputs.join(", ")}</div>
        )}

        {contract.outputs?.length > 0 && (
          <div><strong>Выходы:</strong> {contract.outputs.join(", ")}</div>
        )}

        {contract.constraints?.length > 0 && (
          <div><strong>Ограничения:</strong> {contract.constraints.join(", ")}</div>
        )}

        {contract.assumptions?.length > 0 && (
          <div><strong>Допущения:</strong> {contract.assumptions.join(", ")}</div>
        )}

        {contract.output_mode && (
          <div><strong>Output mode:</strong> {contract.output_mode}</div>
        )}
      </div>
    </details>
  );
}

function PipelineStepsBlock({
  steps,
}: {
  steps: ChatGenerateResponse["pipeline_steps"] | undefined;
}) {
  if (!steps?.length) return null;

  return (
    <details className="details-block">
      <summary className="details-block__summary">Шаги пайплайна</summary>

      <div className="details-block__content">
        {steps.map((step, index) => {
          const stepName =
            typeof step?.name === "string"
              ? step.name
              : typeof step?.step_name === "string"
              ? step.step_name
              : `step_${index + 1}`;

          const stepStatus =
            typeof step?.status === "string" ? step.status : "unknown";

          const duration =
            typeof step?.duration_ms === "number"
              ? `${step.duration_ms} ms`
              : null;

          return (
            <div key={index} className="pipeline-step">
              <div className="pipeline-step__main">
                <span className="pipeline-step__name">{stepName}</span>
                <span className="pipeline-step__status">{stepStatus}</span>
              </div>
              {duration && <div className="pipeline-step__meta">{duration}</div>}
            </div>
          );
        })}
      </div>
    </details>
  );
}

function EvaluationBlock({
  report,
}: {
  report: ChatGenerateResponse["evaluation_report"] | null | undefined;
}) {
  if (!report) return null;

  return (
    <details className="details-block">
      <summary className="details-block__summary">Детали генерации</summary>

      <div className="details-block__content">
        <div><strong>Контекст:</strong> {report.context_mode || "—"}</div>
        <div><strong>Профиль:</strong> {report.domain_profile || "—"}</div>
        <div><strong>Тип задачи:</strong> {report.task_type || "—"}</div>
        <div><strong>Подтип:</strong> {report.task_subtype || "—"}</div>
        <div><strong>Output mode:</strong> {report.output_mode || "—"}</div>
        <div><strong>Попыток:</strong> {report.attempts ?? "—"}</div>
        <div><strong>Финальный статус:</strong> {report.final_status || "—"}</div>
        <div><strong>Провайдер:</strong> {report.provider || "—"}</div>
        <div><strong>Модель:</strong> {report.model || "—"}</div>

        {report.selected_templates?.length > 0 && (
          <div><strong>Шаблоны:</strong> {report.selected_templates.join(", ")}</div>
        )}
      </div>
    </details>
  );
}

function DiffBlock({ diff }: { diff?: string | null }) {
  if (!diff?.trim()) return null;

  return (
    <details className="details-block" open>
      <summary className="details-block__summary">Diff изменений</summary>
      <div className="details-block__content">
        <DiffViewer title="Изменения" diff={diff} language="lua" fileName="changes.diff" />
      </div>
    </details>
  );
}


function ValidationSummary({
  generated,
}: {
  generated: ChatGenerateResponse | null;
}) {
  const validationData = mapValidation(generated);
  if (!validationData) return null;

  return (
    <div className="validation-block">
      <div className="section-title validation-block__title">
        {validationData.isValid ? "Проверка пройдена" : "Результат требует внимания"}
      </div>

      <div className="validation-grid validation-grid--detailed">
        {validationData.items.map((item) => (
          <div
            key={item.key}
            className={`validation-card ${item.ok ? "validation-card--ok" : "validation-card--fail"}`}
          >
            <div className="validation-card__top">
              <div className="validation-card__label">{item.label}</div>
              <div
                className={`validation-card__badge ${
                  item.ok
                    ? "validation-card__badge--ok"
                    : "validation-card__badge--fail"
                }`}
              >
                {item.ok ? "OK" : "Ошибка"}
              </div>
            </div>

            <div className="validation-card__status">
              {item.ok ? "Проверка пройдена" : "Проверка не пройдена"}
            </div>

            <div className="validation-card__description">
              {item.description}
            </div>
          </div>
        ))}
      </div>

      {validationData.errors.length > 0 && (
        <div className="notice notice--error">
          <div className="section-title">Что именно не прошло</div>
          <div className="notice__text">{validationData.errors.join("\n")}</div>
        </div>
      )}

      {validationData.warnings.length > 0 && (
        <div className="notice notice--warn">
          <div className="section-title">На что стоит обратить внимание</div>
          <div className="notice__text">{validationData.warnings.join("\n")}</div>
        </div>
      )}
    </div>
  );
}

function UtilityResultBlock({
  validateResult,
  evaluateResult,
}: {
  validateResult: ValidateCodeResponse | null;
  evaluateResult: EvaluateCodeResponse | null;
}) {
  if (!validateResult && !evaluateResult) return null;

  return (
    <div className="utility-result-block">
      {validateResult && (
        <details className="details-block" open>
          <summary className="details-block__summary">Проверка через /validate</summary>
          <div className="details-block__content">
            <div>
              <strong>Итог:</strong> {validateResult.is_valid ? "код прошёл проверку" : "код не прошёл проверку"}
            </div>
            <div>
              <strong>Этапы:</strong> {Object.entries(validateResult.stage_results)
                .map(([k, v]) => `${k}: ${v ? "ok" : "fail"}`)
                .join(" · ")}
            </div>

            {validateResult.errors.length > 0 && (
              <pre className="details-block__pre">{validateResult.errors.join("\n")}</pre>
            )}

            {validateResult.warnings.length > 0 && (
              <pre className="details-block__pre">{validateResult.warnings.join("\n")}</pre>
            )}
          </div>
        </details>
      )}

      {evaluateResult && (
        <details className="details-block" open>
          <summary className="details-block__summary">Оценка через /evaluate</summary>
          <div className="details-block__content">
            <div><strong>Confidence:</strong> {evaluateResult.confidence.score}</div>
            <div><strong>Финальный статус:</strong> {evaluateResult.evaluation_report.final_status}</div>
            <div><strong>Профиль:</strong> {evaluateResult.evaluation_report.domain_profile}</div>

            {evaluateResult.confidence.reasons?.length > 0 && (
              <pre className="details-block__pre">
                {evaluateResult.confidence.reasons.join("\n")}
              </pre>
            )}
          </div>
        </details>
      )}
    </div>
  );
}

export function AssistantMessageBubble({
  content,
  isStreaming = false,
  statusText,
  generated,
}: AssistantMessageBubbleProps) {
  const [validateLoading, setValidateLoading] = useState(false);
  const [evaluateLoading, setEvaluateLoading] = useState(false);
  const [validateResult, setValidateResult] = useState<ValidateCodeResponse | null>(null);
  const [evaluateResult, setEvaluateResult] = useState<EvaluateCodeResponse | null>(null);
  const [utilityError, setUtilityError] = useState<string | null>(null);

  const hasCode = Boolean(generated?.code?.trim());
  const hasClarification = generated?.status === "needs_clarification";

  async function handleValidate() {
    if (!generated?.code?.trim()) return;

    setValidateLoading(true);
    setUtilityError(null);

    try {
      const result = await validateLuaCode({
        code: generated.code,
        task: generated.task_contract?.goal || "",
        validate_runtime: true,
      });
      setValidateResult(result);
    } catch (err) {
      setUtilityError(err instanceof Error ? err.message : "Не удалось выполнить validate");
    } finally {
      setValidateLoading(false);
    }
  }

  async function handleEvaluate() {
    if (!generated?.code?.trim()) return;

    setEvaluateLoading(true);
    setUtilityError(null);

    try {
      const result = await evaluateLuaCode({
        code: generated.code,
        task: generated.task_contract?.goal || generated.code,
        validate_runtime: true,
      });
      setEvaluateResult(result);
    } catch (err) {
      setUtilityError(err instanceof Error ? err.message : "Не удалось выполнить evaluate");
    } finally {
      setEvaluateLoading(false);
    }
  }

  return (
    <div className="message-row message-row--assistant">
      <div className="message-bubble message-bubble--assistant">
        <div className="message-role">Модель</div>

        {isStreaming && (
          <div className="assistant-status">
            <span className="assistant-status__dot" />
            {statusText || "Думаю..."}
          </div>
        )}

        {!generated && <div className="message-content">{content}</div>}

        {generated && (
          <>
            <div className="status-badges">
              <span className={`status-badge status-badge--${generated.status}`}>
                {generated.status}
              </span>

              <span className="meta-chip">
                {generated.provider || "unknown"} / {generated.model || "unknown"}
              </span>

              <span className="meta-chip">attempts: {generated.attempts}</span>
              <span className="meta-chip">repair: {generated.repaired ? "yes" : "no"}</span>
              <span className="meta-chip">history: {generated.used_history ? "yes" : "no"}</span>
              <span className="meta-chip">mode: {generated.output_mode}</span>

              {generated.resumed_from_clarification && (
                <span className="meta-chip meta-chip--accent">clarification</span>
              )}

              {generated.resumed_from_refinement && (
                <span className="meta-chip meta-chip--accent">refinement</span>
              )}
            </div>

            <ConfidenceBar score={generated.confidence.score} />

            <ResultTabs generated={generated} />

            {hasCode && (
              <div className="code-actions">
                <button
                  type="button"
                  className="mini-button"
                  onClick={handleValidate}
                  disabled={validateLoading}
                >
                  {validateLoading ? "Проверяю..." : "Проверить код"}
                </button>

                <button
                  type="button"
                  className="mini-button"
                  onClick={handleEvaluate}
                  disabled={evaluateLoading}
                >
                  {evaluateLoading ? "Оцениваю..." : "Оценить код"}
                </button>
              </div>
            )}

            {utilityError && (
              <div className="notice notice--error">
                <div className="notice__text">{utilityError}</div>
              </div>
            )}

            <UtilityResultBlock
              validateResult={validateResult}
              evaluateResult={evaluateResult}
            />

            <ValidationSummary generated={generated} />

            {hasClarification && generated.clarification_questions.length > 0 && (
              <div className="notice notice--info">
                <div className="section-title">Нужно уточнение</div>
                <div className="notice__text">
                  {generated.clarification_questions
                    .map((item) => `• ${item.question}`)
                    .join("\n")}
                </div>
              </div>
            )}

            <TaskContractBlock contract={generated.task_contract} />
            <PipelineStepsBlock steps={generated.pipeline_steps} />
            <EvaluationBlock report={generated.evaluation_report} />
            <DiffBlock diff={generated.diff_text} />
          </>
        )}
      </div>
    </div>
  );
}
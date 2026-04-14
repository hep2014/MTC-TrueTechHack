import type { ModelCheckResponse } from "../../types/tools";

interface ModelStatusBarProps {
  status: ModelCheckResponse | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
}

export function ModelStatusBar({
  status,
  loading,
  error,
  onRefresh,
}: ModelStatusBarProps) {
  const isOk = Boolean(status?.ok) && !error;

  return (
    <div className="model-status-bar">
      <div className="model-status-bar__left">
        <span
          className={`model-status-bar__dot ${
            isOk ? "model-status-bar__dot--ok" : "model-status-bar__dot--fail"
          }`}
        />
        <div className="model-status-bar__text">
          <div className="model-status-bar__title">
            {loading
              ? "Проверяю модель..."
              : isOk
              ? "Модель доступна"
              : "Модель недоступна"}
          </div>

          <div className="model-status-bar__meta">
            {error
              ? error
              : status
              ? `${status.provider} / ${status.model}`
              : "Нет данных"}
          </div>
        </div>
      </div>

      <button type="button" className="mini-button" onClick={onRefresh}>
        Обновить
      </button>
    </div>
  );
}
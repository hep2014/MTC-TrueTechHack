import type { PipelineRunListItemResponse } from "../../types/chat";

interface RunsListProps {
  runs: PipelineRunListItemResponse[];
  selectedRunId: number | null;
  onSelect: (runId: number) => void;
  loading: boolean;
  error: string | null;
}

function formatRunTitle(run: PipelineRunListItemResponse): string {
  return `Run #${run.id}`;
}

export function RunsList({
  runs,
  selectedRunId,
  onSelect,
  loading,
  error,
}: RunsListProps) {
  if (loading) {
    return <div className="runs-state">Загрузка запусков...</div>;
  }

  if (error) {
    return <div className="runs-state runs-state--error">{error}</div>;
  }

  if (runs.length === 0) {
    return <div className="runs-state">Для этой сессии запусков пока нет</div>;
  }

  return (
    <div className="runs-list">
      {runs.map((run) => {
        const isActive = run.id === selectedRunId;

        return (
          <button
            key={run.id}
            type="button"
            className={`run-item ${isActive ? "run-item--active" : ""}`}
            onClick={() => onSelect(run.id)}
          >
            <div className="run-item__top">
              <span className="run-item__title">{formatRunTitle(run)}</span>
              <span className={`run-item__status run-item__status--${run.status}`}>
                {run.status}
              </span>
            </div>

            <div className="run-item__meta">
              confidence: {run.confidence_score ?? "—"}
            </div>
            <div className="run-item__meta">
              attempts: {run.attempts} · repair: {run.repaired ? "yes" : "no"}
            </div>
          </button>
        );
      })}
    </div>
  );
}
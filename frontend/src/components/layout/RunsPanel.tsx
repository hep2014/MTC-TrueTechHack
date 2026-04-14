import { RunDetails } from "../runs/RunDetails";
import { RunsList } from "../runs/RunList";
import type {
  PipelineRunDetailsResponse,
  PipelineRunListItemResponse,
} from "../../types/chat";

interface RunsPanelProps {
  runs: PipelineRunListItemResponse[];
  selectedRunId: number | null;
  selectedRun: PipelineRunDetailsResponse | null;
  onSelectRun: (runId: number) => void;
  runsLoading: boolean;
  runDetailsLoading: boolean;
  runsError: string | null;
  runDetailsError: string | null;
}

export function RunsPanel({
  runs,
  selectedRunId,
  selectedRun,
  onSelectRun,
  runsLoading,
  runDetailsLoading,
  runsError,
  runDetailsError,
}: RunsPanelProps) {
  return (
    <aside className="runs-panel">
      <div className="runs-panel__section">
        <div className="runs-panel__title">Запуски</div>
        <RunsList
          runs={runs}
          selectedRunId={selectedRunId}
          onSelect={onSelectRun}
          loading={runsLoading}
          error={runsError}
        />
      </div>

      <div className="runs-panel__section runs-panel__section--details">
        <div className="runs-panel__title">Детали</div>
        <RunDetails
          run={selectedRun}
          loading={runDetailsLoading}
          error={runDetailsError}
        />
      </div>
    </aside>
  );
}
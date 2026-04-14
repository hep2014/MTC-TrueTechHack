import { useEffect, useState } from "react";
import { fetchRunDetails, fetchRunsBySession } from "../api/runs";
import type {
  PipelineRunDetailsResponse,
  PipelineRunListItemResponse,
} from "../types/chat";

export function useRunsData(activeSessionId: string | null) {
  const [runs, setRuns] = useState<PipelineRunListItemResponse[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null);
  const [selectedRun, setSelectedRun] = useState<PipelineRunDetailsResponse | null>(null);

  const [runsLoading, setRunsLoading] = useState(false);
  const [runDetailsLoading, setRunDetailsLoading] = useState(false);

  const [runsError, setRunsError] = useState<string | null>(null);
  const [runDetailsError, setRunDetailsError] = useState<string | null>(null);

  useEffect(() => {
    if (!activeSessionId) {
      setRuns([]);
      setSelectedRunId(null);
      setSelectedRun(null);
      return;
    }

    let cancelled = false;

    async function loadRuns() {
      setRunsLoading(true);
      setRunsError(null);

      try {
        const data = await fetchRunsBySession(activeSessionId);
        if (cancelled) return;

        setRuns(data);
        setSelectedRunId((prev) => prev ?? data[0]?.id ?? null);
      } catch (error) {
        if (cancelled) return;
        setRunsError(
          error instanceof Error ? error.message : "Не удалось загрузить список запусков",
        );
      } finally {
        if (!cancelled) {
          setRunsLoading(false);
        }
      }
    }

    loadRuns();

    return () => {
      cancelled = true;
    };
  }, [activeSessionId]);

  useEffect(() => {
    if (!selectedRunId) {
      setSelectedRun(null);
      return;
    }

    let cancelled = false;

    async function loadRunDetails() {
      setRunDetailsLoading(true);
      setRunDetailsError(null);

      try {
        const data = await fetchRunDetails(selectedRunId);
        if (cancelled) return;
        setSelectedRun(data);
      } catch (error) {
        if (cancelled) return;
        setRunDetailsError(
          error instanceof Error ? error.message : "Не удалось загрузить детали запуска",
        );
      } finally {
        if (!cancelled) {
          setRunDetailsLoading(false);
        }
      }
    }

    loadRunDetails();

    return () => {
      cancelled = true;
    };
  }, [selectedRunId]);

  async function refreshRuns(sessionId: string | null) {
    if (!sessionId) return;

    try {
      setRunsError(null);

      const data = await fetchRunsBySession(sessionId);
      setRuns(data);

      const latestRunId = data[0]?.id ?? null;
      setSelectedRunId(latestRunId);

      if (latestRunId) {
        setRunDetailsLoading(true);
        setRunDetailsError(null);

        try {
          const details = await fetchRunDetails(latestRunId);
          setSelectedRun(details);
        } catch (error) {
          setRunDetailsError(
            error instanceof Error ? error.message : "Не удалось загрузить детали запуска",
          );
        } finally {
          setRunDetailsLoading(false);
        }
      } else {
        setSelectedRun(null);
      }
    } catch (error) {
      setRunsError(
        error instanceof Error ? error.message : "Не удалось обновить список запусков",
      );
    }
  }

  return {
    runs,
    selectedRunId,
    selectedRun,
    setSelectedRunId,
    runsLoading,
    runDetailsLoading,
    runsError,
    runDetailsError,
    refreshRuns,
  };
}
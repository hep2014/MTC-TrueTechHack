import { useEffect, useState } from "react";
import { checkModel } from "../api/model";
import type { ModelCheckResponse } from "../types/tools";

export function useModelStatus() {
  const [status, setStatus] = useState<ModelCheckResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setLoading(true);
    setError(null);

    try {
      const data = await checkModel("ping");
      setStatus(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось проверить модель");
      setStatus(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  return {
    status,
    loading,
    error,
    refresh,
  };
}
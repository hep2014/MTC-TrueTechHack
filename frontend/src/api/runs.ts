import { apiFetch } from "./client";
import type {
  PipelineRunDetailsResponse,
  PipelineRunListItemResponse,
} from "../types/chat";

export function fetchRunsBySession(
  sessionId: string,
): Promise<PipelineRunListItemResponse[]> {
  return apiFetch<PipelineRunListItemResponse[]>(
    `/chat/sessions/${sessionId}/runs`,
  );
}

export function fetchRunDetails(
  runId: number,
): Promise<PipelineRunDetailsResponse> {
  return apiFetch<PipelineRunDetailsResponse>(`/runs/${runId}`);
}
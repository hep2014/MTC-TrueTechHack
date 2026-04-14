import { apiFetch } from "./client";
import type {
  ChatGenerateResponse,
  ChatHistoryResponse,
  ChatSessionResponse,
} from "../types/chat";

export function fetchSessions(): Promise<ChatSessionResponse[]> {
  return apiFetch<ChatSessionResponse[]>("/chat/sessions");
}

export function fetchSessionHistory(sessionId: string): Promise<ChatHistoryResponse> {
  return apiFetch<ChatHistoryResponse>(`/chat/sessions/${sessionId}/history`);
}

export function sendChatMessage(payload: {
  session_id: string;
  message: string;
  title?: string | null;
  validate_runtime?: boolean;
}): Promise<ChatGenerateResponse> {
  return apiFetch<ChatGenerateResponse>("/chat/message", {
    method: "POST",
    body: JSON.stringify({
      session_id: payload.session_id,
      message: payload.message,
      title: payload.title ?? null,
      validate_runtime: payload.validate_runtime ?? true,
    }),
  });
}
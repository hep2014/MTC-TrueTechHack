import type {
  ChatGenerateResponse,
  ChatHistoryResponse,
  ChatMessageResponse,
  UiMessage,
} from "../types/chat";

export function generateSessionId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }

  return `session-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function isRenderableMessage(
  msg: ChatMessageResponse,
): msg is ChatMessageResponse & { role: "user" | "assistant" } {
  return msg.role === "user" || msg.role === "assistant";
}

export function historyToUiMessages(history: ChatHistoryResponse | null): UiMessage[] {
  if (!history) return [];

  return history.messages
    .filter(isRenderableMessage)
    .map((msg) => ({
      id: `history-${msg.id}`,
      role: msg.role,
      content: msg.content,
      isStreaming: false,
      generated: null,
    }));
}

export function buildAssistantDisplayText(result: ChatGenerateResponse): string {
  if (result.status === "needs_clarification") {
    const questions = result.clarification_questions
      .map((item) => `• ${item.question}`)
      .join("\n");

    return `Нужно уточнить несколько моментов перед генерацией Lua-кода.\n\n${questions}`;
  }

  if (result.code?.trim()) {
    return result.code.trim();
  }

  if (result.json_output?.trim()) {
    return result.json_output.trim();
  }

  if (result.wrapped_code?.trim()) {
    return result.wrapped_code.trim();
  }

  return "Ответ получен, но текст для отображения пуст.";
}
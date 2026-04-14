import { useEffect, useMemo, useRef, useState } from "react";
import { fetchSessionHistory, fetchSessions, sendChatMessage } from "../api/chat";
import type {
  ChatHistoryResponse,
  ChatSessionResponse,
  ChatGenerateResponse,
  UiMessage,
} from "../types/chat";
import {
  buildAssistantDisplayText,
  generateSessionId,
  historyToUiMessages,
} from "../utils/chat";

const STREAM_DELAY_MS = 8;

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function mergeHistoryWithLatestAssistant(
  freshHistory: ChatHistoryResponse,
  latestGenerated: ChatGenerateResponse | null,
): UiMessage[] {
  const base = historyToUiMessages(freshHistory);

  if (!latestGenerated) {
    return base;
  }

  const hasAssistantInHistory = freshHistory.messages.some(
    (msg) => msg.role === "assistant" && msg.content.trim().length > 0,
  );

  if (hasAssistantInHistory) {
    let attached = false;
    return base.map((msg) => {
      if (!attached && msg.role === "assistant") {
        attached = true;
        return {
          ...msg,
          generated: latestGenerated,
        };
      }
      return msg;
    });
  }

  const displayText = buildAssistantDisplayText(latestGenerated);

  return [
    ...base,
    {
      id: `assistant-fallback-${Date.now()}`,
      role: "assistant",
      content: displayText,
      isStreaming: false,
      generated: latestGenerated,
    },
  ];
}

export function useChatData() {
  const [sessions, setSessions] = useState<ChatSessionResponse[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [history, setHistory] = useState<ChatHistoryResponse | null>(null);
  const [uiMessages, setUiMessages] = useState<UiMessage[]>([]);

  const [sessionsLoading, setSessionsLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [sending, setSending] = useState(false);

  const [sessionsError, setSessionsError] = useState<string | null>(null);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [sendError, setSendError] = useState<string | null>(null);

  const currentStreamIdRef = useRef<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadSessions() {
      setSessionsLoading(true);
      setSessionsError(null);

      try {
        const data = await fetchSessions();
        if (cancelled) return;

        setSessions(data);
        if (data.length > 0) {
          setActiveSessionId((prev) => prev ?? data[0].session_id);
        }
      } catch (error) {
        if (cancelled) return;
        setSessionsError(error instanceof Error ? error.message : "Не удалось загрузить сессии");
      } finally {
        if (!cancelled) {
          setSessionsLoading(false);
        }
      }
    }

    loadSessions();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!activeSessionId) {
      setHistory(null);
      setUiMessages([]);
      return;
    }

    let cancelled = false;

    async function loadHistory() {
      setHistoryLoading(true);
      setHistoryError(null);

      try {
        const data = await fetchSessionHistory(activeSessionId);
        if (cancelled) return;
        setHistory(data);
        setUiMessages(historyToUiMessages(data));
      } catch (error) {
        if (cancelled) return;
        setHistoryError(error instanceof Error ? error.message : "Не удалось загрузить историю");
      } finally {
        if (!cancelled) {
          setHistoryLoading(false);
        }
      }
    }

    loadHistory();

    return () => {
      cancelled = true;
    };
  }, [activeSessionId]);

  async function refreshSessionsAndPreserve(sessionId: string) {
    try {
      const data = await fetchSessions();
      setSessions(data);
      setActiveSessionId(sessionId);
    } catch {
      // intentionally ignored
    }
  }

  async function streamAssistantMessage(
    messageId: string,
    fullText: string,
    generated: UiMessage["generated"],
  ) {
    currentStreamIdRef.current = messageId;

    setUiMessages((prev) =>
      prev.map((msg) =>
        msg.id === messageId
          ? {
              ...msg,
              content: "",
              isStreaming: true,
              statusText: "Печатаю ответ...",
              generated: null,
            }
          : msg,
      ),
    );

    let current = "";

    for (const char of fullText) {
      if (currentStreamIdRef.current !== messageId) {
        return;
      }

      current += char;

      setUiMessages((prev) =>
        prev.map((msg) =>
          msg.id === messageId
            ? {
                ...msg,
                content: current,
                isStreaming: true,
                statusText: "Печатаю ответ...",
              }
            : msg,
        ),
      );

      await sleep(STREAM_DELAY_MS);
    }

    setUiMessages((prev) =>
      prev.map((msg) =>
        msg.id === messageId
          ? {
              ...msg,
              content: fullText,
              isStreaming: false,
              statusText: undefined,
              generated: generated ?? null,
            }
          : msg,
      ),
    );
  }

  async function sendMessage(messageText: string) {
    const trimmed = messageText.trim();
    if (!trimmed || sending) return;

    setSendError(null);
    setHistoryError(null);

    let sessionId = activeSessionId;
    let createdNewSession = false;

    if (!sessionId) {
      sessionId = generateSessionId();
      createdNewSession = true;
      setActiveSessionId(sessionId);
      setHistory({ session_id: sessionId, messages: [] });
      setSessions((prev) => [
        {
          id: -Date.now(),
          session_id: sessionId,
          title: trimmed.slice(0, 48),
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        ...prev,
      ]);
    }

    const userMessageId = `user-${Date.now()}`;
    const assistantMessageId = `assistant-${Date.now() + 1}`;

    const userUiMessage: UiMessage = {
      id: userMessageId,
      role: "user",
      content: trimmed,
      isStreaming: false,
      generated: null,
    };

    const pendingAssistantMessage: UiMessage = {
      id: assistantMessageId,
      role: "assistant",
      content: "",
      isStreaming: true,
      statusText: "Генерируется код...",
      generated: null,
    };

    setUiMessages((prev) => [...prev, userUiMessage, pendingAssistantMessage]);
    setSending(true);

    try {
      const result = await sendChatMessage({
        session_id: sessionId,
        message: trimmed,
        title: createdNewSession ? trimmed.slice(0, 64) : null,
        validate_runtime: true,
      });

      await refreshSessionsAndPreserve(result.session_id);

      const displayText = buildAssistantDisplayText(result);
      await streamAssistantMessage(assistantMessageId, displayText, result);

      const freshHistory = await fetchSessionHistory(result.session_id);
      setHistory(freshHistory);
      setUiMessages(mergeHistoryWithLatestAssistant(freshHistory, result));
    } catch (error) {
      setSendError(error instanceof Error ? error.message : "Не удалось отправить сообщение");

      setUiMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                content: "Ошибка при обращении к backend.",
                isStreaming: false,
                statusText: undefined,
                generated: null,
              }
            : msg,
        ),
      );
    } finally {
      setSending(false);
    }
  }

  function createNewSession() {
    setActiveSessionId(null);
    setHistory(null);
    setUiMessages([]);
    setHistoryError(null);
    setSendError(null);
  }

  const combinedHistoryError = useMemo(() => {
    return sendError ?? historyError;
  }, [sendError, historyError]);

  return {
    sessions,
    activeSessionId,
    setActiveSessionId,
    history,
    uiMessages,
    sessionsLoading,
    historyLoading,
    sending,
    sessionsError,
    historyError: combinedHistoryError,
    sendMessage,
    createNewSession,
  };
}

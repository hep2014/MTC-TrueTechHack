import type { UiMessage } from "../../types/chat";
import type { ModelCheckResponse } from "../../types/tools";
import { MessageComposer } from "../chat/MessageComposer";
import { MessageList } from "../chat/MessageList";
import { ModelStatusBar } from "./ModelStatusBar";

interface ChatPanelProps {
  messages: UiMessage[];
  loading: boolean;
  error: string | null;
  sending: boolean;
  onSend: (message: string) => Promise<void> | void;

  modelStatus: ModelCheckResponse | null;
  modelLoading: boolean;
  modelError: string | null;
  onRefreshModel: () => void;
}

export function ChatPanel({
  messages,
  loading,
  error,
  sending,
  onSend,
  modelStatus,
  modelLoading,
  modelError,
  onRefreshModel,
}: ChatPanelProps) {
  return (
    <main className="chat-panel">
      <div className="chat-panel__header">
        <div>
          <div className="chat-panel__title">Рабочая область</div>
          <div className="chat-panel__subtitle">
            Генерация, валидация и доработка Lua-кода
          </div>
        </div>
      </div>

      <div className="chat-panel__status">
        <ModelStatusBar
          status={modelStatus}
          loading={modelLoading}
          error={modelError}
          onRefresh={onRefreshModel}
        />
      </div>

      <div className="chat-panel__body">
        <MessageList messages={messages} loading={loading} error={error} />
      </div>

      <div className="chat-panel__composer">
        <MessageComposer onSend={onSend} disabled={sending} />
      </div>
    </main>
  );
}
import { useRef } from "react";
import type { UiMessage } from "../../types/chat";
import { useAutoScroll } from "../../hooks/useAutoScroll";
import { AssistantMessageBubble } from "./AssistantMessageBubble";
import { UserMessageBubble } from "./UserMessageBubble";

interface MessageListProps {
  messages: UiMessage[];
  loading: boolean;
  error: string | null;
}

export function MessageList({ messages, loading, error }: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useAutoScroll(scrollRef, [
    messages.length,
    messages.map((m) => `${m.id}:${m.content.length}:${m.isStreaming ? 1 : 0}`).join("|"),
  ]);

  if (loading) {
    return <div className="chat-state">Загрузка истории...</div>;
  }

  if (error && messages.length === 0) {
    return <div className="chat-state chat-state--error">{error}</div>;
  }

  if (messages.length === 0) {
    return (
      <div className="chat-empty">
        <div className="chat-empty__title">Новый диалог</div>
        <div className="chat-empty__text">
          Отправь задачу, и локальный агент начнёт генерацию Lua-кода
        </div>
      </div>
    );
  }

  return (
    <div ref={scrollRef} className="message-list message-list--scrollable">
      {messages.map((message) => {
        if (message.role === "user") {
          return <UserMessageBubble key={message.id} content={message.content} />;
        }

        return (
          <AssistantMessageBubble
            key={message.id}
            content={message.content}
            isStreaming={message.isStreaming}
            statusText={message.statusText}
            generated={message.generated}
          />
        );
      })}
    </div>
  );
}
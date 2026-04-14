import { useState } from "react";

interface MessageComposerProps {
  onSend: (message: string) => Promise<void> | void;
  disabled?: boolean;
}

export function MessageComposer({
  onSend,
  disabled = false,
}: MessageComposerProps) {
  const [value, setValue] = useState("");

  async function handleSend() {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;

    setValue("");
    await onSend(trimmed);
  }

  async function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      await handleSend();
    }
  }

  return (
    <>
      <textarea
        className="chat-input"
        placeholder="Опиши задачу для Lua-агента..."
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
      />
      <button
        className="send-button"
        onClick={handleSend}
        disabled={disabled || !value.trim()}
      >
        {disabled ? "Обработка..." : "Отправить"}
      </button>
    </>
  );
}
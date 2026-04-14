interface UserMessageBubbleProps {
  content: string;
}

export function UserMessageBubble({ content }: UserMessageBubbleProps) {
  return (
    <div className="message-row message-row--user">
      <div className="message-bubble message-bubble--user">
        <div className="message-role">Вы</div>
        <div className="message-content">{content}</div>
      </div>
    </div>
  );
}
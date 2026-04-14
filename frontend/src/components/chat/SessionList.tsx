import type { ChatSessionResponse } from "../../types/chat";

interface SessionListProps {
  sessions: ChatSessionResponse[];
  activeSessionId: string | null;
  onSelect: (sessionId: string) => void;
  loading: boolean;
  error: string | null;
}

export function SessionList({
  sessions,
  activeSessionId,
  onSelect,
  loading,
  error,
}: SessionListProps) {
  if (loading) {
    return <div className="sidebar-state">Загрузка чатов...</div>;
  }

  if (error) {
    return <div className="sidebar-state sidebar-state--error">{error}</div>;
  }

  if (sessions.length === 0) {
    return <div className="sidebar-state">Сессий пока нет</div>;
  }

  return (
    <div className="session-list">
      {sessions.map((session) => {
        const isActive = session.session_id === activeSessionId;

        return (
          <button
            key={session.session_id}
            type="button"
            className={`session-item ${isActive ? "session-item--active" : ""}`}
            onClick={() => onSelect(session.session_id)}
          >
            <div className="session-item__title">
              {session.title?.trim() || session.session_id}
            </div>
            <div className="session-item__meta">{session.session_id}</div>
          </button>
        );
      })}
    </div>
  );
}
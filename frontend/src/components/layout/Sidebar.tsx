import { NavLink } from "react-router-dom";
import { SessionList } from "../chat/SessionList";
import type { ChatSessionResponse } from "../../types/chat";

interface SidebarProps {
  sessions: ChatSessionResponse[];
  activeSessionId: string | null;
  onSelectSession: (sessionId: string) => void;
  onCreateSession: () => void;
  loading: boolean;
  error: string | null;
}

const navItems = [
  { to: "/chat", label: "Chat" },
  { to: "/generate", label: "Generate" },
  { to: "/validate", label: "Validate" },
  { to: "/evaluate", label: "Evaluate" },
];

export function Sidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onCreateSession,
  loading,
  error,
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar__header">
        <div className="sidebar__brand-badge">MTC</div>
        <div>
          <div className="sidebar__brand-title">LocalScript AI</div>
          <div className="sidebar__brand-subtitle">True Tech Hack</div>
        </div>
      </div>

      <nav className="sidebar__nav">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `sidebar__nav-link ${isActive ? "sidebar__nav-link--active" : ""}`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <button type="button" className="new-chat-button" onClick={onCreateSession}>
        + Новый чат
      </button>

      <div className="sidebar__section-title">Чаты</div>

      <SessionList
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelect={onSelectSession}
        loading={loading}
        error={error}
      />
    </aside>
  );
}
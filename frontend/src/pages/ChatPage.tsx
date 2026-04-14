import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

import { ChatPanel } from "../components/layout/ChatPanel";
import { RunsPanel } from "../components/layout/RunsPanel";
import { Sidebar } from "../components/layout/Sidebar";
import { useChatData } from "../hooks/useChatData";
import { useModelStatus } from "../hooks/useModelStatus";
import { useRunsData } from "../hooks/useRunsData";

export function ChatPage() {
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);

  const chatState = useChatData();
  const runsState = useRunsData(chatState.activeSessionId);
  const modelState = useModelStatus();

  async function handleSend(message: string) {
    await chatState.sendMessage(message);
    await runsState.refreshRuns(chatState.activeSessionId);
    await modelState.refresh();
  }

  return (
    <div className="chat-page">
      <div
        className={[
          "chat-page__grid",
          leftCollapsed ? "chat-page__grid--left-collapsed" : "",
          rightCollapsed ? "chat-page__grid--right-collapsed" : "",
          leftCollapsed && rightCollapsed ? "chat-page__grid--both-collapsed" : "",
        ].join(" ")}
      >
        <div className="chat-page__left-column">
          <div
            className={[
              "chat-page__panel",
              "chat-page__panel--left",
              leftCollapsed ? "chat-page__panel--collapsed" : "",
            ].join(" ")}
          >
            <div className="chat-page__panel-inner">
              <Sidebar
                sessions={chatState.sessions}
                activeSessionId={chatState.activeSessionId}
                onSelectSession={chatState.setActiveSessionId}
                onCreateSession={chatState.createNewSession}
                loading={chatState.sessionsLoading}
                error={chatState.sessionsError}
              />
            </div>
          </div>
        </div>

        <div className="chat-page__center-column">
          <div className="chat-page__center-toolbar">
            <button
              type="button"
              className="panel-handle"
              onClick={() => setLeftCollapsed((v) => !v)}
              title={leftCollapsed ? "Показать чаты" : "Скрыть чаты"}
              aria-label={leftCollapsed ? "Показать чаты" : "Скрыть чаты"}
            >
              {leftCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
            </button>

            <button
              type="button"
              className="panel-handle"
              onClick={() => setRightCollapsed((v) => !v)}
              title={rightCollapsed ? "Показать детали" : "Скрыть детали"}
              aria-label={rightCollapsed ? "Показать детали" : "Скрыть детали"}
            >
              {rightCollapsed ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
            </button>
          </div>

          <div className="chat-page__main">
            <ChatPanel
              messages={chatState.uiMessages}
              loading={chatState.historyLoading}
              error={chatState.historyError}
              sending={chatState.sending}
              onSend={handleSend}
              modelStatus={modelState.status}
              modelLoading={modelState.loading}
              modelError={modelState.error}
              onRefreshModel={modelState.refresh}
            />
          </div>
        </div>

        <div className="chat-page__right-column">
          <div
            className={[
              "chat-page__panel",
              "chat-page__panel--right",
              rightCollapsed ? "chat-page__panel--collapsed" : "",
            ].join(" ")}
          >
            <div className="chat-page__panel-inner">
              <RunsPanel
                runs={runsState.runs}
                selectedRunId={runsState.selectedRunId}
                selectedRun={runsState.selectedRun}
                onSelectRun={runsState.setSelectedRunId}
                runsLoading={runsState.runsLoading}
                runDetailsLoading={runsState.runDetailsLoading}
                runsError={runsState.runsError}
                runDetailsError={runsState.runDetailsError}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
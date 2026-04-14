import { Outlet, useLocation } from "react-router-dom";
import { AppNav } from "./AppNav";

export function WorkspaceLayout() {
  const location = useLocation();
  const isChatPage = location.pathname === "/chat";

  return (
    <div
      className={`workspace-layout ${
        isChatPage ? "workspace-layout--chat" : ""
      }`}
    >
      {!isChatPage && <AppNav />}
      <div className="workspace-layout__content">
        <Outlet />
      </div>
    </div>
  );
}
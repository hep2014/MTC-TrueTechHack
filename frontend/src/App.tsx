import { Navigate, Route, Routes } from "react-router-dom";
import { WorkspaceLayout } from "./components/layout/WorkspaceLayout";
import { ChatPage } from "./pages/ChatPage";
import { GeneratePage } from "./pages/GeneratePage";
import { ValidatePage } from "./pages/ValidatePage";
import { EvaluatePage } from "./pages/EvaluatePage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<WorkspaceLayout />}>
        <Route index element={<Navigate to="/chat" replace />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="generate" element={<GeneratePage />} />
        <Route path="validate" element={<ValidatePage />} />
        <Route path="evaluate" element={<EvaluatePage />} />
      </Route>
    </Routes>
  );
}

export default App;
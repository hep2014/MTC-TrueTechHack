import { useMemo, useState } from "react";
import type { ChatGenerateResponse } from "../../types/chat";
import { CodeViewer } from "../common/CodeViewer";

type TabKey = "code" | "wrapped" | "json";

interface ResultTabsProps {
  generated: ChatGenerateResponse;
}

export function ResultTabs({ generated }: ResultTabsProps) {
  const availableTabs = useMemo(() => {
    const tabs: Array<{
      key: TabKey;
      label: string;
      value: string;
      language: "lua" | "json" | "text";
      fileName: string;
    }> = [];

    if (generated.code?.trim()) {
      tabs.push({
        key: "code",
        label: "Code",
        value: generated.code.trim(),
        language: "lua",
        fileName: "generated.lua",
      });
    }

    if (generated.wrapped_code?.trim()) {
      tabs.push({
        key: "wrapped",
        label: "Wrapped",
        value: generated.wrapped_code.trim(),
        language: "lua",
        fileName: "generated_wrapped.lua",
      });
    }

    if (generated.json_output?.trim()) {
      tabs.push({
        key: "json",
        label: "JSON",
        value: generated.json_output.trim(),
        language: "json",
        fileName: "generated.json",
      });
    }

    return tabs;
  }, [generated]);

  const [activeTab, setActiveTab] = useState<TabKey>(
    availableTabs[0]?.key ?? "code",
  );

  if (availableTabs.length === 0) {
    return null;
  }

  const active =
    availableTabs.find((tab) => tab.key === activeTab) ?? availableTabs[0];

  return (
    <div className="result-tabs">
      <div className="result-tabs__top">
        <div className="result-tabs__switcher">
          {availableTabs.map((tab) => (
            <button
              key={tab.key}
              type="button"
              className={`result-tabs__tab ${
                tab.key === active.key ? "result-tabs__tab--active" : ""
              }`}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <CodeViewer
        title={active.label}
        code={active.value}
        language={active.language}
        fileName={active.fileName}
      />
    </div>
  );
}
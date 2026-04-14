from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass
class FormattedOutput:
    mode: str
    code: str
    wrapped_code: str | None
    json_output: str | None


class OutputFormatService:
    def detect_mode(self, task: str, task_contract: dict) -> str:
        lowered = task.lower()
        domain_profile = task_contract.get("domain_profile", "general")

        if "json" in lowered and "lua{" in lowered:
            return "json_field_wrapped"

        if "json field" in lowered or "в json" in lowered or "в json-поле" in lowered:
            return "json_field_wrapped"

        if "lua{" in lowered or "}lua" in lowered or "оберни в lua" in lowered:
            return "embedded_lua"

        if domain_profile == "lowcode" and (
            "оберт" in lowered or "обёрт" in lowered or "wrapped" in lowered
        ):
            return "embedded_lua"

        return "pure_lua"

    def format_output(
        self,
        code: str,
        mode: str,
        field_name: str = "result",
    ) -> FormattedOutput:
        clean_code = code.strip()
        wrapped_code = None
        json_output = None

        if mode == "embedded_lua":
            wrapped_code = self._wrap_lua(clean_code)

        elif mode == "json_field_wrapped":
            wrapped_code = self._wrap_lua(clean_code)
            json_output = json.dumps(
                {field_name: wrapped_code},
                ensure_ascii=False,
            )

        return FormattedOutput(
            mode=mode,
            code=clean_code,
            wrapped_code=wrapped_code,
            json_output=json_output,
        )

    def _wrap_lua(self, code: str) -> str:
        return f"lua{{{code}}}lua"
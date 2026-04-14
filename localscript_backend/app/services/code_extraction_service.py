from __future__ import annotations

import re


class CodeExtractionService:
    _prefixes = [
        "вот исправленный lua-код:",
        "вот lua-код:",
        "вот исправленный код:",
        "вот код:",
        "lua code:",
        "here is the lua code:",
        "here is the corrected lua code:",
        "corrected code:",
    ]

    def extract_lua(self, text: str) -> str:
        value = text.strip()

        fenced = re.findall(r"```(?:lua)?\s*(.*?)```", value, flags=re.DOTALL | re.IGNORECASE)
        if fenced:
            candidate = fenced[0].strip()
            if candidate:
                return candidate

        lowered = value.lower()
        for prefix in self._prefixes:
            if lowered.startswith(prefix):
                return value[len(prefix):].strip()

        return value
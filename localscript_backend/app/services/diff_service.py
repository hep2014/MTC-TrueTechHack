from __future__ import annotations

import difflib


class DiffService:
    def build_unified_diff(
        self,
        old_code: str,
        new_code: str,
        fromfile: str = "previous.lua",
        tofile: str = "current.lua",
    ) -> str:
        old_lines = old_code.splitlines(keepends=True)
        new_lines = new_code.splitlines(keepends=True)

        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=fromfile,
            tofile=tofile,
            lineterm="",
        )
        return "".join(diff).strip()
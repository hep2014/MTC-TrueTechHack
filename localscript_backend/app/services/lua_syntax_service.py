from __future__ import annotations

import asyncio
import os
import tempfile


class LuaSyntaxService:
    def __init__(self, luac_binary: str = "luac") -> None:
        self._luac_binary = luac_binary

    async def validate(self, code: str) -> tuple[bool, str | None]:
        fd, path = tempfile.mkstemp(suffix=".lua")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp:
                tmp.write(code)

            process = await asyncio.create_subprocess_exec(
                self._luac_binary,
                "-p",
                path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await process.communicate()

            if process.returncode == 0:
                return True, None

            error_text = stderr.decode("utf-8", errors="ignore").strip() or "Lua syntax error"
            return False, error_text
        finally:
            try:
                os.remove(path)
            except OSError:
                pass
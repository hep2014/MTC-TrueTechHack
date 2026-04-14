from __future__ import annotations

import asyncio
import os
import tempfile


class LuaRuntimeValidationService:
    def __init__(self, lua_binary: str = "lua", timeout_seconds: float = 2.0) -> None:
        self._lua_binary = lua_binary
        self._timeout_seconds = timeout_seconds

    def _looks_interactive(self, code: str) -> bool:
        lowered = code.lower()
        interactive_markers = [
            "io.read(",
            "stdin",
        ]
        return any(marker in lowered for marker in interactive_markers)

    async def validate(self, code: str) -> tuple[bool, str | None]:
        if self._looks_interactive(code):
            return True, "runtime skipped for interactive stdin-based script"

        wrapper = f"""
local ok, result = pcall(function()
{code}
end)

if ok then
  print("OK")
else
  io.stderr:write(tostring(result))
  os.exit(1)
end
"""
        fd, path = tempfile.mkstemp(suffix=".lua")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp:
                tmp.write(wrapper)

            process = await asyncio.create_subprocess_exec(
                self._lua_binary,
                path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(input=b"test-input\n"),
                    timeout=self._timeout_seconds,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.communicate()
                return False, "Lua runtime validation timeout"

            if process.returncode == 0:
                return True, None

            error_text = stderr.decode("utf-8", errors="ignore").strip() or "Lua runtime error"
            return False, error_text
        finally:
            try:
                os.remove(path)
            except OSError:
                pass

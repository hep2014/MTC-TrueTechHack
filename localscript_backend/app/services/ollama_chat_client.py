from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import settings


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class ChatLLMResult:
    text: str
    provider: str
    model: str
    raw: dict[str, Any]


class OllamaChatClient:
    def __init__(self) -> None:
        self._settings = settings

    async def chat(self, messages: list[ChatMessage]) -> ChatLLMResult:
        if self._settings.use_stub_model:
            return ChatLLMResult(
                text="stub response: model is alive",
                provider="stub",
                model="stub-model",
                raw={"stub": True},
            )

        payload = {
            "model": self._settings.ollama_model,
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ],
            "stream": False,
            "options": {
                "num_ctx": self._settings.ollama_num_ctx,
                "num_predict": self._settings.ollama_num_predict,
                "batch": self._settings.ollama_batch,
                "parallel": self._settings.ollama_parallel,
                "temperature": self._settings.ollama_temperature,
            }
        }

        async with httpx.AsyncClient(timeout=self._settings.request_timeout_seconds) as client:
            response = await client.post(
                f"{self._settings.ollama_base_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        content = (data.get("message", {}) or {}).get("content", "").strip()

        return ChatLLMResult(
            text=content,
            provider="ollama",
            model=self._settings.ollama_model,
            raw=data,
        )

    async def ping(self, text: str = "ping") -> ChatLLMResult:
        return await self.chat(
            [
                ChatMessage(role="user", content=text),
            ]
        )
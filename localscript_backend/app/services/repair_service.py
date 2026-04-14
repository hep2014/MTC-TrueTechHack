from __future__ import annotations

from dataclasses import dataclass

from app.services.ollama_chat_client import ChatMessage, OllamaChatClient
from app.services.prompt_service import PromptService


@dataclass
class RepairResult:
    code: str
    provider: str
    model: str
    messages: list[ChatMessage]


class RepairService:
    def __init__(
        self,
        chat_client: OllamaChatClient,
        prompt_service: PromptService,
    ) -> None:
        self._chat_client = chat_client
        self._prompt_service = prompt_service

    async def repair(
        self,
        base_messages: list[ChatMessage],
        repair_user_message: str,
        invalid_code: str,
    ) -> RepairResult:
        messages = [
            ChatMessage(
                role="system",
                content=self._prompt_service.REPAIR_SYSTEM_PROMPT,
            ),
            *base_messages,
            ChatMessage(role="assistant", content=invalid_code),
            ChatMessage(role="user", content=repair_user_message),
        ]

        response = await self._chat_client.chat(messages)

        return RepairResult(
            code=response.text.strip(),
            provider=response.provider,
            model=response.model,
            messages=messages,
        )
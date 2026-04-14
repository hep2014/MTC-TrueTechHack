from __future__ import annotations

from dataclasses import dataclass

from app.services.ollama_chat_client import ChatMessage, OllamaChatClient
from app.services.prompt_service import PromptService


@dataclass
class GenerationResult:
    code: str
    provider: str
    model: str
    messages: list[ChatMessage]


class GenerationService:
    def __init__(
        self,
        chat_client: OllamaChatClient,
        prompt_service: PromptService,
    ) -> None:
        self._chat_client = chat_client
        self._prompt_service = prompt_service

    async def generate(
        self,
        task: str,
        history: list[ChatMessage] | None = None,
        task_contract: dict | None = None,
        local_templates: list[dict] | None = None,
    ) -> GenerationResult:
        history = history or []

        messages = [
            ChatMessage(
                role="system",
                content=self._prompt_service.GENERATION_SYSTEM_PROMPT,
            ),
            *history,
            ChatMessage(
                role="user",
                content=self._prompt_service.build_generation_user_message(
                    task=task,
                    task_contract=task_contract,
                    local_templates=local_templates,
                ),
            ),
        ]

        response = await self._chat_client.chat(messages)

        return GenerationResult(
            code=response.text.strip(),
            provider=response.provider,
            model=response.model,
            messages=messages,
        )
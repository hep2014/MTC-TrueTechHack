from __future__ import annotations

import json
import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.run_read_repository import RunReadRepository


class ChatContextService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = RunReadRepository(db)

    async def resolve_context(
        self,
        session_id: str,
        user_message: str,
    ) -> dict:
        pending_run = await self._repo.get_latest_pending_clarification_run_by_session_id(
            session_id=session_id,
        )

        if pending_run is not None:
            return {
                "mode": "clarification",
                "effective_task": self._build_from_clarification(
                    user_message=user_message,
                    pending_run=pending_run,
                ),
                "analysis_task": pending_run.user_prompt.strip(),
                "resumed_from_clarification": True,
                "resumed_from_refinement": False,
            }

        latest_run = await self._repo.get_latest_run_by_session_id(session_id=session_id)
        if latest_run is not None and self._looks_like_refinement(user_message):
            return {
                "mode": "refinement",
                "effective_task": self._build_from_refinement(
                    user_message=user_message,
                    latest_run=latest_run,
                ),
                "analysis_task": latest_run.user_prompt.strip(),
                "resumed_from_clarification": False,
                "resumed_from_refinement": True,
            }

        return {
            "mode": "new_task",
            "effective_task": user_message.strip(),
            "analysis_task": user_message.strip(),
            "resumed_from_clarification": False,
            "resumed_from_refinement": False,
        }

    def _build_from_clarification(
        self,
        user_message: str,
        pending_run,
    ) -> str:
        clarification_questions: list[dict[str, str]] = []
        if pending_run.clarification_questions_json:
            try:
                clarification_questions = json.loads(pending_run.clarification_questions_json)
            except json.JSONDecodeError:
                clarification_questions = []

        task_contract: dict = {}
        if pending_run.task_contract_json:
            try:
                task_contract = json.loads(pending_run.task_contract_json)
            except json.JSONDecodeError:
                task_contract = {}

        questions_block = "\n".join(
            f"- {item.get('question', '')}" for item in clarification_questions
        ).strip()

        effective_task = (
            f"{pending_run.user_prompt.strip()}\n\n"
            "Дополнительные уточнения пользователя:\n"
            f"{user_message.strip()}\n\n"
        )

        if questions_block:
            effective_task += (
                "Это ответ на ранее заданные уточняющие вопросы:\n"
                f"{questions_block}\n\n"
            )

        if task_contract:
            effective_task += (
                "Предыдущее понимание задачи:\n"
                f"- Цель: {task_contract.get('goal', '')}\n"
                f"- Входы: {', '.join(task_contract.get('inputs', [])) or 'не указаны'}\n"
                f"- Выходы: {', '.join(task_contract.get('outputs', [])) or 'не указаны'}\n"
                f"- Ограничения: {', '.join(task_contract.get('constraints', [])) or 'не указаны'}\n"
                f"- Допущения: {', '.join(task_contract.get('assumptions', [])) or 'не указаны'}\n"
                f"- Тип задачи: {task_contract.get('task_type', 'unknown')}\n"
                f"- Подтип задачи: {task_contract.get('task_subtype', '')}\n"
            )

        return effective_task.strip()

    def _build_from_refinement(
        self,
        user_message: str,
        latest_run,
    ) -> str:
        task_contract: dict = {}
        if latest_run.task_contract_json:
            try:
                task_contract = json.loads(latest_run.task_contract_json)
            except json.JSONDecodeError:
                task_contract = {}

        final_code = (latest_run.final_code or "").strip()

        effective_task = (
            f"Исходная задача:\n{latest_run.user_prompt.strip()}\n\n"
            "Новая доработка пользователя:\n"
            f"{user_message.strip()}\n\n"
        )

        if task_contract:
            effective_task += (
                "Предыдущее понимание задачи:\n"
                f"- Цель: {task_contract.get('goal', '')}\n"
                f"- Входы: {', '.join(task_contract.get('inputs', [])) or 'не указаны'}\n"
                f"- Выходы: {', '.join(task_contract.get('outputs', [])) or 'не указаны'}\n"
                f"- Ограничения: {', '.join(task_contract.get('constraints', [])) or 'не указаны'}\n"
                f"- Допущения: {', '.join(task_contract.get('assumptions', [])) or 'не указаны'}\n"
                f"- Тип задачи: {task_contract.get('task_type', 'unknown')}\n"
                f"- Подтип задачи: {task_contract.get('task_subtype', '')}\n\n"
            )

        if final_code:
            effective_task += (
                "Текущий Lua-код, который нужно доработать:\n"
                f"{final_code}\n\n"
                "Нужно вернуть полную обновлённую версию Lua-кода с учётом доработки."
            )

        return effective_task.strip()

    def _looks_like_refinement(self, user_message: str) -> bool:
        lowered = user_message.strip().lower()

        patterns = [
            r"^добав",
            r"^исправ",
            r"^измени",
            r"^передел",
            r"^доработ",
            r"^оптимиз",
            r"^улучш",
            r"^расшир",
            r"^теперь\b",
            r"^ещ[её]\b",
            r"^а теперь\b",
            r"^и ещё\b",
            r"^сделай\b",
            r"^сделай так",
            r"^не используй",
            r"^используй",
            r"^убери",
            r"^замени",
            r"^пусть",
            r"^нужно чтобы",
        ]

        return any(re.search(pattern, lowered) for pattern in patterns)

    async def get_previous_final_code(
        self,
        session_id: str,
    ) -> str | None:
        run = await self._repo.get_latest_completed_run_by_session_id(session_id)
        if run is None:
            return None
        return run.final_code.strip() if run.final_code else None
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_session import ChatSession
from app.models.pipeline_run import PipelineRun
from app.repositories.chat_repository import ChatRepository
from app.repositories.pipeline_repository import PipelineRepository


@dataclass
class PipelineStepSnapshot:
    name: str
    status: str
    duration_ms: int
    details: dict[str, Any]


class PipelineTraceService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._pipeline_repo = PipelineRepository(db)
        self._chat_repo = ChatRepository(db)
        self._steps: list[PipelineStepSnapshot] = []

    async def get_session_by_session_id(self, session_id: str) -> ChatSession | None:
        return await self._chat_repo.get_session_by_session_id(session_id)

    async def start_run(
        self,
        session: ChatSession | None,
        user_prompt: str,
        validate_runtime: bool,
        used_history: bool,
    ) -> PipelineRun:
        run = await self._pipeline_repo.create_run(
            session_pk=session.id if session is not None else None,
            user_prompt=user_prompt,
            validate_runtime=validate_runtime,
            used_history=used_history,
        )
        await self._db.commit()
        return run

    async def add_step(
        self,
        run: PipelineRun,
        name: str,
        status: str,
        started_at: float,
        details: dict[str, Any] | None = None,
    ) -> None:
        payload = details or {}
        duration_ms = int((perf_counter() - started_at) * 1000)

        snapshot = PipelineStepSnapshot(
            name=name,
            status=status,
            duration_ms=duration_ms,
            details=payload,
        )
        self._steps.append(snapshot)

        await self._pipeline_repo.add_step(
            run_pk=run.id,
            step_name=name,
            status=status,
            duration_ms=duration_ms,
            details_json=json.dumps(payload, ensure_ascii=False),
        )
        await self._db.commit()

    async def finalize_run(
        self,
        run: PipelineRun,
        status: str,
        provider: str | None,
        model: str | None,
        repaired: bool,
        attempts: int,
        final_code: str | None,
        confidence_score: int | None,
        confidence_reasons: list[str],
        task_contract: dict[str, Any],
        clarification_questions: list[dict[str, str]],
        evaluation_report: dict[str, Any],
        diff_text: str | None,
    ) -> None:
        await self._pipeline_repo.finalize_run(
            run=run,
            status=status,
            provider=provider,
            model=model,
            repaired=repaired,
            attempts=attempts,
            final_code=final_code,
            confidence_score=confidence_score,
            confidence_reasons_json=json.dumps(confidence_reasons, ensure_ascii=False),
            task_contract_json=json.dumps(task_contract, ensure_ascii=False),
            clarification_questions_json=json.dumps(clarification_questions, ensure_ascii=False),
            evaluation_report_json=json.dumps(evaluation_report, ensure_ascii=False),
            diff_text=diff_text,
        )
        await self._db.commit()

    def to_list(self) -> list[dict[str, Any]]:
        return [asdict(step) for step in self._steps]
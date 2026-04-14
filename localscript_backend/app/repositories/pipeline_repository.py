from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat_session import ChatSession
from app.models.pipeline_run import PipelineRun
from app.models.pipeline_step import PipelineStep


class PipelineRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_run(
        self,
        session_pk: int | None,
        user_prompt: str,
        validate_runtime: bool,
        used_history: bool,
    ) -> PipelineRun:
        run = PipelineRun(
            session_pk=session_pk,
            user_prompt=user_prompt,
            status="running",
            validate_runtime=validate_runtime,
            used_history=used_history,
        )
        self._db.add(run)
        await self._db.flush()
        await self._db.refresh(run)
        return run

    async def add_step(
        self,
        run_pk: int,
        step_name: str,
        status: str,
        duration_ms: int,
        details_json: str | None,
    ) -> PipelineStep:
        step = PipelineStep(
            run_pk=run_pk,
            step_name=step_name,
            status=status,
            duration_ms=duration_ms,
            details_json=details_json,
        )
        self._db.add(step)
        await self._db.flush()
        await self._db.refresh(step)
        return step

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
        confidence_reasons_json: str | None,
        task_contract_json: str | None,
        clarification_questions_json: str | None,
        evaluation_report_json: str | None,
        diff_text: str | None,
    ) -> PipelineRun:
        run.status = status
        run.provider = provider
        run.model = model
        run.repaired = repaired
        run.attempts = attempts
        run.final_code = final_code
        run.confidence_score = confidence_score
        run.confidence_reasons_json = confidence_reasons_json
        run.task_contract_json = task_contract_json
        run.clarification_questions_json = clarification_questions_json
        run.finished_at = datetime.utcnow()
        run.confidence_reasons_json = confidence_reasons_json
        run.evaluation_report_json = evaluation_report_json
        run.diff_text = diff_text

        await self._db.flush()
        await self._db.refresh(run)
        return run

    async def get_run_with_steps(self, run_id: int) -> PipelineRun | None:
        stmt = (
            select(PipelineRun)
            .options(selectinload(PipelineRun.steps))
            .where(PipelineRun.id == run_id)
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()
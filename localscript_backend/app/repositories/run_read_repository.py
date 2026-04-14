from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat_session import ChatSession
from app.models.pipeline_run import PipelineRun


class RunReadRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_latest_completed_run_by_session_id(
        self,
        session_id: str,
    ) -> PipelineRun | None:
        stmt = (
            select(PipelineRun)
            .join(ChatSession, ChatSession.id == PipelineRun.session_pk)
            .where(
                ChatSession.session_id == session_id,
                PipelineRun.status.in_(["completed", "completed_with_warnings"]),
            )
            .order_by(PipelineRun.id.desc())
            .limit(1)
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_run_by_id(self, run_id: int) -> PipelineRun | None:
        stmt = (
            select(PipelineRun)
            .options(selectinload(PipelineRun.steps))
            .where(PipelineRun.id == run_id)
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_runs_by_session_id(self, session_id: str) -> list[PipelineRun]:
        stmt = (
            select(PipelineRun)
            .join(ChatSession, ChatSession.id == PipelineRun.session_pk)
            .where(ChatSession.session_id == session_id)
            .order_by(PipelineRun.id.desc())
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_run_by_session_id(self, session_id: str) -> PipelineRun | None:
        stmt = (
            select(PipelineRun)
            .join(ChatSession, ChatSession.id == PipelineRun.session_pk)
            .where(ChatSession.session_id == session_id)
            .order_by(PipelineRun.id.desc())
            .limit(1)
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_pending_clarification_run_by_session_id(
        self,
        session_id: str,
    ) -> PipelineRun | None:
        stmt = (
            select(PipelineRun)
            .join(ChatSession, ChatSession.id == PipelineRun.session_pk)
            .where(
                ChatSession.session_id == session_id,
                PipelineRun.status == "needs_clarification",
            )
            .order_by(PipelineRun.id.desc())
            .limit(1)
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()
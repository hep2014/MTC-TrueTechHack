from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.run_read_repository import RunReadRepository
from app.schemas.run import (
    PipelineRunDetailsResponse,
    PipelineRunListItemResponse,
    PipelineStepResponse,
)

router = APIRouter(tags=["runs"])


@router.get("/runs/{run_id}", response_model=PipelineRunDetailsResponse)
async def get_run(
    run_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> PipelineRunDetailsResponse:
    repo = RunReadRepository(db)
    run = await repo.get_run_by_id(run_id)

    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запуск не найден",
        )

    return PipelineRunDetailsResponse(
        id=run.id,
        session_pk=run.session_pk,
        user_prompt=run.user_prompt,
        status=run.status,
        provider=run.provider,
        model=run.model,
        repaired=run.repaired,
        attempts=run.attempts,
        used_history=run.used_history,
        validate_runtime=run.validate_runtime,
        final_code=run.final_code,
        confidence_score=run.confidence_score,
        confidence_reasons_json=run.confidence_reasons_json,
        task_contract_json=run.task_contract_json,
        clarification_questions_json=run.clarification_questions_json,
        created_at=run.created_at,
        finished_at=run.finished_at,
        steps=[
            PipelineStepResponse(
                id=step.id,
                step_name=step.step_name,
                status=step.status,
                duration_ms=step.duration_ms,
                details_json=step.details_json,
                created_at=step.created_at,
            )
            for step in run.steps
        ],
        evaluation_report_json=run.evaluation_report_json,
        diff_text=run.diff_text,
    )


@router.get("/chat/sessions/{session_id}/runs", response_model=list[PipelineRunListItemResponse])
async def list_runs_for_session(
    session_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> list[PipelineRunListItemResponse]:
    repo = RunReadRepository(db)
    runs = await repo.list_runs_by_session_id(session_id)

    return [
        PipelineRunListItemResponse(
            id=run.id,
            status=run.status,
            provider=run.provider,
            model=run.model,
            repaired=run.repaired,
            attempts=run.attempts,
            used_history=run.used_history,
            validate_runtime=run.validate_runtime,
            confidence_score=run.confidence_score,
            created_at=run.created_at,
            finished_at=run.finished_at,
        )
        for run in runs
    ]
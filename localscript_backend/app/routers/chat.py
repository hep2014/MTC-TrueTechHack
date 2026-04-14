from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.chat_session import ChatSession
from app.schemas.chat import ChatHistoryResponse, ChatSessionResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db_session),
) -> list[ChatSessionResponse]:
    stmt = select(ChatSession).order_by(ChatSession.updated_at.desc())
    result = await db.execute(stmt)
    sessions = list(result.scalars().all())
    return [ChatSessionResponse.model_validate(item) for item in sessions]


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> ChatSessionResponse:
    stmt = select(ChatSession).where(ChatSession.session_id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия не найдена",
        )

    return ChatSessionResponse.model_validate(session)


@router.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
async def get_session_history(
    session_id: str,
    db: AsyncSession = Depends(get_db_session),
) -> ChatHistoryResponse:
    stmt = select(ChatSession).where(ChatSession.session_id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия не найдена",
        )

    await db.refresh(session, attribute_names=["messages"])

    return ChatHistoryResponse(
        session_id=session.session_id,
        messages=[item for item in session.messages],
    )
from __future__ import annotations

from sqlalchemy import Select, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession


class ChatRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_session_by_session_id(self, session_id: str) -> ChatSession | None:
        stmt: Select[tuple[ChatSession]] = (
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(ChatSession.session_id == session_id)
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_session(
        self,
        session_id: str,
        title: str | None = None,
    ) -> ChatSession:
        session = ChatSession(
            session_id=session_id,
            title=title,
        )
        self._db.add(session)
        await self._db.flush()
        await self._db.refresh(session)
        return session

    async def get_or_create_session(
        self,
        session_id: str,
        title: str | None = None,
    ) -> ChatSession:
        existing = await self.get_session_by_session_id(session_id)
        if existing is not None:
            return existing
        return await self.create_session(session_id=session_id, title=title)

    async def get_next_order_index(self, session_pk: int) -> int:
        stmt = select(func.max(ChatMessage.order_index)).where(ChatMessage.session_pk == session_pk)
        result = await self._db.execute(stmt)
        current_max = result.scalar_one_or_none()
        return 0 if current_max is None else current_max + 1

    async def add_message(
        self,
        session: ChatSession,
        role: str,
        content: str,
    ) -> ChatMessage:
        next_index = await self.get_next_order_index(session.id)

        message = ChatMessage(
            session_pk=session.id,
            role=role,
            content=content,
            order_index=next_index,
        )
        self._db.add(message)
        await self._db.flush()
        await self._db.refresh(message)
        return message

    async def list_messages(self, session_id: str) -> list[ChatMessage]:
        session = await self.get_session_by_session_id(session_id)
        if session is None:
            return []
        return list(session.messages)

    async def delete_session(self, session_id: str) -> bool:
        stmt = delete(ChatSession).where(ChatSession.session_id == session_id)
        result = await self._db.execute(stmt)
        return result.rowcount > 0
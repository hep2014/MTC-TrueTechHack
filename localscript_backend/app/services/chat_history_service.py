from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.chat_repository import ChatRepository
from app.services.ollama_chat_client import ChatMessage


class ChatHistoryService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._repo = ChatRepository(db)

    async def ensure_session(
        self,
        session_id: str,
        title: str | None = None,
    ):
        session = await self._repo.get_or_create_session(
            session_id=session_id,
            title=title,
        )
        await self._db.commit()
        return session

    async def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        title: str | None = None,
    ):
        session = await self._repo.get_or_create_session(
            session_id=session_id,
            title=title,
        )
        message = await self._repo.add_message(
            session=session,
            role=role,
            content=content,
        )
        await self._db.commit()
        await self._db.refresh(message)
        return message

    async def get_history(self, session_id: str):
        return await self._repo.list_messages(session_id=session_id)

    async def get_chat_messages(self, session_id: str) -> list[ChatMessage]:
        messages = await self.get_history(session_id=session_id)
        return [
            ChatMessage(role=msg.role, content=msg.content)
            for msg in messages
        ]

    async def delete_session(self, session_id: str) -> bool:
        deleted = await self._repo.delete_session(session_id)
        await self._db.commit()
        return deleted
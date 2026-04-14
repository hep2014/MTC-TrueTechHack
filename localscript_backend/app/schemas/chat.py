from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatMessageSchema(BaseModel):
    role: Literal["system", "user", "assistant"] = Field(
        ...,
        description="Роль сообщения в чате",
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Текст сообщения",
    )


class ChatSessionCreateRequest(BaseModel):
    session_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Внешний идентификатор сессии",
    )
    title: str | None = Field(
        default=None,
        max_length=255,
        description="Необязательный заголовок сессии",
    )


class ChatMessageCreateRequest(BaseModel):
    session_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Идентификатор сессии",
    )
    role: Literal["system", "user", "assistant"] = Field(
        ...,
        description="Роль сообщения",
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Текст сообщения",
    )
    title: str | None = Field(
        default=None,
        max_length=255,
        description="Заголовок сессии, если нужно создать её на лету",
    )


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Идентификатор сообщения")
    role: str = Field(..., description="Роль сообщения")
    content: str = Field(..., description="Текст сообщения")
    order_index: int = Field(..., description="Порядковый номер сообщения в сессии")
    created_at: datetime = Field(..., description="Время создания сообщения")


class ChatSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Идентификатор записи сессии")
    session_id: str = Field(..., description="Внешний идентификатор сессии")
    title: str | None = Field(None, description="Заголовок сессии")
    created_at: datetime = Field(..., description="Время создания сессии")
    updated_at: datetime = Field(..., description="Время последнего обновления сессии")


class ChatHistoryResponse(BaseModel):
    session_id: str = Field(..., description="Идентификатор сессии")
    messages: list[ChatMessageResponse] = Field(
        default_factory=list,
        description="Сообщения сессии в порядке их следования",
    )
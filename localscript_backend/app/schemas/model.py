from pydantic import BaseModel, Field


class ModelCheckRequest(BaseModel):
    prompt: str = Field(
        default="ping",
        min_length=1,
        description="Текст для пробного вызова модели",
    )


class ModelCheckResponse(BaseModel):
    ok: bool = Field(..., description="Доступна ли модель")
    provider: str = Field(..., description="Источник ответа: stub или ollama")
    model: str = Field(..., description="Название модели")
    preview: str = Field(..., description="Короткий фрагмент ответа модели")
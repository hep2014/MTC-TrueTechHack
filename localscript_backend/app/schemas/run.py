from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class PipelineStepResponse(BaseModel):
    id: int = Field(..., description="ID шага")
    step_name: str = Field(..., description="Имя шага")
    status: str = Field(..., description="Статус шага")
    duration_ms: int = Field(..., description="Длительность шага в миллисекундах")
    details_json: str | None = Field(None, description="JSON-детали шага")
    created_at: datetime = Field(..., description="Время создания шага")


class PipelineRunListItemResponse(BaseModel):
    id: int = Field(..., description="ID запуска")
    status: str = Field(..., description="Статус запуска")
    provider: str | None = Field(None, description="Провайдер")
    model: str | None = Field(None, description="Модель")
    repaired: bool = Field(..., description="Был ли repair")
    attempts: int = Field(..., description="Количество попыток")
    used_history: bool = Field(..., description="Использовалась ли история")
    validate_runtime: bool = Field(..., description="Была ли включена runtime-валидация")
    confidence_score: int | None = Field(None, description="Оценка уверенности")
    created_at: datetime = Field(..., description="Время создания запуска")
    finished_at: datetime | None = Field(None, description="Время завершения запуска")


class PipelineRunDetailsResponse(BaseModel):
    id: int = Field(..., description="ID запуска")
    session_pk: int | None = Field(None, description="Связанная chat session")
    user_prompt: str = Field(..., description="Исходный prompt")
    status: str = Field(..., description="Статус запуска")
    provider: str | None = Field(None, description="Провайдер")
    model: str | None = Field(None, description="Модель")
    repaired: bool = Field(..., description="Был ли repair")
    attempts: int = Field(..., description="Количество попыток")
    used_history: bool = Field(..., description="Использовалась ли история")
    validate_runtime: bool = Field(..., description="Была ли включена runtime-валидация")
    final_code: str | None = Field(None, description="Итоговый код")
    confidence_score: int | None = Field(None, description="Оценка уверенности")
    confidence_reasons_json: str | None = Field(None, description="JSON причин confidence")
    task_contract_json: str | None = Field(None, description="JSON контракта задачи")
    clarification_questions_json: str | None = Field(None, description="JSON уточняющих вопросов")
    created_at: datetime = Field(..., description="Время создания запуска")
    finished_at: datetime | None = Field(None, description="Время завершения запуска")
    steps: list[PipelineStepResponse] = Field(default_factory=list, description="Шаги запуска")
    evaluation_report_json: str | None = Field(None, description="JSON отчёта оценки")
    diff_text: str | None = Field(None, description="Diff текста кода")
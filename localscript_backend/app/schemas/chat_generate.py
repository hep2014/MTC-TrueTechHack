from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.evaluation import EvaluationReport
from app.schemas.generation import ValidationInfo
from app.schemas.pipeline import ClarificationQuestion, ConfidenceInfo, PipelineStatus, TaskContract


class ChatGenerateRequest(BaseModel):
    session_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Идентификатор чат-сессии",
    )
    message: str = Field(
        ...,
        min_length=1,
        description="Новая пользовательская реплика",
    )
    title: str | None = Field(
        default=None,
        max_length=255,
        description="Необязательный заголовок сессии",
    )
    validate_runtime: bool = Field(
        default=True,
        description="Нужно ли выполнять runtime-валидацию",
    )


class ChatGenerateResponse(BaseModel):
    session_id: str = Field(..., description="Идентификатор чат-сессии")
    resumed_from_clarification: bool = Field(
        default=False,
        description="Был ли текущий запрос продолжением clarification flow",
    )
    resumed_from_refinement: bool = Field(
        default=False,
        description="Был ли текущий запрос доработкой предыдущего кода",
    )
    status: PipelineStatus = Field(..., description="Итоговый статус пайплайна")
    code: str = Field(default="", description="Итоговый Lua-код")
    output_mode: str = Field(default="pure_lua", description="Режим форматирования ответа")
    wrapped_code: str | None = Field(default=None, description="Lua-код в формате lua{...}lua")
    json_output: str | None = Field(default=None, description="JSON-обёртка с Lua-кодом")
    diff_text: str | None = Field(default=None, description="Diff относительно предыдущей версии кода")
    provider: str = Field(default="", description="Источник ответа модели")
    model: str = Field(default="", description="Название модели")
    repaired: bool = Field(default=False, description="Был ли repair")
    attempts: int = Field(default=0, description="Количество попыток")
    used_history: bool = Field(default=False, description="Использовалась ли история")
    validation: ValidationInfo = Field(..., description="Результат итоговой валидации")
    clarification_questions: list[ClarificationQuestion] = Field(
        default_factory=list,
        description="Список уточняющих вопросов",
    )
    task_contract: TaskContract = Field(..., description="Контракт задачи")
    confidence: ConfidenceInfo = Field(..., description="Оценка уверенности")
    evaluation_report: EvaluationReport = Field(..., description="Автоматический отчёт оценки")
    pipeline_steps: list[dict] = Field(default_factory=list, description="Шаги пайплайна")
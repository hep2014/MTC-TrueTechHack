from pydantic import BaseModel, Field

from app.schemas.chat import ChatMessageSchema
from app.schemas.evaluation import EvaluationReport
from app.schemas.pipeline import ClarificationQuestion, ConfidenceInfo, PipelineStatus, TaskContract


class GenerateCodeRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=1,
        description="Текст задачи на естественном языке",
    )
    session_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
        description="Идентификатор чат-сессии для работы с сохранённой историей",
    )
    messages: list[ChatMessageSchema] = Field(
        default_factory=list,
        description="История сообщений, если она передаётся напрямую",
    )
    validate_runtime: bool = Field(
        default=True,
        description="Нужно ли выполнять runtime-валидацию через lua",
    )


class ValidationInfo(BaseModel):
    is_valid: bool = Field(..., description="Прошла ли итоговая валидация")
    stage_results: dict[str, bool] = Field(
        default_factory=dict,
        description="Результаты этапов валидации",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Ошибки валидации",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Предупреждения валидации",
    )


class GenerateCodeResponse(BaseModel):
    status: PipelineStatus = Field(..., description="Итоговый статус пайплайна")
    code: str = Field(default="", description="Итоговый Lua-код")
    output_mode: str = Field(default="pure_lua", description="Режим форматирования ответа")
    wrapped_code: str | None = Field(default=None, description="Lua-код в формате lua{...}lua")
    json_output: str | None = Field(default=None, description="JSON-обёртка с Lua-кодом")
    diff_text: str | None = Field(default=None, description="Diff относительно предыдущей версии кода")
    provider: str = Field(default="", description="Источник ответа модели")
    model: str = Field(default="", description="Название модели")
    repaired: bool = Field(default=False, description="Была ли выполнена repair-итерация")
    attempts: int = Field(default=0, description="Количество попыток генерации/исправления")
    used_history: bool = Field(default=False, description="Использовалась ли история сообщений")
    validation: ValidationInfo = Field(..., description="Результат итоговой валидации")
    clarification_questions: list[ClarificationQuestion] = Field(
        default_factory=list,
        description="Список уточняющих вопросов, если данных недостаточно",
    )
    task_contract: TaskContract = Field(
        default_factory=TaskContract,
        description="Структурированное понимание задачи",
    )
    confidence: ConfidenceInfo = Field(
        ...,
        description="Инженерная оценка уверенности в результате",
    )
    evaluation_report: EvaluationReport = Field(..., description="Автоматический отчёт оценки")
    pipeline_steps: list[dict] = Field(
        default_factory=list,
        description="Трассировка шагов пайплайна",
    )
from __future__ import annotations

from pydantic import BaseModel, Field


class EvaluationReport(BaseModel):
    context_mode: str = Field(..., description="Режим контекста")
    domain_profile: str = Field(..., description="Доменный профиль")
    task_type: str = Field(..., description="Тип задачи")
    task_subtype: str = Field(..., description="Подтип задачи")
    selected_templates: list[str] = Field(default_factory=list, description="Выбранные шаблоны")
    output_mode: str = Field(..., description="Режим форматирования вывода")
    validation_summary: dict = Field(..., description="Сводка валидации")
    repair_used: bool = Field(..., description="Использовался ли repair")
    attempts: int = Field(..., description="Количество попыток")
    confidence_score: int = Field(..., description="Оценка confidence")
    confidence_reasons: list[str] = Field(default_factory=list, description="Причины confidence")
    provider: str = Field(default="", description="Провайдер")
    model: str = Field(default="", description="Модель")
    has_diff: bool = Field(default=False, description="Есть ли diff")
    diff_text: str | None = Field(default=None, description="Текст diff")
    final_status: str = Field(..., description="Финальный статус")


class EvaluateCodeRequest(BaseModel):
    task: str = Field(..., min_length=1, description="Текст задачи")
    code: str = Field(..., min_length=1, description="Lua-код для оценки")
    validate_runtime: bool = Field(default=True, description="Нужно ли выполнять runtime-валидацию")


class EvaluateCodeResponse(BaseModel):
    validation: dict = Field(..., description="Результат валидации")
    confidence: dict = Field(..., description="Оценка confidence")
    evaluation_report: EvaluationReport = Field(..., description="Отчёт оценки")
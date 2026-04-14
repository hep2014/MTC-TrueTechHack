from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


PipelineStatus = Literal[
    "completed",
    "needs_clarification",
    "completed_with_warnings",
    "failed_validation",
]


class ClarificationQuestion(BaseModel):
    key: str = Field(..., description="Машинно-читаемый ключ вопроса")
    question: str = Field(..., description="Текст уточняющего вопроса")


class TaskContract(BaseModel):
    goal: str = Field(default="", description="Краткая цель задачи")
    inputs: list[str] = Field(default_factory=list, description="Предполагаемые входные данные")
    outputs: list[str] = Field(default_factory=list, description="Предполагаемые выходные данные")
    constraints: list[str] = Field(default_factory=list, description="Ограничения задачи")
    assumptions: list[str] = Field(default_factory=list, description="Принятые допущения")
    target_runtime: str = Field(default="lua", description="Целевая среда исполнения")
    complexity_note: str = Field(default="", description="Краткое замечание о сложности")
    task_type: str = Field(default="unknown", description="Тип задачи")
    task_subtype: str = Field(default="", description="Подтип задачи")
    risk_flags: list[str] = Field(default_factory=list, description="Риски и недостающие части постановки")
    domain_profile: str = Field(default="general", description="Доменный профиль задачи")
    profile_rules: list[str] = Field(default_factory=list, description="Активные доменные правила")
    output_mode: str = Field(default="pure_lua", description="Режим форматирования ответа")


class ConfidenceInfo(BaseModel):
    score: int = Field(..., ge=0, le=100, description="Инженерная оценка уверенности")
    reasons: list[str] = Field(
        default_factory=list,
        description="Причины, повлиявшие на оценку",
    )
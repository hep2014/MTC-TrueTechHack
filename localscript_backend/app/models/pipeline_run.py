from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    session_pk: Mapped[int | None] = mapped_column(
        ForeignKey("chat_sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    user_prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    provider: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    model: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    repaired: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    used_history: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    validate_runtime: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    final_code: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    confidence_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    confidence_reasons_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    task_contract_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    clarification_questions_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    steps: Mapped[list["PipelineStep"]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
        order_by="PipelineStep.id",
    )

    session: Mapped["ChatSession | None"] = relationship(
        back_populates="runs",
    )

    evaluation_report_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    diff_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
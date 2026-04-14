"""add pipeline runs

Revision ID: f8b99c8df992
Revises: 20260414_0001
Create Date: 2026-04-14 03:15:59.122885

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260414_0002"
down_revision: Union[str, None] = "20260414_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pipeline_runs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("session_pk", sa.Integer(), nullable=True),
        sa.Column("user_prompt", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=True),
        sa.Column("model", sa.String(length=128), nullable=True),
        sa.Column("repaired", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("used_history", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("validate_runtime", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("final_code", sa.Text(), nullable=True),
        sa.Column("confidence_score", sa.Integer(), nullable=True),
        sa.Column("confidence_reasons_json", sa.Text(), nullable=True),
        sa.Column("task_contract_json", sa.Text(), nullable=True),
        sa.Column("clarification_questions_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["session_pk"],
            ["chat_sessions.id"],
            name="fk_pipeline_runs_session_pk_chat_sessions",
            ondelete="SET NULL",
        ),
    )

    op.create_index(
        "ix_pipeline_runs_session_pk",
        "pipeline_runs",
        ["session_pk"],
        unique=False,
    )

    op.create_index(
        "ix_pipeline_runs_status",
        "pipeline_runs",
        ["status"],
        unique=False,
    )

    op.create_table(
        "pipeline_steps",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("run_pk", sa.Integer(), nullable=False),
        sa.Column("step_name", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("details_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["run_pk"],
            ["pipeline_runs.id"],
            name="fk_pipeline_steps_run_pk_pipeline_runs",
            ondelete="CASCADE",
        ),
    )

    op.create_index(
        "ix_pipeline_steps_run_pk",
        "pipeline_steps",
        ["run_pk"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_pipeline_steps_run_pk", table_name="pipeline_steps")
    op.drop_table("pipeline_steps")

    op.drop_index("ix_pipeline_runs_status", table_name="pipeline_runs")
    op.drop_index("ix_pipeline_runs_session_pk", table_name="pipeline_runs")
    op.drop_table("pipeline_runs")

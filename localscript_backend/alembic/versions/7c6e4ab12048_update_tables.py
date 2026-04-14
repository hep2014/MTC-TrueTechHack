"""update tables

Revision ID: 7c6e4ab12048
Revises: 20260414_0002
Create Date: 2026-04-14 04:58:35.936346

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260414_0003"
down_revision: Union[str, None] = "20260414_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "pipeline_runs",
        sa.Column("evaluation_report_json", sa.Text(), nullable=True),
    )
    op.add_column(
        "pipeline_runs",
        sa.Column("diff_text", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("pipeline_runs", "diff_text")
    op.drop_column("pipeline_runs", "evaluation_report_json")

"""init_chat_tables

Revision ID: cd924d88da3b
Revises: 
Create Date: 2026-04-14 02:22:01.140829

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260414_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("session_id", name="uq_chat_sessions_session_id"),
    )

    op.create_index(
        "ix_chat_sessions_session_id",
        "chat_sessions",
        ["session_id"],
        unique=False,
    )

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("session_pk", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_pk"],
            ["chat_sessions.id"],
            name="fk_chat_messages_session_pk_chat_sessions",
            ondelete="CASCADE",
        ),
    )

    op.create_index(
        "ix_chat_messages_session_pk",
        "chat_messages",
        ["session_pk"],
        unique=False,
    )

    op.create_index(
        "ix_chat_messages_session_pk_order_index",
        "chat_messages",
        ["session_pk", "order_index"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_chat_messages_session_pk_order_index", table_name="chat_messages")
    op.drop_index("ix_chat_messages_session_pk", table_name="chat_messages")
    op.drop_table("chat_messages")

    op.drop_index("ix_chat_sessions_session_id", table_name="chat_sessions")
    op.drop_table("chat_sessions")
"""Phase 12b: materialized habit statistics table.

Revision ID: 20260321_habit_stat_table
Revises: 20260314_private_alpha_feedback_linkage
Create Date: 2026-03-21
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260321_habit_stat_table"
down_revision = "20260314_private_alpha_feedback_linkage"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "habits_habit_stat",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("habit_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("current_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("longest_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_rate_30d", sa.Float(), nullable=True),
        sa.Column("total_logs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_logged_at", sa.Date(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["habit_id"],
            ["habits_habit.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("habit_id", name="uq_habits_habit_stat_habit_id"),
    )
    op.create_index(
        "ix_habits_habit_stat_user_id",
        "habits_habit_stat",
        ["user_id"],
    )


def downgrade():
    op.drop_index("ix_habits_habit_stat_user_id", table_name="habits_habit_stat")
    op.drop_table("habits_habit_stat")

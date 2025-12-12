"""add habits tables

Revision ID: 20251209_habits_initial
Revises: 20251208_skills_enhancements
Create Date: 2025-12-09
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251209_habits_initial"
down_revision = "20251208_skills_enhancements"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "habits_habit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("user.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("domain_link", sa.String(length=64)),
        sa.Column(
            "schedule_type",
            sa.String(length=32),
            nullable=False,
            server_default="daily",
        ),
        sa.Column("target_count", sa.Integer()),
        sa.Column("time_of_day", sa.String(length=32)),
        sa.Column("difficulty", sa.String(length=32)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index(
        "ux_habits_habit_user_name", "habits_habit", ["user_id", "name"], unique=True
    )
    op.create_index(
        "ix_habits_habit_user_domain_link", "habits_habit", ["user_id", "domain_link"]
    )

    op.create_table(
        "habits_habit_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("user.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "habit_id",
            sa.Integer(),
            sa.ForeignKey("habits_habit.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("value", sa.Numeric(10, 2)),
        sa.Column("note", sa.Text()),
        sa.Column(
            "logged_date",
            sa.Date(),
            nullable=False,
            server_default=sa.func.current_date(),
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index(
        "ix_habits_log_user_logged_date", "habits_habit_log", ["user_id", "logged_date"]
    )
    op.create_index(
        "ix_habits_log_habit_logged_date",
        "habits_habit_log",
        ["habit_id", "logged_date"],
    )


def downgrade():
    op.drop_index("ix_habits_log_habit_logged_date", table_name="habits_habit_log")
    op.drop_index("ix_habits_log_user_logged_date", table_name="habits_habit_log")
    op.drop_table("habits_habit_log")
    op.drop_index("ix_habits_habit_user_domain_link", table_name="habits_habit")
    op.drop_index("ux_habits_habit_user_name", table_name="habits_habit")
    op.drop_table("habits_habit")

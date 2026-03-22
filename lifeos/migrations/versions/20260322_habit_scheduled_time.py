"""Phase 12d: add scheduled_time column to habits_habit for time-aware cues.

Revision ID: 20260322_habit_scheduled_time
Revises: 20260321_habit_stat_table
Create Date: 2026-03-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260322_habit_scheduled_time"
down_revision = "20260321_habit_stat_table"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("habits_habit", sa.Column("scheduled_time", sa.Time(), nullable=True))


def downgrade():
    op.drop_column("habits_habit", "scheduled_time")

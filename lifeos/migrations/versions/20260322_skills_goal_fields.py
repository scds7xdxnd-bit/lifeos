"""Phase 12 skills v2: add goal fields with safe defaults.

Revision ID: 20260322_skills_goal_fields
Revises: 20260322_habit_scheduled_time
Create Date: 2026-03-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260322_skills_goal_fields"
down_revision = "20260322_habit_scheduled_time"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("skill", sa.Column("goal_type", sa.String(length=32), nullable=True))
    op.add_column("skill", sa.Column("goal_target_value", sa.Integer(), nullable=True))
    op.add_column("skill", sa.Column("goal_deadline", sa.DateTime(timezone=True), nullable=True))

    # Backfill safe defaults for existing skills.
    op.execute("UPDATE skill SET goal_type = 'sessions' WHERE goal_type IS NULL")
    op.execute(
        """
        UPDATE skill
        SET goal_target_value = (
            SELECT COALESCE(COUNT(sps.id), 0) + 8
            FROM skill_practice_session sps
            WHERE sps.skill_id = skill.id
        )
        WHERE goal_target_value IS NULL
        """
    )


def downgrade():
    op.drop_column("skill", "goal_deadline")
    op.drop_column("skill", "goal_target_value")
    op.drop_column("skill", "goal_type")

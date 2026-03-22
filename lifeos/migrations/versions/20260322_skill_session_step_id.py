"""Phase 12 skills v2: add optional step_id to practice sessions.

Revision ID: 20260322_skill_session_step_id
Revises: 20260322_skills_goal_fields
Create Date: 2026-03-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260322_skill_session_step_id"
down_revision = "20260322_skills_goal_fields"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("skill_practice_session", sa.Column("step_id", sa.Integer(), nullable=True))
    op.create_index("ix_skill_session_step_id", "skill_practice_session", ["step_id"], unique=False)


def downgrade():
    op.drop_index("ix_skill_session_step_id", table_name="skill_practice_session")
    op.drop_column("skill_practice_session", "step_id")

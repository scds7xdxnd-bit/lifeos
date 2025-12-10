"""enhance skills tables to match new models

Revision ID: 20251208_skills_enhancements
Revises: 20251207_finance_journal_entry_index
Create Date: 2025-12-08
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20251208_skills_enhancements"
down_revision = "20251207_finance_journal_entry_index"
branch_labels = None
depends_on = None
TWO_PHASE = True


def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)

    def _has_column(table: str, name: str) -> bool:
        return name in {col["name"] for col in inspector.get_columns(table)}

    def _has_index(table: str, name: str) -> bool:
        return any(ix["name"] == name for ix in inspector.get_indexes(table))

    # skill table additions (direct add; SQLite supports ADD COLUMN)
    if not _has_column("skill", "category"):
        op.add_column("skill", sa.Column("category", sa.String(length=128), nullable=True))
    if not _has_column("skill", "difficulty"):
        op.add_column("skill", sa.Column("difficulty", sa.String(length=32), nullable=True))
    if not _has_column("skill", "target_level"):
        op.add_column("skill", sa.Column("target_level", sa.Integer(), nullable=True))
    if not _has_column("skill", "current_level"):
        op.add_column("skill", sa.Column("current_level", sa.Integer(), nullable=True))
    if not _has_column("skill", "description"):
        op.add_column("skill", sa.Column("description", sa.Text(), nullable=True))
    if not _has_column("skill", "tags"):
        op.add_column("skill", sa.Column("tags", sa.JSON(), nullable=True, server_default=sa.text("'[]'")))
    if not _has_column("skill", "updated_at"):
        op.add_column("skill", sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now()))
    if not _has_index("skill", "ux_skill_user_name"):
        op.create_index("ux_skill_user_name", "skill", ["user_id", "name"], unique=True)
    if not _has_index("skill", "ix_skill_user_category"):
        op.create_index("ix_skill_user_category", "skill", ["user_id", "category"])

    # practice session additions (avoid FK constraint on SQLite)
    if not _has_column("skill_practice_session", "user_id"):
        op.add_column("skill_practice_session", sa.Column("user_id", sa.Integer(), nullable=True))
    if not _has_column("skill_practice_session", "intensity"):
        op.add_column("skill_practice_session", sa.Column("intensity", sa.Integer(), nullable=True))
    if not _has_column("skill_practice_session", "created_at"):
        op.add_column("skill_practice_session", sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()))
    if not _has_index("skill_practice_session", "ix_skill_session_user_practiced_at"):
        op.create_index("ix_skill_session_user_practiced_at", "skill_practice_session", ["user_id", "practiced_at"])
    if not _has_index("skill_practice_session", "ix_skill_session_skill_practiced_at"):
        op.create_index("ix_skill_session_skill_practiced_at", "skill_practice_session", ["skill_id", "practiced_at"])

    # best-effort backfill user_id on practice sessions
    op.execute(
        """
        UPDATE skill_practice_session AS s
        SET user_id = (
            SELECT user_id FROM skill WHERE skill.id = s.skill_id
        )
        WHERE user_id IS NULL
        """
    )


def downgrade():
    conn = op.get_bind()
    inspector = inspect(conn)

    def _has_column(table: str, name: str) -> bool:
        return name in {col["name"] for col in inspector.get_columns(table)}

    def _has_index(table: str, name: str) -> bool:
        return any(ix["name"] == name for ix in inspector.get_indexes(table))

    op.execute("UPDATE skill_practice_session SET user_id = NULL")
    if _has_index("skill_practice_session", "ix_skill_session_skill_practiced_at"):
        op.drop_index("ix_skill_session_skill_practiced_at", table_name="skill_practice_session")
    if _has_index("skill_practice_session", "ix_skill_session_user_practiced_at"):
        op.drop_index("ix_skill_session_user_practiced_at", table_name="skill_practice_session")
    if _has_column("skill_practice_session", "created_at"):
        op.drop_column("skill_practice_session", "created_at")
    if _has_column("skill_practice_session", "intensity"):
        op.drop_column("skill_practice_session", "intensity")
    if _has_column("skill_practice_session", "user_id"):
        op.drop_column("skill_practice_session", "user_id")

    if _has_index("skill", "ix_skill_user_category"):
        op.drop_index("ix_skill_user_category", table_name="skill")
    if _has_index("skill", "ux_skill_user_name"):
        op.drop_index("ux_skill_user_name", table_name="skill")
    for col in ("updated_at", "tags", "description", "current_level", "target_level", "difficulty", "category"):
        if _has_column("skill", col):
            op.drop_column("skill", col)

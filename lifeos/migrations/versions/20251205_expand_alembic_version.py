"""Expand alembic_version.version_num to store longer revision IDs."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251205_expand_alembic_version"
down_revision = "20251205_skills_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    # SQLite ignores VARCHAR length and ALTER COLUMN isn't supported; skip there.
    if bind.dialect.name != "sqlite":
        op.alter_column(
            "alembic_version",
            "version_num",
            existing_type=sa.String(length=32),
            type_=sa.String(length=64),
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        op.alter_column(
            "alembic_version",
            "version_num",
            existing_type=sa.String(length=64),
            type_=sa.String(length=32),
        )

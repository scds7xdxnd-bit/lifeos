"""add composite index for finance journal entry

Revision ID: 20251207_finance_journal_entry_index
Revises: 20251205_skills_initial_schema
Create Date: 2025-12-07
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "20251207_finance_journal_entry_index"
down_revision = "20251205_skills_initial_schema"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_finance_journal_entry_user_posted_at",
        "finance_journal_entry",
        ["user_id", "posted_at"],
    )


def downgrade():
    op.drop_index("ix_finance_journal_entry_user_posted_at", table_name="finance_journal_entry")

"""journal v1 enhancements

Revision ID: 20251211_journal_enhancements
Revises: 20251210_relationships_initial
Create Date: 2025-12-11
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251211_journal_enhancements"
down_revision = "20251210_relationships_initial"
branch_labels = None
depends_on = None
TWO_PHASE = True


def upgrade():
    op.add_column("journal_entry", sa.Column("body", sa.Text(), nullable=False, server_default=""))
    op.add_column(
        "journal_entry",
        sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
    )
    op.add_column(
        "journal_entry",
        sa.Column(
            "entry_date",
            sa.Date(),
            nullable=False,
            server_default=sa.func.current_date(),
        ),
    )
    op.add_column(
        "journal_entry",
        sa.Column("is_private", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column("journal_entry", sa.Column("sentiment_score", sa.Numeric(5, 2)))
    op.add_column("journal_entry", sa.Column("emotion_label", sa.String(length=64)))
    op.add_column(
        "journal_entry",
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.add_column("journal_entry", sa.Column("mood_int", sa.Integer()))

    op.execute(
        """
        UPDATE journal_entry
        SET body = content
        WHERE (body IS NULL OR body = '')
        """
    )
    op.execute(
        """
        UPDATE journal_entry
        SET mood_int = CAST(mood AS INTEGER)
        WHERE mood_int IS NULL AND mood IS NOT NULL
        """
    )

    op.create_index("ix_journal_entry_user_entry_date", "journal_entry", ["user_id", "entry_date"])
    op.create_index("ix_journal_entry_user_created_at", "journal_entry", ["user_id", "created_at"])
    op.create_index("ix_journal_entry_user_mood", "journal_entry", ["user_id", "mood_int"])


def downgrade():
    op.drop_index("ix_journal_entry_user_mood", table_name="journal_entry")
    op.drop_index("ix_journal_entry_user_created_at", table_name="journal_entry")
    op.drop_index("ix_journal_entry_user_entry_date", table_name="journal_entry")
    op.drop_column("journal_entry", "mood_int")
    op.drop_column("journal_entry", "updated_at")
    op.drop_column("journal_entry", "emotion_label")
    op.drop_column("journal_entry", "sentiment_score")
    op.drop_column("journal_entry", "is_private")
    op.drop_column("journal_entry", "entry_date")
    op.drop_column("journal_entry", "tags")
    op.drop_column("journal_entry", "body")

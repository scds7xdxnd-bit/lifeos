"""Calendar view/ledger indexes and normalized date columns.

Revision ID: 20251222_calendar_view_indexes
Revises: 20251221_auth_session_table
Create Date: 2025-12-21
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "20251222_calendar_view_indexes"
down_revision = "20251221_auth_session_table"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "calendar_event",
        sa.Column("normalized_start_date", sa.Date(), nullable=True),
    )
    op.add_column(
        "calendar_event",
        sa.Column("normalized_end_date", sa.Date(), nullable=True),
    )

    bind = op.get_bind()
    # Backfill normalized dates for existing rows
    bind.execute(
        text(
            "UPDATE calendar_event "
            "SET normalized_start_date = DATE(start_time), "
            "    normalized_end_date = CASE WHEN end_time IS NOT NULL THEN DATE(end_time) ELSE NULL END "
            "WHERE normalized_start_date IS NULL"
        )
    )

    op.create_index(
        "ix_calendar_event_user_start_end",
        "calendar_event",
        ["user_id", "start_time", "end_time"],
    )
    op.create_index(
        "ix_calendar_event_user_start_id",
        "calendar_event",
        ["user_id", "start_time", "id"],
    )
    op.create_index(
        "ix_calendar_event_user_start_date",
        "calendar_event",
        ["user_id", "normalized_start_date"],
    )
    op.create_index(
        "ix_calendar_event_user_end_date",
        "calendar_event",
        ["user_id", "normalized_end_date"],
    )


def downgrade():
    op.drop_index("ix_calendar_event_user_end_date", table_name="calendar_event")
    op.drop_index("ix_calendar_event_user_start_date", table_name="calendar_event")
    op.drop_index("ix_calendar_event_user_start_id", table_name="calendar_event")
    op.drop_index("ix_calendar_event_user_start_end", table_name="calendar_event")
    op.drop_column("calendar_event", "normalized_end_date")
    op.drop_column("calendar_event", "normalized_start_date")

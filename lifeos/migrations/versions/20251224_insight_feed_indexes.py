"""Add composite index for insight feed filtering.

Revision ID: 20251224_insight_feed_indexes
Revises: 20251223_insight_routing_columns
Create Date: 2025-12-24
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "20251224_insight_feed_indexes"
down_revision = "20251223_insight_routing_columns"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_insight_record_user_event_type_created",
        "insight_record",
        ["user_id", "event_type", "created_at"],
    )


def downgrade():
    op.drop_index("ix_insight_record_user_event_type_created", table_name="insight_record")

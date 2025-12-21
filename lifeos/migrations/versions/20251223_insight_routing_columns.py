"""Add confidence routing columns to insight_record.

Revision ID: 20251223_insight_routing_columns
Revises: 20251222_calendar_view_indexes
Create Date: 2025-12-22
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251223_insight_routing_columns"
down_revision = "20251222_calendar_view_indexes"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("insight_record", sa.Column("confidence_band", sa.String(length=32), nullable=True))
    op.add_column("insight_record", sa.Column("routing", sa.String(length=32), nullable=True))
    op.create_index(
        "ix_insight_record_user_band_created",
        "insight_record",
        ["user_id", "confidence_band", "created_at"],
    )
    op.create_index(
        "ix_insight_record_user_routing_created",
        "insight_record",
        ["user_id", "routing", "created_at"],
    )


def downgrade():
    op.drop_index("ix_insight_record_user_routing_created", table_name="insight_record")
    op.drop_index("ix_insight_record_user_band_created", table_name="insight_record")
    op.drop_column("insight_record", "routing")
    op.drop_column("insight_record", "confidence_band")

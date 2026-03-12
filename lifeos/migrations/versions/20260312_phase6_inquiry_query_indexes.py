"""Phase 6: inquiry query support indexes.

Revision ID: 20260312_phase6_inquiry_query_indexes
Revises: 20260312_phase6_focused_inquiry_v1
Create Date: 2026-03-12
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260312_phase6_inquiry_query_indexes"
down_revision = "20260312_phase6_focused_inquiry_v1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_inquiry_request_user_domain_timeframe",
        "inquiry_request",
        ["user_id", "primary_domain", "timeframe_start", "timeframe_end"],
    )
    op.create_index(
        "ix_inquiry_request_user_hash_asof",
        "inquiry_request",
        ["user_id", "normalized_hash", "as_of_ts"],
    )


def downgrade():
    op.drop_index("ix_inquiry_request_user_hash_asof", table_name="inquiry_request")
    op.drop_index("ix_inquiry_request_user_domain_timeframe", table_name="inquiry_request")

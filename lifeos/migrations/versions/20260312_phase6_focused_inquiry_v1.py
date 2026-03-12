"""Phase 6: focused inquiry v1 tables.

Revision ID: 20260312_phase6_focused_inquiry_v1
Revises: 20260205_phase5c_feature_store_v1
Create Date: 2026-03-12
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260312_phase6_focused_inquiry_v1"
down_revision = "20260205_phase5c_feature_store_v1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "inquiry_request",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("lens", sa.String(length=32), nullable=False),
        sa.Column("primary_domain", sa.String(length=32), nullable=False),
        sa.Column("domains", sa.JSON(), nullable=False),
        sa.Column("timeframe_start", sa.DateTime(), nullable=False),
        sa.Column("timeframe_end", sa.DateTime(), nullable=False),
        sa.Column("as_of_ts", sa.DateTime(), nullable=False),
        sa.Column("normalized_payload", sa.JSON(), nullable=False),
        sa.Column("normalized_hash", sa.String(length=64), nullable=False),
        sa.Column("user_input_context", sa.Text(), nullable=True),
        sa.Column(
            "context_is_non_evidence",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("last_version_number", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("last_version_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_inquiry_request_user_created_at", "inquiry_request", ["user_id", "created_at"])
    op.create_index("ix_inquiry_request_user_normalized_hash", "inquiry_request", ["user_id", "normalized_hash"])
    op.create_index("ix_inquiry_request_user_as_of", "inquiry_request", ["user_id", "as_of_ts"])

    op.create_table(
        "inquiry_brief_version",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("inquiry_id", sa.Integer(), sa.ForeignKey("inquiry_request.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("brief_payload", sa.JSON(), nullable=False),
        sa.Column("brief_hash", sa.String(length=64), nullable=False),
        sa.Column("normalized_hash", sa.String(length=64), nullable=False),
        sa.Column("as_of_ts", sa.DateTime(), nullable=False),
        sa.Column("evidence_refs", sa.JSON(), nullable=False),
        sa.Column("parent_version_id", sa.Integer(), sa.ForeignKey("inquiry_brief_version.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("inquiry_id", "version_number", name="uq_inquiry_version_number"),
    )
    op.create_index(
        "ix_inquiry_brief_user_inquiry_version",
        "inquiry_brief_version",
        ["user_id", "inquiry_id", "version_number"],
    )
    op.create_index("ix_inquiry_brief_created_at", "inquiry_brief_version", ["created_at"])
    op.create_index("ix_inquiry_brief_hash", "inquiry_brief_version", ["brief_hash"])


def downgrade():
    op.drop_index("ix_inquiry_brief_hash", table_name="inquiry_brief_version")
    op.drop_index("ix_inquiry_brief_created_at", table_name="inquiry_brief_version")
    op.drop_index("ix_inquiry_brief_user_inquiry_version", table_name="inquiry_brief_version")
    op.drop_table("inquiry_brief_version")

    op.drop_index("ix_inquiry_request_user_as_of", table_name="inquiry_request")
    op.drop_index("ix_inquiry_request_user_normalized_hash", table_name="inquiry_request")
    op.drop_index("ix_inquiry_request_user_created_at", table_name="inquiry_request")
    op.drop_table("inquiry_request")

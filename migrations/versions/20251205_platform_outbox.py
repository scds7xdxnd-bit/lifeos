"""add platform outbox table

Revision ID: 20251204_platform_outbox
Revises: 20251204_core_user_query_indexes
Create Date: 2025-12-04
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20251204_platform_outbox"
down_revision = "20251204_core_user_query_indexes"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "platform_outbox",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), index=True),
        sa.Column("event_type", sa.String(length=128), nullable=False, index=True),
        sa.Column("payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default="pending",
            index=True,
        ),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "available_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            index=True,
        ),
        sa.Column("last_error", sa.Text()),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index(
        "ix_platform_outbox_user_available_at",
        "platform_outbox",
        ["user_id", "available_at"],
    )
    op.create_index(
        "ix_platform_outbox_user_status",
        "platform_outbox",
        ["user_id", "status", "available_at"],
    )


def downgrade():
    op.drop_index("ix_platform_outbox_user_status", table_name="platform_outbox")
    op.drop_index("ix_platform_outbox_user_available_at", table_name="platform_outbox")
    op.drop_table("platform_outbox")

"""add insight record table

Revision ID: 0002_add_insight_record
Revises: 0001_initial
Create Date: 2025-12-04
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_add_insight_record"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "insight_record",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), index=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("event_record.id"), index=True),
        sa.Column("event_type", sa.String(length=128), nullable=False, index=True),
        sa.Column("kind", sa.String(length=64), nullable=False, index=True),
        sa.Column("message", sa.Text(), nullable=False, server_default=""),
        sa.Column("severity", sa.String(length=16), nullable=False, server_default="info"),
        sa.Column("data", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            index=True,
        ),
    )
    op.create_index(
        "ix_insight_record_user_created_at",
        "insight_record",
        ["user_id", "created_at"],
    )


def downgrade():
    op.drop_index("ix_insight_record_user_created_at", table_name="insight_record")
    op.drop_table("insight_record")

"""Add auth_session table for session lifecycle scaffold.

Revision ID: 20251221_auth_session_table
Revises: 20251220_readmodels_bootstrap
Create Date: 2025-12-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251221_auth_session_table"
down_revision = "20251220_readmodels_bootstrap"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "auth_session",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("lifecycle_state", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("device_id", sa.String(length=128), nullable=True),
        sa.Column("invalidated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.UniqueConstraint("session_id", name="uq_auth_session_session_id"),
    )
    op.create_index("ix_auth_session_user", "auth_session", ["user_id"])
    op.create_index("ix_auth_session_user_state", "auth_session", ["user_id", "lifecycle_state"])


def downgrade():
    op.drop_index("ix_auth_session_user_state", table_name="auth_session")
    op.drop_index("ix_auth_session_user", table_name="auth_session")
    op.drop_table("auth_session")

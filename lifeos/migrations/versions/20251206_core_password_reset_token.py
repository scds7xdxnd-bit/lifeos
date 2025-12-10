"""add password reset token table

Revision ID: 20251206_core_password_reset_token
Revises: 20251205_skills_initial_schema
Create Date: 2025-12-06
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251206_core_password_reset_token"
down_revision = "20251205_expand_alembic_version"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "password_reset_token",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("user.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("jti", sa.String(length=128), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("used_at", sa.DateTime()),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_password_reset_user_expires_at",
        "password_reset_token",
        ["user_id", "expires_at"],
    )
    op.create_index("ix_password_reset_jti", "password_reset_token", ["jti"])


def downgrade():
    op.drop_index("ix_password_reset_jti", table_name="password_reset_token")
    op.drop_index("ix_password_reset_user_expires_at", table_name="password_reset_token")
    op.drop_table("password_reset_token")

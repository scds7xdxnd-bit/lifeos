"""Add calendar OAuth token table for Google/Apple sync.

Revision ID: 20251219_calendar_oauth_tokens
Revises: 20251207_standardize_user_roles
Create Date: 2025-12-07
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20251219_calendar_oauth_tokens"
down_revision = "20251207_standardize_user_roles"
branch_labels = None
depends_on = None

# TWO_PHASE migration: must pass architecture tests
TWO_PHASE = True


def upgrade():
    op.create_table(
        "calendar_oauth_token",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("token_type", sa.String(32), nullable=False, server_default="Bearer"),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("last_sync_at", sa.DateTime(), nullable=True),
        sa.Column("sync_token", sa.String(512), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("error_message", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name="fk_calendar_oauth_token_user"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "provider", name="uq_user_provider"),
    )
    op.create_index("ix_calendar_oauth_token_user_id", "calendar_oauth_token", ["user_id"])


def downgrade():
    op.drop_index("ix_calendar_oauth_token_user_id", table_name="calendar_oauth_token")
    op.drop_table("calendar_oauth_token")

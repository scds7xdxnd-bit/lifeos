"""Private alpha invite persistence.

Revision ID: 20260314_private_alpha_invites
Revises: 20260312_phase8_cross_domain_inquiry_metadata
Create Date: 2026-03-14
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260314_private_alpha_invites"
down_revision = "20260312_phase8_cross_domain_inquiry_metadata"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "private_alpha_invite",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("invited_email", sa.String(length=255), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("issued_by_user_id", sa.Integer(), nullable=True),
        sa.Column("accepted_by_user_id", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["accepted_by_user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["issued_by_user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_private_alpha_invite_email", "private_alpha_invite", ["invited_email"])
    op.create_index("ix_private_alpha_invite_expires", "private_alpha_invite", ["expires_at"])
    op.create_index("ix_private_alpha_invite_accepted", "private_alpha_invite", ["accepted_at"])


def downgrade():
    op.drop_index("ix_private_alpha_invite_accepted", table_name="private_alpha_invite")
    op.drop_index("ix_private_alpha_invite_expires", table_name="private_alpha_invite")
    op.drop_index("ix_private_alpha_invite_email", table_name="private_alpha_invite")
    op.drop_table("private_alpha_invite")

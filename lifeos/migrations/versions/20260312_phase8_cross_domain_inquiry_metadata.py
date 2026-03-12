"""Phase 8: cross-domain inquiry metadata and indexes.

Revision ID: 20260312_phase8_cross_domain_inquiry_metadata
Revises: 20260312_phase7_domain_expert_brief_metadata
Create Date: 2026-03-12
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260312_phase8_cross_domain_inquiry_metadata"
down_revision = "20260312_phase7_domain_expert_brief_metadata"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("inquiry_brief_version", sa.Column("cross_domain_profile", sa.String(length=64), nullable=True))
    op.add_column(
        "inquiry_brief_version",
        sa.Column("cross_domain_profile_version", sa.String(length=16), nullable=True),
    )
    op.add_column("inquiry_brief_version", sa.Column("selected_domains", sa.JSON(), nullable=True))
    op.add_column("inquiry_brief_version", sa.Column("selected_domains_key", sa.String(length=128), nullable=True))
    op.add_column("inquiry_brief_version", sa.Column("blocked_claim_count", sa.Integer(), nullable=True))

    op.create_index(
        "ix_inquiry_brief_user_cross_profile_created",
        "inquiry_brief_version",
        ["user_id", "cross_domain_profile", "created_at"],
    )
    op.create_index(
        "ix_inquiry_brief_user_cross_profile_version_created",
        "inquiry_brief_version",
        ["user_id", "cross_domain_profile_version", "created_at"],
    )
    op.create_index(
        "ix_inquiry_brief_user_selected_domains_created",
        "inquiry_brief_version",
        ["user_id", "selected_domains_key", "created_at"],
    )


def downgrade():
    op.drop_index("ix_inquiry_brief_user_selected_domains_created", table_name="inquiry_brief_version")
    op.drop_index("ix_inquiry_brief_user_cross_profile_version_created", table_name="inquiry_brief_version")
    op.drop_index("ix_inquiry_brief_user_cross_profile_created", table_name="inquiry_brief_version")

    op.drop_column("inquiry_brief_version", "blocked_claim_count")
    op.drop_column("inquiry_brief_version", "selected_domains_key")
    op.drop_column("inquiry_brief_version", "selected_domains")
    op.drop_column("inquiry_brief_version", "cross_domain_profile_version")
    op.drop_column("inquiry_brief_version", "cross_domain_profile")

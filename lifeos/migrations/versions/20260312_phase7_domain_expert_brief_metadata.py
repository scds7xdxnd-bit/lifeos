"""Phase 7: domain expert brief metadata columns and indexes.

Revision ID: 20260312_phase7_domain_expert_brief_metadata
Revises: 20260312_phase6_1_inquiry_quality_metadata
Create Date: 2026-03-12
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260312_phase7_domain_expert_brief_metadata"
down_revision = "20260312_phase6_1_inquiry_quality_metadata"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("inquiry_brief_version", sa.Column("brief_profile", sa.String(length=64), nullable=True))
    op.add_column("inquiry_brief_version", sa.Column("brief_profile_version", sa.String(length=16), nullable=True))
    op.add_column("inquiry_brief_version", sa.Column("brief_strategy", sa.String(length=64), nullable=True))
    op.add_column("inquiry_brief_version", sa.Column("brief_strategy_version", sa.String(length=16), nullable=True))
    op.add_column("inquiry_brief_version", sa.Column("brief_domain", sa.String(length=32), nullable=True))
    op.add_column("inquiry_brief_version", sa.Column("brief_expert_mode", sa.Boolean(), nullable=True))
    op.add_column("inquiry_brief_version", sa.Column("finding_categories", sa.JSON(), nullable=True))

    op.create_index(
        "ix_inquiry_brief_user_domain_created",
        "inquiry_brief_version",
        ["user_id", "brief_domain", "created_at"],
    )
    op.create_index(
        "ix_inquiry_brief_user_expert_created",
        "inquiry_brief_version",
        ["user_id", "brief_expert_mode", "created_at"],
    )
    op.create_index(
        "ix_inquiry_brief_user_profile_created",
        "inquiry_brief_version",
        ["user_id", "brief_profile", "created_at"],
    )
    op.create_index(
        "ix_inquiry_brief_user_domain_quality_created",
        "inquiry_brief_version",
        ["user_id", "brief_domain", "quality_state", "created_at"],
    )


def downgrade():
    op.drop_index("ix_inquiry_brief_user_domain_quality_created", table_name="inquiry_brief_version")
    op.drop_index("ix_inquiry_brief_user_profile_created", table_name="inquiry_brief_version")
    op.drop_index("ix_inquiry_brief_user_expert_created", table_name="inquiry_brief_version")
    op.drop_index("ix_inquiry_brief_user_domain_created", table_name="inquiry_brief_version")

    op.drop_column("inquiry_brief_version", "finding_categories")
    op.drop_column("inquiry_brief_version", "brief_expert_mode")
    op.drop_column("inquiry_brief_version", "brief_domain")
    op.drop_column("inquiry_brief_version", "brief_strategy_version")
    op.drop_column("inquiry_brief_version", "brief_strategy")
    op.drop_column("inquiry_brief_version", "brief_profile_version")
    op.drop_column("inquiry_brief_version", "brief_profile")

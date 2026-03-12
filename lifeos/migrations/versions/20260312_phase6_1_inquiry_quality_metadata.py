"""Phase 6.1: inquiry quality metadata storage and query indexes.

Revision ID: 20260312_phase6_1_inquiry_quality_metadata
Revises: 20260312_phase6_inquiry_query_indexes
Create Date: 2026-03-12
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260312_phase6_1_inquiry_quality_metadata"
down_revision = "20260312_phase6_inquiry_query_indexes"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("inquiry_brief_version", sa.Column("quality_findings_total", sa.Integer(), nullable=True))
    op.add_column("inquiry_brief_version", sa.Column("quality_findings_with_evidence", sa.Integer(), nullable=True))
    op.add_column(
        "inquiry_brief_version",
        sa.Column("quality_evidence_coverage_ratio", sa.Numeric(precision=6, scale=4), nullable=True),
    )
    op.add_column("inquiry_brief_version", sa.Column("quality_structure_gaps", sa.JSON(), nullable=True))
    op.add_column("inquiry_brief_version", sa.Column("quality_sparse_domains", sa.JSON(), nullable=True))
    op.add_column("inquiry_brief_version", sa.Column("quality_refine_guidance", sa.JSON(), nullable=True))
    op.add_column("inquiry_brief_version", sa.Column("quality_state", sa.String(length=32), nullable=True))

    op.create_index(
        "ix_inquiry_brief_user_created_at",
        "inquiry_brief_version",
        ["user_id", "created_at"],
    )
    op.create_index(
        "ix_inquiry_brief_user_quality_state_created",
        "inquiry_brief_version",
        ["user_id", "quality_state", "created_at"],
    )
    op.create_index(
        "ix_inquiry_brief_user_coverage_created",
        "inquiry_brief_version",
        ["user_id", "quality_evidence_coverage_ratio", "created_at"],
    )


def downgrade():
    op.drop_index("ix_inquiry_brief_user_coverage_created", table_name="inquiry_brief_version")
    op.drop_index("ix_inquiry_brief_user_quality_state_created", table_name="inquiry_brief_version")
    op.drop_index("ix_inquiry_brief_user_created_at", table_name="inquiry_brief_version")

    op.drop_column("inquiry_brief_version", "quality_state")
    op.drop_column("inquiry_brief_version", "quality_refine_guidance")
    op.drop_column("inquiry_brief_version", "quality_sparse_domains")
    op.drop_column("inquiry_brief_version", "quality_structure_gaps")
    op.drop_column("inquiry_brief_version", "quality_evidence_coverage_ratio")
    op.drop_column("inquiry_brief_version", "quality_findings_with_evidence")
    op.drop_column("inquiry_brief_version", "quality_findings_total")

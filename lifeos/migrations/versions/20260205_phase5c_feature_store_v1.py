"""Phase 5c: feature store v1.

Revision ID: 20260205_phase5c_feature_store_v1
Revises: 20251227_phase5b_features_daily
Create Date: 2026-02-05
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260205_phase5c_feature_store_v1"
down_revision = "20251227_phase5b_features_daily"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "features_v1",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("entity_type", sa.String(length=32), nullable=False),
        sa.Column("entity_id", sa.String(length=128), nullable=False),
        sa.Column("feature_name", sa.String(length=128), nullable=False),
        sa.Column("dtype", sa.String(length=16), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("window", sa.String(length=32), nullable=False),
        sa.Column("computed_at", sa.DateTime(), nullable=False),
        sa.Column("as_of_ts", sa.DateTime(), nullable=False),
        sa.Column("feature_version", sa.String(length=16), nullable=False),
        sa.Column("source_event_types", sa.JSON(), nullable=True),
        sa.Column("provenance_ref", sa.JSON(), nullable=True),
        sa.Column(
            "backfill_policy",
            sa.String(length=16),
            nullable=False,
            server_default=sa.text("'allowed'"),
        ),
        sa.Column(
            "lifecycle_state",
            sa.String(length=16),
            nullable=False,
            server_default=sa.text("'shadow'"),
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint(
            "user_id",
            "entity_type",
            "entity_id",
            "feature_name",
            "as_of_ts",
            "feature_version",
            name="uq_features_v1_scope_name_asof_version",
        ),
    )
    op.create_index(
        "ix_features_v1_user_name_asof",
        "features_v1",
        ["user_id", "feature_name", "as_of_ts"],
    )
    op.create_index(
        "ix_features_v1_entity_name_asof",
        "features_v1",
        ["entity_type", "entity_id", "feature_name", "as_of_ts"],
    )
    op.create_index(
        "ix_features_v1_name_version",
        "features_v1",
        ["feature_name", "feature_version"],
    )


def downgrade():
    op.drop_index("ix_features_v1_name_version", table_name="features_v1")
    op.drop_index("ix_features_v1_entity_name_asof", table_name="features_v1")
    op.drop_index("ix_features_v1_user_name_asof", table_name="features_v1")
    op.drop_table("features_v1")

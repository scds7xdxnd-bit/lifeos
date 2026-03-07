"""Phase 5b: feature storage + insight delivery metadata.

Revision ID: 20251227_phase5b_features_daily
Revises: 20251226_phase5a_insight_substrate_tables
Create Date: 2025-12-27
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20251227_phase5b_features_daily"
down_revision = "20251226_phase5a_insight_substrate_tables"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "insight_record",
        sa.Column("priority", sa.Integer(), nullable=False, server_default=sa.text("50")),
    )
    op.add_column(
        "insight_record",
        sa.Column("delivery_policy", sa.String(length=32), nullable=False, server_default=sa.text("'feed'")),
    )

    op.create_table(
        "features_daily",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=True),
        sa.Column("feature_date", sa.Date(), nullable=False),
        sa.Column("feature_key", sa.String(length=128), nullable=False),
        sa.Column("feature_value", sa.Numeric(14, 4), nullable=False),
        sa.Column("source_domain", sa.String(length=64), nullable=False),
        sa.Column("definition_version", sa.String(length=16), nullable=False, server_default="v1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint(
            "user_id",
            "feature_date",
            "feature_key",
            "definition_version",
            name="uq_features_daily_user_date_key_version",
        ),
    )
    op.create_index("ix_features_daily_user_date", "features_daily", ["user_id", "feature_date"])
    op.create_index(
        "ix_features_daily_user_key_date",
        "features_daily",
        ["user_id", "feature_key", "feature_date"],
    )


def downgrade():
    op.drop_index("ix_features_daily_user_key_date", table_name="features_daily")
    op.drop_index("ix_features_daily_user_date", table_name="features_daily")
    op.drop_table("features_daily")

    op.drop_column("insight_record", "delivery_policy")
    op.drop_column("insight_record", "priority")

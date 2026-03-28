"""Add calorie report table for health calculator.

Revision ID: 20260328_health_calorie_report
Revises: 20260328_health_food_library
Create Date: 2026-03-28
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260328_health_calorie_report"
down_revision = "20260328_health_food_library"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "health_calorie_report",
        # Identity
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("user.id"), nullable=False, index=True),
        # Input snapshot
        sa.Column("weight_kg", sa.Numeric(10, 2), nullable=False),
        sa.Column("height_cm", sa.Numeric(10, 2), nullable=False),
        sa.Column("age_years", sa.Integer, nullable=False),
        sa.Column("gender", sa.String(16), nullable=False),
        sa.Column("body_fat_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("activity_level", sa.String(32), nullable=False),
        sa.Column("goal_type", sa.String(16), nullable=False),
        sa.Column("goal_weight_kg", sa.Numeric(10, 2), nullable=True),
        sa.Column("goal_timeline_months", sa.Integer, nullable=True),
        # Computed values
        sa.Column("method_used", sa.String(32), nullable=False),
        sa.Column("lean_body_mass", sa.Numeric(10, 2), nullable=True),
        sa.Column("bmr", sa.Numeric(10, 2), nullable=False),
        sa.Column("activity_multiplier", sa.Numeric(4, 3), nullable=False),
        sa.Column("tdee", sa.Numeric(10, 2), nullable=False),
        # Delta breakdown
        sa.Column("delta_bw", sa.Numeric(10, 2), nullable=True),
        sa.Column("total_delta_kcal", sa.Numeric(12, 2), nullable=True),
        sa.Column("delta_kcal_per_day", sa.Numeric(10, 2), nullable=True),
        sa.Column("kcal_per_kg_used", sa.Integer, nullable=True),
        # Daily targets
        sa.Column("daily_calories", sa.Numeric(10, 2), nullable=False),
        sa.Column("protein_g_per_day", sa.Numeric(10, 2), nullable=False),
        sa.Column("fat_g_per_day", sa.Numeric(10, 2), nullable=False),
        sa.Column("carbs_g_per_day", sa.Numeric(10, 2), nullable=False),
        sa.Column("fiber_g_per_day", sa.Numeric(10, 2), nullable=False),
        # Monthly targets (daily × 30)
        sa.Column("monthly_calories", sa.Numeric(12, 2), nullable=False),
        sa.Column("monthly_protein_g", sa.Numeric(10, 2), nullable=False),
        sa.Column("monthly_fat_g", sa.Numeric(10, 2), nullable=False),
        sa.Column("monthly_carbs_g", sa.Numeric(10, 2), nullable=False),
        sa.Column("monthly_fiber_g", sa.Numeric(10, 2), nullable=False),
        # Timestamp
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_health_calorie_report_user_created",
        "health_calorie_report",
        ["user_id", "created_at"],
    )


def downgrade():
    op.drop_index("ix_health_calorie_report_user_created")
    op.drop_table("health_calorie_report")

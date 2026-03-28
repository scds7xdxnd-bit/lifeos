"""Add food library table for health optimizer.

Revision ID: 20260328_health_food_library
Revises: 20260322_skill_session_step_id
Create Date: 2026-03-28
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260328_health_food_library"
down_revision = "20260322_skill_session_step_id"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "health_food_library_item",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("cost_per_100g", sa.Numeric(10, 4), nullable=False),
        sa.Column("calories_per_100g", sa.Numeric(10, 2), nullable=False),
        sa.Column("protein_per_100g", sa.Numeric(10, 2), nullable=False),
        sa.Column("carbohydrate_per_100g", sa.Numeric(10, 2), nullable=False),
        sa.Column("fat_per_100g", sa.Numeric(10, 2), nullable=False),
        sa.Column("fiber_per_100g", sa.Numeric(10, 2), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index(
        "ix_health_food_library_item_user_name",
        "health_food_library_item",
        ["user_id", "name"],
        unique=True,
    )


def downgrade():
    op.drop_index("ix_health_food_library_item_user_name")
    op.drop_table("health_food_library_item")

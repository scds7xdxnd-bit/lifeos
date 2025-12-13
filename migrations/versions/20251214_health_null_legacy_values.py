"""Relax legacy value columns for health rework."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20251214_health_null_legacy_values"
down_revision = "20251213_health_relax_legacy_columns"
branch_labels = None
depends_on = None
TWO_PHASE = True


def upgrade():
    # Backfill blanks where legacy columns are still non-nullable downstream
    op.execute("UPDATE health_biometric SET value = 0 WHERE value IS NULL")
    op.execute("UPDATE health_nutrition_log SET calories = 0 WHERE calories IS NULL")

    with op.batch_alter_table("health_biometric") as batch_op:
        batch_op.alter_column(
            "value",
            existing_type=sa.Numeric(10, 2),
            nullable=True,
            server_default="0",
        )
    with op.batch_alter_table("health_nutrition_log") as batch_op:
        batch_op.alter_column(
            "calories",
            existing_type=sa.Numeric(10, 2),
            nullable=True,
            server_default="0",
        )


def downgrade():
    with op.batch_alter_table("health_biometric") as batch_op:
        batch_op.alter_column(
            "value",
            existing_type=sa.Numeric(10, 2),
            nullable=False,
            server_default=None,
        )
    with op.batch_alter_table("health_nutrition_log") as batch_op:
        batch_op.alter_column(
            "calories",
            existing_type=sa.Numeric(10, 2),
            nullable=False,
            server_default=None,
        )

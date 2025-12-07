"""Make legacy health columns nullable for new schema."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251213_health_relax_legacy_columns"
down_revision = "20251212_health_rework"
branch_labels = None
depends_on = None
TWO_PHASE = True


def upgrade():
    # Allow legacy columns (metric/meal/activity) to be nullable now that new schema paths do not populate them.
    op.execute("UPDATE health_biometric SET metric = '' WHERE metric IS NULL")
    op.execute("UPDATE health_nutrition_log SET meal = '' WHERE meal IS NULL")
    op.execute("UPDATE health_workout SET activity = '' WHERE activity IS NULL")

    with op.batch_alter_table("health_biometric") as batch_op:
        batch_op.alter_column(
            "metric",
            existing_type=sa.String(length=64),
            nullable=True,
            server_default="",
        )
    with op.batch_alter_table("health_nutrition_log") as batch_op:
        batch_op.alter_column(
            "meal",
            existing_type=sa.String(length=128),
            nullable=True,
            server_default="",
        )
    with op.batch_alter_table("health_workout") as batch_op:
        batch_op.alter_column(
            "activity",
            existing_type=sa.String(length=128),
            nullable=True,
            server_default="",
        )


def downgrade():
    with op.batch_alter_table("health_biometric") as batch_op:
        batch_op.alter_column(
            "metric",
            existing_type=sa.String(length=64),
            nullable=False,
            server_default=None,
        )
    with op.batch_alter_table("health_nutrition_log") as batch_op:
        batch_op.alter_column(
            "meal",
            existing_type=sa.String(length=128),
            nullable=False,
            server_default=None,
        )
    with op.batch_alter_table("health_workout") as batch_op:
        batch_op.alter_column(
            "activity",
            existing_type=sa.String(length=128),
            nullable=False,
            server_default=None,
        )

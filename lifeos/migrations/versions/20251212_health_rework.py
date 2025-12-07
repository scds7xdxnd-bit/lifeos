"""Health domain v1 schema."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20251212_health_rework"
down_revision = "20251211_journal_enhancements"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)

    def _has_column(table: str, name: str) -> bool:
        return name in {col["name"] for col in inspector.get_columns(table)}

    def _has_index(table: str, name: str) -> bool:
        return any(ix["name"] == name for ix in inspector.get_indexes(table))

    # health_biometric additions
    if not _has_column("health_biometric", "date"):
        op.add_column("health_biometric", sa.Column("date", sa.Date(), nullable=False, server_default=sa.func.current_date()))
    if not _has_column("health_biometric", "weight"):
        op.add_column("health_biometric", sa.Column("weight", sa.Numeric(10, 2)))
    if not _has_column("health_biometric", "body_fat_pct"):
        op.add_column("health_biometric", sa.Column("body_fat_pct", sa.Numeric(5, 2)))
    if not _has_column("health_biometric", "resting_hr"):
        op.add_column("health_biometric", sa.Column("resting_hr", sa.Integer()))
    if not _has_column("health_biometric", "energy_level"):
        op.add_column("health_biometric", sa.Column("energy_level", sa.Integer()))
    if not _has_column("health_biometric", "stress_level"):
        op.add_column("health_biometric", sa.Column("stress_level", sa.Integer()))
    if not _has_column("health_biometric", "notes"):
        op.add_column("health_biometric", sa.Column("notes", sa.Text()))
    if not _has_column("health_biometric", "created_at"):
        op.add_column("health_biometric", sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
    if not _has_index("health_biometric", "ix_health_biometric_user_date"):
        op.create_index("ix_health_biometric_user_date", "health_biometric", ["user_id", "date"])

    # health_workout additions
    if not _has_column("health_workout", "date"):
        op.add_column("health_workout", sa.Column("date", sa.Date(), nullable=False, server_default=sa.func.current_date()))
    if not _has_column("health_workout", "workout_type"):
        op.add_column("health_workout", sa.Column("workout_type", sa.String(length=64)))
    if not _has_column("health_workout", "intensity"):
        op.add_column("health_workout", sa.Column("intensity", sa.String(length=16)))
    if not _has_column("health_workout", "calories_est"):
        op.add_column("health_workout", sa.Column("calories_est", sa.Numeric(10, 2)))
    if not _has_column("health_workout", "notes"):
        op.add_column("health_workout", sa.Column("notes", sa.Text()))
    if not _has_column("health_workout", "created_at"):
        op.add_column("health_workout", sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
    if not _has_index("health_workout", "ix_health_workout_user_date"):
        op.create_index("ix_health_workout_user_date", "health_workout", ["user_id", "date"])

    # health_nutrition_log additions
    if not _has_column("health_nutrition_log", "date"):
        op.add_column("health_nutrition_log", sa.Column("date", sa.Date(), nullable=False, server_default=sa.func.current_date()))
    if not _has_column("health_nutrition_log", "meal_type"):
        op.add_column("health_nutrition_log", sa.Column("meal_type", sa.String(length=32)))
    if not _has_column("health_nutrition_log", "items"):
        op.add_column("health_nutrition_log", sa.Column("items", sa.Text(), nullable=True))
    if not _has_column("health_nutrition_log", "calories_est"):
        op.add_column("health_nutrition_log", sa.Column("calories_est", sa.Numeric(10, 2)))
    if not _has_column("health_nutrition_log", "quality_score"):
        op.add_column("health_nutrition_log", sa.Column("quality_score", sa.Integer()))
    if not _has_column("health_nutrition_log", "created_at"):
        op.add_column("health_nutrition_log", sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
    if not _has_index("health_nutrition_log", "ix_health_nutrition_log_user_date"):
        op.create_index("ix_health_nutrition_log_user_date", "health_nutrition_log", ["user_id", "date"])


def downgrade():
    # Best-effort cleanup
    if op.get_context().dialect.name != "sqlite":
        op.drop_index("ix_health_nutrition_log_user_date", table_name="health_nutrition_log")
        op.drop_index("ix_health_workout_user_date", table_name="health_workout")
        op.drop_index("ix_health_biometric_user_date", table_name="health_biometric")
        op.drop_column("health_nutrition_log", "created_at")
        op.drop_column("health_nutrition_log", "quality_score")
        op.drop_column("health_nutrition_log", "calories_est")
        op.drop_column("health_nutrition_log", "items")
        op.drop_column("health_nutrition_log", "meal_type")
        op.drop_column("health_nutrition_log", "date")
        op.drop_column("health_workout", "created_at")
        op.drop_column("health_workout", "notes")
        op.drop_column("health_workout", "calories_est")
        op.drop_column("health_workout", "intensity")
        op.drop_column("health_workout", "workout_type")
        op.drop_column("health_workout", "date")
        op.drop_column("health_biometric", "created_at")
        op.drop_column("health_biometric", "notes")
        op.drop_column("health_biometric", "stress_level")
        op.drop_column("health_biometric", "energy_level")
        op.drop_column("health_biometric", "resting_hr")
        op.drop_column("health_biometric", "body_fat_pct")
        op.drop_column("health_biometric", "weight")
        op.drop_column("health_biometric", "date")

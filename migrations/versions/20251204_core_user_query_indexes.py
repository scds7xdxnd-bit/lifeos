"""add user + query dimension indexes

Revision ID: 20251204_core_user_query_indexes
Revises: 0002_add_insight_record
Create Date: 2025-12-04
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "20251204_core_user_query_indexes"
down_revision = "0002_add_insight_record"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_event_record_user_created_at",
        "event_record",
        ["user_id", "created_at"],
    )
    op.create_index(
        "ix_event_record_user_event_type",
        "event_record",
        ["user_id", "event_type"],
    )
    op.create_index(
        "ix_finance_transaction_user_occurred_at",
        "finance_transaction",
        ["user_id", "occurred_at"],
    )
    op.create_index(
        "ix_finance_money_schedule_row_user_event_date",
        "finance_money_schedule_row",
        ["user_id", "event_date"],
    )
    op.create_index(
        "ix_finance_money_schedule_daily_balance_user_as_of",
        "finance_money_schedule_daily_balance",
        ["user_id", "as_of"],
    )
    op.create_index(
        "ix_health_biometric_user_recorded_at",
        "health_biometric",
        ["user_id", "recorded_at"],
    )
    op.create_index(
        "ix_health_workout_user_performed_at",
        "health_workout",
        ["user_id", "performed_at"],
    )
    op.create_index(
        "ix_health_nutrition_log_user_logged_at",
        "health_nutrition_log",
        ["user_id", "logged_at"],
    )
    op.create_index(
        "ix_project_user_created_at",
        "project",
        ["user_id", "created_at"],
    )


def downgrade():
    op.drop_index("ix_project_user_created_at", table_name="project")
    op.drop_index("ix_health_nutrition_log_user_logged_at", table_name="health_nutrition_log")
    op.drop_index("ix_health_workout_user_performed_at", table_name="health_workout")
    op.drop_index("ix_health_biometric_user_recorded_at", table_name="health_biometric")
    op.drop_index(
        "ix_finance_money_schedule_daily_balance_user_as_of",
        table_name="finance_money_schedule_daily_balance",
    )
    op.drop_index("ix_finance_money_schedule_row_user_event_date", table_name="finance_money_schedule_row")
    op.drop_index("ix_finance_transaction_user_occurred_at", table_name="finance_transaction")
    op.drop_index("ix_event_record_user_event_type", table_name="event_record")
    op.drop_index("ix_event_record_user_created_at", table_name="event_record")

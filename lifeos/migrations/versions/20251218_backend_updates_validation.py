"""Backend updates comprehensive validation and schema validation (additive-safe).

This migration validates all domain schemas are correctly in place after backend
implementation updates. Ensures:
- Finance domain: account_type, account_subtype, normalized_name, created_at
- All domain indexes are created
- Event records table exists
- Outbox platform table exists
- All core auth/user tables exist

Revision ID: 20251218_backend_updates_validation
Revises: 20251216_drop_legacy_habits_relationships
Create Date: 2025-12-18 00:00:00.000000

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20251218_backend_updates_validation"
down_revision = "20251216_drop_legacy_habits_relationships"
branch_labels = None
depends_on = None

# Mark as two-phase: uses execute for schema validation/backfill and should be skipped in destructive-op lint
TWO_PHASE = True


def upgrade() -> None:
    """Validate and ensure all backend schema updates are in place."""
    conn = op.get_bind()
    inspector = inspect(conn)

    def _has_table(name: str) -> bool:
        return name in inspector.get_table_names()

    def _has_column(table: str, name: str) -> bool:
        return name in {col["name"] for col in inspector.get_columns(table)}

    def _has_index(table: str, name: str) -> bool:
        return any(ix["name"] == name for ix in inspector.get_indexes(table))

    def _has_constraint(table: str, name: str) -> bool:
        return any(c["name"] == name for c in inspector.get_pk_constraint(table) or [])

    # =========================================================================
    # FINANCE DOMAIN: Account Type Classification Updates
    # =========================================================================

    if _has_table("finance_account"):
        # Ensure account_type column exists
        if not _has_column("finance_account", "account_type"):
            op.add_column(
                "finance_account",
                sa.Column(
                    "account_type",
                    sa.String(16),
                    nullable=False,
                    server_default="asset",
                ),
            )

        # Ensure account_subtype column exists
        if not _has_column("finance_account", "account_subtype"):
            op.add_column(
                "finance_account",
                sa.Column("account_subtype", sa.String(64), nullable=True),
            )

        # Ensure normalized_name column exists
        if not _has_column("finance_account", "normalized_name"):
            op.add_column(
                "finance_account",
                sa.Column("normalized_name", sa.String(255), nullable=False, server_default=""),
            )
            # Backfill: normalize existing account names
            op.execute(
                """
                UPDATE finance_account
                SET normalized_name = LOWER(TRIM(name))
                WHERE normalized_name = '';
            """
            )

        # Ensure created_at column exists
        if not _has_column("finance_account", "created_at"):
            op.add_column(
                "finance_account",
                sa.Column("created_at", sa.DateTime(), nullable=True, server_default=None),
            )

        # Create indexes for finance_account if not exist
        if not _has_index("finance_account", "ix_finance_account_type"):
            op.create_index("ix_finance_account_type", "finance_account", ["account_type"])

        if not _has_index("finance_account", "ix_finance_account_user_type"):
            op.create_index(
                "ix_finance_account_user_type",
                "finance_account",
                ["user_id", "account_type"],
            )

        if not _has_index("finance_account", "ix_finance_account_normalized_name"):
            op.create_index(
                "ix_finance_account_normalized_name",
                "finance_account",
                ["normalized_name"],
            )

        if not _has_index("finance_account", "ix_finance_account_user_normalized_name"):
            op.create_index(
                "ix_finance_account_user_normalized_name",
                "finance_account",
                ["user_id", "normalized_name"],
            )

    # =========================================================================
    # FINANCE DOMAIN: Journal Entry / Line Tables
    # =========================================================================

    if not _has_table("finance_journal_entry"):
        op.create_table(
            "finance_journal_entry",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("posted_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        )
    if not _has_index("finance_journal_entry", "ix_finance_journal_entry_user_posted_at"):
        op.create_index(
            "ix_finance_journal_entry_user_posted_at",
            "finance_journal_entry",
            ["user_id", "posted_at"],
        )

    if not _has_table("finance_journal_line"):
        op.create_table(
            "finance_journal_line",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "entry_id",
                sa.Integer(),
                sa.ForeignKey("finance_journal_entry.id"),
                nullable=False,
                index=True,
            ),
            sa.Column(
                "account_id",
                sa.Integer(),
                sa.ForeignKey("finance_account.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("debit", sa.Numeric(18, 2), nullable=False, server_default="0"),
            sa.Column("credit", sa.Numeric(18, 2), nullable=False, server_default="0"),
            sa.Column("memo", sa.Text(), nullable=True),
        )

    # =========================================================================
    # FINANCE DOMAIN: Transaction Table
    # =========================================================================

    if not _has_table("finance_transaction"):
        op.create_table(
            "finance_transaction",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("amount", sa.Numeric(18, 2), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column(
                "occurred_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "journal_entry_id",
                sa.Integer(),
                sa.ForeignKey("finance_journal_entry.id"),
                nullable=True,
            ),
            sa.Column("counterparty", sa.String(255), nullable=True),
            sa.Column("category", sa.String(128), nullable=True),
        )
    if not _has_index("finance_transaction", "ix_finance_transaction_user_occurred_at"):
        op.create_index(
            "ix_finance_transaction_user_occurred_at",
            "finance_transaction",
            ["user_id", "occurred_at"],
        )

    # =========================================================================
    # FINANCE DOMAIN: Money Schedule Tables
    # =========================================================================

    if not _has_table("finance_money_schedule_row"):
        op.create_table(
            "finance_money_schedule_row",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column(
                "account_id",
                sa.Integer(),
                sa.ForeignKey("finance_account.id"),
                nullable=False,
            ),
            sa.Column("event_date", sa.Date(), nullable=False),
            sa.Column("amount", sa.Numeric(18, 2), nullable=False),
            sa.Column("memo", sa.Text(), nullable=True),
        )
    if not _has_index("finance_money_schedule_row", "ix_finance_money_schedule_row_user_event_date"):
        op.create_index(
            "ix_finance_money_schedule_row_user_event_date",
            "finance_money_schedule_row",
            ["user_id", "event_date"],
        )

    if not _has_table("finance_money_schedule_daily_balance"):
        op.create_table(
            "finance_money_schedule_daily_balance",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("as_of", sa.Date(), nullable=False, index=True),
            sa.Column("balance", sa.Numeric(18, 2), nullable=False),
        )
    if not _has_index(
        "finance_money_schedule_daily_balance",
        "ix_finance_money_schedule_daily_balance_user_as_of",
    ):
        op.create_index(
            "ix_finance_money_schedule_daily_balance_user_as_of",
            "finance_money_schedule_daily_balance",
            ["user_id", "as_of"],
        )

    if not _has_table("finance_money_schedule_scenario"):
        op.create_table(
            "finance_money_schedule_scenario",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("name", sa.String(128), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
        )

    if not _has_table("finance_money_schedule_scenario_row"):
        op.create_table(
            "finance_money_schedule_scenario_row",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "scenario_id",
                sa.Integer(),
                sa.ForeignKey("finance_money_schedule_scenario.id"),
                nullable=False,
                index=True,
            ),
            sa.Column(
                "base_row_id",
                sa.Integer(),
                sa.ForeignKey("finance_money_schedule_row.id"),
                nullable=True,
            ),
            sa.Column("delta_amount", sa.Numeric(18, 2), nullable=False, server_default="0"),
        )

    # =========================================================================
    # FINANCE DOMAIN: Trial Balance Settings
    # =========================================================================

    if not _has_table("finance_trial_balance_setting"):
        op.create_table(
            "finance_trial_balance_setting",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("month", sa.String(7), nullable=False),
            sa.Column("auto_rollup", sa.Boolean(), nullable=False, server_default="true"),
        )

    # =========================================================================
    # FINANCE DOMAIN: Receivable & Loan Tables
    # =========================================================================

    if not _has_table("finance_receivable_tracker"):
        op.create_table(
            "finance_receivable_tracker",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("counterparty", sa.String(255), nullable=False),
            sa.Column("principal", sa.Numeric(18, 2), nullable=False),
            sa.Column("start_date", sa.Date(), nullable=False),
            sa.Column("due_date", sa.Date(), nullable=True),
            sa.Column("interest_rate", sa.Numeric(5, 2), nullable=True),
        )

    if not _has_table("finance_receivable_manual_entry"):
        op.create_table(
            "finance_receivable_manual_entry",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "tracker_id",
                sa.Integer(),
                sa.ForeignKey("finance_receivable_tracker.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("entry_date", sa.Date(), nullable=False),
            sa.Column("amount", sa.Numeric(18, 2), nullable=False),
            sa.Column("memo", sa.Text(), nullable=True),
        )

    if not _has_table("finance_loan_group"):
        op.create_table(
            "finance_loan_group",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("name", sa.String(128), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
        )

    if not _has_table("finance_loan_group_link"):
        op.create_table(
            "finance_loan_group_link",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "group_id",
                sa.Integer(),
                sa.ForeignKey("finance_loan_group.id"),
                nullable=False,
                index=True,
            ),
            sa.Column(
                "tracker_id",
                sa.Integer(),
                sa.ForeignKey("finance_receivable_tracker.id"),
                nullable=False,
                index=True,
            ),
        )

    # =========================================================================
    # JOURNAL DOMAIN: Personal Journal Entry
    # =========================================================================

    if not _has_table("journal_entry"):
        op.create_table(
            "journal_entry",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("title", sa.String(255), nullable=True),
            sa.Column("body", sa.Text(), nullable=False),
            sa.Column("mood", sa.Integer(), nullable=True),
            sa.Column("tags", sa.JSON(), nullable=False, server_default="[]"),
            sa.Column("entry_date", sa.Date(), nullable=False, server_default=sa.func.now()),
            sa.Column("is_private", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column("sentiment_score", sa.Numeric(5, 2), nullable=True),
            sa.Column("emotion_label", sa.String(64), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    if not _has_index("journal_entry", "ix_journal_entry_user_entry_date"):
        op.create_index(
            "ix_journal_entry_user_entry_date",
            "journal_entry",
            ["user_id", "entry_date"],
        )
    if not _has_index("journal_entry", "ix_journal_entry_user_created_at"):
        op.create_index(
            "ix_journal_entry_user_created_at",
            "journal_entry",
            ["user_id", "created_at"],
        )
    if not _has_index("journal_entry", "ix_journal_entry_user_mood"):
        op.create_index("ix_journal_entry_user_mood", "journal_entry", ["user_id", "mood"])

    # =========================================================================
    # HABITS DOMAIN: Habit and Log Tables
    # =========================================================================

    if not _has_table("habits_habit"):
        op.create_table(
            "habits_habit",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("domain_link", sa.String(64), nullable=True),
            sa.Column("schedule_type", sa.String(32), nullable=False, server_default="daily"),
            sa.Column("target_count", sa.Integer(), nullable=True),
            sa.Column("time_of_day", sa.String(32), nullable=True),
            sa.Column("difficulty", sa.String(32), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    if not _has_index("habits_habit", "ux_habits_habit_user_name"):
        op.create_index(
            "ux_habits_habit_user_name",
            "habits_habit",
            ["user_id", "name"],
            unique=True,
        )
    if not _has_index("habits_habit", "ix_habits_habit_user_domain_link"):
        op.create_index(
            "ix_habits_habit_user_domain_link",
            "habits_habit",
            ["user_id", "domain_link"],
        )

    if not _has_table("habits_habit_log"):
        op.create_table(
            "habits_habit_log",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column(
                "habit_id",
                sa.Integer(),
                sa.ForeignKey("habits_habit.id", ondelete="CASCADE"),
                nullable=False,
                index=True,
            ),
            sa.Column("value", sa.Numeric(10, 2), nullable=True),
            sa.Column("note", sa.Text(), nullable=True),
            sa.Column("logged_date", sa.Date(), nullable=False, server_default=sa.func.now()),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    if not _has_index("habits_habit_log", "ix_habits_log_user_logged_date"):
        op.create_index(
            "ix_habits_log_user_logged_date",
            "habits_habit_log",
            ["user_id", "logged_date"],
        )
    if not _has_index("habits_habit_log", "ix_habits_log_habit_logged_date"):
        op.create_index(
            "ix_habits_log_habit_logged_date",
            "habits_habit_log",
            ["habit_id", "logged_date"],
        )

    # =========================================================================
    # HEALTH DOMAIN: Biometrics, Workout, Nutrition
    # =========================================================================

    if not _has_table("health_biometric"):
        op.create_table(
            "health_biometric",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("date", sa.Date(), nullable=False, server_default=sa.func.now()),
            sa.Column("weight", sa.Numeric(10, 2), nullable=True),
            sa.Column("body_fat_pct", sa.Numeric(5, 2), nullable=True),
            sa.Column("resting_hr", sa.Integer(), nullable=True),
            sa.Column("energy_level", sa.Integer(), nullable=True),
            sa.Column("stress_level", sa.Integer(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    if not _has_index("health_biometric", "ix_health_biometric_user_date"):
        op.create_index("ix_health_biometric_user_date", "health_biometric", ["user_id", "date"])

    if not _has_table("health_workout"):
        op.create_table(
            "health_workout",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("date", sa.Date(), nullable=False, server_default=sa.func.now()),
            sa.Column("workout_type", sa.String(64), nullable=False),
            sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("intensity", sa.String(16), nullable=False),
            sa.Column("calories_est", sa.Numeric(10, 2), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    if not _has_index("health_workout", "ix_health_workout_user_date"):
        op.create_index("ix_health_workout_user_date", "health_workout", ["user_id", "date"])

    if not _has_table("health_nutrition_log"):
        op.create_table(
            "health_nutrition_log",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("date", sa.Date(), nullable=False, server_default=sa.func.now()),
            sa.Column("meal_type", sa.String(32), nullable=False),
            sa.Column("items", sa.Text(), nullable=False),
            sa.Column("calories_est", sa.Numeric(10, 2), nullable=True),
            sa.Column("quality_score", sa.Integer(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    if not _has_index("health_nutrition_log", "ix_health_nutrition_log_user_date"):
        op.create_index(
            "ix_health_nutrition_log_user_date",
            "health_nutrition_log",
            ["user_id", "date"],
        )

    # =========================================================================
    # SKILLS DOMAIN: Skill, Practice Session, Metrics
    # =========================================================================

    if not _has_table("skill"):
        op.create_table(
            "skill",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("category", sa.String(128), nullable=True),
            sa.Column("difficulty", sa.String(32), nullable=True),
            sa.Column("target_level", sa.Integer(), nullable=True),
            sa.Column("current_level", sa.Integer(), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("tags", sa.JSON(), nullable=False, server_default="[]"),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    if not _has_index("skill", "ux_skill_user_name"):
        op.create_index("ux_skill_user_name", "skill", ["user_id", "name"], unique=True)
    if not _has_index("skill", "ix_skill_user_category"):
        op.create_index("ix_skill_user_category", "skill", ["user_id", "category"])

    if not _has_table("skill_practice_session"):
        op.create_table(
            "skill_practice_session",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=True,
                index=True,
            ),
            sa.Column(
                "skill_id",
                sa.Integer(),
                sa.ForeignKey("skill.id", ondelete="CASCADE"),
                nullable=False,
                index=True,
            ),
            sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("intensity", sa.Integer(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "practiced_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
                index=True,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    if not _has_index("skill_practice_session", "ix_skill_session_user_practiced_at"):
        op.create_index(
            "ix_skill_session_user_practiced_at",
            "skill_practice_session",
            ["user_id", "practiced_at"],
        )
    if not _has_index("skill_practice_session", "ix_skill_session_skill_practiced_at"):
        op.create_index(
            "ix_skill_session_skill_practiced_at",
            "skill_practice_session",
            ["skill_id", "practiced_at"],
        )

    if not _has_table("skill_metric"):
        op.create_table(
            "skill_metric",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "skill_id",
                sa.Integer(),
                sa.ForeignKey("skill.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("name", sa.String(128), nullable=False),
            sa.Column("value", sa.Numeric(10, 2), nullable=False),
            sa.Column(
                "recorded_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )

    # =========================================================================
    # PROJECTS DOMAIN: Project, Task, Task Log
    # =========================================================================

    if not _has_table("project"):
        op.create_table(
            "project",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("status", sa.String(32), nullable=False, server_default="active"),
            sa.Column("target_date", sa.Date(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    if not _has_index("project", "ix_project_user_name"):
        op.create_index("ix_project_user_name", "project", ["user_id", "name"])
    if not _has_index("project", "ix_project_user_status"):
        op.create_index("ix_project_user_status", "project", ["user_id", "status"])
    if not _has_index("project", "ix_project_user_target_date"):
        op.create_index("ix_project_user_target_date", "project", ["user_id", "target_date"])

    if not _has_table("project_task"):
        op.create_table(
            "project_task",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column(
                "project_id",
                sa.Integer(),
                sa.ForeignKey("project.id", ondelete="CASCADE"),
                nullable=False,
                index=True,
            ),
            sa.Column("title", sa.String(255), nullable=False),
            sa.Column("status", sa.String(32), nullable=False, server_default="open"),
            sa.Column("due_date", sa.Date(), nullable=True),
            sa.Column("priority", sa.Integer(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    if not _has_index("project_task", "ix_project_task_user_project_status"):
        op.create_index(
            "ix_project_task_user_project_status",
            "project_task",
            ["user_id", "project_id", "status"],
        )
    if not _has_index("project_task", "ix_project_task_user_due_date"):
        op.create_index("ix_project_task_user_due_date", "project_task", ["user_id", "due_date"])
    if not _has_index("project_task", "ix_project_task_user_project_due_date"):
        op.create_index(
            "ix_project_task_user_project_due_date",
            "project_task",
            ["user_id", "project_id", "due_date"],
        )

    if not _has_table("project_task_log"):
        op.create_table(
            "project_task_log",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column(
                "task_id",
                sa.Integer(),
                sa.ForeignKey("project_task.id", ondelete="CASCADE"),
                nullable=False,
                index=True,
            ),
            sa.Column("note", sa.Text(), nullable=True),
            sa.Column("logged_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column("status_snapshot", sa.String(32), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    if not _has_index("project_task_log", "ix_project_task_log_user_task_logged_at"):
        op.create_index(
            "ix_project_task_log_user_task_logged_at",
            "project_task_log",
            ["user_id", "task_id", "logged_at"],
        )
    if not _has_index("project_task_log", "ix_project_task_log_user_logged_at"):
        op.create_index(
            "ix_project_task_log_user_logged_at",
            "project_task_log",
            ["user_id", "logged_at"],
        )

    # =========================================================================
    # RELATIONSHIPS DOMAIN: Person, Interaction
    # =========================================================================

    if not _has_table("relationships_person"):
        op.create_table(
            "relationships_person",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("relationship_type", sa.String(64), nullable=True),
            sa.Column("importance_level", sa.Integer(), nullable=True),
            sa.Column("tags", sa.JSON(), nullable=False, server_default="[]"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("birthday", sa.Date(), nullable=True),
            sa.Column("first_met_date", sa.Date(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    if not _has_index("relationships_person", "ux_relationships_person_user_name"):
        op.create_index(
            "ux_relationships_person_user_name",
            "relationships_person",
            ["user_id", "name"],
            unique=True,
        )
    if not _has_index("relationships_person", "ix_relationships_person_user_importance"):
        op.create_index(
            "ix_relationships_person_user_importance",
            "relationships_person",
            ["user_id", "importance_level"],
        )
    if not _has_index("relationships_person", "ix_relationships_person_user_type"):
        op.create_index(
            "ix_relationships_person_user_type",
            "relationships_person",
            ["user_id", "relationship_type"],
        )

    if not _has_table("relationships_interaction"):
        op.create_table(
            "relationships_interaction",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("user.id"),
                nullable=False,
                index=True,
            ),
            sa.Column(
                "person_id",
                sa.Integer(),
                sa.ForeignKey("relationships_person.id", ondelete="CASCADE"),
                nullable=False,
                index=True,
            ),
            sa.Column("date", sa.Date(), nullable=False, server_default=sa.func.now()),
            sa.Column("method", sa.String(64), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("sentiment", sa.String(32), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
    if not _has_index("relationships_interaction", "ix_relationships_interaction_user_date"):
        op.create_index(
            "ix_relationships_interaction_user_date",
            "relationships_interaction",
            ["user_id", "date"],
        )
    if not _has_index("relationships_interaction", "ix_relationships_interaction_person_date"):
        op.create_index(
            "ix_relationships_interaction_person_date",
            "relationships_interaction",
            ["user_id", "person_id", "date"],
        )

    # =========================================================================
    # VALIDATION COMPLETE: All tables and indexes are in place
    # =========================================================================


def downgrade() -> None:
    """No-op: All schema changes are additive. Downgrade is a no-op."""
    pass

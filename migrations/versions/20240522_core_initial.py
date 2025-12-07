"""initial schema for LifeOS

Revision ID: 0001_initial
Revises:
Create Date: 2024-05-22
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "permission",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=128), nullable=False, unique=True),
        sa.Column("description", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table(
        "role",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=64), nullable=False, unique=True),
        sa.Column("description", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255)),
        sa.Column("timezone", sa.String(length=64)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table(
        "jwt_blocklist",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("jti", sa.String(length=64), nullable=False, unique=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("user.id")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table(
        "session_token",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("jti", sa.String(length=64), nullable=False, unique=True),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("expires_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table(
        "user_preference",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_table(
        "role_permission",
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("role.id"), primary_key=True),
        sa.Column("permission_id", sa.Integer(), sa.ForeignKey("permission.id"), primary_key=True),
    )
    op.create_table(
        "user_role",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), primary_key=True),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("role.id"), primary_key=True),
    )
    op.create_table(
        "event_record",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_type", sa.String(length=128), nullable=False, index=True),
        sa.Column("payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), index=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "finance_account_category",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=16), nullable=False, unique=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("normal_balance", sa.String(length=8), nullable=False, server_default="debit"),
    )
    op.create_table(
        "finance_account",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("finance_account_category.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=32), index=True),
        sa.Column("description", sa.Text()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "finance_journal_entry",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("description", sa.Text()),
        sa.Column("posted_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "finance_journal_line",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entry_id", sa.Integer(), sa.ForeignKey("finance_journal_entry.id"), nullable=False, index=True),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("finance_account.id"), nullable=False, index=True),
        sa.Column("debit", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("credit", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("memo", sa.Text()),
    )
    op.create_table(
        "finance_transaction",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("occurred_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("journal_entry_id", sa.Integer(), sa.ForeignKey("finance_journal_entry.id")),
        sa.Column("counterparty", sa.String(length=255)),
        sa.Column("category", sa.String(length=128)),
    )
    op.create_table(
        "finance_trial_balance_setting",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("month", sa.String(length=7), nullable=False),
        sa.Column("auto_rollup", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "finance_money_schedule_row",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("finance_account.id"), nullable=False),
        sa.Column("event_date", sa.Date(), nullable=False, index=True),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("memo", sa.Text()),
    )
    op.create_table(
        "finance_money_schedule_daily_balance",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("as_of", sa.Date(), nullable=False, index=True),
        sa.Column("balance", sa.Numeric(18, 2), nullable=False),
    )
    op.create_table(
        "finance_money_schedule_scenario",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text()),
    )
    op.create_table(
        "finance_money_schedule_scenario_row",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("scenario_id", sa.Integer(), sa.ForeignKey("finance_money_schedule_scenario.id"), nullable=False, index=True),
        sa.Column("base_row_id", sa.Integer(), sa.ForeignKey("finance_money_schedule_row.id")),
        sa.Column("delta_amount", sa.Numeric(18, 2), nullable=False, server_default="0"),
    )
    op.create_table(
        "finance_receivable_tracker",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("counterparty", sa.String(length=255), nullable=False),
        sa.Column("principal", sa.Numeric(18, 2), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date()),
        sa.Column("interest_rate", sa.Numeric(5, 2)),
    )
    op.create_table(
        "finance_receivable_manual_entry",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tracker_id", sa.Integer(), sa.ForeignKey("finance_receivable_tracker.id"), nullable=False, index=True),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("memo", sa.Text()),
    )
    op.create_table(
        "finance_loan_group",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text()),
    )
    op.create_table(
        "finance_loan_group_link",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("group_id", sa.Integer(), sa.ForeignKey("finance_loan_group.id"), nullable=False, index=True),
        sa.Column("tracker_id", sa.Integer(), sa.ForeignKey("finance_receivable_tracker.id"), nullable=False, index=True),
    )
    op.create_table(
        "habit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("cadence", sa.String(length=32), nullable=False, server_default="daily"),
        sa.Column("target", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "habit_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("habit_id", sa.Integer(), sa.ForeignKey("habit.id"), nullable=False, index=True),
        sa.Column("logged_date", sa.Date(), nullable=False, index=True),
        sa.Column("value", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_table(
        "skill",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("level", sa.String(length=32), nullable=False, server_default="beginner"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "skill_practice_session",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skill.id"), nullable=False, index=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text()),
        sa.Column("practiced_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "skill_metric",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skill.id"), nullable=False, index=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("value", sa.Numeric(10, 2), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "health_biometric",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("metric", sa.String(length=64), nullable=False),
        sa.Column("value", sa.Numeric(10, 2), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "health_workout",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("activity", sa.String(length=128), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("calories", sa.Numeric(10, 2)),
        sa.Column("performed_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "health_nutrition_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("meal", sa.String(length=128), nullable=False),
        sa.Column("calories", sa.Numeric(10, 2), nullable=False),
        sa.Column("protein", sa.Numeric(10, 2)),
        sa.Column("carbs", sa.Numeric(10, 2)),
        sa.Column("fat", sa.Numeric(10, 2)),
        sa.Column("logged_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "journal_entry",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("title", sa.String(length=255)),
        sa.Column("content", sa.Text()),
        sa.Column("mood", sa.String(length=32)),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "journal_tag",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=64), nullable=False, unique=True),
    )
    op.create_table(
        "journal_entry_tag",
        sa.Column("entry_id", sa.Integer(), sa.ForeignKey("journal_entry.id"), primary_key=True),
        sa.Column("tag_id", sa.Integer(), sa.ForeignKey("journal_tag.id"), primary_key=True),
    )
    op.create_table(
        "relationship_contact",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255)),
        sa.Column("phone", sa.String(length=64)),
        sa.Column("closeness", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_table(
        "relationship_interaction",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("contact_id", sa.Integer(), sa.ForeignKey("relationship_contact.id"), nullable=False, index=True),
        sa.Column("occurred_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("notes", sa.Text()),
        sa.Column("sentiment", sa.String(length=32)),
    )
    op.create_table(
        "project",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False, index=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "project_task",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("project.id"), nullable=False, index=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="open"),
        sa.Column("due_date", sa.Date()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "project_task_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("project_task.id"), nullable=False, index=True),
        sa.Column("note", sa.Text()),
        sa.Column("logged_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("project_task_log")
    op.drop_table("project_task")
    op.drop_table("project")
    op.drop_table("relationship_interaction")
    op.drop_table("relationship_contact")
    op.drop_table("journal_entry_tag")
    op.drop_table("journal_tag")
    op.drop_table("journal_entry")
    op.drop_table("health_nutrition_log")
    op.drop_table("health_workout")
    op.drop_table("health_biometric")
    op.drop_table("skill_metric")
    op.drop_table("skill_practice_session")
    op.drop_table("skill")
    op.drop_table("habit_log")
    op.drop_table("habit")
    op.drop_table("finance_loan_group_link")
    op.drop_table("finance_loan_group")
    op.drop_table("finance_receivable_manual_entry")
    op.drop_table("finance_receivable_tracker")
    op.drop_table("finance_money_schedule_scenario_row")
    op.drop_table("finance_money_schedule_scenario")
    op.drop_table("finance_money_schedule_daily_balance")
    op.drop_table("finance_money_schedule_row")
    op.drop_table("finance_trial_balance_setting")
    op.drop_table("finance_transaction")
    op.drop_table("finance_journal_line")
    op.drop_table("finance_journal_entry")
    op.drop_table("finance_account")
    op.drop_table("finance_account_category")
    op.drop_table("event_record")
    op.drop_table("user_role")
    op.drop_table("role_permission")
    op.drop_table("user_preference")
    op.drop_table("session_token")
    op.drop_table("jwt_blocklist")
    op.drop_table("user")
    op.drop_table("role")
    op.drop_table("permission")

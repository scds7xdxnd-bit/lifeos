"""Align schema with Phase 3a models across calendar, finance, health, journal, projects, and skills.

Key changes:
- Tighten nullability/defaults for calendar events/interpretations and OAuth tokens.
- Relax finance_account.category_id, normalize finance categories, and add missing indexes.
- Standardize inference score types and calendar_event references across domains.
- Normalize journal mood column to integer while keeping legacy fields intact.
- Harden project/task metadata and skill telemetry fields.
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text

# revision identifiers, used by Alembic.
revision = "0c76fa610e14"
down_revision = "20251219_calendar_oauth_tokens"
branch_labels = None
depends_on = None

# Two-phase to permit alter_column/batch changes in alignment with architecture constraints.
TWO_PHASE = True


def _has_index(table: str, name: str) -> bool:
    inspector = inspect(op.get_bind())
    return any(ix["name"] == name for ix in inspector.get_indexes(table))


def _has_index_columns(table: str, columns: list[str]) -> bool:
    inspector = inspect(op.get_bind())
    cols = tuple(columns)
    for ix in inspector.get_indexes(table):
        if tuple(ix["column_names"]) == cols:
            return True
    return False


def _set_default_if_null(table: str, column: str, default_sql: str) -> None:
    op.execute(text(f"UPDATE {table} SET {column} = {default_sql} WHERE {column} IS NULL"))


def _create_fk_if_supported(
    table: str,
    constraint_name: str,
    referent: str,
    local_cols: list[str],
    remote_cols: list[str],
    ondelete: str | None = None,
) -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        # SQLite cannot add FK constraints without table rebuild; skip to keep migration safe.
        return
    inspector = inspect(bind)
    if any(fk["name"] == constraint_name for fk in inspector.get_foreign_keys(table)):
        return
    op.create_foreign_key(constraint_name, table, referent, local_cols, remote_cols, ondelete=ondelete)


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    # Calendar events: enforce JSON/timestamp defaults and add helper indexes.
    _set_default_if_null("calendar_event", "tags", "'[]'")
    _set_default_if_null("calendar_event", "metadata", "'{}'")
    _set_default_if_null("calendar_event", "created_at", "CURRENT_TIMESTAMP")
    _set_default_if_null("calendar_event", "updated_at", "CURRENT_TIMESTAMP")
    with op.batch_alter_table("calendar_event") as batch:
        batch.alter_column(
            "tags",
            existing_type=sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        )
        batch.alter_column(
            "metadata",
            existing_type=sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        )
        batch.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )
        batch.alter_column(
            "updated_at",
            existing_type=sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )
    if not _has_index("calendar_event", "ix_calendar_event_user_id"):
        op.create_index("ix_calendar_event_user_id", "calendar_event", ["user_id"])
    if not _has_index_columns("calendar_event", ["start_time"]):
        op.create_index("ix_calendar_event_start_time", "calendar_event", ["start_time"])

    # Calendar interpretations: tighten types/nullability and ensure lookup indexes.
    _set_default_if_null("calendar_event_interpretation", "classification_data", "'{}'")
    _set_default_if_null("calendar_event_interpretation", "created_at", "CURRENT_TIMESTAMP")
    _set_default_if_null("calendar_event_interpretation", "updated_at", "CURRENT_TIMESTAMP")
    with op.batch_alter_table("calendar_event_interpretation") as batch:
        batch.alter_column(
            "domain",
            existing_type=sa.String(length=50),
            type_=sa.String(length=32),
            nullable=False,
        )
        batch.alter_column(
            "record_type",
            existing_type=sa.String(length=50),
            type_=sa.String(length=64),
            nullable=False,
        )
        batch.alter_column(
            "confidence_score",
            existing_type=sa.Float(),
            type_=sa.Numeric(3, 2),
            nullable=False,
        )
        batch.alter_column(
            "status",
            existing_type=sa.String(length=20),
            type_=sa.String(length=16),
            nullable=False,
            server_default=sa.text("'inferred'"),
        )
        batch.alter_column(
            "classification_data",
            existing_type=sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        )
        batch.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )
        batch.alter_column(
            "updated_at",
            existing_type=sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )
    if not _has_index_columns("calendar_event_interpretation", ["calendar_event_id"]):
        op.create_index(
            "ix_calendar_event_interpretation_calendar_event_id",
            "calendar_event_interpretation",
            ["calendar_event_id"],
        )
    if not _has_index_columns("calendar_event_interpretation", ["user_id"]):
        op.create_index(
            "ix_calendar_event_interpretation_user_id",
            "calendar_event_interpretation",
            ["user_id"],
        )

    # Calendar OAuth tokens: timestamps required for rotation/monitoring.
    _set_default_if_null("calendar_oauth_token", "created_at", "CURRENT_TIMESTAMP")
    _set_default_if_null("calendar_oauth_token", "updated_at", "CURRENT_TIMESTAMP")
    with op.batch_alter_table("calendar_oauth_token") as batch:
        batch.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )
        batch.alter_column(
            "updated_at",
            existing_type=sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )

    # Event audit: index by created_at for feed ordering.
    if not _has_index_columns("event_record", ["created_at"]):
        op.create_index("ix_event_record_created_at", "event_record", ["created_at"])

    # Finance: account classification updates.
    _set_default_if_null("finance_account", "created_at", "CURRENT_TIMESTAMP")
    with op.batch_alter_table("finance_account") as batch:
        batch.alter_column("category_id", existing_type=sa.Integer(), nullable=True)
        batch.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )

    op.execute(text("UPDATE finance_account_category SET slug = lower(name) WHERE slug IS NULL OR slug = ''"))
    _set_default_if_null("finance_account_category", "created_at", "CURRENT_TIMESTAMP")
    _set_default_if_null("finance_account_category", "updated_at", "CURRENT_TIMESTAMP")
    with op.batch_alter_table("finance_account_category") as batch:
        batch.alter_column("slug", existing_type=sa.String(length=128), nullable=False)
        batch.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )
        batch.alter_column(
            "updated_at",
            existing_type=sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )
    if not _has_index("finance_account_category", "ix_finance_account_category_user_id"):
        op.create_index(
            "ix_finance_account_category_user_id",
            "finance_account_category",
            ["user_id"],
        )
    _create_fk_if_supported(
        "finance_account_category",
        "fk_finance_account_category_user",
        "user",
        ["user_id"],
        ["id"],
    )

    # Money schedule: ensure composite date index exists.
    if not _has_index("finance_money_schedule_row", "ix_finance_money_schedule_row_user_event_date"):
        op.create_index(
            "ix_finance_money_schedule_row_user_event_date",
            "finance_money_schedule_row",
            ["user_id", "event_date"],
        )

    # Finance transactions: numeric confidence and calendar links.
    with op.batch_alter_table("finance_transaction") as batch:
        batch.alter_column(
            "confidence_score",
            existing_type=sa.Float(),
            type_=sa.Numeric(3, 2),
            nullable=True,
        )
    if not _has_index_columns("finance_transaction", ["calendar_event_id"]):
        op.create_index(
            "ix_finance_transaction_calendar_event",
            "finance_transaction",
            ["calendar_event_id"],
        )
    _create_fk_if_supported(
        "finance_transaction",
        "fk_finance_transaction_calendar_event",
        "calendar_event",
        ["calendar_event_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Health: nutrition log shape + inference precision.
    _set_default_if_null("health_nutrition_log", "meal_type", "'unspecified'")
    _set_default_if_null("health_nutrition_log", "items", "''")
    with op.batch_alter_table("health_nutrition_log") as batch:
        batch.alter_column(
            "meal_type",
            existing_type=sa.String(length=32),
            nullable=False,
        )
        batch.alter_column(
            "items",
            existing_type=sa.Text(),
            nullable=False,
        )
        batch.alter_column(
            "confidence_score",
            existing_type=sa.Float(),
            type_=sa.Numeric(3, 2),
            nullable=True,
        )
    if not _has_index_columns("health_nutrition_log", ["calendar_event_id"]):
        op.create_index(
            "ix_health_nutrition_log_calendar_event",
            "health_nutrition_log",
            ["calendar_event_id"],
        )
    _create_fk_if_supported(
        "health_nutrition_log",
        "fk_health_nutrition_log_calendar_event",
        "calendar_event",
        ["calendar_event_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Health: workouts
    _set_default_if_null("health_workout", "workout_type", "'unknown'")
    _set_default_if_null("health_workout", "intensity", "'unknown'")
    with op.batch_alter_table("health_workout") as batch:
        batch.alter_column(
            "workout_type",
            existing_type=sa.String(length=64),
            nullable=False,
        )
        batch.alter_column(
            "intensity",
            existing_type=sa.String(length=16),
            nullable=False,
        )
        batch.alter_column(
            "confidence_score",
            existing_type=sa.Float(),
            type_=sa.Numeric(3, 2),
            nullable=True,
        )
    if not _has_index_columns("health_workout", ["calendar_event_id"]):
        op.create_index("ix_health_workout_calendar_event", "health_workout", ["calendar_event_id"])
    _create_fk_if_supported(
        "health_workout",
        "fk_health_workout_calendar_event",
        "calendar_event",
        ["calendar_event_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Journal: normalize mood to integer; keep legacy columns for compatibility.
    op.execute(text("UPDATE journal_entry SET mood = mood_int WHERE mood_int IS NOT NULL"))
    if dialect == "sqlite":
        op.execute(
            text(
                """
                UPDATE journal_entry
                SET mood = CAST(mood AS INTEGER)
                WHERE mood_int IS NULL AND mood IS NOT NULL
                """
            )
        )
    else:
        op.execute(
            text(
                """
                UPDATE journal_entry
                SET mood = CAST(mood AS INTEGER)
                WHERE mood_int IS NULL AND mood ~ '^-?[0-9]+$'
                """
            )
        )
        op.execute(text("UPDATE journal_entry SET mood = NULL WHERE mood IS NOT NULL AND mood !~ '^-?[0-9]+$'"))
    with op.batch_alter_table("journal_entry") as batch:
        batch.alter_column(
            "mood",
            existing_type=sa.String(length=32),
            type_=sa.Integer(),
            nullable=True,
            postgresql_using="mood::integer",
        )
    if _has_index("journal_entry", "ix_journal_entry_user_mood"):
        op.drop_index("ix_journal_entry_user_mood", table_name="journal_entry")
    op.create_index("ix_journal_entry_user_mood", "journal_entry", ["user_id", "mood"])

    # Projects: enforce user ownership metadata.
    op.execute(
        text(
            """
            UPDATE project_task
            SET user_id = (
                SELECT project.user_id FROM project WHERE project.id = project_task.project_id
            )
            WHERE user_id IS NULL
            """
        )
    )
    _set_default_if_null("project_task", "updated_at", "CURRENT_TIMESTAMP")
    with op.batch_alter_table("project_task") as batch:
        batch.alter_column("user_id", existing_type=sa.Integer(), nullable=False)
        batch.alter_column(
            "updated_at",
            existing_type=sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )
    if not _has_index("project_task", "ix_project_task_user_id"):
        op.create_index("ix_project_task_user_id", "project_task", ["user_id"])
    _create_fk_if_supported("project_task", "fk_project_task_user", "user", ["user_id"], ["id"])

    op.execute(
        text(
            """
            UPDATE project_task_log
            SET user_id = (
                SELECT project_task.user_id FROM project_task WHERE project_task.id = project_task_log.task_id
            )
            WHERE user_id IS NULL
            """
        )
    )
    _set_default_if_null("project_task_log", "created_at", "CURRENT_TIMESTAMP")
    with op.batch_alter_table("project_task_log") as batch:
        batch.alter_column("user_id", existing_type=sa.Integer(), nullable=False)
        batch.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )
        batch.alter_column(
            "confidence_score",
            existing_type=sa.Float(),
            type_=sa.Numeric(3, 2),
            nullable=True,
        )
    if not _has_index("project_task_log", "ix_project_task_log_user_id"):
        op.create_index("ix_project_task_log_user_id", "project_task_log", ["user_id"])
    if not _has_index_columns("project_task_log", ["calendar_event_id"]):
        op.create_index(
            "ix_project_task_log_calendar_event",
            "project_task_log",
            ["calendar_event_id"],
        )
    _create_fk_if_supported(
        "project_task_log",
        "fk_project_task_log_calendar_event",
        "calendar_event",
        ["calendar_event_id"],
        ["id"],
        ondelete="SET NULL",
    )
    _create_fk_if_supported("project_task_log", "fk_project_task_log_user", "user", ["user_id"], ["id"])

    # Relationships: inference precision + calendar linkage.
    with op.batch_alter_table("relationships_interaction") as batch:
        batch.alter_column(
            "confidence_score",
            existing_type=sa.Float(),
            type_=sa.Numeric(3, 2),
            nullable=True,
        )
    if not _has_index_columns("relationships_interaction", ["calendar_event_id"]):
        op.create_index(
            "ix_relationships_interaction_calendar_event",
            "relationships_interaction",
            ["calendar_event_id"],
        )
    _create_fk_if_supported(
        "relationships_interaction",
        "fk_relationships_interaction_calendar_event",
        "calendar_event",
        ["calendar_event_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Skills: tags/telemetry defaults and inference precision.
    _set_default_if_null("skill", "tags", "'[]'")
    _set_default_if_null("skill", "updated_at", "CURRENT_TIMESTAMP")
    with op.batch_alter_table("skill") as batch:
        batch.alter_column(
            "tags",
            existing_type=sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        )
        batch.alter_column(
            "updated_at",
            existing_type=sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )

    _set_default_if_null("skill_practice_session", "created_at", "CURRENT_TIMESTAMP")
    with op.batch_alter_table("skill_practice_session") as batch:
        batch.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )
        batch.alter_column(
            "confidence_score",
            existing_type=sa.Float(),
            type_=sa.Numeric(3, 2),
            nullable=True,
        )
    if not _has_index("skill_practice_session", "ix_skill_practice_session_user_id"):
        op.create_index("ix_skill_practice_session_user_id", "skill_practice_session", ["user_id"])
    if not _has_index_columns("skill_practice_session", ["calendar_event_id"]):
        op.create_index(
            "ix_skill_session_calendar_event",
            "skill_practice_session",
            ["calendar_event_id"],
        )
    _create_fk_if_supported(
        "skill_practice_session",
        "fk_skill_practice_session_calendar_event",
        "calendar_event",
        ["calendar_event_id"],
        ["id"],
        ondelete="SET NULL",
    )
    _create_fk_if_supported(
        "skill_practice_session",
        "fk_skill_practice_session_user",
        "user",
        ["user_id"],
        ["id"],
    )


def downgrade() -> None:
    raise RuntimeError("Downgrade is not supported for 0c76fa610e14_phase3a_new_models.")

"""Utility to purge a user and all referencing rows."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure stdlib modules (e.g., platform) are resolved before local packages named platform.
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(CURRENT_DIR) in sys.path:
    sys.path.remove(str(CURRENT_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text

from lifeos import create_app  # noqa: E402
from lifeos.extensions import db  # noqa: E402


def _configure_sqlite_busy_timeout() -> None:
    engine = db.engine
    if engine.url.get_backend_name() == "sqlite":
        with engine.connect() as conn:
            # Increase busy timeout and use WAL to reduce lock contention during bulk deletes.
            conn.exec_driver_sql("PRAGMA busy_timeout=5000;")
            conn.exec_driver_sql("PRAGMA journal_mode=WAL;")


def _exec_stmt(sql: str, user_id: int) -> None:
    db.session.execute(text(sql), {"uid": user_id})


def delete_user_everywhere(user_id: int) -> None:
    # Auth/core
    _exec_stmt("DELETE FROM user_role WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM session_token WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM jwt_blocklist WHERE created_by=:uid", user_id)
    _exec_stmt("DELETE FROM user_preference WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM event_record WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM insight_record WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM platform_outbox WHERE user_id=:uid", user_id)

    # Finance
    _exec_stmt("DELETE FROM finance_money_schedule_daily_balance WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM finance_money_schedule_row WHERE user_id=:uid", user_id)
    _exec_stmt(
        """
        DELETE FROM finance_receivable_manual_entry
        WHERE tracker_id IN (SELECT id FROM finance_receivable_tracker WHERE user_id=:uid)
    """,
        user_id,
    )
    _exec_stmt(
        """
        DELETE FROM finance_loan_group_link
        WHERE tracker_id IN (SELECT id FROM finance_receivable_tracker WHERE user_id=:uid)
    """,
        user_id,
    )
    _exec_stmt("DELETE FROM finance_loan_group WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM finance_receivable_tracker WHERE user_id=:uid", user_id)
    _exec_stmt(
        """
        DELETE FROM finance_journal_line
        WHERE entry_id IN (SELECT id FROM finance_journal_entry WHERE user_id=:uid)
    """,
        user_id,
    )
    _exec_stmt("DELETE FROM finance_journal_entry WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM finance_transaction WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM finance_account WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM finance_trial_balance_setting WHERE user_id=:uid", user_id)

    # Habits/Health/Skills/Projects/Relationships/Journal
    _exec_stmt("DELETE FROM habits_habit_log WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM habits_habit WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM health_biometric WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM health_workout WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM health_nutrition_log WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM skill_practice_session WHERE user_id=:uid", user_id)
    _exec_stmt(
        "DELETE FROM skill_metric WHERE skill_id IN (SELECT id FROM skill WHERE user_id=:uid)",
        user_id,
    )
    _exec_stmt("DELETE FROM skill WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM project_task_log WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM project_task WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM project WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM relationships_interaction WHERE user_id=:uid", user_id)
    _exec_stmt("DELETE FROM relationships_person WHERE user_id=:uid", user_id)
    _exec_stmt(
        "DELETE FROM journal_entry_tag WHERE entry_id IN (SELECT id FROM journal_entry WHERE user_id=:uid)",
        user_id,
    )
    _exec_stmt("DELETE FROM journal_entry WHERE user_id=:uid", user_id)

    # Finally remove the user
    _exec_stmt('DELETE FROM "user" WHERE id=:uid', user_id)
    db.session.commit()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m lifeos.cleaner <user_id>")
        sys.exit(1)
    user_id = int(sys.argv[1])
    app = create_app()
    with app.app_context():
        _configure_sqlite_busy_timeout()
        delete_user_everywhere(user_id)
    print(f"Deleted user {user_id} and related rows.")


if __name__ == "__main__":
    main()

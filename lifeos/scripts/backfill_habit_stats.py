"""Backfill habits_habit_stat from existing habit_log data.

Idempotent: safe to run multiple times. Creates or updates stat rows.

Usage:
    python -m lifeos.scripts.backfill_habit_stats
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from lifeos import create_app
from lifeos.domains.habits.models import Habit, HabitLog, HabitStat
from lifeos.extensions import db


def _streaks(logs: list[HabitLog]) -> tuple[int, int]:
    """Calculate (current_streak, best_streak) from logs sorted desc."""
    if not logs:
        return 0, 0
    best = 0
    current = 0
    expected = logs[0].logged_date
    for log in logs:
        if log.logged_date == expected:
            current += 1
            expected = expected - timedelta(days=1)
        elif (expected - log.logged_date).days == 1:
            current += 1
            expected = log.logged_date - timedelta(days=1)
        else:
            best = max(best, current)
            current = 1
            expected = log.logged_date - timedelta(days=1)
    best = max(best, current)
    return current, best


def backfill():
    app = create_app()
    with app.app_context():
        habits = Habit.query.all()
        created = 0
        updated = 0

        for habit in habits:
            logs = HabitLog.query.filter_by(habit_id=habit.id).order_by(HabitLog.logged_date.desc()).all()

            current_streak, longest_streak = _streaks(logs)
            total_logs = len(logs)
            last_logged_at = logs[0].logged_date if logs else None

            # Completion rate: days logged in last 30 days
            thirty_days_ago = date.today() - timedelta(days=30)
            recent_count = sum(1 for lg in logs if lg.logged_date >= thirty_days_ago)
            completion_rate_30d = recent_count / 30.0 if total_logs > 0 else None

            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            if stat:
                stat.current_streak = current_streak
                stat.longest_streak = longest_streak
                stat.completion_rate_30d = completion_rate_30d
                stat.total_logs = total_logs
                stat.last_logged_at = last_logged_at
                stat.updated_at = datetime.utcnow()
                updated += 1
            else:
                stat = HabitStat(
                    habit_id=habit.id,
                    user_id=habit.user_id,
                    current_streak=current_streak,
                    longest_streak=longest_streak,
                    completion_rate_30d=completion_rate_30d,
                    total_logs=total_logs,
                    last_logged_at=last_logged_at,
                )
                db.session.add(stat)
                created += 1

        db.session.commit()
        print(f"Backfill complete: {created} created, {updated} updated, " f"{len(habits)} habits processed.")


if __name__ == "__main__":
    backfill()

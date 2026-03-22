"""Habit stat recomputation service.

Recomputes materialized HabitStat rows on every log create/update/delete.
Emits habits.stat.recomputed and habits.habit.streak_milestone events.
"""

from __future__ import annotations

import time
from datetime import date, datetime, timedelta
from typing import List, Tuple

from lifeos.core.observability import record_habits_stat_recompute_latency
from lifeos.domains.habits.events import (
    HABITS_HABIT_STREAK_MILESTONE,
    HABITS_STAT_RECOMPUTED,
)
from lifeos.domains.habits.models.habit_models import HabitLog, HabitStat
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox import enqueue as enqueue_outbox

STREAK_MILESTONES = (7, 30, 100)


def compute_streaks(logs: List[HabitLog]) -> Tuple[int, int]:
    """Calculate (current_streak, best_streak) from logs sorted desc by logged_date.

    Deterministic: gaps of >1 day reset the streak counter.
    The "current streak" is the most recent consecutive run (first streak
    encountered when walking from newest to oldest).
    """
    if not logs:
        return 0, 0
    best = 0
    run = 0
    recent_streak: int | None = None
    expected = logs[0].logged_date
    for log in logs:
        if log.logged_date == expected:
            run += 1
            expected = expected - timedelta(days=1)
        elif (expected - log.logged_date).days == 1:
            run += 1
            expected = log.logged_date - timedelta(days=1)
        else:
            if recent_streak is None:
                recent_streak = run
            best = max(best, run)
            run = 1
            expected = log.logged_date - timedelta(days=1)
    best = max(best, run)
    if recent_streak is None:
        recent_streak = run
    return recent_streak, best


def recompute_habit_stat(user_id: int, habit_id: int) -> HabitStat:
    """Recompute and persist materialized stats for a single habit.

    Creates the HabitStat row if it doesn't exist yet (upsert).
    Emits habits.stat.recomputed event.
    Emits habits.habit.streak_milestone if a milestone threshold is crossed.
    """
    t0 = time.monotonic()
    logs = HabitLog.query.filter_by(habit_id=habit_id).order_by(HabitLog.logged_date.desc()).all()

    current_streak, longest_streak = compute_streaks(logs)
    total_logs = len(logs)
    last_logged_at = logs[0].logged_date if logs else None

    thirty_days_ago = date.today() - timedelta(days=30)
    recent_count = sum(1 for lg in logs if lg.logged_date >= thirty_days_ago)
    completion_rate_30d = recent_count / 30.0 if total_logs > 0 else None

    stat = HabitStat.query.filter_by(habit_id=habit_id).first()
    previous_streak = stat.current_streak if stat else 0

    if stat:
        stat.current_streak = current_streak
        stat.longest_streak = longest_streak
        stat.completion_rate_30d = completion_rate_30d
        stat.total_logs = total_logs
        stat.last_logged_at = last_logged_at
        stat.updated_at = datetime.utcnow()
    else:
        stat = HabitStat(
            habit_id=habit_id,
            user_id=user_id,
            current_streak=current_streak,
            longest_streak=longest_streak,
            completion_rate_30d=completion_rate_30d,
            total_logs=total_logs,
            last_logged_at=last_logged_at,
        )
        db.session.add(stat)

    db.session.flush()

    enqueue_outbox(
        HABITS_STAT_RECOMPUTED,
        {
            "habit_id": habit_id,
            "user_id": user_id,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "completion_rate_30d": completion_rate_30d,
            "total_logs": total_logs,
        },
        user_id=user_id,
    )

    # Check milestone crossings
    for milestone in STREAK_MILESTONES:
        if current_streak >= milestone > previous_streak:
            enqueue_outbox(
                HABITS_HABIT_STREAK_MILESTONE,
                {
                    "habit_id": habit_id,
                    "user_id": user_id,
                    "streak_length": current_streak,
                    "milestone_type": milestone,
                    "achieved_at": datetime.utcnow().isoformat(),
                },
                user_id=user_id,
            )

    record_habits_stat_recompute_latency(time.monotonic() - t0)
    return stat

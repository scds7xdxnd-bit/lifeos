"""Habit services: CRUD, logging, and aggregates with outbox events."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import func

from lifeos.domains.habits.events import (
    HABITS_HABIT_CREATED,
    HABITS_HABIT_DEACTIVATED,
    HABITS_HABIT_DELETED,
    HABITS_HABIT_LOGGED,
    HABITS_HABIT_UPDATED,
)
from lifeos.domains.habits.models.habit_models import Habit, HabitLog
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox import enqueue as enqueue_outbox


def create_habit(
    user_id: int,
    *,
    name: str,
    description: str | None = None,
    domain_link: str | None = None,
    schedule_type: str | None = None,
    target_count: int | None = None,
    time_of_day: str | None = None,
    difficulty: str | None = None,
    cadence: str | None = None,
    target: int | None = None,
) -> Habit:
    name_norm = (name or "").strip()
    if not name_norm:
        raise ValueError("validation_error")
    existing = Habit.query.filter_by(user_id=user_id, name=name_norm).first()
    if existing:
        raise ValueError("duplicate")

    habit = Habit(
        user_id=user_id,
        name=name_norm,
        description=(description or "").strip() or None,
        domain_link=(domain_link or "").strip() or None,
        schedule_type=schedule_type or cadence or "daily",
        target_count=target_count if target_count is not None else target,
        time_of_day=(time_of_day or "").strip() or None,
        difficulty=(difficulty or "").strip() or None,
    )
    db.session.add(habit)
    db.session.flush()
    enqueue_outbox(
        HABITS_HABIT_CREATED,
        {
            "habit_id": habit.id,
            "user_id": user_id,
            "name": habit.name,
            "schedule_type": habit.schedule_type,
            "target_count": habit.target_count,
            "domain_link": habit.domain_link,
            "is_active": habit.is_active,
            "created_at": habit.created_at.isoformat(),
        },
        user_id=user_id,
    )
    db.session.commit()
    return habit


def update_habit(user_id: int, habit_id: int, **fields) -> Optional[Habit]:
    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        return None

    allowed = (
        "name",
        "description",
        "domain_link",
        "schedule_type",
        "target_count",
        "time_of_day",
        "difficulty",
        "is_active",
    )
    changed: Dict[str, object] = {}
    for key in allowed:
        if key in fields:
            val = fields[key]
            if isinstance(val, str):
                val = val.strip()
            setattr(habit, key, val)
            changed[key] = val
    enqueue_outbox(
        HABITS_HABIT_UPDATED,
        {
            "habit_id": habit.id,
            "user_id": user_id,
            "fields": changed,
            "updated_at": (
                habit.updated_at.isoformat()
                if habit.updated_at
                else datetime.utcnow().isoformat()
            ),
        },
        user_id=user_id,
    )
    db.session.commit()
    return habit


def deactivate_habit(user_id: int, habit_id: int) -> Optional[Habit]:
    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        return None
    habit.is_active = False
    enqueue_outbox(
        HABITS_HABIT_DEACTIVATED,
        {
            "habit_id": habit.id,
            "user_id": user_id,
            "deactivated_at": datetime.utcnow().isoformat(),
        },
        user_id=user_id,
    )
    db.session.commit()
    return habit


def delete_habit(user_id: int, habit_id: int) -> bool:
    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        return False
    db.session.delete(habit)
    enqueue_outbox(
        HABITS_HABIT_DELETED,
        {
            "habit_id": habit_id,
            "user_id": user_id,
            "deleted_at": datetime.utcnow().isoformat(),
        },
        user_id=user_id,
    )
    db.session.commit()
    return True


def log_habit_completion(
    user_id: int,
    habit_id: int,
    *,
    logged_date: Optional[date] = None,
    value: float | None = None,
    note: str | None = None,
    allow_inactive: bool = True,
) -> HabitLog:
    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        raise ValueError("not_found")
    if not allow_inactive and not habit.is_active:
        raise ValueError("inactive")

    log = HabitLog(
        user_id=user_id,
        habit_id=habit_id,
        logged_date=logged_date or date.today(),
        value=value,
        note=(note or "").strip() or None,
    )
    db.session.add(log)
    db.session.flush()
    enqueue_outbox(
        HABITS_HABIT_LOGGED,
        {
            "log_id": log.id,
            "habit_id": habit_id,
            "user_id": user_id,
            "logged_date": log.logged_date.isoformat(),
            "value": value,
            "note": log.note,
        },
        user_id=user_id,
    )
    db.session.commit()
    return log


# Backwards-compatible alias used in tests
def log_habit(
    habit_id: int, logged_date: Optional[date] = None, value: float | None = None
) -> HabitLog:
    habit = Habit.query.get(habit_id)
    if not habit:
        raise ValueError("not_found")
    return log_habit_completion(
        habit.user_id, habit_id, logged_date=logged_date, value=value
    )


def update_habit_log(user_id: int, log_id: int, **fields) -> Optional[HabitLog]:
    log = HabitLog.query.filter_by(id=log_id, user_id=user_id).first()
    if not log:
        return None
    for key in ("logged_date", "value", "note"):
        if key in fields:
            setattr(log, key, fields[key])
    db.session.commit()
    return log


def delete_habit_log(user_id: int, log_id: int) -> bool:
    log = HabitLog.query.filter_by(id=log_id, user_id=user_id).first()
    if not log:
        return False
    db.session.delete(log)
    db.session.commit()
    return True


def get_today_habits(user_id: int, today: date) -> List[dict]:
    habits = Habit.query.filter_by(user_id=user_id, is_active=True).all()
    log_map = {
        log.habit_id: log
        for log in HabitLog.query.filter_by(user_id=user_id, logged_date=today).all()
    }
    payload = []
    for habit in habits:
        log = log_map.get(habit.id)
        payload.append(
            {
                "habit": habit,
                "logged": bool(log),
                "log": log,
            }
        )
    return payload


def get_habit_history(
    user_id: int, habit_id: int, start: date, end: date
) -> List[HabitLog]:
    return (
        HabitLog.query.filter_by(user_id=user_id, habit_id=habit_id)
        .filter(HabitLog.logged_date >= start, HabitLog.logged_date <= end)
        .order_by(HabitLog.logged_date.desc())
        .all()
    )


def compute_habit_stats(user_id: int, habit_id: int, window_days: int = 30) -> dict:
    end_date = date.today()
    start_date = end_date - timedelta(days=max(window_days, 1))
    logs = (
        HabitLog.query.filter_by(user_id=user_id, habit_id=habit_id)
        .filter(HabitLog.logged_date >= start_date)
        .order_by(HabitLog.logged_date.desc())
        .all()
    )
    total_count = len(logs)
    total_value = sum(float(log.value or 0) for log in logs)
    current_streak, best_streak = _streaks(logs)

    last7 = [log for log in logs if (end_date - log.logged_date).days <= 7]
    last30 = [log for log in logs if (end_date - log.logged_date).days <= 30]

    return {
        "total_count": total_count,
        "total_value": total_value,
        "current_streak": current_streak,
        "best_streak": best_streak,
        "logs_last_7": len(last7),
        "logs_last_30": len(last30),
        "last_logged_date": logs[0].logged_date if logs else None,
    }


def compute_streak(habit: Habit) -> int:
    logs = (
        HabitLog.query.filter_by(habit_id=habit.id, user_id=habit.user_id)
        .order_by(HabitLog.logged_date.desc())
        .all()
    )
    current, _ = _streaks(logs)
    return current


def get_habit_detail(user_id: int, habit_id: int) -> Optional[dict]:
    habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        return None
    stats = compute_habit_stats(user_id, habit_id)
    recent_logs = (
        HabitLog.query.filter_by(user_id=user_id, habit_id=habit_id)
        .order_by(HabitLog.logged_date.desc())
        .limit(30)
        .all()
    )
    return {"habit": habit, "stats": stats, "logs": recent_logs}


def list_habits(user_id: int) -> List[dict]:
    habits = Habit.query.filter_by(user_id=user_id).all()
    log_counts = (
        db.session.query(
            HabitLog.habit_id,
            func.count(HabitLog.id).label("count"),
            func.max(HabitLog.logged_date).label("last_logged_date"),
        )
        .filter(HabitLog.user_id == user_id)
        .filter(HabitLog.habit_id.in_([h.id for h in habits] or [0]))
        .group_by(HabitLog.habit_id)
        .all()
    )
    stats_by_id = {
        row.habit_id: {
            "count": int(row.count or 0),
            "last_logged_date": row.last_logged_date,
        }
        for row in log_counts
    }
    today = date.today()
    today_logs = {
        log.habit_id: log
        for log in HabitLog.query.filter_by(user_id=user_id, logged_date=today).all()
    }

    payload = []
    for habit in habits:
        s = stats_by_id.get(habit.id, {"count": 0, "last_logged_date": None})
        payload.append(
            {
                "habit": habit,
                "count": s["count"],
                "last_logged_date": s["last_logged_date"],
                "completed_today": habit.id in today_logs,
            }
        )
    return payload


def _streaks(logs: List[HabitLog]) -> Tuple[int, int]:
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

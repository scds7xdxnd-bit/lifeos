"""Health services for biometrics, workouts, and nutrition."""

from __future__ import annotations

from datetime import date, timedelta
from typing import List, Tuple

from sqlalchemy import func

from lifeos.domains.health.events import (
    HEALTH_BIOMETRIC_LOGGED,
    HEALTH_NUTRITION_LOGGED,
    HEALTH_WORKOUT_LOGGED,
)
from lifeos.domains.health.models.health_models import Biometric, NutritionLog, Workout
from lifeos.extensions import db
from lifeos.platform.outbox import enqueue as enqueue_outbox

_INTENSITY = {"low", "medium", "high"}
_MEAL_TYPES = {"breakfast", "lunch", "dinner", "snack", "other"}


def _paginate(query, page: int, per_page: int) -> Tuple[List, int]:
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def create_biometric_entry(
    user_id: int,
    *,
    date_value: date,
    weight: float | None = None,
    body_fat_pct: float | None = None,
    resting_hr: int | None = None,
    energy_level: int | None = None,
    stress_level: int | None = None,
    notes: str | None = None,
) -> Biometric:
    if energy_level is not None and not (1 <= energy_level <= 5):
        raise ValueError("validation_error")
    if stress_level is not None and not (1 <= stress_level <= 5):
        raise ValueError("validation_error")
    existing = Biometric.query.filter_by(user_id=user_id, date=date_value).first()
    if existing:
        raise ValueError("duplicate")

    biometric = Biometric(
        user_id=user_id,
        date=date_value,
        weight=weight,
        body_fat_pct=body_fat_pct,
        resting_hr=resting_hr,
        energy_level=energy_level,
        stress_level=stress_level,
        notes=(notes or "").strip() or None,
    )
    db.session.add(biometric)
    db.session.flush()
    enqueue_outbox(
        HEALTH_BIOMETRIC_LOGGED,
        {
            "biometric_id": biometric.id,
            "user_id": user_id,
            "date": biometric.date.isoformat(),
            "weight": float(biometric.weight) if biometric.weight is not None else None,
            "body_fat_pct": float(biometric.body_fat_pct) if biometric.body_fat_pct is not None else None,
            "resting_hr": biometric.resting_hr,
            "energy_level": biometric.energy_level,
            "stress_level": biometric.stress_level,
        },
        user_id=user_id,
    )
    db.session.commit()
    return biometric


def list_biometrics(
    user_id: int, start_date: date | None = None, end_date: date | None = None, page: int = 1, per_page: int = 50
) -> tuple[list[Biometric], int]:
    query = Biometric.query.filter_by(user_id=user_id)
    if start_date:
        query = query.filter(Biometric.date >= start_date)
    if end_date:
        query = query.filter(Biometric.date <= end_date)
    query = query.order_by(Biometric.date.desc(), Biometric.created_at.desc())
    return _paginate(query, page, per_page)


def create_workout(
    user_id: int,
    *,
    date_value: date,
    workout_type: str,
    duration_minutes: int,
    intensity: str,
    calories_est: float | None = None,
    notes: str | None = None,
) -> Workout:
    intensity_norm = (intensity or "").strip().lower()
    if intensity_norm not in _INTENSITY:
        raise ValueError("validation_error")
    if duration_minutes < 0:
        raise ValueError("validation_error")
    workout = Workout(
        user_id=user_id,
        date=date_value,
        workout_type=workout_type.strip(),
        duration_minutes=duration_minutes,
        intensity=intensity_norm,
        calories_est=calories_est,
        notes=(notes or "").strip() or None,
    )
    db.session.add(workout)
    db.session.flush()
    enqueue_outbox(
        HEALTH_WORKOUT_LOGGED,
        {
            "workout_id": workout.id,
            "user_id": user_id,
            "date": workout.date.isoformat(),
            "workout_type": workout.workout_type,
            "duration_minutes": workout.duration_minutes,
            "intensity": workout.intensity,
            "calories_est": float(workout.calories_est) if workout.calories_est is not None else None,
        },
        user_id=user_id,
    )
    db.session.commit()
    return workout


def list_workouts(
    user_id: int, start_date: date | None = None, end_date: date | None = None, page: int = 1, per_page: int = 50
) -> tuple[list[Workout], int]:
    query = Workout.query.filter_by(user_id=user_id)
    if start_date:
        query = query.filter(Workout.date >= start_date)
    if end_date:
        query = query.filter(Workout.date <= end_date)
    query = query.order_by(Workout.date.desc(), Workout.created_at.desc())
    return _paginate(query, page, per_page)


def create_nutrition_log(
    user_id: int,
    *,
    date_value: date,
    meal_type: str,
    items: str,
    calories_est: float | None = None,
    quality_score: int | None = None,
) -> NutritionLog:
    meal_norm = (meal_type or "").strip().lower()
    if meal_norm not in _MEAL_TYPES:
        raise ValueError("validation_error")
    if quality_score is not None and not (1 <= quality_score <= 5):
        raise ValueError("validation_error")
    log = NutritionLog(
        user_id=user_id,
        date=date_value,
        meal_type=meal_norm,
        items=items.strip(),
        calories_est=calories_est,
        quality_score=quality_score,
    )
    db.session.add(log)
    db.session.flush()
    enqueue_outbox(
        HEALTH_NUTRITION_LOGGED,
        {
            "nutrition_id": log.id,
            "user_id": user_id,
            "date": log.date.isoformat(),
            "meal_type": log.meal_type,
            "calories_est": float(log.calories_est) if log.calories_est is not None else None,
            "quality_score": log.quality_score,
        },
        user_id=user_id,
    )
    db.session.commit()
    return log


def list_nutrition_logs(
    user_id: int, start_date: date | None = None, end_date: date | None = None, page: int = 1, per_page: int = 50
) -> tuple[list[NutritionLog], int]:
    query = NutritionLog.query.filter_by(user_id=user_id)
    if start_date:
        query = query.filter(NutritionLog.date >= start_date)
    if end_date:
        query = query.filter(NutritionLog.date <= end_date)
    query = query.order_by(NutritionLog.date.desc(), NutritionLog.created_at.desc())
    return _paginate(query, page, per_page)


def get_daily_summary(user_id: int, summary_date: date) -> dict:
    biometrics = (
        Biometric.query.filter_by(user_id=user_id, date=summary_date)
        .order_by(Biometric.created_at.desc(), Biometric.id.desc())
        .all()
    )
    biometric = biometrics[0] if biometrics else None
    workouts = Workout.query.filter_by(user_id=user_id, date=summary_date).all()
    nutrition_logs = NutritionLog.query.filter_by(user_id=user_id, date=summary_date).all()

    workout_total = sum(w.duration_minutes for w in workouts)
    workout_by_type: dict[str, int] = {}
    for w in workouts:
        workout_by_type[w.workout_type] = workout_by_type.get(w.workout_type, 0) + 1

    nutrition_calories = sum(float(n.calories_est) for n in nutrition_logs if n.calories_est is not None)

    return {
        "date": summary_date,
        "biometric": biometric,
        "workouts": {
            "count": len(workouts),
            "total_duration_minutes": workout_total,
            "by_type": workout_by_type,
        },
        "nutrition": {
            "count": len(nutrition_logs),
            "calories_est_total": nutrition_calories,
        },
        "energy_level": biometric.energy_level if biometric else None,
        "stress_level": biometric.stress_level if biometric else None,
    }


def get_weekly_summary(user_id: int, week_start: date) -> dict:
    week_end = week_start + timedelta(days=6)
    biometrics = (
        Biometric.query.filter(Biometric.user_id == user_id, Biometric.date >= week_start, Biometric.date <= week_end)
        .order_by(Biometric.date.desc(), Biometric.created_at.desc())
        .all()
    )
    latest_by_date: dict[date, Biometric] = {}
    for b in biometrics:
        latest_by_date.setdefault(b.date, b)

    weights = [float(b.weight) for b in latest_by_date.values() if b.weight is not None]
    resting = [b.resting_hr for b in latest_by_date.values() if b.resting_hr is not None]
    energy = [b.energy_level for b in latest_by_date.values() if b.energy_level is not None]
    stress = [b.stress_level for b in latest_by_date.values() if b.stress_level is not None]

    workouts = (
        Workout.query.filter(Workout.user_id == user_id, Workout.date >= week_start, Workout.date <= week_end).all()
    )
    nutrition_logs = (
        NutritionLog.query.filter(
            NutritionLog.user_id == user_id, NutritionLog.date >= week_start, NutritionLog.date <= week_end
        ).all()
    )

    workout_by_type: dict[str, int] = {}
    total_workout_duration = 0
    for w in workouts:
        workout_by_type[w.workout_type] = workout_by_type.get(w.workout_type, 0) + 1
        total_workout_duration += w.duration_minutes

    nutrition_calories = sum(float(n.calories_est) for n in nutrition_logs if n.calories_est is not None)

    def _avg(vals: list[float | int]) -> float | None:
        return round(sum(vals) / len(vals), 2) if vals else None

    return {
        "week_start": week_start,
        "week_end": week_end,
        "biometric": {
            "average_weight": _avg(weights),
            "average_resting_hr": _avg(resting),
            "average_energy_level": _avg(energy),
            "average_stress_level": _avg(stress),
        },
        "workouts": {
            "count": len(workouts),
            "total_duration_minutes": total_workout_duration,
            "by_type": workout_by_type,
        },
        "nutrition": {
            "count": len(nutrition_logs),
            "calories_est_total": nutrition_calories,
        },
    }

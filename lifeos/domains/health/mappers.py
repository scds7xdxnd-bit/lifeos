"""DTO mappers for health domain."""

from __future__ import annotations

from lifeos.domains.health.models.health_models import Biometric, NutritionLog, Workout


def map_biometric(b: Biometric) -> dict:
    return {
        "id": b.id,
        "date": b.date.isoformat(),
        "weight": float(b.weight) if b.weight is not None else None,
        "body_fat_pct": float(b.body_fat_pct) if b.body_fat_pct is not None else None,
        "resting_hr": b.resting_hr,
        "energy_level": b.energy_level,
        "stress_level": b.stress_level,
        "notes": b.notes,
        "created_at": b.created_at.isoformat() if b.created_at else None,
    }


def map_workout(w: Workout) -> dict:
    return {
        "id": w.id,
        "date": w.date.isoformat(),
        "workout_type": w.workout_type,
        "duration_minutes": w.duration_minutes,
        "intensity": w.intensity,
        "calories_est": float(w.calories_est) if w.calories_est is not None else None,
        "notes": w.notes,
        "created_at": w.created_at.isoformat() if w.created_at else None,
    }


def map_nutrition_log(n: NutritionLog) -> dict:
    raw_items = n.items
    if isinstance(raw_items, str):
        items_list = [part.strip() for part in raw_items.replace("\n", ",").split(",") if part.strip()]
    elif isinstance(raw_items, list):
        items_list = raw_items
    else:
        items_list = []
    return {
        "id": n.id,
        "date": n.date.isoformat(),
        "meal_type": n.meal_type,
        "items": items_list,
        "calories_est": float(n.calories_est) if n.calories_est is not None else None,
        "quality_score": n.quality_score,
        "created_at": n.created_at.isoformat() if n.created_at else None,
    }

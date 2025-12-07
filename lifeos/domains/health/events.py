"""Health domain event catalog."""

from __future__ import annotations

HEALTH_BIOMETRIC_LOGGED = "health.biometric.logged"
HEALTH_WORKOUT_LOGGED = "health.workout.logged"
HEALTH_NUTRITION_LOGGED = "health.nutrition.logged"

EVENT_CATALOG = {
    HEALTH_BIOMETRIC_LOGGED: {
        "version": "v1",
        "payload": {
            "biometric_id": "int",
            "user_id": "int",
            "date": "date",
            "weight": "decimal?",
            "body_fat_pct": "decimal?",
            "resting_hr": "int?",
            "energy_level": "int?",
            "stress_level": "int?",
        },
    },
    HEALTH_WORKOUT_LOGGED: {
        "version": "v1",
        "payload": {
            "workout_id": "int",
            "user_id": "int",
            "date": "date",
            "workout_type": "str",
            "duration_minutes": "int",
            "intensity": "str",
            "calories_est": "decimal?",
        },
    },
    HEALTH_NUTRITION_LOGGED: {
        "version": "v1",
        "payload": {
            "nutrition_id": "int",
            "user_id": "int",
            "date": "date",
            "meal_type": "str",
            "calories_est": "decimal?",
            "quality_score": "int?",
        },
    },
}

__all__ = [
    "EVENT_CATALOG",
    "HEALTH_BIOMETRIC_LOGGED",
    "HEALTH_WORKOUT_LOGGED",
    "HEALTH_NUTRITION_LOGGED",
]

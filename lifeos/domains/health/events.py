"""Health domain event catalog."""

from __future__ import annotations

HEALTH_BIOMETRIC_LOGGED = "health.biometric.logged"
HEALTH_WORKOUT_LOGGED = "health.workout.logged"
HEALTH_NUTRITION_LOGGED = "health.nutrition.logged"
HEALTH_METRIC_UPDATED = "health.metric.updated"
HEALTH_MEAL_INFERRED = "health.meal.inferred"
HEALTH_WORKOUT_INFERRED = "health.workout.inferred"

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
    HEALTH_METRIC_UPDATED: {
        "version": "v1",
        "payload": {
            "user_id": "int",
            "metric": "str",
            "value": "float|int|str",
            "recorded_at": "datetime?",
            "payload_version": "str",
        },
    },
    HEALTH_MEAL_INFERRED: {
        "version": "v1",
        "payload": {
            "nutrition_id": "int",
            "calendar_event_id": "int",
            "user_id": "int",
            "confidence_score": "float",
            "meal_type": "str",
            "payload_version": "str",
            "model_version": "str?",
            "is_false_positive": "bool?",
            "is_false_negative": "bool?",
        },
    },
    HEALTH_WORKOUT_INFERRED: {
        "version": "v1",
        "payload": {
            "workout_id": "int",
            "calendar_event_id": "int",
            "user_id": "int",
            "confidence_score": "float",
            "workout_type": "str",
            "duration_minutes": "int?",
            "payload_version": "str",
            "model_version": "str?",
            "is_false_positive": "bool?",
            "is_false_negative": "bool?",
        },
    },
}

__all__ = [
    "EVENT_CATALOG",
    "HEALTH_BIOMETRIC_LOGGED",
    "HEALTH_WORKOUT_LOGGED",
    "HEALTH_NUTRITION_LOGGED",
    "HEALTH_METRIC_UPDATED",
    "HEALTH_MEAL_INFERRED",
    "HEALTH_WORKOUT_INFERRED",
]

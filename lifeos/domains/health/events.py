"""Health domain event catalog."""

from __future__ import annotations

# --- Calculator Events ---
HEALTH_CALORIE_REPORT_CREATED = "health.calorie_report.created"

# --- Food Library Events ---
HEALTH_FOOD_LIBRARY_CREATED = "health.food_library.created"
HEALTH_FOOD_LIBRARY_UPDATED = "health.food_library.updated"
HEALTH_FOOD_LIBRARY_DELETED = "health.food_library.deleted"

HEALTH_BIOMETRIC_LOGGED = "health.biometric.logged"
HEALTH_WORKOUT_LOGGED = "health.workout.logged"
HEALTH_NUTRITION_LOGGED = "health.nutrition.logged"
HEALTH_METRIC_UPDATED = "health.metric.updated"
HEALTH_MEAL_INFERRED = "health.meal.inferred"
HEALTH_WORKOUT_INFERRED = "health.workout.inferred"

EVENT_CATALOG = {
    HEALTH_CALORIE_REPORT_CREATED: {
        "version": "v1",
        "payload": {
            "report_id": "int",
            "user_id": "int",
            "bmr": "decimal",
            "tdee": "decimal",
            "daily_calories": "decimal",
            "goal_type": "str",
            "goal_weight_kg": "decimal?",
            "timeline_months": "int?",
            "method_used": "str",
            "created_at": "datetime",
        },
    },
    HEALTH_FOOD_LIBRARY_CREATED: {
        "version": "v1",
        "payload": {
            "food_id": "int",
            "user_id": "int",
            "name": "str",
            "cost_per_100g": "decimal",
            "calories_per_100g": "decimal",
            "protein_per_100g": "decimal",
            "carbohydrate_per_100g": "decimal",
            "fat_per_100g": "decimal",
            "fiber_per_100g": "decimal?",
            "created_at": "datetime",
        },
    },
    HEALTH_FOOD_LIBRARY_UPDATED: {
        "version": "v1",
        "payload": {
            "food_id": "int",
            "user_id": "int",
            "fields": "dict",
            "updated_at": "datetime",
        },
    },
    HEALTH_FOOD_LIBRARY_DELETED: {
        "version": "v1",
        "payload": {
            "food_id": "int",
            "user_id": "int",
            "deleted_at": "datetime",
        },
    },
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
    "HEALTH_CALORIE_REPORT_CREATED",
    "HEALTH_FOOD_LIBRARY_CREATED",
    "HEALTH_FOOD_LIBRARY_UPDATED",
    "HEALTH_FOOD_LIBRARY_DELETED",
    "HEALTH_BIOMETRIC_LOGGED",
    "HEALTH_WORKOUT_LOGGED",
    "HEALTH_NUTRITION_LOGGED",
    "HEALTH_METRIC_UPDATED",
    "HEALTH_MEAL_INFERRED",
    "HEALTH_WORKOUT_INFERRED",
]

"""Compatibility wrapper for workouts."""

from __future__ import annotations

from datetime import date

from lifeos.domains.health.models.health_models import Workout
from lifeos.domains.health.services.health_service import create_workout


def log_workout(user_id: int, activity: str, duration_minutes: int, calories: float | None = None) -> Workout:
    # Legacy wrapper mapping to new service
    return create_workout(
        user_id,
        date_value=date.today(),
        workout_type=activity,
        duration_minutes=duration_minutes,
        intensity="medium",
        calories_est=calories,
    )

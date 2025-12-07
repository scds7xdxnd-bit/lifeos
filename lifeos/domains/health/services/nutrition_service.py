"""Nutrition logging service (wrapper)."""

from __future__ import annotations

from datetime import date

from lifeos.domains.health.models.health_models import NutritionLog
from lifeos.domains.health.services.health_service import create_nutrition_log


def log_meal(
    user_id: int, meal: str, calories: float, protein: float | None = None, carbs: float | None = None, fat: float | None = None
) -> NutritionLog:
    # Legacy wrapper: map to new schema fields
    return create_nutrition_log(
        user_id,
        date_value=date.today(),
        meal_type=meal,
        items=f"protein:{protein or 0}, carbs:{carbs or 0}, fat:{fat or 0}",
        calories_est=calories,
    )

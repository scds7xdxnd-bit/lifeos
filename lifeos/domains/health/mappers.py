"""DTO mappers for health domain."""

from __future__ import annotations

from lifeos.domains.health.models.calorie_report import CalorieReport
from lifeos.domains.health.models.food_library import FoodLibraryItem
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


def map_food_item(f: FoodLibraryItem) -> dict:
    return {
        "id": f.id,
        "name": f.name,
        "cost_per_100g": float(f.cost_per_100g),
        "calories_per_100g": float(f.calories_per_100g),
        "protein_per_100g": float(f.protein_per_100g),
        "carbohydrate_per_100g": float(f.carbohydrate_per_100g),
        "fat_per_100g": float(f.fat_per_100g),
        "fiber_per_100g": float(f.fiber_per_100g) if f.fiber_per_100g is not None else None,
        "created_at": f.created_at.isoformat() if f.created_at else None,
        "updated_at": f.updated_at.isoformat() if f.updated_at else None,
    }


def map_calorie_report(r: CalorieReport) -> dict:
    return {
        "id": r.id,
        # Input snapshot
        "weight_kg": float(r.weight_kg),
        "height_cm": float(r.height_cm),
        "age_years": r.age_years,
        "gender": r.gender,
        "body_fat_pct": float(r.body_fat_pct) if r.body_fat_pct is not None else None,
        "activity_level": r.activity_level,
        "goal_type": r.goal_type,
        "goal_weight_kg": float(r.goal_weight_kg) if r.goal_weight_kg is not None else None,
        "goal_timeline_months": r.goal_timeline_months,
        # Computed values
        "method_used": r.method_used,
        "lean_body_mass": float(r.lean_body_mass) if r.lean_body_mass is not None else None,
        "bmr": float(r.bmr),
        "activity_multiplier": float(r.activity_multiplier),
        "tdee": float(r.tdee),
        # Delta breakdown
        "delta_bw": float(r.delta_bw) if r.delta_bw is not None else None,
        "total_delta_kcal": float(r.total_delta_kcal) if r.total_delta_kcal is not None else None,
        "delta_kcal_per_day": float(r.delta_kcal_per_day) if r.delta_kcal_per_day is not None else None,
        "kcal_per_kg_used": r.kcal_per_kg_used,
        # Daily targets
        "daily_calories": float(r.daily_calories),
        "protein_g_per_day": float(r.protein_g_per_day),
        "fat_g_per_day": float(r.fat_g_per_day),
        "carbs_g_per_day": float(r.carbs_g_per_day),
        "fiber_g_per_day": float(r.fiber_g_per_day),
        # Monthly targets
        "monthly_calories": float(r.monthly_calories),
        "monthly_protein_g": float(r.monthly_protein_g),
        "monthly_fat_g": float(r.monthly_fat_g),
        "monthly_carbs_g": float(r.monthly_carbs_g),
        "monthly_fiber_g": float(r.monthly_fiber_g),
        # Metadata
        "created_at": r.created_at.isoformat() if r.created_at else None,
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

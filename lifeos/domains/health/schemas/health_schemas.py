"""Health schemas."""

import datetime as dt
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=200)


class BiometricCreate(BaseModel):
    date: dt.date = Field(default_factory=dt.date.today)
    weight: Optional[float] = Field(default=None, ge=0)
    body_fat_pct: Optional[float] = Field(default=None, ge=0)
    resting_hr: Optional[int] = Field(default=None, ge=0)
    energy_level: Optional[int] = Field(default=None, ge=1, le=5)
    stress_level: Optional[int] = Field(default=None, ge=1, le=5)
    notes: Optional[str] = Field(default=None, max_length=4096)


class BiometricListFilter(Pagination):
    start_date: Optional[dt.date] = None
    end_date: Optional[dt.date] = None


class WorkoutCreate(BaseModel):
    date: dt.date = Field(default_factory=dt.date.today)
    workout_type: str = Field(min_length=1, max_length=64)
    duration_minutes: int = Field(default=0, ge=0)
    intensity: str = Field(default="medium", max_length=16)
    calories_est: Optional[float] = Field(default=None, ge=0)
    notes: Optional[str] = Field(default=None, max_length=4096)

    @field_validator("intensity")
    @classmethod
    def validate_intensity(cls, v: str) -> str:
        allowed = {"low", "medium", "high"}
        val = (v or "").strip().lower()
        if val not in allowed:
            raise ValueError("invalid_intensity")
        return val


class WorkoutListFilter(Pagination):
    start_date: Optional[dt.date] = None
    end_date: Optional[dt.date] = None


class NutritionCreate(BaseModel):
    date: dt.date = Field(default_factory=dt.date.today)
    meal_type: str = Field(min_length=1, max_length=32)
    items: str = Field(min_length=1, max_length=4096)
    calories_est: Optional[float] = Field(default=None, ge=0)
    quality_score: Optional[int] = Field(default=None, ge=1, le=5)

    @field_validator("meal_type")
    @classmethod
    def validate_meal_type(cls, v: str) -> str:
        allowed = {"breakfast", "lunch", "dinner", "snack", "other"}
        val = (v or "").strip().lower()
        if val not in allowed:
            raise ValueError("invalid_meal_type")
        return val


class NutritionListFilter(Pagination):
    start_date: Optional[dt.date] = None
    end_date: Optional[dt.date] = None


class DailySummaryResponse(BaseModel):
    date: dt.date
    biometric: Optional[dict]
    workouts: dict
    nutrition: dict
    energy_level: Optional[int] = None
    stress_level: Optional[int] = None


class WeeklySummaryResponse(BaseModel):
    week_start: dt.date
    week_end: dt.date
    biometric: dict
    workouts: dict
    nutrition: dict

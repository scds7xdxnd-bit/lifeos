"""Calorie calculator Pydantic DTOs."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class CalculatorInput(BaseModel):
    """Request body for POST /api/v1/health/calculator/calculate."""

    weight_kg: float = Field(gt=0, le=500)
    height_cm: float = Field(gt=0, le=300)
    age_years: int = Field(ge=1, le=120)
    gender: Literal["male", "female"]
    body_fat_pct: Optional[float] = Field(default=None, ge=0, le=80)
    activity_level: Literal["sedentary", "lightly_active", "moderately_active", "very_active", "extra_active"]
    goal_type: Literal["lose", "gain", "maintain"]
    goal_weight_kg: Optional[float] = Field(default=None, gt=0, le=500)
    goal_timeline_months: Optional[int] = Field(default=None, ge=1, le=120)

    # Whether to persist the height/age/gender to UserPreference for future visits
    save_profile: bool = Field(default=True)

    @model_validator(mode="after")
    def validate_goal_fields(self):
        if self.goal_type in ("lose", "gain"):
            if self.goal_weight_kg is None:
                raise ValueError("goal_weight_kg is required when goal_type is 'lose' or 'gain'")
            if self.goal_timeline_months is None:
                raise ValueError("goal_timeline_months is required when goal_type is 'lose' or 'gain'")
        return self


class ReportListParams(BaseModel):
    """Query params for GET /api/v1/health/calculator/reports."""

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

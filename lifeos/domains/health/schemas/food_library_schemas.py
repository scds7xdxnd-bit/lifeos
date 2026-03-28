"""Food library Pydantic DTOs."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class FoodItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=256)
    cost_per_100g: float = Field(ge=0)
    calories_per_100g: float = Field(ge=0)
    protein_per_100g: float = Field(ge=0)
    carbohydrate_per_100g: float = Field(ge=0)
    fat_per_100g: float = Field(ge=0)
    fiber_per_100g: Optional[float] = Field(default=None, ge=0)


class FoodItemUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=256)
    cost_per_100g: Optional[float] = Field(default=None, ge=0)
    calories_per_100g: Optional[float] = Field(default=None, ge=0)
    protein_per_100g: Optional[float] = Field(default=None, ge=0)
    carbohydrate_per_100g: Optional[float] = Field(default=None, ge=0)
    fat_per_100g: Optional[float] = Field(default=None, ge=0)
    fiber_per_100g: Optional[float] = Field(default=None, ge=0)


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=200)

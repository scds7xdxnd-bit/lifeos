"""Habit DTOs and schemas."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class HabitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=4096)
    domain_link: Optional[str] = Field(default=None, max_length=64)
    schedule_type: str = Field(default="daily", max_length=32)
    target_count: Optional[int] = Field(default=None, ge=0)
    time_of_day: Optional[str] = Field(default=None, max_length=32)
    difficulty: Optional[str] = Field(default=None, max_length=32)


class HabitUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=4096)
    domain_link: Optional[str] = Field(default=None, max_length=64)
    schedule_type: Optional[str] = Field(default=None, max_length=32)
    target_count: Optional[int] = Field(default=None, ge=0)
    time_of_day: Optional[str] = Field(default=None, max_length=32)
    difficulty: Optional[str] = Field(default=None, max_length=32)
    is_active: Optional[bool] = None


class HabitLogCreate(BaseModel):
    logged_date: Optional[date] = None
    value: Optional[float] = None
    note: Optional[str] = Field(default=None, max_length=2048)


class HabitLogUpdate(BaseModel):
    logged_date: Optional[date] = None
    value: Optional[float] = None
    note: Optional[str] = Field(default=None, max_length=2048)


class HabitLogResponse(BaseModel):
    id: int
    habit_id: int
    logged_date: date
    value: Optional[float]
    note: Optional[str]


class HabitSummaryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    schedule_type: str
    target_count: Optional[int]
    time_of_day: Optional[str]
    difficulty: Optional[str]
    is_active: bool
    count: int
    last_logged_date: Optional[date]
    completed_today: bool


class HabitDetailResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    schedule_type: str
    target_count: Optional[int]
    time_of_day: Optional[str]
    difficulty: Optional[str]
    is_active: bool
    stats: dict
    logs: List[HabitLogResponse]

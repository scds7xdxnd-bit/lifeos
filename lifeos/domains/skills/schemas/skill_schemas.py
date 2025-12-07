"""Skill schemas and DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class SkillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: Optional[str] = Field(default=None, max_length=128)
    difficulty: Optional[str] = Field(default=None, max_length=32)
    target_level: Optional[int] = Field(default=None, ge=0)
    current_level: Optional[int] = Field(default=None, ge=0)
    description: Optional[str] = Field(default=None, max_length=4096)
    tags: Optional[List[str]] = None


class SkillUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    category: Optional[str] = Field(default=None, max_length=128)
    difficulty: Optional[str] = Field(default=None, max_length=32)
    target_level: Optional[int] = Field(default=None, ge=0)
    current_level: Optional[int] = Field(default=None, ge=0)
    description: Optional[str] = Field(default=None, max_length=4096)
    tags: Optional[List[str]] = None


class PracticeSessionCreate(BaseModel):
    duration_minutes: int = Field(gt=0)
    intensity: Optional[int] = Field(default=None, ge=1, le=10)
    notes: Optional[str] = Field(default=None, max_length=4096)
    practiced_at: Optional[datetime] = None


class PracticeSessionUpdate(BaseModel):
    duration_minutes: Optional[int] = Field(default=None, gt=0)
    intensity: Optional[int] = Field(default=None, ge=1, le=10)
    notes: Optional[str] = Field(default=None, max_length=4096)
    practiced_at: Optional[datetime] = None


class PracticeSessionResponse(BaseModel):
    id: int
    skill_id: int
    duration_minutes: int
    intensity: Optional[int]
    notes: Optional[str]
    practiced_at: datetime

    @field_validator("practiced_at", mode="before")
    @classmethod
    def _coerce_dt(cls, v):
        return v


class SkillSummaryResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    difficulty: Optional[str]
    target_level: Optional[int]
    current_level: Optional[int]
    description: Optional[str]
    tags: List[str] = []
    total_minutes: int
    session_count: int
    last_practiced_at: Optional[datetime]
    streak_days: int
    sessions_last_7: int
    sessions_last_30: int
    recent_sessions: List[PracticeSessionResponse]

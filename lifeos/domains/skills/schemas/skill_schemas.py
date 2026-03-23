"""Skill schemas and DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class SkillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: Optional[str] = Field(default=None, max_length=128)
    difficulty: Optional[str] = Field(default=None, max_length=32)
    goal_type: Optional[Literal["hours", "sessions", "milestones", "benchmark", "deadline"]] = None
    goal_target_value: Optional[int] = Field(default=None, gt=0)
    goal_deadline: Optional[datetime] = None
    target_level: Optional[int] = Field(default=None, ge=0)
    current_level: Optional[int] = Field(default=None, ge=0)
    description: Optional[str] = Field(default=None, max_length=4096)
    tags: Optional[List[str]] = None


class SkillUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    category: Optional[str] = Field(default=None, max_length=128)
    difficulty: Optional[str] = Field(default=None, max_length=32)
    goal_type: Optional[Literal["hours", "sessions", "milestones", "benchmark", "deadline"]] = None
    goal_target_value: Optional[int] = Field(default=None, gt=0)
    goal_deadline: Optional[datetime] = None
    target_level: Optional[int] = Field(default=None, ge=0)
    current_level: Optional[int] = Field(default=None, ge=0)
    description: Optional[str] = Field(default=None, max_length=4096)
    tags: Optional[List[str]] = None


class PracticeSessionCreate(BaseModel):
    duration_minutes: int = Field(gt=0)
    intensity: Optional[int] = Field(default=None, ge=1, le=10)
    step_id: Optional[int] = Field(default=None, ge=1)
    notes: Optional[str] = Field(default=None, max_length=4096)
    practiced_at: Optional[datetime] = None


class PracticeSessionUpdate(BaseModel):
    duration_minutes: Optional[int] = Field(default=None, gt=0)
    intensity: Optional[int] = Field(default=None, ge=1, le=10)
    step_id: Optional[int] = Field(default=None, ge=1)
    notes: Optional[str] = Field(default=None, max_length=4096)
    practiced_at: Optional[datetime] = None


class PracticeSessionResponse(BaseModel):
    id: int
    skill_id: int
    duration_minutes: int
    intensity: Optional[int]
    step_id: Optional[int]
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


class SkillGoalEndpointResponse(BaseModel):
    goal_type: Literal["hours", "sessions", "milestones", "benchmark", "deadline"]
    target_value: float
    current_value: float
    progress_ratio: float = Field(ge=0.0, le=1.0)
    deadline: Optional[datetime] = None


class SkillOverviewCardResponse(BaseModel):
    skill_id: int
    name: str
    category: Optional[str]
    total_minutes: int
    session_count: int
    progress_state: Literal["on_track", "at_risk", "completed"]
    goal: Optional[SkillGoalEndpointResponse] = None
    primary_action: Literal["continue_practice"]
    requires_goal_setup: bool
    risk_reason: Optional[Literal["no_recent_sessions"]] = None


class SkillPathStepResponse(BaseModel):
    step_id: str
    label: str
    status: Literal["ready", "recommended", "blocked", "completed"]
    action: Literal["continue_practice", "setup_goal", "review_goal"]


class SkillPathResponse(BaseModel):
    skill_id: int
    progress_state: Literal["on_track", "at_risk", "completed"]
    risk_reason: Optional[Literal["no_recent_sessions"]] = None
    goal: Optional[SkillGoalEndpointResponse] = None
    steps: List[SkillPathStepResponse]
    next_recommended_step: Optional[SkillPathStepResponse] = None


class SkillForecastBaselineResponse(BaseModel):
    avg_daily_minutes_last_14: float
    sessions_last_14: int
    total_minutes_last_14: int


class SkillForecastProjectionResponse(BaseModel):
    projected_minutes_next_window: int
    projected_sessions_next_window: int
    projected_goal_progress_ratio: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class SkillForecastResponse(BaseModel):
    skill_id: int
    horizon_days: int = Field(ge=1, le=90)
    forecast_state: Literal["on_track", "at_risk", "completed", "insufficient_data"]
    risk_reason: Optional[
        Literal["no_recent_sessions", "no_goal_configured", "insufficient_history", "non_projectable_goal_type"]
    ] = None
    goal: Optional[SkillGoalEndpointResponse] = None
    baseline: SkillForecastBaselineResponse
    projection: SkillForecastProjectionResponse

"""Calendar domain Pydantic schemas."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CalendarEventCreate(BaseModel):
    """Request body for creating a calendar event."""

    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    all_day: bool = False
    location: Optional[str] = Field(default=None, max_length=512)
    color: Optional[str] = Field(default=None, max_length=16)
    is_private: bool = False
    tags: list[str] = []
    metadata: dict = {}


class CalendarEventUpdate(BaseModel):
    """Request body for updating a calendar event."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    all_day: Optional[bool] = None
    location: Optional[str] = Field(default=None, max_length=512)
    color: Optional[str] = Field(default=None, max_length=16)
    is_private: Optional[bool] = None
    tags: Optional[list[str]] = None
    metadata: Optional[dict] = None


class CalendarEventResponse(BaseModel):
    """Response schema for a calendar event."""

    id: int
    user_id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    all_day: bool
    location: Optional[str]
    source: str
    external_id: Optional[str]
    color: Optional[str]
    is_private: bool
    tags: list[str]
    duration_minutes: Optional[int]
    created_at: datetime
    updated_at: datetime
    interpretations: Optional[list["InterpretationResponse"]] = None

    model_config = ConfigDict(from_attributes=True)


class InterpretationResponse(BaseModel):
    """Response schema for a calendar event interpretation."""

    id: int
    calendar_event_id: int
    domain: str
    record_type: str
    record_id: Optional[int]
    confidence_score: float
    status: str
    classification_data: dict
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InterpretationUpdate(BaseModel):
    """Request body for updating interpretation status."""

    status: Literal["confirmed", "rejected", "ignored"]


class CalendarEventListParams(BaseModel):
    """Query parameters for listing calendar events."""

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    source: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)

    @model_validator(mode="before")
    @classmethod
    def _normalize_dates(cls, values: dict):
        """Accept naive/offset datetimes or date strings; tolerate trailing Z."""

        def _parse(val):
            if val is None:
                return None
            if isinstance(val, datetime):
                return val
            if isinstance(val, date):
                return datetime.combine(val, time.min)
            if isinstance(val, str):
                raw = val.strip()
                if raw.endswith("Z"):
                    raw = raw[:-1] + "+00:00"
                try:
                    return datetime.fromisoformat(raw)
                except Exception:
                    return None
            return None

        values = dict(values or {})
        values["start_date"] = _parse(values.get("start_date"))
        values["end_date"] = _parse(values.get("end_date"))
        return values


class InterpretationListParams(BaseModel):
    """Query parameters for listing interpretations."""

    domain: Optional[str] = None
    status: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)

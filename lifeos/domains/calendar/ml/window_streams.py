"""ML-facing accessors for deterministic calendar windows and ledger slices.

These helpers wrap the backend-owned window logic (day/week/month) and the
ledger cursor API so ML/analysis code can consume canonical, replayable
event slices without reimplementing overlap or spillover rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Literal, Optional

from lifeos.domains.calendar.services import calendar_service

# Projection version for ML consumption; bump if overlap/spillover/ordering rules change.
CALENDAR_WINDOW_PROJECTION_VERSION = "v1"


@dataclass
class CalendarWindowSlice:
    """Deterministic calendar window suitable for ML/analysis."""

    window_type: Literal["day", "week", "month"]
    window_start: datetime
    window_end: datetime
    events: List[dict]
    spillover_days: List[str] = field(default_factory=list)
    projection_version: str = CALENDAR_WINDOW_PROJECTION_VERSION


@dataclass
class CalendarLedgerSlice:
    """Chronological ledger slice anchored to a date with stable ordering."""

    anchor: str
    direction: Literal["forward", "backward"]
    cursor: Optional[str]
    next_cursor: Optional[str]
    prev_cursor: Optional[str]
    events: List[dict]
    projection_version: str = CALENDAR_WINDOW_PROJECTION_VERSION


def day_slice_for_ml(user_id: int, target_date: date) -> CalendarWindowSlice:
    """Return the deterministic day window; no filters applied."""
    data = calendar_service.get_day_view(user_id, target_date)
    return CalendarWindowSlice(
        window_type="day",
        window_start=data["window_start"],
        window_end=data["window_end"],
        events=data["events"],
        spillover_days=[],
    )


def week_slice_for_ml(user_id: int, start_date: date) -> CalendarWindowSlice:
    """Return the deterministic week window starting on the given date."""
    data = calendar_service.get_week_view(user_id, start_date)
    return CalendarWindowSlice(
        window_type="week",
        window_start=data["window_start"],
        window_end=data["window_end"],
        events=data["events"],
        spillover_days=[],
    )


def month_slice_for_ml(user_id: int, year: int, month: int) -> CalendarWindowSlice:
    """Return the deterministic month grid window with spillover days included."""
    data = calendar_service.get_month_view(user_id, year, month)
    return CalendarWindowSlice(
        window_type="month",
        window_start=data["window_start"],
        window_end=data["window_end"],
        events=data["events"],
        spillover_days=data.get("spillover_days") or [],
    )


def ledger_slice_for_ml(
    user_id: int,
    anchor_date: date,
    direction: Literal["forward", "backward"] = "backward",
    limit: int = 50,
    cursor: Optional[str] = None,
) -> CalendarLedgerSlice:
    """Return a chronological ledger slice anchored to a date (default: today)."""
    data = calendar_service.get_ledger(
        user_id=user_id,
        anchor_date=anchor_date,
        direction=direction,
        limit=limit,
        cursor=cursor,
    )
    return CalendarLedgerSlice(
        anchor=data["anchor"],
        direction=data["direction"],
        cursor=data["cursor"],
        next_cursor=data["next_cursor"],
        prev_cursor=data["prev_cursor"],
        events=data["events"],
    )

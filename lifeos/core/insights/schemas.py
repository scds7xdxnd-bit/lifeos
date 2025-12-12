"""Pydantic schemas for insights API."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class InsightsFeedQuery(BaseModel):
    """Query params for /api/v1/insights/feed."""

    domain: Optional[str] = None
    severity: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

"""Pydantic schemas for insights API."""

from __future__ import annotations

from datetime import date
from typing import List, Optional, Sequence

from pydantic import BaseModel, Field, field_validator

ALLOWED_INFERENCE_STATUSES = {"inferred", "confirmed", "rejected", "ambiguous", "ignored"}
ALLOWED_INTERPRETATION_ACTIONS = {"accepted", "rejected", "corrected"}


class InsightsFeedQuery(BaseModel):
    """Query params for /api/v1/insights/feed."""

    domain: Optional[List[str]] = Field(
        default=None, description="Domain prefixes to match (comma-separated string or list)."
    )
    severity: Optional[str] = Field(default=None, description="Optional severity filter.")
    status: Optional[str] = Field(
        default=None,
        description="Optional inference status filter (inferred|confirmed|rejected|ambiguous|ignored).",
    )
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

    @field_validator("domain", mode="before")
    @classmethod
    def _normalize_domain(cls, value: Optional[Sequence[str] | str]):
        if value is None:
            return None
        parts: List[str] = []
        if isinstance(value, str):
            parts = [chunk.strip().lower() for chunk in value.split(",") if chunk.strip()]
        elif isinstance(value, Sequence):
            for item in value:
                if item is None:
                    continue
                if isinstance(item, str):
                    parts.extend([chunk.strip().lower() for chunk in item.split(",") if chunk.strip()])
                else:
                    parts.append(str(item))
        else:
            parts.append(str(value))
        return parts or None

    @field_validator("severity", mode="before")
    @classmethod
    def _normalize_severity(cls, value: Optional[str]):
        if value is None:
            return None
        normalized = str(value).strip().lower()
        return normalized or None

    @field_validator("status", mode="before")
    @classmethod
    def _validate_status(cls, value: Optional[str]):
        if value is None:
            return None
        normalized = str(value).strip().lower()
        if not normalized:
            return None
        if normalized not in ALLOWED_INFERENCE_STATUSES:
            raise ValueError("invalid_status")
        return normalized


class InterpretationDecisionRequest(BaseModel):
    """Decision payload for proposal acceptance/rejection/correction."""

    action: str = Field(description="accepted|rejected|corrected")
    person_id: Optional[int] = None
    method: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("action", mode="before")
    @classmethod
    def _validate_action(cls, value: Optional[str]):
        if value is None:
            raise ValueError("invalid_action")
        normalized = str(value).strip().lower()
        if normalized not in ALLOWED_INTERPRETATION_ACTIONS:
            raise ValueError("invalid_action")
        return normalized

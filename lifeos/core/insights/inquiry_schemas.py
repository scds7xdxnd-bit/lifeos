"""Pydantic schemas for Phase 6 focused inquiry APIs."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

ALLOWED_INQUIRY_DOMAINS = {
    "calendar",
    "finance",
    "habits",
    "skills",
    "health",
    "projects",
    "relationships",
    "journal",
}


def _normalize_question(value: str) -> str:
    return " ".join((value or "").strip().split())


def _normalize_context(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = " ".join(value.strip().split())
    return normalized or None


def _normalize_domains(value: Optional[list[str] | str]) -> list[str]:
    if value is None:
        return []
    parts: list[str] = []
    if isinstance(value, str):
        parts = [chunk.strip().lower() for chunk in value.split(",") if chunk.strip()]
    else:
        for item in value:
            if item is None:
                continue
            parts.extend([chunk.strip().lower() for chunk in str(item).split(",") if chunk.strip()])
    # Stable deterministic ordering.
    return sorted(set(parts))


class InquiryCreateRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    domain: Optional[str] = None
    domains: Optional[list[str] | str] = None
    cross_domain: bool = False
    timeframe_start: date
    timeframe_end: date
    as_of_ts: Optional[datetime] = None
    context_text: Optional[str] = None

    @field_validator("question", mode="before")
    @classmethod
    def _question(cls, value: str):
        normalized = _normalize_question(value)
        if len(normalized) < 3:
            raise ValueError("question_too_short")
        return normalized

    @field_validator("domain", mode="before")
    @classmethod
    def _domain(cls, value: Optional[str]):
        if value is None:
            return None
        normalized = str(value).strip().lower()
        return normalized or None

    @field_validator("domains", mode="before")
    @classmethod
    def _domains(cls, value):
        return _normalize_domains(value)

    @field_validator("context_text", mode="before")
    @classmethod
    def _context_text(cls, value):
        return _normalize_context(value)

    @model_validator(mode="after")
    def _validate_scope(self):
        if self.timeframe_start > self.timeframe_end:
            raise ValueError("invalid_timeframe")

        scoped_domains = set(self.domains or [])
        if self.domain:
            scoped_domains.add(self.domain)
        if not scoped_domains:
            raise ValueError("domain_required")

        invalid = scoped_domains - ALLOWED_INQUIRY_DOMAINS
        if invalid:
            raise ValueError(f"invalid_domain:{','.join(sorted(invalid))}")

        if self.cross_domain:
            if len(scoped_domains) < 2:
                raise ValueError("cross_domain_requires_multiple_domains")
        elif len(scoped_domains) != 1:
            raise ValueError("single_domain_required")

        self.domains = sorted(scoped_domains)
        self.domain = self.domains[0]
        return self


class InquiryRefineRequest(BaseModel):
    question: Optional[str] = Field(default=None, min_length=3, max_length=500)
    domain: Optional[str] = None
    domains: Optional[list[str] | str] = None
    cross_domain: Optional[bool] = None
    timeframe_start: Optional[date] = None
    timeframe_end: Optional[date] = None
    as_of_ts: Optional[datetime] = None
    context_text: Optional[str] = None

    @field_validator("question", mode="before")
    @classmethod
    def _question(cls, value):
        if value is None:
            return None
        normalized = _normalize_question(value)
        if len(normalized) < 3:
            raise ValueError("question_too_short")
        return normalized

    @field_validator("domain", mode="before")
    @classmethod
    def _domain(cls, value):
        if value is None:
            return None
        normalized = str(value).strip().lower()
        return normalized or None

    @field_validator("domains", mode="before")
    @classmethod
    def _domains(cls, value):
        if value is None:
            return None
        return _normalize_domains(value)

    @field_validator("context_text", mode="before")
    @classmethod
    def _context_text(cls, value):
        if value is None:
            return None
        return _normalize_context(value)

    @model_validator(mode="after")
    def _validate_changes(self):
        if (
            self.question is None
            and self.domain is None
            and self.domains is None
            and self.cross_domain is None
            and self.timeframe_start is None
            and self.timeframe_end is None
            and self.as_of_ts is None
            and self.context_text is None
        ):
            raise ValueError("no_refine_changes")

        if (self.timeframe_start and not self.timeframe_end) or (self.timeframe_end and not self.timeframe_start):
            raise ValueError("timeframe_pair_required")
        if self.timeframe_start and self.timeframe_end and self.timeframe_start > self.timeframe_end:
            raise ValueError("invalid_timeframe")

        if self.domain and self.domain not in ALLOWED_INQUIRY_DOMAINS:
            raise ValueError("invalid_domain")
        if self.domains:
            invalid = set(self.domains) - ALLOWED_INQUIRY_DOMAINS
            if invalid:
                raise ValueError("invalid_domain")
        return self

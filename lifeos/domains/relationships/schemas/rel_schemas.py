"""Relationships schemas and DTOs."""

from __future__ import annotations

from datetime import date as dt_date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class PersonCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    relationship_type: Optional[str] = Field(default=None, max_length=64)
    importance_level: Optional[int] = Field(default=None, ge=0)
    tags: Optional[List[str]] = None
    notes: Optional[str] = Field(default=None, max_length=4096)
    birthday: Optional[dt_date] = None
    first_met_date: Optional[dt_date] = None


class PersonUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    relationship_type: Optional[str] = Field(default=None, max_length=64)
    importance_level: Optional[int] = Field(default=None, ge=0)
    tags: Optional[List[str]] = None
    notes: Optional[str] = Field(default=None, max_length=4096)
    birthday: Optional[dt_date] = None
    first_met_date: Optional[dt_date] = None


class InteractionCreate(BaseModel):
    date: Optional[dt_date] = None
    method: Optional[str] = Field(default=None, max_length=64)
    notes: Optional[str] = Field(default=None, max_length=4096)
    sentiment: Optional[str] = Field(default=None, max_length=32)

    @field_validator("date", mode="before")
    @classmethod
    def _coerce_date(cls, value):
        if value is None or isinstance(value, dt_date):
            return value
        if isinstance(value, str) and value.strip():
            return dt_date.fromisoformat(value)
        raise ValueError("invalid_date")


class InteractionUpdate(BaseModel):
    date: Optional[dt_date] = None
    method: Optional[str] = Field(default=None, max_length=64)
    notes: Optional[str] = Field(default=None, max_length=4096)
    sentiment: Optional[str] = Field(default=None, max_length=32)

    @field_validator("date", mode="before")
    @classmethod
    def _coerce_date(cls, value):
        if value is None or isinstance(value, dt_date):
            return value
        if isinstance(value, str) and value.strip():
            return dt_date.fromisoformat(value)
        raise ValueError("invalid_date")

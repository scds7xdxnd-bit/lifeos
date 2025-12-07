"""Relationships schemas and DTOs."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class PersonCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    relationship_type: Optional[str] = Field(default=None, max_length=64)
    importance_level: Optional[int] = Field(default=None, ge=0)
    tags: Optional[List[str]] = None
    notes: Optional[str] = Field(default=None, max_length=4096)
    birthday: Optional[date] = None
    first_met_date: Optional[date] = None


class PersonUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    relationship_type: Optional[str] = Field(default=None, max_length=64)
    importance_level: Optional[int] = Field(default=None, ge=0)
    tags: Optional[List[str]] = None
    notes: Optional[str] = Field(default=None, max_length=4096)
    birthday: Optional[date] = None
    first_met_date: Optional[date] = None


class InteractionCreate(BaseModel):
    date: Optional[date] = None
    method: Optional[str] = Field(default=None, max_length=64)
    notes: Optional[str] = Field(default=None, max_length=4096)
    sentiment: Optional[str] = Field(default=None, max_length=32)


class InteractionUpdate(BaseModel):
    date: Optional[date] = None
    method: Optional[str] = Field(default=None, max_length=64)
    notes: Optional[str] = Field(default=None, max_length=4096)
    sentiment: Optional[str] = Field(default=None, max_length=32)

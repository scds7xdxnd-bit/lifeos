"""Project schemas."""

from __future__ import annotations

import datetime as dt
from typing import Optional

from pydantic import BaseModel, Field


class Pagination(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=50, ge=1, le=200)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=4096)
    target_date: Optional[dt.date] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=4096)
    status: Optional[str] = Field(default=None, max_length=32)
    target_date: Optional[dt.date] = None


class ProjectListFilter(Pagination):
    status: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    status: str
    target_date: Optional[dt.date]
    created_at: dt.datetime
    updated_at: Optional[dt.datetime]

    model_config = {"from_attributes": True}


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    due_date: Optional[dt.date] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    notes: Optional[str] = Field(default=None, max_length=4096)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    status: Optional[str] = Field(default=None, max_length=32)
    due_date: Optional[dt.date] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    notes: Optional[str] = Field(default=None, max_length=4096)


class TaskListFilter(Pagination):
    status: Optional[str] = None
    due_before: Optional[dt.date] = None


class TaskLogCreate(BaseModel):
    note: Optional[str] = Field(default=None, max_length=4096)
    status_snapshot: Optional[str] = Field(default=None, max_length=32)

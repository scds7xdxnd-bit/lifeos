"""Journal request/response schemas."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class JournalEntryCreate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    body: str = Field(min_length=1)
    entry_date: Optional[date] = None
    mood: Optional[int] = Field(default=None)
    tags: Optional[List[str]] = None
    is_private: bool = True
    sentiment_score: Optional[float] = None
    emotion_label: Optional[str] = Field(default=None, max_length=64)


class JournalEntryUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)
    body: Optional[str] = None
    entry_date: Optional[date] = None
    mood: Optional[int] = None
    tags: Optional[List[str]] = None
    is_private: Optional[bool] = None
    sentiment_score: Optional[float] = None
    emotion_label: Optional[str] = Field(default=None, max_length=64)


class JournalEntryListFilter(BaseModel):
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    mood: Optional[int] = None
    tag: Optional[str] = None
    search_text: Optional[str] = None
    page: int = 1
    per_page: int = 20


class JournalEntryResponse(BaseModel):
    id: int
    title: Optional[str]
    body: str
    entry_date: date
    mood: Optional[int]
    tags: List[str]
    is_private: bool
    sentiment_score: Optional[float]
    emotion_label: Optional[str]
    created_at: str
    updated_at: str

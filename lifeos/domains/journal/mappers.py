"""Journal mappers for DTO responses."""

from __future__ import annotations

from lifeos.domains.journal.models import JournalEntry
from lifeos.domains.journal.schemas.journal_schemas import JournalEntryResponse


def map_entry(entry: JournalEntry) -> dict:
    return JournalEntryResponse(
        id=entry.id,
        title=entry.title,
        body=entry.body,
        entry_date=entry.entry_date,
        mood=entry.mood,
        tags=entry.tags or [],
        is_private=entry.is_private,
        sentiment_score=(float(entry.sentiment_score) if entry.sentiment_score is not None else None),
        emotion_label=entry.emotion_label,
        created_at=entry.created_at.isoformat() if entry.created_at else "",
        updated_at=entry.updated_at.isoformat() if entry.updated_at else "",
    ).model_dump()

"""Journal services: CRUD and listing with event emission."""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import List, Optional, Tuple

import sqlalchemy as sa

from lifeos.domains.journal.events import (
    JOURNAL_ENTRY_CREATED,
    JOURNAL_ENTRY_DELETED,
    JOURNAL_ENTRY_UPDATED,
)
from lifeos.domains.journal.models import JournalEntry
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox import enqueue as enqueue_outbox

MOOD_MIN = -5
MOOD_MAX = 10


def create_entry(
    user_id: int,
    *,
    title: Optional[str],
    body: str,
    entry_date: date,
    mood: Optional[int] = None,
    tags: Optional[List[str]] = None,
    is_private: bool = True,
    sentiment_score: float | None = None,
    emotion_label: str | None = None,
) -> JournalEntry:
    mood_val = _validate_mood(mood)
    title_norm = (title or "").strip() or None
    body_text = (body or "").strip()
    if not body_text:
        raise ValueError("validation_error")
    tags_norm = _normalize_tags(tags)
    entry = JournalEntry(
        user_id=user_id,
        title=title_norm,
        body=body_text,
        entry_date=entry_date or date.today(),
        mood=mood_val,
        tags=tags_norm,
        is_private=bool(is_private),
        sentiment_score=sentiment_score,
        emotion_label=(emotion_label or "").strip() or None,
    )
    db.session.add(entry)
    db.session.flush()
    enqueue_outbox(
        JOURNAL_ENTRY_CREATED,
        {
            "entry_id": entry.id,
            "user_id": user_id,
            "entry_date": entry.entry_date.isoformat(),
            "mood": entry.mood,
            "tags": entry.tags,
            "is_private": entry.is_private,
            "created_at": (entry.created_at.isoformat() if entry.created_at else datetime.utcnow().isoformat()),
        },
        user_id=user_id,
    )
    db.session.commit()
    return entry


def update_entry(user_id: int, entry_id: int, **fields) -> Optional[JournalEntry]:
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=user_id).first()
    if not entry:
        return None
    changed = {}
    for key in (
        "title",
        "body",
        "entry_date",
        "mood",
        "tags",
        "is_private",
        "sentiment_score",
        "emotion_label",
    ):
        if key in fields:
            val = fields[key]
            if key == "mood":
                val = _validate_mood(val)
            if key == "tags":
                val = _normalize_tags(val)
            if isinstance(val, str):
                val = val.strip()
            setattr(entry, key if key != "body" else "body", val)
            changed[key] = val
    enqueue_outbox(
        JOURNAL_ENTRY_UPDATED,
        {
            "entry_id": entry.id,
            "user_id": user_id,
            "fields": changed,
            "updated_at": (entry.updated_at.isoformat() if entry.updated_at else datetime.utcnow().isoformat()),
        },
        user_id=user_id,
    )
    db.session.commit()
    return entry


def delete_entry(user_id: int, entry_id: int) -> bool:
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=user_id).first()
    if not entry:
        return False
    db.session.delete(entry)
    enqueue_outbox(
        JOURNAL_ENTRY_DELETED,
        {"entry_id": entry_id, "user_id": user_id},
        user_id=user_id,
    )
    db.session.commit()
    return True


def get_entry(user_id: int, entry_id: int) -> Optional[JournalEntry]:
    return JournalEntry.query.filter_by(id=entry_id, user_id=user_id).first()


def list_entries(
    user_id: int,
    *,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    mood: Optional[int] = None,
    tag: Optional[str] = None,
    search_text: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
) -> Tuple[List[JournalEntry], int]:
    query = JournalEntry.query.filter_by(user_id=user_id)
    if date_from:
        query = query.filter(JournalEntry.entry_date >= date_from)
    if date_to:
        query = query.filter(JournalEntry.entry_date <= date_to)
    if mood is not None:
        query = query.filter(JournalEntry.mood == _validate_mood(mood))
    if tag:
        normalized_tag = _normalize_tag(tag)
        if normalized_tag:
            dialect = db.session.bind.dialect.name if db.session.bind else ""
            tag_variants = [normalized_tag, f"#{normalized_tag}"]
            if dialect == "postgresql":
                # Explicit JSONB containment to avoid LIKE fallback.
                tag_literal = json.dumps([tag_variants[0]])
                tag_literal_alt = json.dumps([tag_variants[1]])
                query = query.filter(
                    sa.or_(
                        sa.text("journal_entry.tags::jsonb @> :tag_literal"),
                        sa.text("journal_entry.tags::jsonb @> :tag_literal_alt"),
                    )
                ).params(tag_literal=tag_literal, tag_literal_alt=tag_literal_alt)
            elif dialect == "sqlite":
                clauses = []
                params = {}
                for idx, variant in enumerate(tag_variants):
                    key = f"tag_{idx}"
                    clauses.append(
                        sa.text(
                            "EXISTS (SELECT 1 FROM json_each(journal_entry.tags) WHERE value = :{key})".format(key=key)
                        )
                    )
                    params[key] = variant
                query = query.filter(sa.or_(*clauses)).params(**params)
            else:
                clauses = [JournalEntry.tags.contains([variant]) for variant in tag_variants if variant]
                query = query.filter(sa.or_(*clauses))
    if search_text:
        like = f"%{search_text}%"
        query = query.filter(
            db.or_(
                JournalEntry.title.ilike(like),
                JournalEntry.body.ilike(like),
            )
        )
    total = query.count()
    entries = (
        query.order_by(JournalEntry.entry_date.desc(), JournalEntry.created_at.desc())
        .offset((max(page, 1) - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return entries, total


def _validate_mood(mood: Optional[int]) -> Optional[int]:
    if mood is None:
        return None
    try:
        mood_int = int(mood)
    except (TypeError, ValueError):
        raise ValueError("validation_error")
    if mood_int < MOOD_MIN or mood_int > MOOD_MAX:
        raise ValueError("validation_error")
    return mood_int


def _normalize_tag(tag: str | None) -> str:
    if not tag:
        return ""
    return str(tag).strip().lstrip("#")


def _normalize_tags(tags: Optional[List[str]]) -> List[str]:
    cleaned: List[str] = []
    for tag in tags or []:
        normalized = _normalize_tag(tag)
        if not normalized:
            continue
        if normalized in cleaned:
            continue
        cleaned.append(normalized)
    return cleaned

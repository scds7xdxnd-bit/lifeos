"""Journal domain event catalog."""

from __future__ import annotations

JOURNAL_ENTRY_CREATED = "journal.entry.created"
JOURNAL_ENTRY_UPDATED = "journal.entry.updated"
JOURNAL_ENTRY_DELETED = "journal.entry.deleted"

EVENT_CATALOG = {
    JOURNAL_ENTRY_CREATED: {
        "version": "v1",
        "payload": {
            "entry_id": "int",
            "user_id": "int",
            "entry_date": "date",
            "mood": "int?",
            "tags": "list[str]",
            "is_private": "bool",
            "created_at": "datetime",
        },
    },
    JOURNAL_ENTRY_UPDATED: {
        "version": "v1",
        "payload": {
            "entry_id": "int",
            "user_id": "int",
            "fields": "dict",
            "updated_at": "datetime",
        },
    },
    JOURNAL_ENTRY_DELETED: {
        "version": "v1",
        "payload": {
            "entry_id": "int",
            "user_id": "int",
        },
    },
}

__all__ = [
    "EVENT_CATALOG",
    "JOURNAL_ENTRY_CREATED",
    "JOURNAL_ENTRY_UPDATED",
    "JOURNAL_ENTRY_DELETED",
]

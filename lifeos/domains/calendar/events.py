"""Calendar domain event catalog."""

from __future__ import annotations

# Event type constants
CALENDAR_EVENT_CREATED = "calendar.event.created"
CALENDAR_EVENT_UPDATED = "calendar.event.updated"
CALENDAR_EVENT_DELETED = "calendar.event.deleted"
CALENDAR_EVENT_SYNCED = "calendar.event.synced"

CALENDAR_INTERPRETATION_CREATED = "calendar.interpretation.created"
CALENDAR_INTERPRETATION_CONFIRMED = "calendar.interpretation.confirmed"
CALENDAR_INTERPRETATION_REJECTED = "calendar.interpretation.rejected"

EVENT_CATALOG = {
    CALENDAR_EVENT_CREATED: {
        "version": "v1",
        "payload": {
            "event_id": "int",
            "user_id": "int",
            "title": "str",
            "start_time": "datetime",
            "end_time": "datetime?",
            "source": "str",
            "all_day": "bool",
            "created_at": "datetime",
        },
    },
    CALENDAR_EVENT_UPDATED: {
        "version": "v1",
        "payload": {
            "event_id": "int",
            "user_id": "int",
            "title": "str",
            "start_time": "datetime",
            "end_time": "datetime?",
            "source": "str",
            "updated_at": "datetime",
            "changed_fields": "list[str]",
        },
    },
    CALENDAR_EVENT_DELETED: {
        "version": "v1",
        "payload": {
            "event_id": "int",
            "user_id": "int",
            "deleted_at": "datetime",
        },
    },
    CALENDAR_EVENT_SYNCED: {
        "version": "v1",
        "payload": {
            "user_id": "int",
            "source": "str",
            "events_synced": "int",
            "synced_at": "datetime",
        },
    },
    CALENDAR_INTERPRETATION_CREATED: {
        "version": "v1",
        "payload": {
            "interpretation_id": "int",
            "calendar_event_id": "int",
            "user_id": "int",
            "domain": "str",
            "record_type": "str",
            "confidence_score": "float",
            "created_at": "datetime",
        },
    },
    CALENDAR_INTERPRETATION_CONFIRMED: {
        "version": "v1",
        "payload": {
            "interpretation_id": "int",
            "calendar_event_id": "int",
            "user_id": "int",
            "domain": "str",
            "record_type": "str",
            "record_id": "int",
            "confirmed_at": "datetime",
        },
    },
    CALENDAR_INTERPRETATION_REJECTED: {
        "version": "v1",
        "payload": {
            "interpretation_id": "int",
            "calendar_event_id": "int",
            "user_id": "int",
            "domain": "str",
            "record_type": "str",
            "rejected_at": "datetime",
        },
    },
}

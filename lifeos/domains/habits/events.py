"""Habits domain event catalog."""

from __future__ import annotations

HABITS_HABIT_CREATED = "habits.habit.created"
HABITS_HABIT_UPDATED = "habits.habit.updated"
HABITS_HABIT_DEACTIVATED = "habits.habit.deactivated"
HABITS_HABIT_LOGGED = "habits.habit.logged"
HABITS_HABIT_DELETED = "habits.habit.deleted"
HABITS_HABIT_INFERRED = "habits.habit.inferred"

EVENT_CATALOG = {
    HABITS_HABIT_CREATED: {
        "version": "v1",
        "payload": {
            "habit_id": "int",
            "user_id": "int",
            "name": "str",
            "schedule_type": "str",
            "target_count": "int?",
            "domain_link": "str?",
            "is_active": "bool",
            "created_at": "datetime",
        },
    },
    HABITS_HABIT_UPDATED: {
        "version": "v1",
        "payload": {
            "habit_id": "int",
            "user_id": "int",
            "fields": "dict",
            "updated_at": "datetime",
        },
    },
    HABITS_HABIT_DEACTIVATED: {
        "version": "v1",
        "payload": {
            "habit_id": "int",
            "user_id": "int",
            "deactivated_at": "datetime",
        },
    },
    HABITS_HABIT_LOGGED: {
        "version": "v1",
        "payload": {
            "log_id": "int",
            "habit_id": "int",
            "user_id": "int",
            "logged_date": "date",
            "value": "decimal?",
            "note": "str?",
        },
    },
    HABITS_HABIT_DELETED: {
        "version": "v1",
        "payload": {
            "habit_id": "int",
            "user_id": "int",
            "deleted_at": "datetime",
        },
    },
    HABITS_HABIT_INFERRED: {
        "version": "v1",
        "payload": {
            "log_id": "int",
            "habit_id": "int",
            "calendar_event_id": "int",
            "user_id": "int",
            "confidence_score": "float",
            "payload_version": "str",
            "is_false_positive": "bool?",
            "is_false_negative": "bool?",
        },
    },
}

__all__ = [
    "EVENT_CATALOG",
    "HABITS_HABIT_CREATED",
    "HABITS_HABIT_UPDATED",
    "HABITS_HABIT_DEACTIVATED",
    "HABITS_HABIT_LOGGED",
    "HABITS_HABIT_DELETED",
    "HABITS_HABIT_INFERRED",
]

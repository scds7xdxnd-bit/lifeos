"""Projects domain event catalog."""

from __future__ import annotations

PROJECT_CREATED = "projects.project.created"
PROJECT_UPDATED = "projects.project.updated"
PROJECT_ARCHIVED = "projects.project.archived"
PROJECT_COMPLETED = "projects.project.completed"
TASK_CREATED = "projects.task.created"
TASK_UPDATED = "projects.task.updated"
TASK_COMPLETED = "projects.task.completed"
TASK_LOGGED = "projects.task.logged"
WORK_SESSION_INFERRED = "projects.work_session.inferred"

EVENT_CATALOG = {
    PROJECT_CREATED: {
        "version": "v1",
        "payload": {
            "project_id": "int",
            "user_id": "int",
            "name": "str",
            "status": "str",
            "target_date": "date?",
            "created_at": "datetime",
        },
    },
    PROJECT_UPDATED: {
        "version": "v1",
        "payload": {
            "project_id": "int",
            "user_id": "int",
            "fields": "dict",
            "updated_at": "datetime",
        },
    },
    PROJECT_ARCHIVED: {
        "version": "v1",
        "payload": {
            "project_id": "int",
            "user_id": "int",
            "archived_at": "datetime",
        },
    },
    PROJECT_COMPLETED: {
        "version": "v1",
        "payload": {
            "project_id": "int",
            "user_id": "int",
            "completed_at": "datetime",
        },
    },
    TASK_CREATED: {
        "version": "v1",
        "payload": {
            "task_id": "int",
            "project_id": "int",
            "user_id": "int",
            "title": "str",
            "status": "str",
            "due_date": "date?",
            "priority": "int?",
        },
    },
    TASK_UPDATED: {
        "version": "v1",
        "payload": {
            "task_id": "int",
            "project_id": "int",
            "user_id": "int",
            "fields": "dict",
            "updated_at": "datetime",
        },
    },
    TASK_COMPLETED: {
        "version": "v1",
        "payload": {
            "task_id": "int",
            "project_id": "int",
            "user_id": "int",
            "completed_at": "datetime",
        },
    },
    TASK_LOGGED: {
        "version": "v1",
        "payload": {
            "log_id": "int",
            "task_id": "int",
            "project_id": "int",
            "user_id": "int",
            "status_snapshot": "str?",
            "logged_at": "datetime",
        },
    },
    WORK_SESSION_INFERRED: {
        "version": "v1",
        "payload": {
            "log_id": "int",
            "project_id": "int?",
            "task_id": "int?",
            "calendar_event_id": "int",
            "user_id": "int",
            "confidence_score": "float",
            "payload_version": "str",
            "model_version": "str?",
            "is_false_positive": "bool?",
            "is_false_negative": "bool?",
        },
    },
}

__all__ = [
    "EVENT_CATALOG",
    "PROJECT_CREATED",
    "PROJECT_UPDATED",
    "PROJECT_ARCHIVED",
    "PROJECT_COMPLETED",
    "TASK_CREATED",
    "TASK_UPDATED",
    "TASK_COMPLETED",
    "TASK_LOGGED",
    "WORK_SESSION_INFERRED",
]

"""Relationships domain event catalog."""

from __future__ import annotations

REL_PERSON_CREATED = "relationships.person.created"
REL_PERSON_UPDATED = "relationships.person.updated"
REL_PERSON_DELETED = "relationships.person.deleted"
REL_INTERACTION_LOGGED = "relationships.interaction.logged"
REL_INTERACTION_UPDATED = "relationships.interaction.updated"
REL_INTERACTION_INFERRED = "relationships.interaction.inferred"

EVENT_CATALOG = {
    REL_PERSON_CREATED: {
        "version": "v1",
        "payload": {
            "person_id": "int",
            "user_id": "int",
            "name": "str",
            "relationship_type": "str?",
            "importance_level": "int?",
            "created_at": "datetime",
        },
    },
    REL_PERSON_UPDATED: {
        "version": "v1",
        "payload": {
            "person_id": "int",
            "user_id": "int",
            "fields": "dict",
            "updated_at": "datetime",
        },
    },
    REL_PERSON_DELETED: {
        "version": "v1",
        "payload": {
            "person_id": "int",
            "user_id": "int",
        },
    },
    REL_INTERACTION_LOGGED: {
        "version": "v1",
        "payload": {
            "interaction_id": "int",
            "person_id": "int",
            "user_id": "int",
            "date": "date",
            "method": "str?",
            "sentiment": "str?",
        },
    },
    REL_INTERACTION_UPDATED: {
        "version": "v1",
        "payload": {
            "interaction_id": "int",
            "person_id": "int",
            "user_id": "int",
            "fields": "dict",
            "updated_at": "datetime",
        },
    },
    REL_INTERACTION_INFERRED: {
        "version": "v1",
        "payload": {
            "interaction_id": "int",
            "person_id": "int?",
            "calendar_event_id": "int",
            "user_id": "int",
            "confidence_score": "float",
            "interaction_type": "str",
            "payload_version": "str",
            "model_version": "str?",
            "is_false_positive": "bool?",
            "is_false_negative": "bool?",
        },
    },
}

__all__ = [
    "EVENT_CATALOG",
    "REL_PERSON_CREATED",
    "REL_PERSON_UPDATED",
    "REL_PERSON_DELETED",
    "REL_INTERACTION_LOGGED",
    "REL_INTERACTION_UPDATED",
    "REL_INTERACTION_INFERRED",
]

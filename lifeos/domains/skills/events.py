"""Skills domain event catalog."""

from __future__ import annotations

SKILLS_SKILL_CREATED = "skills.skill.created"
SKILLS_SKILL_UPDATED = "skills.skill.updated"
SKILLS_SKILL_DELETED = "skills.skill.deleted"
SKILLS_PRACTICE_LOGGED = "skills.practice.logged"

EVENT_CATALOG = {
    SKILLS_SKILL_CREATED: {
        "version": "v1",
        "payload": {
            "skill_id": "int",
            "user_id": "int",
            "name": "str",
            "category": "str?",
            "difficulty": "str?",
            "target_level": "int?",
            "current_level": "int?",
            "created_at": "datetime",
        },
    },
    SKILLS_SKILL_UPDATED: {
        "version": "v1",
        "payload": {
            "skill_id": "int",
            "user_id": "int",
            "fields": "dict",
            "updated_at": "datetime",
        },
    },
    SKILLS_SKILL_DELETED: {
        "version": "v1",
        "payload": {
            "skill_id": "int",
            "user_id": "int",
        },
    },
    SKILLS_PRACTICE_LOGGED: {
        "version": "v1",
        "payload": {
            "session_id": "int",
            "skill_id": "int",
            "user_id": "int",
            "duration_minutes": "int",
            "intensity": "int?",
            "practiced_at": "datetime",
        },
    },
}

__all__ = [
    "EVENT_CATALOG",
    "SKILLS_SKILL_CREATED",
    "SKILLS_SKILL_UPDATED",
    "SKILLS_SKILL_DELETED",
    "SKILLS_PRACTICE_LOGGED",
]

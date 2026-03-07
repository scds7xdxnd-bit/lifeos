"""DTO ↔ dict mappers for relationships domain."""

from __future__ import annotations

from lifeos.domains.relationships.models.interaction_models import Interaction
from lifeos.domains.relationships.models.person_models import Person


def map_person(person: Person) -> dict:
    last_date = getattr(person, "last_interaction_date", None)
    return {
        "id": person.id,
        "name": person.name,
        "relationship_type": person.relationship_type,
        "importance_level": person.importance_level,
        "tags": person.tags or [],
        "notes": person.notes,
        "birthday": person.birthday.isoformat() if person.birthday else None,
        "first_met_date": (person.first_met_date.isoformat() if person.first_met_date else None),
        "last_interaction_date": last_date.isoformat() if last_date else None,
        "last_interaction_method": getattr(person, "last_interaction_method", None),
        "created_at": person.created_at.isoformat() if person.created_at else None,
        "updated_at": person.updated_at.isoformat() if person.updated_at else None,
    }


def map_interaction(interaction: Interaction) -> dict:
    return {
        "id": interaction.id,
        "person_id": interaction.person_id,
        "date": interaction.date.isoformat(),
        "method": interaction.method,
        "notes": interaction.notes,
        "sentiment": interaction.sentiment,
        "created_at": (interaction.created_at.isoformat() if interaction.created_at else None),
    }

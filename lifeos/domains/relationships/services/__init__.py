"""Relationship services: people and interactions with outbox events."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from lifeos.domains.relationships.events import (
    REL_INTERACTION_LOGGED,
    REL_INTERACTION_UPDATED,
    REL_PERSON_CREATED,
    REL_PERSON_DELETED,
    REL_PERSON_UPDATED,
)
from lifeos.domains.relationships.models.interaction_models import Interaction
from lifeos.domains.relationships.models.person_models import Person
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox import enqueue as enqueue_outbox


def _latest_interaction_subquery(user_id: int):
    return (
        db.session.query(
            Interaction.person_id.label("person_id"),
            Interaction.date.label("date"),
            Interaction.method.label("method"),
            func.row_number()
            .over(
                partition_by=Interaction.person_id,
                order_by=(
                    Interaction.date.desc(),
                    Interaction.created_at.desc(),
                    Interaction.id.desc(),
                ),
            )
            .label("rank"),
        )
        .filter(Interaction.user_id == user_id)
        .subquery()
    )


def create_person(
    user_id: int,
    *,
    name: str,
    relationship_type: Optional[str] = None,
    importance_level: Optional[int] = None,
    tags: Optional[List[str]] = None,
    notes: Optional[str] = None,
    birthday: Optional[date] = None,
    first_met_date: Optional[date] = None,
) -> Person:
    name_norm = (name or "").strip()
    if not name_norm:
        raise ValueError("validation_error")
    existing = Person.query.filter_by(user_id=user_id, name=name_norm).first()
    if existing:
        raise ValueError("duplicate")

    person = Person(
        user_id=user_id,
        name=name_norm,
        relationship_type=(relationship_type or "").strip() or None,
        importance_level=importance_level,
        tags=tags or [],
        notes=(notes or "").strip() or None,
        birthday=birthday,
        first_met_date=first_met_date,
    )
    db.session.add(person)
    db.session.flush()
    enqueue_outbox(
        REL_PERSON_CREATED,
        {
            "person_id": person.id,
            "user_id": user_id,
            "name": person.name,
            "relationship_type": person.relationship_type,
            "importance_level": person.importance_level,
            "created_at": person.created_at.isoformat(),
        },
        user_id=user_id,
    )
    db.session.commit()
    return person


def update_person(user_id: int, person_id: int, **fields) -> Optional[Person]:
    person = Person.query.filter_by(id=person_id, user_id=user_id).first()
    if not person:
        return None

    allowed = (
        "name",
        "relationship_type",
        "importance_level",
        "tags",
        "notes",
        "birthday",
        "first_met_date",
    )
    changed: Dict[str, object] = {}
    for key in allowed:
        if key in fields:
            val = fields[key]
            if isinstance(val, str):
                val = val.strip()
            setattr(person, key, val)
            changed[key] = val
    enqueue_outbox(
        REL_PERSON_UPDATED,
        {
            "person_id": person.id,
            "user_id": user_id,
            "fields": changed,
            "updated_at": (person.updated_at.isoformat() if person.updated_at else datetime.utcnow().isoformat()),
        },
        user_id=user_id,
    )
    db.session.commit()
    return person


def delete_person(user_id: int, person_id: int) -> bool:
    person = Person.query.filter_by(id=person_id, user_id=user_id).first()
    if not person:
        return False
    db.session.delete(person)
    enqueue_outbox(
        REL_PERSON_DELETED,
        {"person_id": person_id, "user_id": user_id},
        user_id=user_id,
    )
    db.session.commit()
    return True


def get_person(user_id: int, person_id: int) -> Optional[Person]:
    latest = _latest_interaction_subquery(user_id)
    row = (
        db.session.query(Person, latest.c.date, latest.c.method)
        .outerjoin(latest, (Person.id == latest.c.person_id) & (latest.c.rank == 1))
        .filter(Person.id == person_id, Person.user_id == user_id)
        .options(joinedload(Person.interactions))
        .first()
    )
    if not row:
        return None
    person, last_date, last_method = row
    person.last_interaction_date = last_date
    person.last_interaction_method = last_method
    return person


def list_people(
    user_id: int,
    *,
    tag: Optional[str] = None,
    relationship_type: Optional[str] = None,
    importance_level: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Person]:
    latest = _latest_interaction_subquery(user_id)
    query = (
        db.session.query(Person, latest.c.date, latest.c.method)
        .outerjoin(latest, (Person.id == latest.c.person_id) & (latest.c.rank == 1))
        .filter(Person.user_id == user_id)
    )
    if tag:
        query = query.filter(Person.tags.contains([tag]))
    if relationship_type:
        query = query.filter(Person.relationship_type == relationship_type)
    if importance_level is not None:
        query = query.filter(Person.importance_level == importance_level)
    if search:
        like = f"%{search}%"
        query = query.filter(Person.name.ilike(like))
    people: List[Person] = []
    for person, last_date, last_method in query.order_by(Person.created_at.desc()).offset(offset).limit(limit).all():
        person.last_interaction_date = last_date
        person.last_interaction_method = last_method
        people.append(person)
    return people


def compute_reconnect_candidates(user_id: int, limit: int = 20, cutoff_days: int = 30) -> List[dict]:
    cutoff_date = date.today() - timedelta(days=cutoff_days)
    subq = (
        db.session.query(
            Interaction.person_id,
            func.max(Interaction.date).label("last_date"),
        )
        .filter(Interaction.user_id == user_id)
        .group_by(Interaction.person_id)
        .subquery()
    )
    query = (
        db.session.query(Person, subq.c.last_date)
        .outerjoin(subq, Person.id == subq.c.person_id)
        .filter(Person.user_id == user_id)
        .filter(or_(subq.c.last_date.is_(None), subq.c.last_date < cutoff_date))
        .order_by(subq.c.last_date.asc().nullsfirst(), Person.created_at.asc())
        .limit(limit)
    )
    results = []
    for person, last_date in query.all():
        days_since = (date.today() - last_date).days if last_date else None
        results.append(
            {
                "person": person,
                "last_interaction_date": last_date,
                "days_since": days_since,
            }
        )
    return results


def log_interaction(
    user_id: int,
    person_id: int,
    *,
    date_value: Optional[date] = None,
    method: Optional[str] = None,
    notes: Optional[str] = None,
    sentiment: Optional[str] = None,
) -> Interaction:
    person = Person.query.filter_by(id=person_id, user_id=user_id).first()
    if not person:
        raise ValueError("not_found")
    interaction = Interaction(
        user_id=user_id,
        person_id=person_id,
        date=date_value or date.today(),
        method=(method or "").strip() or None,
        notes=(notes or "").strip() or None,
        sentiment=(sentiment or "").strip() or None,
    )
    db.session.add(interaction)
    db.session.flush()
    enqueue_outbox(
        REL_INTERACTION_LOGGED,
        {
            "interaction_id": interaction.id,
            "person_id": person_id,
            "user_id": user_id,
            "date": interaction.date.isoformat(),
            "method": interaction.method,
            "sentiment": interaction.sentiment,
        },
        user_id=user_id,
    )
    db.session.commit()
    return interaction


def list_interactions(user_id: int, person_id: int, page: int = 1, per_page: int = 50) -> List[Interaction]:
    person = Person.query.filter_by(id=person_id, user_id=user_id).first()
    if not person:
        raise ValueError("not_found")
    return (
        Interaction.query.filter_by(user_id=user_id, person_id=person_id)
        .order_by(Interaction.date.desc(), Interaction.created_at.desc())
        .offset((max(page, 1) - 1) * per_page)
        .limit(per_page)
        .all()
    )


def edit_interaction(user_id: int, interaction_id: int, **fields) -> Optional[Interaction]:
    interaction = Interaction.query.filter_by(id=interaction_id, user_id=user_id).first()
    if not interaction:
        return None
    for key in ("date", "method", "notes", "sentiment"):
        if key in fields:
            setattr(interaction, key, fields[key])
    enqueue_outbox(
        REL_INTERACTION_UPDATED,
        {
            "interaction_id": interaction.id,
            "person_id": interaction.person_id,
            "user_id": user_id,
            "fields": {k: v for k, v in fields.items()},
            "updated_at": datetime.utcnow().isoformat(),
        },
        user_id=user_id,
    )
    db.session.commit()
    return interaction


def delete_interaction(user_id: int, interaction_id: int) -> bool:
    interaction = Interaction.query.filter_by(id=interaction_id, user_id=user_id).first()
    if not interaction:
        return False
    db.session.delete(interaction)
    db.session.commit()
    return True

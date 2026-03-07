"""Phase 5a insight substrate services."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime, time
from typing import Iterable, List, Optional

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.substrate_models import (
    Interpretation,
    TimelineEvent,
    UserFeedbackEvent,
)
from lifeos.domains.relationships.models.person_models import Person
from lifeos.domains.relationships.services import delete_interaction, log_interaction
from lifeos.extensions import db

INTERPRETATION_STATUS_PROPOSED = "proposed"
INTERPRETATION_STATUS_ACCEPTED = "accepted"
INTERPRETATION_STATUS_REJECTED = "rejected"

FEEDBACK_ACCEPTED = "accepted"
FEEDBACK_REJECTED = "rejected"
FEEDBACK_CORRECTED = "corrected"

INTERPRETATION_TYPE_RELATIONSHIP_INTERACTION = "calendar.relationship.interaction"

TIMELINE_EVENT_TYPES = {
    "calendar.event.created",
    "calendar.event.updated",
    "calendar.event.deleted",
    "journal.entry.created",
    "journal.entry.updated",
    "journal.entry.deleted",
    "finance.journal.posted",
}


def ingest_timeline_event(event: EventRecord) -> Optional[TimelineEvent]:
    """Persist a canonical timeline event from a domain event."""
    if not event or event.event_type not in TIMELINE_EVENT_TYPES:
        return None
    payload = event.payload or {}
    user_id = event.user_id or payload.get("user_id")
    if not user_id:
        return None

    event_id = _timeline_event_id(event)
    existing = TimelineEvent.query.filter_by(user_id=user_id, event_id=event_id).first()
    if existing:
        return existing

    timestamp_start, timestamp_end = _extract_timestamps(event)
    source_domain = event.event_type.split(".", 1)[0] if event.event_type else "unknown"
    source_object_ref = _source_object_ref(event.event_type, payload)

    timeline_event = TimelineEvent(
        event_id=event_id,
        user_id=user_id,
        timestamp_start=timestamp_start,
        timestamp_end=timestamp_end,
        source_domain=source_domain,
        event_type=event.event_type,
        source_object_ref=source_object_ref,
        raw_payload=payload,
    )
    db.session.add(timeline_event)
    db.session.commit()
    return timeline_event


def generate_interpretations_for_timeline_event(timeline_event: TimelineEvent) -> List[Interpretation]:
    """Generate interpretations for a timeline event (proposal-only)."""
    if not timeline_event:
        return []
    if timeline_event.source_domain == "calendar":
        proposal = _propose_calendar_relationship_interaction(timeline_event)
        return [proposal] if proposal else []
    return []


def list_interpretations(
    user_id: int,
    *,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Interpretation]:
    query = Interpretation.query.filter_by(user_id=user_id)
    if status:
        query = query.filter_by(status=status)
    return query.order_by(Interpretation.created_at.desc()).offset(offset).limit(limit).all()


def decide_interpretation(
    user_id: int,
    interpretation_id: int,
    *,
    action: str,
    correction: Optional[dict] = None,
) -> Interpretation:
    interpretation = Interpretation.query.filter_by(id=interpretation_id, user_id=user_id).first()
    if not interpretation:
        raise ValueError("not_found")

    if action == FEEDBACK_REJECTED:
        if interpretation.applied_writes:
            _undo_applied_writes(interpretation.applied_writes, interpretation.user_id)
        interpretation.applied_writes = []
        interpretation.status = INTERPRETATION_STATUS_REJECTED
        interpretation.decided_at = datetime.utcnow()
        _record_feedback(interpretation, FEEDBACK_REJECTED, correction)
        db.session.commit()
        return interpretation

    if action in {FEEDBACK_ACCEPTED, FEEDBACK_CORRECTED}:
        if interpretation.status == INTERPRETATION_STATUS_ACCEPTED and action == FEEDBACK_ACCEPTED and not correction:
            return interpretation
        applied_writes = _apply_interpretation(interpretation, correction=correction)
        interpretation.status = INTERPRETATION_STATUS_ACCEPTED
        interpretation.decided_at = datetime.utcnow()
        interpretation.applied_writes = applied_writes
        interpretation.reversible_plan = _materialize_reversible_plan(applied_writes)
        _record_feedback(interpretation, action, correction)
        db.session.commit()
        return interpretation

    raise ValueError("invalid_action")


def _timeline_event_id(event: EventRecord) -> str:
    if event.id is not None:
        return str(event.id)
    payload = event.payload or {}
    payload_id = (
        payload.get("event_id") or payload.get("entry_id") or payload.get("transaction_id") or payload.get("row_id")
    )
    if payload_id is not None:
        return f"{event.event_type}:{payload_id}"
    payload_str = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(f"{event.event_type}:{payload_str}".encode("utf-8")).hexdigest()


def _extract_timestamps(event: EventRecord) -> tuple[datetime, Optional[datetime]]:
    payload = event.payload or {}
    event_type = event.event_type
    start = None
    end = None
    if event_type and event_type.startswith("calendar.event."):
        start = _parse_datetime(payload.get("start_time"))
        end = _parse_datetime(payload.get("end_time"))
        if not start:
            start = _parse_datetime(payload.get("created_at") or payload.get("updated_at") or payload.get("deleted_at"))
    elif event_type and event_type.startswith("journal.entry."):
        start = _parse_datetime(payload.get("entry_date") or payload.get("created_at") or payload.get("updated_at"))
    elif event_type == "finance.journal.posted":
        start = _parse_datetime(payload.get("posted_at"))
    if not start:
        start = event.created_at or datetime.utcnow()
    return start, end


def _source_object_ref(event_type: str, payload: dict) -> Optional[str]:
    if not event_type:
        return None
    if event_type.startswith("calendar.event."):
        if payload.get("event_id") is not None:
            return f"calendar_event:{payload.get('event_id')}"
    if event_type.startswith("journal.entry."):
        if payload.get("entry_id") is not None:
            return f"journal_entry:{payload.get('entry_id')}"
    if event_type == "finance.journal.posted":
        if payload.get("entry_id") is not None:
            return f"finance_journal_entry:{payload.get('entry_id')}"
    return None


def _parse_datetime(value) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, time.min)
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def _propose_calendar_relationship_interaction(timeline_event: TimelineEvent) -> Optional[Interpretation]:
    if timeline_event.event_type != "calendar.event.created":
        return None
    payload = timeline_event.raw_payload or {}
    title = str(payload.get("title") or "").strip()
    if not title:
        return None

    candidate_name = _extract_person_name(title)
    if not candidate_name:
        return None
    person = _match_person(timeline_event.user_id, candidate_name)
    if not person:
        return None

    event_date = timeline_event.timestamp_start.date()
    method = _infer_interaction_method(title)
    proposed_writes = [
        {
            "action": "relationships.log_interaction",
            "person_id": person.id,
            "date": event_date.isoformat(),
            "method": method,
            "notes": f"From calendar: {title}",
            "calendar_event_id": payload.get("event_id"),
        }
    ]
    evidence = f'Calendar event "{title}" suggests an interaction with {person.name}.'
    fingerprint = _interpretation_fingerprint(
        INTERPRETATION_TYPE_RELATIONSHIP_INTERACTION,
        [timeline_event.event_id],
        proposed_writes,
    )
    if _feedback_blocks_proposal(timeline_event.user_id, fingerprint):
        return None
    existing = Interpretation.query.filter_by(user_id=timeline_event.user_id, fingerprint=fingerprint).first()
    if existing:
        return existing

    interpretation = Interpretation(
        user_id=timeline_event.user_id,
        interpretation_type=INTERPRETATION_TYPE_RELATIONSHIP_INTERACTION,
        input_event_ids=[timeline_event.event_id],
        proposed_writes=proposed_writes,
        confidence=0.55,
        evidence=evidence,
        status=INTERPRETATION_STATUS_PROPOSED,
        reversible_plan={"action": "relationships.delete_interaction", "record_ref": "interaction_id"},
        fingerprint=fingerprint,
    )
    db.session.add(interpretation)
    db.session.commit()
    return interpretation


def _interpretation_fingerprint(
    interpretation_type: str,
    input_event_ids: Iterable[str],
    proposed_writes: List[dict],
) -> str:
    payload = {
        "type": interpretation_type,
        "inputs": list(input_event_ids),
        "writes": proposed_writes,
    }
    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _feedback_blocks_proposal(user_id: int, fingerprint: str) -> bool:
    if not fingerprint:
        return False
    blocked = (
        UserFeedbackEvent.query.filter_by(user_id=user_id, fingerprint=fingerprint)
        .filter(UserFeedbackEvent.feedback_type.in_([FEEDBACK_REJECTED, FEEDBACK_CORRECTED]))
        .first()
    )
    return blocked is not None


def _extract_person_name(title: str) -> Optional[str]:
    normalized = title.strip()
    patterns = [
        r"\bwith\s+(?P<name>.+)$",
        r"\bmeeting\s+with\s+(?P<name>.+)$",
        r"\bmeet\s+(?P<name>.+)$",
        r"\bcall\s+(?P<name>.+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            candidate = match.group("name").strip()
            if candidate:
                return candidate
    return None


def _match_person(user_id: int, candidate_name: str) -> Optional[Person]:
    if not candidate_name:
        return None
    candidate_lower = candidate_name.lower()
    people = Person.query.filter_by(user_id=user_id).all()
    exact = [p for p in people if p.name.lower() == candidate_lower]
    if len(exact) == 1:
        return exact[0]
    fuzzy = [p for p in people if candidate_lower in p.name.lower() or p.name.lower() in candidate_lower]
    if len(fuzzy) == 1:
        return fuzzy[0]
    return None


def _infer_interaction_method(title: str) -> str:
    lowered = title.lower()
    if "call" in lowered:
        return "call"
    if "meet" in lowered or "meeting" in lowered:
        return "meeting"
    if "lunch" in lowered or "dinner" in lowered:
        return "meal"
    return "meeting"


def _apply_interpretation(interpretation: Interpretation, correction: Optional[dict]) -> List[dict]:
    if interpretation.interpretation_type != INTERPRETATION_TYPE_RELATIONSHIP_INTERACTION:
        return interpretation.applied_writes or []

    if interpretation.applied_writes:
        _undo_applied_writes(interpretation.applied_writes, interpretation.user_id)

    proposed = list(interpretation.proposed_writes or [])
    if not proposed:
        raise ValueError("invalid_proposal")
    write = dict(proposed[0])
    if correction:
        if correction.get("person_id"):
            write["person_id"] = correction["person_id"]
        if correction.get("method"):
            write["method"] = correction["method"]
        if correction.get("notes"):
            write["notes"] = correction["notes"]
        interpretation.proposed_writes = [write]

    date_value = _parse_date(write.get("date"))
    interaction = log_interaction(
        interpretation.user_id,
        write["person_id"],
        date_value=date_value,
        method=write.get("method"),
        notes=write.get("notes"),
        sentiment=None,
    )
    return [
        {
            "action": "relationships.log_interaction",
            "interaction_id": interaction.id,
            "person_id": write["person_id"],
        }
    ]


def _undo_applied_writes(applied_writes: List[dict], user_id: int) -> None:
    for write in applied_writes or []:
        if write.get("action") == "relationships.log_interaction" and write.get("interaction_id"):
            delete_interaction(user_id, int(write["interaction_id"]))


def _materialize_reversible_plan(applied_writes: List[dict]) -> dict:
    for write in applied_writes or []:
        if write.get("action") == "relationships.log_interaction":
            return {"action": "relationships.delete_interaction", "interaction_id": write.get("interaction_id")}
    return {}


def _parse_date(value) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _record_feedback(interpretation: Interpretation, feedback_type: str, correction: Optional[dict]) -> None:
    feedback = UserFeedbackEvent(
        user_id=interpretation.user_id,
        interpretation_id=interpretation.id,
        feedback_type=feedback_type,
        fingerprint=interpretation.fingerprint,
        payload={"correction": correction or {}},
    )
    db.session.add(feedback)

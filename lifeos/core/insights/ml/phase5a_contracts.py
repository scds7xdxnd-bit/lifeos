"""Phase 5a ML substrate contracts (structure only, no inference)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

INTERPRETATION_STATUSES: Tuple[str, ...] = ("proposed", "accepted", "rejected")
INTERPRETATION_ACTIONS: Tuple[str, ...] = ("accepted", "rejected", "corrected")


@dataclass(frozen=True)
class TimelineEventContract:
    """Canonical timeline event requirements (ML-consumed)."""

    name: str
    required_fields: List[str]
    immutable_fields: List[str]
    idempotency_key_fields: List[str]


@dataclass(frozen=True)
class InterpretationTypeContract:
    """Interpretation proposal contract for Phase 5a."""

    interpretation_type: str
    description: str
    input_event_types: List[str]
    proposed_write_actions: List[str]
    required_fields: List[str]
    correction_fields: List[str]
    reversible_plan_required: bool = True
    confidence_range: Tuple[float, float] = (0.0, 1.0)


@dataclass(frozen=True)
class FeedbackEventContract:
    """User feedback recording requirements for proposals."""

    name: str
    allowed_feedback_types: List[str]
    required_fields: List[str]


TIMELINE_EVENT_CONTRACT = TimelineEventContract(
    name="timeline_event",
    required_fields=[
        "event_id",
        "user_id",
        "timestamp_start",
        "source_domain",
        "event_type",
        "raw_payload",
        "ingested_at",
    ],
    immutable_fields=[
        "event_id",
        "user_id",
        "timestamp_start",
        "timestamp_end",
        "source_domain",
        "event_type",
        "source_object_ref",
        "raw_payload",
        "ingested_at",
    ],
    idempotency_key_fields=["user_id", "event_id"],
)


INTERPRETATION_TYPE_CONTRACTS: dict[str, InterpretationTypeContract] = {
    "calendar.relationship.interaction": InterpretationTypeContract(
        interpretation_type="calendar.relationship.interaction",
        description="Propose a relationship interaction derived from a calendar event.",
        input_event_types=["calendar.event.created"],
        proposed_write_actions=["relationships.log_interaction"],
        required_fields=[
            "user_id",
            "interpretation_type",
            "input_event_ids",
            "proposed_writes",
            "confidence",
            "evidence",
            "status",
            "reversible_plan",
            "fingerprint",
            "created_at",
        ],
        correction_fields=["person_id", "method", "notes"],
    ),
    "calendar.obligation": InterpretationTypeContract(
        interpretation_type="calendar.obligation",
        description="Optional: propose an obligation concept from calendar text (no writes).",
        input_event_types=["calendar.event.created"],
        proposed_write_actions=[],
        required_fields=[
            "user_id",
            "interpretation_type",
            "input_event_ids",
            "proposed_writes",
            "confidence",
            "evidence",
            "status",
            "reversible_plan",
            "fingerprint",
            "created_at",
        ],
        correction_fields=[],
    ),
}


USER_FEEDBACK_EVENT_CONTRACT = FeedbackEventContract(
    name="user_feedback_event",
    allowed_feedback_types=list(INTERPRETATION_ACTIONS),
    required_fields=[
        "user_id",
        "interpretation_id",
        "feedback_type",
        "fingerprint",
        "payload",
        "created_at",
    ],
)


def get_interpretation_contract(interpretation_type: str) -> InterpretationTypeContract | None:
    return INTERPRETATION_TYPE_CONTRACTS.get(interpretation_type)


def list_interpretation_contracts() -> Iterable[InterpretationTypeContract]:
    return INTERPRETATION_TYPE_CONTRACTS.values()


__all__ = [
    "INTERPRETATION_STATUSES",
    "INTERPRETATION_ACTIONS",
    "TimelineEventContract",
    "InterpretationTypeContract",
    "FeedbackEventContract",
    "TIMELINE_EVENT_CONTRACT",
    "INTERPRETATION_TYPE_CONTRACTS",
    "USER_FEEDBACK_EVENT_CONTRACT",
    "get_interpretation_contract",
    "list_interpretation_contracts",
]

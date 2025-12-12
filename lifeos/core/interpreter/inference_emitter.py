"""Emit standardized inference events using typed payload schemas."""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from lifeos.core.insights.telemetry import insight_telemetry
from lifeos.core.insights.ml.event_schemas import INFERENCE_EVENT_MODELS
from lifeos.lifeos_platform.outbox import enqueue as enqueue_outbox

# Default model version for rule-based calendar interpreter outputs.
DEFAULT_MODEL_VERSION = "calendar-interpreter-v1"
# Default payload version for all inference events (bump alongside schema changes).
DEFAULT_PAYLOAD_VERSION = "v1"

_EVENT_MODEL_MAP: Dict[Tuple[str, str], str] = {
    ("finance", "transaction"): "finance.transaction.inferred",
    ("health", "meal"): "health.meal.inferred",
    ("health", "workout"): "health.workout.inferred",
    ("habits", "habit_log"): "habits.habit.inferred",
    ("skills", "practice"): "skills.practice.inferred",
    ("projects", "work_session"): "projects.work_session.inferred",
    ("relationships", "interaction"): "relationships.interaction.inferred",
}


def emit_inference_event(
    *,
    domain: str,
    record_type: str,
    user_id: int | str,
    calendar_event_id: int | str,
    confidence: float,
    inferred_data: Dict[str, Any] | None = None,
    record_id: Optional[int] = None,
    status: str = "inferred",
    model_version: Optional[str] = None,
    label_confidences: Optional[Dict[str, float]] = None,
    context: Optional[Dict[str, Any]] = None,
    is_false_positive: Optional[bool] = None,
    is_false_negative: Optional[bool] = None,
) -> None:
    """
    Construct and enqueue a typed inference event for downstream consumers.

    Producers should pass domain/record_type plus the extracted data for the domain.
    """
    event_name = _EVENT_MODEL_MAP.get((domain, record_type))
    if not event_name:
        return

    model_cls = INFERENCE_EVENT_MODELS.get(event_name)
    if not model_cls:
        return

    payload_kwargs = {
        "user_id": user_id,
        "calendar_event_id": calendar_event_id,
        "confidence": confidence,
        "status": status,
        "payload_version": DEFAULT_PAYLOAD_VERSION,
        "model_version": model_version or DEFAULT_MODEL_VERSION,
        "label_confidences": label_confidences,
        "context": context,
        "inferred": inferred_data or {},
        "is_false_positive": is_false_positive,
        "is_false_negative": is_false_negative,
    }

    # Attach domain-specific identifiers when applicable
    if event_name == "finance.transaction.inferred":
        payload_kwargs["transaction_id"] = record_id
    elif event_name == "health.meal.inferred":
        payload_kwargs["nutrition_id"] = record_id
    elif event_name == "health.workout.inferred":
        payload_kwargs["workout_id"] = record_id
    elif event_name == "habits.habit.inferred":
        payload_kwargs["log_id"] = record_id
    elif event_name == "skills.practice.inferred":
        payload_kwargs["session_id"] = record_id
    elif event_name == "projects.work_session.inferred":
        payload_kwargs["log_id"] = record_id
    elif event_name == "relationships.interaction.inferred":
        payload_kwargs["interaction_id"] = record_id
    else:
        # Fallback: include record_id if provided
        if record_id is not None:
            payload_kwargs["record_id"] = record_id

    event_model = model_cls(**payload_kwargs)
    enqueue_outbox(
        event_model.event_name,
        event_model.to_payload(),
        user_id if isinstance(user_id, int) else None,
    )
    insight_telemetry.record_inference_feedback(
        event_model.event_name,
        event_model.model_version or DEFAULT_MODEL_VERSION,
        bool(event_model.is_false_positive),
        bool(event_model.is_false_negative),
    )

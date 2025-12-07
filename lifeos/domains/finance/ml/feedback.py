"""Capture ML suggestion feedback."""

from __future__ import annotations

from lifeos.core.events.event_service import log_event


def record_feedback(user_id: int, suggestion_id: str, accepted: bool, score: float | None = None) -> None:
    log_event(
        "finance.ml.feedback",
        {"user_id": user_id, "suggestion_id": suggestion_id, "accepted": accepted, "score": score},
        user_id=user_id,
    )

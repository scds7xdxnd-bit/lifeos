"""Phase 2.5 ML attachment contracts (structure only, no training/tuning)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from lifeos.core.insights.ml.event_schemas import INFERENCE_EVENT_MODELS

REQUIRED_ML_LOGGING_FIELDS = ("model_version", "payload_version")


@dataclass(frozen=True)
class MLAttachmentContract:
    """Defines where ML may attach later and required logging fields."""

    name: str
    description: str
    allowed_event_types: list[str]
    required_logging_fields: list[str]


ML_ATTACHMENT_CONTRACTS: dict[str, MLAttachmentContract] = {
    "calendar_inference_events": MLAttachmentContract(
        name="calendar_inference_events",
        description=(
            "ML may attach to calendar-derived inference events only; "
            "no direct attachment to UI-filtered calendar views."
        ),
        allowed_event_types=sorted(INFERENCE_EVENT_MODELS.keys()),
        required_logging_fields=list(REQUIRED_ML_LOGGING_FIELDS),
    ),
}


def get_ml_attachment_contract(name: str) -> MLAttachmentContract | None:
    return ML_ATTACHMENT_CONTRACTS.get(name)


def list_ml_attachment_contracts() -> Iterable[MLAttachmentContract]:
    return ML_ATTACHMENT_CONTRACTS.values()


__all__ = [
    "REQUIRED_ML_LOGGING_FIELDS",
    "MLAttachmentContract",
    "ML_ATTACHMENT_CONTRACTS",
    "get_ml_attachment_contract",
    "list_ml_attachment_contracts",
]

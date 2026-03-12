"""Phase 3b.1 ML stability contracts (structure only)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class StabilityPatchContract:
    """Defines ML guardrails for the Phase 3b.1 stability patch."""

    name: str
    purpose: str
    allowed_changes: List[str]
    forbidden_changes: List[str]
    required_invariants: List[str]
    required_checks: List[str]


PHASE3B1_STABILITY_CONTRACT = StabilityPatchContract(
    name="phase_3b_1_stability_patch",
    purpose="Restore functional correctness without changing ML behavior or contracts.",
    allowed_changes=[
        "No ML behavior changes; logging-only updates if required for observability.",
        "No changes to inference outputs, confidence routing, or insight semantics.",
    ],
    forbidden_changes=[
        "Model training or tuning",
        "New ML features or ranking logic",
        "New insight types or confidence vocabulary changes",
    ],
    required_invariants=[
        "model_version and payload_version are preserved in ML-relevant events",
        "confidence bands remain unchanged",
        "replay determinism remains intact",
    ],
    required_checks=[
        "Phase 3b SLO metrics remain emitted",
        "Determinism tests continue to pass",
        "No contract violations introduced",
    ],
)


def get_phase3b1_stability_contract() -> StabilityPatchContract:
    return PHASE3B1_STABILITY_CONTRACT


def list_stability_contracts() -> Iterable[StabilityPatchContract]:
    return [PHASE3B1_STABILITY_CONTRACT]


__all__ = [
    "StabilityPatchContract",
    "PHASE3B1_STABILITY_CONTRACT",
    "get_phase3b1_stability_contract",
    "list_stability_contracts",
]

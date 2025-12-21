"""Phase 3b ML SLO metric contracts (structure only)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Literal


@dataclass(frozen=True)
class SLOMetricContract:
    """Defines required metric names for Phase 3b SLOs."""

    name: str
    metric_type: Literal["counter", "histogram"]
    description: str
    required_samples: List[str]


PHASE3B_SLO_METRICS: dict[str, SLOMetricContract] = {
    "insight_latency": SLOMetricContract(
        name="lifeos_insight_latency_seconds",
        metric_type="histogram",
        description="Insight generation latency in seconds (Phase 3b SLO).",
        required_samples=["lifeos_insight_latency_seconds_bucket"],
    ),
    "projection_correctness_total": SLOMetricContract(
        name="lifeos_projection_correctness_total",
        metric_type="counter",
        description="Total read-only projection checks (Phase 3b SLO).",
        required_samples=["lifeos_projection_correctness_total"],
    ),
    "projection_correctness_errors": SLOMetricContract(
        name="lifeos_projection_correctness_errors_total",
        metric_type="counter",
        description="Read-only projection correctness errors (Phase 3b SLO).",
        required_samples=["lifeos_projection_correctness_errors_total"],
    ),
    "replay_determinism_failures": SLOMetricContract(
        name="lifeos_replay_determinism_failures_total",
        metric_type="counter",
        description="Replay determinism failures (Phase 3b SLO).",
        required_samples=["lifeos_replay_determinism_failures_total"],
    ),
    "contract_violations": SLOMetricContract(
        name="lifeos_contract_violations_total",
        metric_type="counter",
        description="Contract violations (Phase 3b SLO).",
        required_samples=["lifeos_contract_violations_total"],
    ),
}


def get_phase3b_slo_metric(name: str) -> SLOMetricContract | None:
    return PHASE3B_SLO_METRICS.get(name)


def list_phase3b_slo_metrics() -> Iterable[SLOMetricContract]:
    return PHASE3B_SLO_METRICS.values()


__all__ = [
    "SLOMetricContract",
    "PHASE3B_SLO_METRICS",
    "get_phase3b_slo_metric",
    "list_phase3b_slo_metrics",
]

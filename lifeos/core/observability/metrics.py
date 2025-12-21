"""Prometheus metrics for Phase 3b SLOs."""

from __future__ import annotations

from prometheus_client import Counter, Histogram

INSIGHT_LATENCY_SECONDS = Histogram(
    "lifeos_insight_latency_seconds",
    "Insight generation latency in seconds",
    buckets=(0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0),
)

PROJECTION_CORRECTNESS_TOTAL = Counter(
    "lifeos_projection_correctness_total",
    "Total read-only projection checks",
)

PROJECTION_CORRECTNESS_ERRORS_TOTAL = Counter(
    "lifeos_projection_correctness_errors_total",
    "Read-only projection correctness errors",
)

REPLAY_DETERMINISM_FAILURES_TOTAL = Counter(
    "lifeos_replay_determinism_failures_total",
    "Replay determinism failures",
)

CONTRACT_VIOLATIONS_TOTAL = Counter(
    "lifeos_contract_violations_total",
    "API contract violations",
)


def record_insight_latency_ms(latency_ms: float) -> None:
    """Record insight latency in milliseconds."""
    if latency_ms is None:
        return
    INSIGHT_LATENCY_SECONDS.observe(max(0.0, latency_ms / 1000.0))


def record_projection_check() -> None:
    """Record a read-only projection evaluation."""
    PROJECTION_CORRECTNESS_TOTAL.inc()


def record_projection_error() -> None:
    """Record a projection correctness failure."""
    PROJECTION_CORRECTNESS_ERRORS_TOTAL.inc()


def record_replay_determinism_failure() -> None:
    """Record a replay determinism failure."""
    REPLAY_DETERMINISM_FAILURES_TOTAL.inc()


def record_contract_violation() -> None:
    """Record an API contract violation."""
    CONTRACT_VIOLATIONS_TOTAL.inc()

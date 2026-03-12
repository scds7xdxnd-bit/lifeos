"""Prometheus metrics for LifeOS operational SLOs and feature rollouts."""

from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

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

READ_CACHE_HITS_TOTAL = Counter(
    "lifeos_read_cache_hits_total",
    "Read-through cache hits",
    ["scope"],
)

READ_CACHE_MISSES_TOTAL = Counter(
    "lifeos_read_cache_misses_total",
    "Read-through cache misses",
    ["scope"],
)

HTTP_REQUEST_LATENCY_SECONDS = Histogram(
    "lifeos_http_request_latency_seconds",
    "HTTP request latency in seconds",
    ["method", "route", "status_code"],
    buckets=(0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0),
)

EVENT_DISPATCH_LATENCY_SECONDS = Histogram(
    "lifeos_event_dispatch_latency_seconds",
    "In-process event dispatch latency in seconds",
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0),
)

INQUIRY_CREATED_TOTAL = Counter(
    "lifeos_inquiry_created_total",
    "Total focused inquiries created",
)

INQUIRY_GENERATED_TOTAL = Counter(
    "lifeos_inquiry_generated_total",
    "Total focused inquiry briefs generated",
)

INQUIRY_VIEWED_TOTAL = Counter(
    "lifeos_inquiry_viewed_total",
    "Total focused inquiry brief views",
)

INQUIRY_REFINED_TOTAL = Counter(
    "lifeos_inquiry_refined_total",
    "Total focused inquiry refinements",
)

INQUIRY_GENERATION_LATENCY_SECONDS = Histogram(
    "lifeos_inquiry_generation_latency_seconds",
    "Focused inquiry generation latency in seconds",
    buckets=(0.05, 0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0),
)

INQUIRY_ERRORS_TOTAL = Counter(
    "lifeos_inquiry_errors_total",
    "Total focused inquiry pipeline errors",
    ["stage", "error_type"],
)

INQUIRY_EMPTY_BRIEF_TOTAL = Counter(
    "lifeos_inquiry_empty_brief_total",
    "Total focused inquiry briefs with zero evidence coverage",
)

INQUIRY_FINDINGS_TOTAL = Counter(
    "lifeos_inquiry_findings_total",
    "Total focused inquiry findings generated",
)

INQUIRY_FINDINGS_WITH_EVIDENCE_TOTAL = Counter(
    "lifeos_inquiry_findings_with_evidence_total",
    "Total focused inquiry findings that include at least one evidence reference",
)

INQUIRY_ERROR_RATE = Gauge(
    "lifeos_inquiry_error_rate",
    "Focused inquiry runtime error ratio",
)

INQUIRY_EMPTY_BRIEF_RATE = Gauge(
    "lifeos_inquiry_empty_brief_rate",
    "Focused inquiry empty-brief ratio",
)

INQUIRY_EVIDENCE_COVERAGE_RATIO = Gauge(
    "lifeos_inquiry_evidence_coverage_ratio",
    "Focused inquiry findings with evidence ratio",
)

PHASE6_INQUIRY_MIGRATION_MISMATCH = Gauge(
    "lifeos_phase6_inquiry_migration_mismatch",
    "Focused Inquiry migration mismatch state (1=mismatch, 0=applied)",
    ["expected_head"],
)

# Pre-register a default label set so histograms appear even without traffic.
HTTP_REQUEST_LATENCY_SECONDS.labels(method="GET", route="unknown", status_code="200")
EVENT_DISPATCH_LATENCY_SECONDS.observe(0)
INQUIRY_ERRORS_TOTAL.labels(stage="create", error_type="validation_error").inc(0)
INQUIRY_ERRORS_TOTAL.labels(stage="create", error_type="internal_error").inc(0)
INQUIRY_ERRORS_TOTAL.labels(stage="refine", error_type="validation_error").inc(0)
INQUIRY_ERRORS_TOTAL.labels(stage="refine", error_type="internal_error").inc(0)
INQUIRY_ERRORS_TOTAL.labels(stage="list", error_type="validation_error").inc(0)
INQUIRY_ERRORS_TOTAL.labels(stage="detail", error_type="not_found").inc(0)
INQUIRY_ERROR_RATE.set(0.0)
INQUIRY_EMPTY_BRIEF_RATE.set(0.0)
INQUIRY_EVIDENCE_COVERAGE_RATIO.set(1.0)

_inquiry_generated_count = 0
_inquiry_error_count = 0
_inquiry_empty_count = 0
_inquiry_findings_count = 0
_inquiry_findings_with_evidence_count = 0


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


def record_read_cache_hit(scope: str) -> None:
    """Record a read cache hit by scope."""
    READ_CACHE_HITS_TOTAL.labels(scope=scope).inc()


def record_read_cache_miss(scope: str) -> None:
    """Record a read cache miss by scope."""
    READ_CACHE_MISSES_TOTAL.labels(scope=scope).inc()


def record_http_request_latency_seconds(
    duration_seconds: float,
    method: str,
    route: str,
    status_code: str,
) -> None:
    """Record HTTP request latency in seconds."""
    if duration_seconds is None:
        return
    HTTP_REQUEST_LATENCY_SECONDS.labels(
        method=method or "unknown",
        route=route or "unknown",
        status_code=status_code or "0",
    ).observe(max(0.0, duration_seconds))


def record_event_dispatch_latency_seconds(duration_seconds: float) -> None:
    """Record in-process event dispatch latency in seconds."""
    if duration_seconds is None:
        return
    EVENT_DISPATCH_LATENCY_SECONDS.observe(max(0.0, duration_seconds))


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return max(0.0, float(numerator) / float(denominator))


def record_inquiry_created() -> None:
    """Record successful focused inquiry creation."""
    INQUIRY_CREATED_TOTAL.inc()


def record_inquiry_generated(
    *,
    latency_seconds: float | None,
    is_empty: bool,
    findings_total: int,
    findings_with_evidence: int,
) -> None:
    """Record focused inquiry brief generation and coverage stats."""
    global _inquiry_generated_count
    global _inquiry_empty_count
    global _inquiry_findings_count
    global _inquiry_findings_with_evidence_count

    INQUIRY_GENERATED_TOTAL.inc()
    _inquiry_generated_count += 1

    if latency_seconds is not None:
        INQUIRY_GENERATION_LATENCY_SECONDS.observe(max(0.0, latency_seconds))

    if is_empty:
        INQUIRY_EMPTY_BRIEF_TOTAL.inc()
        _inquiry_empty_count += 1

    findings_total = max(0, int(findings_total))
    findings_with_evidence = max(0, min(findings_total, int(findings_with_evidence)))
    if findings_total:
        INQUIRY_FINDINGS_TOTAL.inc(findings_total)
        INQUIRY_FINDINGS_WITH_EVIDENCE_TOTAL.inc(findings_with_evidence)
        _inquiry_findings_count += findings_total
        _inquiry_findings_with_evidence_count += findings_with_evidence

    INQUIRY_EMPTY_BRIEF_RATE.set(_safe_ratio(_inquiry_empty_count, _inquiry_generated_count))
    INQUIRY_EVIDENCE_COVERAGE_RATIO.set(_safe_ratio(_inquiry_findings_with_evidence_count, _inquiry_findings_count))
    INQUIRY_ERROR_RATE.set(_safe_ratio(_inquiry_error_count, _inquiry_generated_count + _inquiry_error_count))


def record_inquiry_viewed() -> None:
    """Record focused inquiry brief view."""
    INQUIRY_VIEWED_TOTAL.inc()


def record_inquiry_refined() -> None:
    """Record focused inquiry refinement."""
    INQUIRY_REFINED_TOTAL.inc()


def record_inquiry_error(stage: str, error_type: str) -> None:
    """Record focused inquiry pipeline errors."""
    global _inquiry_error_count
    INQUIRY_ERRORS_TOTAL.labels(stage=stage or "unknown", error_type=error_type or "unknown").inc()
    _inquiry_error_count += 1
    INQUIRY_ERROR_RATE.set(_safe_ratio(_inquiry_error_count, _inquiry_generated_count + _inquiry_error_count))


def set_phase6_inquiry_migration_mismatch(expected_head: str, mismatch: bool) -> None:
    """Expose Focused Inquiry migration head state for deployment health."""
    PHASE6_INQUIRY_MIGRATION_MISMATCH.labels(expected_head=expected_head or "unknown").set(1 if mismatch else 0)

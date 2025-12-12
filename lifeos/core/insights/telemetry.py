"""Lightweight telemetry counters for insight generation."""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Dict, List


@dataclass
class InsightTelemetrySnapshot:
    events_processed: int
    events_with_insights: int
    total_insights: int
    per_rule_counts: Dict[str, int]
    avg_latency_ms: float
    per_rule_avg_latency_ms: Dict[str, float]
    false_positives: int
    false_negatives: int
    per_domain_false_positives: Dict[str, int]
    per_domain_false_negatives: Dict[str, int]
    per_model_false_positives: Dict[str, int]
    per_model_false_negatives: Dict[str, int]
    coverage: float
    per_event_counts: Dict[str, int]
    recent_events: List[Dict[str, str]]


class InsightTelemetry:
    """In-memory telemetry recorder; intentionally simple for Phase 3a."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._reset_state()

    def _reset_state(self) -> None:
        self.events_processed = 0
        self.events_with_insights = 0
        self.total_insights = 0
        self.false_positives = 0
        self.false_negatives = 0
        self.per_rule_counts: Counter[str] = Counter()
        self.per_rule_latency_ms: defaultdict[str, List[float]] = defaultdict(list)
        self.per_event_latency_ms: List[float] = []
        self.per_event_counts: Counter[str] = Counter()
        self.per_domain_false_positives: Counter[str] = Counter()
        self.per_domain_false_negatives: Counter[str] = Counter()
        self.per_model_false_positives: Counter[str] = Counter()
        self.per_model_false_negatives: Counter[str] = Counter()
        self.recent_events = deque(maxlen=50)

    def reset(self) -> None:
        """Clear all counters (useful in tests)."""
        with self._lock:
            self._reset_state()

    def record_rule(
        self,
        rule_name: str,
        insights_count: int,
        latency_ms: float,
        false_positive: int = 0,
        false_negative: int = 0,
    ) -> None:
        """Record metrics for a single rule invocation."""
        with self._lock:
            self.per_rule_counts[rule_name] += insights_count
            self.per_rule_latency_ms[rule_name].append(latency_ms)
            self.total_insights += insights_count
            self.false_positives += false_positive
            self.false_negatives += false_negative

    def record_event(self, event_type: str, has_insights: bool, latency_ms: float) -> None:
        """Record metrics for an ingested event."""
        with self._lock:
            self.events_processed += 1
            if has_insights:
                self.events_with_insights += 1
            self.per_event_latency_ms.append(latency_ms)
            self.per_event_counts[event_type] += 1
            self.recent_events.append(
                {
                    "event_type": event_type,
                    "has_insights": has_insights,
                    "latency_ms": latency_ms,
                    "at": datetime.now(timezone.utc).isoformat(),
                }
            )

    def record_inference_feedback(
        self,
        event_type: str,
        model_version: str,
        is_false_positive: bool = False,
        is_false_negative: bool = False,
    ) -> None:
        """Capture per-domain and per-model error markers from inference corrections."""
        if not (is_false_positive or is_false_negative):
            return
        domain = event_type.split(".")[0] if event_type else "unknown"
        with self._lock:
            if is_false_positive:
                self.false_positives += 1
                self.per_domain_false_positives[domain] += 1
                self.per_model_false_positives[model_version or "unknown"] += 1
            if is_false_negative:
                self.false_negatives += 1
                self.per_domain_false_negatives[domain] += 1
                self.per_model_false_negatives[model_version or "unknown"] += 1

    def snapshot(self) -> InsightTelemetrySnapshot:
        """Return a read-only snapshot of telemetry counters."""
        with self._lock:
            avg_latency_ms = (
                sum(self.per_event_latency_ms) / len(self.per_event_latency_ms) if self.per_event_latency_ms else 0.0
            )
            per_rule_avg_latency_ms = {
                rule: (sum(latencies) / len(latencies)) if latencies else 0.0
                for rule, latencies in self.per_rule_latency_ms.items()
            }
            coverage = (self.events_with_insights / self.events_processed) if self.events_processed else 0.0
            return InsightTelemetrySnapshot(
                events_processed=self.events_processed,
                events_with_insights=self.events_with_insights,
                total_insights=self.total_insights,
                per_rule_counts=dict(self.per_rule_counts),
                avg_latency_ms=avg_latency_ms,
                per_rule_avg_latency_ms=per_rule_avg_latency_ms,
                false_positives=self.false_positives,
                false_negatives=self.false_negatives,
                per_domain_false_positives=dict(self.per_domain_false_positives),
                per_domain_false_negatives=dict(self.per_domain_false_negatives),
                per_model_false_positives=dict(self.per_model_false_positives),
                per_model_false_negatives=dict(self.per_model_false_negatives),
                coverage=coverage,
                per_event_counts=dict(self.per_event_counts),
                recent_events=list(self.recent_events),
            )


insight_telemetry = InsightTelemetry()

__all__ = ["InsightTelemetry", "InsightTelemetrySnapshot", "insight_telemetry"]

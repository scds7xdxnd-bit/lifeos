"""Deterministic Phase 9 timeline contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Mapping


@dataclass(frozen=True)
class TimelineWindow:
    token: str
    label: str
    start_local_date: date
    end_local_date: date
    order_index: int
    is_active: bool = False
    is_prior: bool = False


@dataclass(frozen=True)
class TimelineWindowSpec:
    token: str
    duration_days: int
    timezone_token: str
    active_window: TimelineWindow | None
    prior_window: TimelineWindow | None
    baseline_windows: tuple[TimelineWindow, ...]
    ordered_windows: tuple[TimelineWindow, ...]


@dataclass(frozen=True)
class TimelineProfile:
    profile_id: str
    profile_version: str
    scope: str
    domains: tuple[str, ...]
    adapter_key: str
    baseline_window_count: int
    min_recurrence_windows: int
    min_trend_windows: int
    max_findings: int
    baseline_policy_token: str
    value_label: str
    observation_label: str
    supports_streaks: bool = False

    @property
    def profile_token(self) -> str:
        return f"{self.profile_id}:{self.profile_version}"


@dataclass(frozen=True)
class TimelineRequest:
    lens: str
    domains: tuple[str, ...]
    primary_domain: str
    timeframe_start: datetime
    timeframe_end: datetime
    as_of_ts: datetime
    timezone_token: str
    profile: TimelineProfile
    events_by_domain: Mapping[str, tuple[object, ...]]


@dataclass(frozen=True)
class TimelineObservation:
    domain: str
    source_kind: str
    source_id: int | None
    source_ref: str | None
    event_type: str | None
    anchor_ts: datetime
    anchor_local_date: date
    created_at: datetime | None
    value: float
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class TimelineFeatureWindow:
    window: TimelineWindow
    observation_count: int
    total_value: float
    occupied: bool
    evidence_refs: tuple[dict[str, object], ...]


@dataclass(frozen=True)
class TimelinePairFeatureWindow:
    window: TimelineWindow
    domain_counts: Mapping[str, int]
    aligned: bool
    evidence_refs: tuple[dict[str, object], ...]


@dataclass(frozen=True)
class TimelineCoverage:
    prior_window_available: bool
    baseline_windows_available: int
    baseline_windows_required: int
    recurrence_windows_available: int
    trend_windows_available: int


@dataclass(frozen=True)
class TimelineFinding:
    claim: str
    finding_category: str
    confidence_label: str
    uncertainty_note: str
    source_domains: tuple[str, ...]
    evidence_refs: tuple[dict[str, object], ...]
    timeline_context: Mapping[str, object]


@dataclass(frozen=True)
class TimelineSummary:
    profile_id: str
    profile_version: str
    timeline_engine_version: str
    window_spec_token: str
    active_window_token: str | None
    comparison_window_token: str | None
    baseline_policy_token: str
    timezone_token: str
    as_of_ts: str
    evidence_manifest_hash: str
    timeline_summary_hash: str
    coverage: TimelineCoverage
    findings: tuple[TimelineFinding, ...]
    limits: tuple[str, ...]
    blocked_claim_count: int
    insufficiency_count: int


__all__ = [
    "TimelineCoverage",
    "TimelineFeatureWindow",
    "TimelineFinding",
    "TimelineObservation",
    "TimelinePairFeatureWindow",
    "TimelineProfile",
    "TimelineRequest",
    "TimelineSummary",
    "TimelineWindow",
    "TimelineWindowSpec",
]

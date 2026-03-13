"""Timeline feature building from canonical evidence."""

from __future__ import annotations

import hashlib
import json
from typing import Iterable, Mapping

from lifeos.core.events.event_models import EventRecord
from lifeos.core.timeline.adapters import get_timeline_adapter
from lifeos.core.timeline.contracts import (
    TimelineFeatureWindow,
    TimelineObservation,
    TimelinePairFeatureWindow,
    TimelineRequest,
    TimelineWindow,
    TimelineWindowSpec,
)
from lifeos.core.timeline.semantics import SOURCE_KIND_PRIORITY, isoformat_utc, window_contains


def build_domain_observations(request: TimelineRequest) -> dict[str, tuple[TimelineObservation, ...]]:
    observations: dict[str, tuple[TimelineObservation, ...]] = {}
    for domain in request.domains:
        adapter = get_timeline_adapter(domain)
        if adapter is None:
            observations[domain] = ()
            continue
        rows: list[TimelineObservation] = []
        for event in request.events_by_domain.get(domain, ()):
            if not isinstance(event, EventRecord) or not adapter.matches(event.event_type):
                continue
            observation = adapter.build_observation(event, request.timezone_token)
            if observation is None:
                continue
            rows.append(observation)
        observations[domain] = tuple(sorted(rows, key=_observation_sort_key))
    return observations


def build_domain_windows(
    observations: Iterable[TimelineObservation],
    window_spec: TimelineWindowSpec,
) -> tuple[TimelineFeatureWindow, ...]:
    return tuple(_build_window(window, observations) for window in window_spec.ordered_windows)


def build_pair_windows(
    observations_by_domain: Mapping[str, tuple[TimelineObservation, ...]],
    window_spec: TimelineWindowSpec,
) -> tuple[TimelinePairFeatureWindow, ...]:
    pair_windows: list[TimelinePairFeatureWindow] = []
    domains = sorted(observations_by_domain.keys())
    for window in window_spec.ordered_windows:
        refs: list[dict[str, object]] = []
        domain_counts: dict[str, int] = {}
        for domain in domains:
            matching = [
                item
                for item in observations_by_domain.get(domain, ())
                if window_contains(item.anchor_local_date, window)
            ]
            domain_counts[domain] = len(matching)
            refs.extend(_observation_ref(item) for item in matching)
        refs = sorted(refs, key=_evidence_sort_key)
        pair_windows.append(
            TimelinePairFeatureWindow(
                window=window,
                domain_counts=domain_counts,
                aligned=all(domain_counts.get(domain, 0) > 0 for domain in domains),
                evidence_refs=tuple(refs),
            )
        )
    return tuple(pair_windows)


def evidence_manifest_hash(observations: Mapping[str, tuple[TimelineObservation, ...]]) -> str:
    payload: list[dict[str, object]] = []
    for domain in sorted(observations.keys()):
        for item in observations[domain]:
            payload.append(
                {
                    "domain": item.domain,
                    "source_kind": item.source_kind,
                    "source_id": item.source_id,
                    "source_ref": item.source_ref,
                    "event_type": item.event_type,
                    "anchor_ts": isoformat_utc(item.anchor_ts),
                    "created_at": isoformat_utc(item.created_at),
                    "value": round(float(item.value or 0.0), 4),
                }
            )
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _build_window(window: TimelineWindow, observations: Iterable[TimelineObservation]) -> TimelineFeatureWindow:
    matching = [item for item in observations if window_contains(item.anchor_local_date, window)]
    refs = tuple(sorted((_observation_ref(item) for item in matching), key=_evidence_sort_key))
    return TimelineFeatureWindow(
        window=window,
        observation_count=len(matching),
        total_value=round(sum(float(item.value or 0.0) for item in matching), 4),
        occupied=bool(matching),
        evidence_refs=refs,
    )


def _observation_ref(observation: TimelineObservation) -> dict[str, object]:
    return {
        "source_kind": observation.source_kind,
        "source_id": observation.source_id,
        "source_ref": observation.source_ref,
        "event_type": observation.event_type,
        "domain": observation.domain,
        "created_at": isoformat_utc(observation.anchor_ts),
    }


def _observation_sort_key(item: TimelineObservation) -> tuple[str, int, int, str]:
    return (
        isoformat_utc(item.anchor_ts) or "",
        SOURCE_KIND_PRIORITY.get(str(item.source_kind or ""), 99),
        int(item.source_id or 0),
        str(item.source_ref or ""),
    )


def _evidence_sort_key(item: Mapping[str, object]) -> tuple[str, int, int, str]:
    return (
        str(item.get("created_at") or ""),
        SOURCE_KIND_PRIORITY.get(str(item.get("source_kind") or ""), 99),
        int(item.get("source_id") or 0),
        str(item.get("source_ref") or ""),
    )


__all__ = [
    "build_domain_observations",
    "build_domain_windows",
    "build_pair_windows",
    "evidence_manifest_hash",
]

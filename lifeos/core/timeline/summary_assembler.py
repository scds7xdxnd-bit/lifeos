"""Timeline summary assembly for Phase 9 inquiry integration."""

from __future__ import annotations

import hashlib
import json
from typing import Mapping

from lifeos.core.timeline.baseline_estimator import estimate_domain_baseline, estimate_pair_baseline
from lifeos.core.timeline.contracts import TimelineCoverage, TimelineFinding, TimelineRequest, TimelineSummary
from lifeos.core.timeline.drift_detector import domain_drift_findings, pair_drift_findings
from lifeos.core.timeline.feature_builder import (
    build_domain_observations,
    build_domain_windows,
    build_pair_windows,
    evidence_manifest_hash,
)
from lifeos.core.timeline.recurrence_engine import domain_recurrence_findings, pair_recurrence_findings
from lifeos.core.timeline.semantics import build_window_spec
from lifeos.core.timeline.window_comparator import compare_domain_windows, compare_pair_windows

_FORBIDDEN_CLAIM_TOKENS = ("because", "caused", "therefore", "will likely", "recommend", "should")
TIMELINE_ENGINE_VERSION = "phase9_timeline_engine_v1"


def assemble_timeline_summary(request: TimelineRequest) -> TimelineSummary:
    window_spec = build_window_spec(
        timeframe_start=request.timeframe_start,
        timeframe_end=request.timeframe_end,
        as_of_ts=request.as_of_ts,
        timezone_token=request.timezone_token,
        baseline_window_count=request.profile.baseline_window_count,
    )
    domain_observations = build_domain_observations(request)
    manifest_hash = evidence_manifest_hash(domain_observations)
    findings: list[TimelineFinding] = []
    limits: list[str] = []
    blocked_claim_count = 0
    insufficiency_count = 0

    if request.profile.scope == "domain":
        domain = request.profile.domains[0]
        windows = build_domain_windows(domain_observations.get(domain, ()), window_spec)
        occupied_windows = sum(1 for window in windows if window.occupied)
        coverage = TimelineCoverage(
            prior_window_available=len(windows) >= 2,
            baseline_windows_available=max(0, len(windows) - 1),
            baseline_windows_required=request.profile.baseline_window_count,
            recurrence_windows_available=len(windows),
            trend_windows_available=len(windows),
        )
        if not window_spec.active_window or len(windows) < 2:
            insufficiency_count += 1
            limits.append(
                "Timeline comparison is insufficient because fewer than two closed comparable windows are available."
            )
        else:
            findings.extend(compare_domain_windows(profile=request.profile, windows=windows, window_spec=window_spec))
            findings.extend(
                domain_recurrence_findings(profile=request.profile, windows=windows, window_spec=window_spec)
            )
            if occupied_windows < request.profile.min_recurrence_windows:
                insufficiency_count += 1
                limits.append(
                    "Recurrence interpretation is insufficient because fewer than two "
                    "comparable windows contain canonical evidence."
                )
            baseline = estimate_domain_baseline(request.profile, windows)
            if baseline.available_windows < request.profile.baseline_window_count:
                insufficiency_count += 1
                limits.append(
                    "Baseline comparison is insufficient because only "
                    f"{baseline.available_windows} prior comparable windows are available."
                )
            findings.extend(
                domain_drift_findings(
                    profile=request.profile,
                    windows=windows,
                    baseline=baseline,
                    window_spec=window_spec,
                )
            )
    else:
        pair_windows = build_pair_windows(domain_observations, window_spec)
        aligned_windows = sum(1 for window in pair_windows if window.aligned)
        coverage = TimelineCoverage(
            prior_window_available=len(pair_windows) >= 2,
            baseline_windows_available=max(0, len(pair_windows) - 1),
            baseline_windows_required=request.profile.baseline_window_count,
            recurrence_windows_available=len(pair_windows),
            trend_windows_available=len(pair_windows),
        )
        if not window_spec.active_window or len(pair_windows) < 2:
            insufficiency_count += 1
            limits.append(
                "Approved pair timeline comparison is insufficient because fewer than "
                "two closed comparable windows are available."
            )
        else:
            findings.extend(
                compare_pair_windows(profile=request.profile, windows=pair_windows, window_spec=window_spec)
            )
            findings.extend(
                pair_recurrence_findings(profile=request.profile, windows=pair_windows, window_spec=window_spec)
            )
            if aligned_windows < request.profile.min_recurrence_windows:
                insufficiency_count += 1
                limits.append(
                    "Approved pair persistence is insufficient because fewer than two "
                    "comparable windows show aligned canonical evidence."
                )
            baseline = estimate_pair_baseline(request.profile, pair_windows)
            if baseline.available_windows < request.profile.baseline_window_count:
                insufficiency_count += 1
                limits.append(
                    "Approved pair baseline comparison is insufficient because only "
                    f"{baseline.available_windows} prior comparable windows are available."
                )
            findings.extend(
                pair_drift_findings(
                    profile=request.profile,
                    windows=pair_windows,
                    baseline=baseline,
                    window_spec=window_spec,
                )
            )

    deduped: list[TimelineFinding] = []
    for finding in findings:
        if _blocked(finding):
            blocked_claim_count += 1
            continue
        if not _has_valid_provenance(finding):
            insufficiency_count += 1
            _append_unique_limit(
                limits,
                "Timeline "
                f"{finding.finding_category.replace('_', ' ')} was suppressed because "
                "canonical evidence provenance is absent in the compared windows.",
            )
            continue
        if finding.claim not in {item.claim for item in deduped}:
            deduped.append(finding)
    deduped = deduped[: request.profile.max_findings]
    summary_hash = hashlib.sha256(
        json.dumps(
            {
                "profile_id": request.profile.profile_id,
                "profile_version": request.profile.profile_version,
                "timeline_engine_version": TIMELINE_ENGINE_VERSION,
                "window_spec_token": window_spec.token,
                "active_window_token": (
                    window_spec.active_window.token if window_spec.active_window is not None else None
                ),
                "comparison_window_token": (
                    window_spec.prior_window.token if window_spec.prior_window is not None else None
                ),
                "baseline_policy_token": request.profile.baseline_policy_token,
                "timezone_token": request.timezone_token,
                "as_of_ts": request.as_of_ts.isoformat(),
                "findings": [
                    {
                        "claim": item.claim,
                        "category": item.finding_category,
                        "context": dict(item.timeline_context),
                    }
                    for item in deduped
                ],
                "limits": limits,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return TimelineSummary(
        profile_id=request.profile.profile_id,
        profile_version=request.profile.profile_version,
        timeline_engine_version=TIMELINE_ENGINE_VERSION,
        window_spec_token=window_spec.token,
        active_window_token=window_spec.active_window.token if window_spec.active_window is not None else None,
        comparison_window_token=window_spec.prior_window.token if window_spec.prior_window is not None else None,
        baseline_policy_token=request.profile.baseline_policy_token,
        timezone_token=request.timezone_token,
        as_of_ts=request.as_of_ts.isoformat(),
        evidence_manifest_hash=manifest_hash,
        timeline_summary_hash=summary_hash,
        coverage=coverage,
        findings=tuple(deduped),
        limits=tuple(limits),
        blocked_claim_count=blocked_claim_count,
        insufficiency_count=insufficiency_count,
    )


def _blocked(finding: TimelineFinding) -> bool:
    lowered = finding.claim.lower()
    return any(token in lowered for token in _FORBIDDEN_CLAIM_TOKENS)


def _has_valid_provenance(finding: TimelineFinding) -> bool:
    for ref in finding.evidence_refs:
        if not isinstance(ref, Mapping):
            continue
        if str(ref.get("source_kind") or "").strip() and str(ref.get("domain") or "").strip():
            return True
    return False


def _append_unique_limit(limits: list[str], note: str) -> None:
    if note not in limits:
        limits.append(note)


__all__ = ["TIMELINE_ENGINE_VERSION", "assemble_timeline_summary"]

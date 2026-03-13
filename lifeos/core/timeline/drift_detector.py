"""Drift, trend, and volatility descriptors."""

from __future__ import annotations

from lifeos.core.timeline.baseline_estimator import BaselineEstimate, PairBaselineEstimate
from lifeos.core.timeline.contracts import (
    TimelineFeatureWindow,
    TimelineFinding,
    TimelinePairFeatureWindow,
    TimelineProfile,
    TimelineWindowSpec,
)


def domain_drift_findings(
    *,
    profile: TimelineProfile,
    windows: tuple[TimelineFeatureWindow, ...],
    baseline: BaselineEstimate,
    window_spec: TimelineWindowSpec,
) -> tuple[TimelineFinding, ...]:
    active = next((window for window in windows if window.window.is_active), None)
    if active is None or baseline.available_windows <= 0:
        return ()
    active_value = _window_value(active)
    findings: list[TimelineFinding] = []
    if baseline.available_windows >= baseline.required_windows:
        if active_value > baseline.average_value:
            relation = "above"
        elif active_value < baseline.average_value:
            relation = "below"
        else:
            relation = "in line with"
        findings.append(
            TimelineFinding(
                claim=(
                    f"Relative to the recent baseline, {profile.observation_label} is {relation} "
                    "recent history in the active window."
                ),
                finding_category="baseline_relative_change",
                confidence_label="informational",
                uncertainty_note=f"Baseline uses {baseline.available_windows} fixed prior comparable windows.",
                source_domains=profile.domains,
                evidence_refs=tuple(active.evidence_refs[:6]),
                timeline_context={
                    "claim_type": "baseline_relative_change",
                    "active_window_label": active.window.label,
                    "comparison_label": f"baseline of {baseline.available_windows} prior windows",
                    "window_spec_token": window_spec.token,
                    "baseline_policy_token": profile.baseline_policy_token,
                    "coverage_status": "sufficient",
                },
            )
        )
    values = tuple(_window_value(window) for window in windows)
    if len(values) >= profile.min_trend_windows:
        deltas = [curr - prev for prev, curr in zip(values, values[1:])]
        if all(delta >= 0 for delta in deltas) and any(delta > 0 for delta in deltas):
            direction = "increasing"
        elif all(delta <= 0 for delta in deltas) and any(delta < 0 for delta in deltas):
            direction = "decreasing"
        else:
            direction = "mixed or flat"
        findings.append(
            TimelineFinding(
                claim=f"Across closed comparable windows, {profile.observation_label} shows a {direction} direction.",
                finding_category="trend_direction",
                confidence_label="informational" if direction != "mixed or flat" else "needs_review",
                uncertainty_note=f"Trend uses {len(values)} ordered comparable windows.",
                source_domains=profile.domains,
                evidence_refs=tuple(active.evidence_refs[:6]),
                timeline_context={
                    "claim_type": "trend_direction",
                    "active_window_label": active.window.label,
                    "comparison_label": f"{len(values)} ordered comparable windows",
                    "window_spec_token": window_spec.token,
                    "baseline_policy_token": profile.baseline_policy_token,
                    "coverage_status": "sufficient",
                },
            )
        )
    if len(values) >= 2:
        average = sum(values) / len(values)
        spread = max(values) - min(values)
        descriptor = "more variable" if average > 0 and spread / max(average, 1.0) >= 0.5 else "relatively stable"
        findings.append(
            TimelineFinding(
                claim=f"Across comparable windows, {profile.observation_label} appears {descriptor}.",
                finding_category="volatility_description",
                confidence_label="informational",
                uncertainty_note=f"Observed spread is {round(spread, 4)} across the comparison horizon.",
                source_domains=profile.domains,
                evidence_refs=tuple(active.evidence_refs[:6]),
                timeline_context={
                    "claim_type": "volatility_description",
                    "active_window_label": active.window.label,
                    "comparison_label": "comparison horizon dispersion",
                    "window_spec_token": window_spec.token,
                    "baseline_policy_token": profile.baseline_policy_token,
                    "coverage_status": "sufficient",
                },
            )
        )
    return tuple(findings)


def pair_drift_findings(
    *,
    profile: TimelineProfile,
    windows: tuple[TimelinePairFeatureWindow, ...],
    baseline: PairBaselineEstimate,
    window_spec: TimelineWindowSpec,
) -> tuple[TimelineFinding, ...]:
    active = next((window for window in windows if window.window.is_active), None)
    if active is None or baseline.available_windows <= 0:
        return ()
    relation = "above" if (1.0 if active.aligned else 0.0) > baseline.average_alignment else "in line with"
    if not active.aligned and baseline.average_alignment > 0:
        relation = "below"
    return (
        TimelineFinding(
            claim=(
                "Relative to the recent baseline, approved pair alignment is "
                f"{relation} recent history in the active window."
            ),
            finding_category="approved_pair_alignment_persistence",
            confidence_label=(
                "informational" if baseline.available_windows >= baseline.required_windows else "needs_review"
            ),
            uncertainty_note=f"Baseline uses {baseline.available_windows} fixed prior comparable windows.",
            source_domains=profile.domains,
            evidence_refs=tuple(active.evidence_refs[:6]),
            timeline_context={
                "claim_type": "approved_pair_alignment_persistence",
                "active_window_label": active.window.label,
                "comparison_label": f"baseline of {baseline.available_windows} prior windows",
                "window_spec_token": window_spec.token,
                "baseline_policy_token": profile.baseline_policy_token,
                "coverage_status": (
                    "sufficient" if baseline.available_windows >= baseline.required_windows else "insufficient"
                ),
            },
        ),
    )


def _window_value(window: TimelineFeatureWindow) -> float:
    total_value = float(window.total_value or 0.0)
    return total_value if total_value > 0 else float(window.observation_count)


__all__ = ["domain_drift_findings", "pair_drift_findings"]

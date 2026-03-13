"""Recurrence and continuity detection."""

from __future__ import annotations

from lifeos.core.timeline.contracts import (
    TimelineFeatureWindow,
    TimelineFinding,
    TimelinePairFeatureWindow,
    TimelineProfile,
    TimelineWindowSpec,
)


def domain_recurrence_findings(
    *,
    profile: TimelineProfile,
    windows: tuple[TimelineFeatureWindow, ...],
    window_spec: TimelineWindowSpec,
) -> tuple[TimelineFinding, ...]:
    occupied = [window for window in windows if window.occupied]
    findings: list[TimelineFinding] = []
    if len(occupied) >= profile.min_recurrence_windows:
        findings.append(
            TimelineFinding(
                claim=(
                    f"In the available record, {profile.observation_label} recurred across multiple comparable windows."
                ),
                finding_category="recurrence_observation",
                confidence_label="informational",
                uncertainty_note=(
                    f"Observed in {len(occupied)} comparable windows including " f"{occupied[-1].window.label}."
                ),
                source_domains=profile.domains,
                evidence_refs=tuple(ref for window in occupied[-2:] for ref in window.evidence_refs[:3])[:6],
                timeline_context={
                    "claim_type": "recurrence_observation",
                    "active_window_label": windows[-1].window.label if windows else "",
                    "comparison_label": f"{len(occupied)} occupied comparable windows",
                    "window_spec_token": window_spec.token,
                    "baseline_policy_token": profile.baseline_policy_token,
                    "coverage_status": "sufficient",
                },
            )
        )
    if profile.supports_streaks and len(windows) >= 2:
        prior = windows[-2]
        active = windows[-1]
        if prior.occupied and active.occupied:
            findings.append(
                TimelineFinding(
                    claim=(
                        "In the available record, continuity persisted across the active "
                        "and prior comparable windows."
                    ),
                    finding_category="continuity_or_break",
                    confidence_label="informational",
                    uncertainty_note=(
                        f"Active window {active.window.label} remained occupied after " f"{prior.window.label}."
                    ),
                    source_domains=profile.domains,
                    evidence_refs=tuple((*prior.evidence_refs, *active.evidence_refs)[:6]),
                    timeline_context={
                        "claim_type": "continuity_or_break",
                        "active_window_label": active.window.label,
                        "comparison_label": f"prior comparable window {prior.window.label}",
                        "window_spec_token": window_spec.token,
                        "baseline_policy_token": profile.baseline_policy_token,
                        "coverage_status": "sufficient",
                    },
                )
            )
        elif prior.occupied and not active.occupied:
            findings.append(
                TimelineFinding(
                    claim=(
                        "In the available record, continuity broke between the prior "
                        "comparable window and the active window."
                    ),
                    finding_category="continuity_or_break",
                    confidence_label="needs_review",
                    uncertainty_note=(
                        f"The prior comparable window {prior.window.label} was occupied and "
                        f"the active window {active.window.label} was not."
                    ),
                    source_domains=profile.domains,
                    evidence_refs=tuple(prior.evidence_refs[:6]),
                    timeline_context={
                        "claim_type": "continuity_or_break",
                        "active_window_label": active.window.label,
                        "comparison_label": f"prior comparable window {prior.window.label}",
                        "window_spec_token": window_spec.token,
                        "baseline_policy_token": profile.baseline_policy_token,
                        "coverage_status": "sufficient",
                    },
                )
            )
    if windows:
        occupied_ratio = len(occupied) / len(windows)
        if len(occupied) < 2:
            return tuple(findings)
        if occupied_ratio >= 0.6:
            claim = f"Across comparable windows, {profile.observation_label} appears sustained rather than recent-only."
            note = f"Observed in {len(occupied)} of {len(windows)} comparable windows."
        else:
            claim = f"Across comparable windows, {profile.observation_label} appears episodic rather than sustained."
            note = f"Observed in {len(occupied)} of {len(windows)} comparable windows."
        findings.append(
            TimelineFinding(
                claim=claim,
                finding_category="episodic_vs_sustained",
                confidence_label="informational",
                uncertainty_note=note,
                source_domains=profile.domains,
                evidence_refs=tuple(ref for window in occupied[-2:] for ref in window.evidence_refs[:3])[:6],
                timeline_context={
                    "claim_type": "episodic_vs_sustained",
                    "active_window_label": windows[-1].window.label,
                    "comparison_label": f"{len(occupied)} occupied windows out of {len(windows)}",
                    "window_spec_token": window_spec.token,
                    "baseline_policy_token": profile.baseline_policy_token,
                    "coverage_status": "sufficient",
                },
            )
        )
    return tuple(findings)


def pair_recurrence_findings(
    *,
    profile: TimelineProfile,
    windows: tuple[TimelinePairFeatureWindow, ...],
    window_spec: TimelineWindowSpec,
) -> tuple[TimelineFinding, ...]:
    aligned = [window for window in windows if window.aligned]
    if not windows:
        return ()
    if len(aligned) < 2:
        return ()
    claim = (
        "Across comparable windows, approved pair alignment appears sustained rather than recent-only."
        if len(aligned) >= profile.min_recurrence_windows
        else "Across comparable windows, approved pair alignment appears episodic rather than sustained."
    )
    return (
        TimelineFinding(
            claim=claim,
            finding_category="approved_pair_alignment_persistence",
            confidence_label="informational" if len(aligned) >= profile.min_recurrence_windows else "needs_review",
            uncertainty_note=f"Alignment was present in {len(aligned)} of {len(windows)} comparable windows.",
            source_domains=profile.domains,
            evidence_refs=tuple(ref for window in aligned[-2:] for ref in window.evidence_refs[:3])[:6],
            timeline_context={
                "claim_type": "approved_pair_alignment_persistence",
                "active_window_label": windows[-1].window.label,
                "comparison_label": f"{len(aligned)} aligned windows out of {len(windows)}",
                "window_spec_token": window_spec.token,
                "baseline_policy_token": profile.baseline_policy_token,
                "coverage_status": "sufficient" if len(windows) >= 2 else "insufficient",
            },
        ),
    )


__all__ = ["domain_recurrence_findings", "pair_recurrence_findings"]

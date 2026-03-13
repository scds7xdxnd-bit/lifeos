"""Equal-duration prior-window comparisons."""

from __future__ import annotations

from lifeos.core.timeline.contracts import (
    TimelineFeatureWindow,
    TimelineFinding,
    TimelinePairFeatureWindow,
    TimelineProfile,
    TimelineWindowSpec,
)


def compare_domain_windows(
    *,
    profile: TimelineProfile,
    windows: tuple[TimelineFeatureWindow, ...],
    window_spec: TimelineWindowSpec,
) -> tuple[TimelineFinding, ...]:
    active = _active_window(windows)
    prior = _prior_window(windows)
    if active is None or prior is None:
        return ()
    active_value = _window_value(active)
    prior_value = _window_value(prior)
    if active_value == prior_value:
        relation = "similar to"
        confidence = "informational" if active.observation_count + prior.observation_count >= 2 else "needs_review"
    elif active_value > prior_value:
        relation = "higher than"
        confidence = "informational"
    else:
        relation = "lower than"
        confidence = "informational" if prior.observation_count > 0 else "needs_review"
    finding = TimelineFinding(
        claim=(
            f"Across comparable windows, {profile.observation_label} was {relation} the prior comparable window "
            f"in the active window {active.window.label}."
        ),
        finding_category="prior_window_comparison",
        confidence_label=confidence,
        uncertainty_note=f"Compared with prior comparable window {prior.window.label}.",
        source_domains=profile.domains,
        evidence_refs=tuple((*prior.evidence_refs, *active.evidence_refs)[:6]),
        timeline_context={
            "claim_type": "prior_window_comparison",
            "active_window_label": active.window.label,
            "comparison_label": f"prior comparable window {prior.window.label}",
            "window_spec_token": window_spec.token,
            "baseline_policy_token": profile.baseline_policy_token,
            "coverage_status": "sufficient",
        },
    )
    return (finding,)


def compare_pair_windows(
    *,
    profile: TimelineProfile,
    windows: tuple[TimelinePairFeatureWindow, ...],
    window_spec: TimelineWindowSpec,
) -> tuple[TimelineFinding, ...]:
    active = _active_pair_window(windows)
    prior = _prior_pair_window(windows)
    if active is None or prior is None:
        return ()
    if active.aligned == prior.aligned:
        relation = "matched"
        note = "Alignment status matched the prior comparable window."
    elif active.aligned:
        relation = "appeared in"
        note = "Alignment was present in the active window and absent in the prior comparable window."
    else:
        relation = "weakened in"
        note = "Alignment was absent in the active window after appearing in the prior comparable window."
    finding = TimelineFinding(
        claim=(
            f"Across comparable windows, approved pair alignment {relation} the active window {active.window.label}."
        ),
        finding_category="approved_pair_alignment_persistence",
        confidence_label="informational" if active.aligned or prior.aligned else "needs_review",
        uncertainty_note=note,
        source_domains=profile.domains,
        evidence_refs=tuple((*prior.evidence_refs, *active.evidence_refs)[:6]),
        timeline_context={
            "claim_type": "approved_pair_alignment_persistence",
            "active_window_label": active.window.label,
            "comparison_label": f"prior comparable window {prior.window.label}",
            "window_spec_token": window_spec.token,
            "baseline_policy_token": profile.baseline_policy_token,
            "coverage_status": "sufficient",
        },
    )
    return (finding,)


def _window_value(window: TimelineFeatureWindow) -> float:
    return float(window.total_value or 0.0) if float(window.total_value or 0.0) > 0 else float(window.observation_count)


def _active_window(windows: tuple[TimelineFeatureWindow, ...]) -> TimelineFeatureWindow | None:
    return next((window for window in windows if window.window.is_active), None)


def _prior_window(windows: tuple[TimelineFeatureWindow, ...]) -> TimelineFeatureWindow | None:
    active = _active_window(windows)
    if active is None:
        return None
    candidates = [window for window in windows if window.window.order_index == active.window.order_index - 1]
    return candidates[0] if candidates else None


def _active_pair_window(windows: tuple[TimelinePairFeatureWindow, ...]) -> TimelinePairFeatureWindow | None:
    return next((window for window in windows if window.window.is_active), None)


def _prior_pair_window(windows: tuple[TimelinePairFeatureWindow, ...]) -> TimelinePairFeatureWindow | None:
    active = _active_pair_window(windows)
    if active is None:
        return None
    candidates = [window for window in windows if window.window.order_index == active.window.order_index - 1]
    return candidates[0] if candidates else None


__all__ = ["compare_domain_windows", "compare_pair_windows"]

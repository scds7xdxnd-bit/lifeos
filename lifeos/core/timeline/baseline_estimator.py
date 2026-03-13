"""Fixed baseline estimation for Phase 9."""

from __future__ import annotations

from dataclasses import dataclass

from lifeos.core.timeline.contracts import TimelineFeatureWindow, TimelinePairFeatureWindow, TimelineProfile


@dataclass(frozen=True)
class BaselineEstimate:
    average_value: float
    available_windows: int
    required_windows: int
    values: tuple[float, ...]


@dataclass(frozen=True)
class PairBaselineEstimate:
    average_alignment: float
    available_windows: int
    required_windows: int
    values: tuple[float, ...]


def estimate_domain_baseline(profile: TimelineProfile, windows: tuple[TimelineFeatureWindow, ...]) -> BaselineEstimate:
    baseline = tuple(window for window in windows if not window.window.is_active)
    values = tuple(_window_value(window) for window in baseline)
    available = len(values)
    average = round(sum(values) / available, 4) if available else 0.0
    return BaselineEstimate(
        average_value=average,
        available_windows=available,
        required_windows=profile.baseline_window_count,
        values=values,
    )


def estimate_pair_baseline(
    profile: TimelineProfile, windows: tuple[TimelinePairFeatureWindow, ...]
) -> PairBaselineEstimate:
    baseline = tuple(window for window in windows if not window.window.is_active)
    values = tuple(1.0 if window.aligned else 0.0 for window in baseline)
    available = len(values)
    average = round(sum(values) / available, 4) if available else 0.0
    return PairBaselineEstimate(
        average_alignment=average,
        available_windows=available,
        required_windows=profile.baseline_window_count,
        values=values,
    )


def _window_value(window: TimelineFeatureWindow) -> float:
    total_value = float(window.total_value or 0.0)
    return total_value if total_value > 0 else float(window.observation_count)


__all__ = [
    "BaselineEstimate",
    "PairBaselineEstimate",
    "estimate_domain_baseline",
    "estimate_pair_baseline",
]

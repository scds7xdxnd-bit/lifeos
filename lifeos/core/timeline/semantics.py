"""Canonical timeline semantics for Phase 9."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from lifeos.core.timeline.contracts import TimelineWindow, TimelineWindowSpec

DEFAULT_TIMEZONE_TOKEN = "UTC"
SOURCE_KIND_PRIORITY = {
    "event_record": 0,
    "insight_record": 1,
    "read_model": 2,
}
WINDOW_SPEC_VERSION = "phase9_window_spec_v1"


def resolve_timezone_token(value: str | None) -> str:
    candidate = str(value or "").strip() or DEFAULT_TIMEZONE_TOKEN
    try:
        ZoneInfo(candidate)
    except ZoneInfoNotFoundError:
        return DEFAULT_TIMEZONE_TOKEN
    return candidate


def timezone_info(token: str) -> ZoneInfo:
    return ZoneInfo(resolve_timezone_token(token))


def utc_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def local_datetime(value: datetime, timezone_token: str) -> datetime:
    return utc_aware(value).astimezone(timezone_info(timezone_token))


def local_date_from_datetime(value: datetime, timezone_token: str) -> date:
    return local_datetime(value, timezone_token).date()


def local_date_from_value(value: object, timezone_token: str) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return local_date_from_datetime(value, timezone_token)
    try:
        parsed = datetime.fromisoformat(str(value))
    except ValueError:
        try:
            return date.fromisoformat(str(value))
        except ValueError:
            return None
    return local_date_from_datetime(parsed, timezone_token)


def isoformat_utc(value: datetime | None) -> str | None:
    if value is None:
        return None
    return utc_aware(value).replace(tzinfo=None).isoformat()


def build_window_spec(
    *,
    timeframe_start: datetime,
    timeframe_end: datetime,
    as_of_ts: datetime,
    timezone_token: str,
    baseline_window_count: int,
) -> TimelineWindowSpec:
    start_date = timeframe_start.date()
    requested_end_date = timeframe_end.date()
    as_of_local = local_datetime(as_of_ts, timezone_token)
    capped_end_date = min(requested_end_date, as_of_local.date())
    duration_days = max(1, (requested_end_date - start_date).days + 1)
    active_window = None
    prior_window = None

    if capped_end_date >= start_date:
        active_window = _window(
            start_date,
            duration_days,
            order_index=baseline_window_count,
            is_active=True,
        )
        if active_window.end_local_date > capped_end_date + timedelta(days=1):
            active_window = _window(
                capped_end_date - timedelta(days=duration_days - 1),
                duration_days,
                order_index=baseline_window_count,
                is_active=True,
            )
        prior_window = _window(
            active_window.start_local_date - timedelta(days=duration_days),
            duration_days,
            order_index=baseline_window_count - 1,
            is_prior=True,
        )

    baseline_windows: list[TimelineWindow] = []
    ordered_windows: list[TimelineWindow] = []
    if active_window is not None:
        for index in range(baseline_window_count, 0, -1):
            baseline_windows.append(
                _window(
                    active_window.start_local_date - timedelta(days=duration_days * index),
                    duration_days,
                    order_index=baseline_window_count - index,
                    is_prior=index == 1,
                )
            )
        ordered_windows.extend(baseline_windows)
        ordered_windows.append(active_window)

    token = (
        f"{WINDOW_SPEC_VERSION}:d{duration_days}:b{baseline_window_count}:"
        f"tz:{resolve_timezone_token(timezone_token)}"
    )
    return TimelineWindowSpec(
        token=token,
        duration_days=duration_days,
        timezone_token=resolve_timezone_token(timezone_token),
        active_window=active_window,
        prior_window=prior_window,
        baseline_windows=tuple(baseline_windows),
        ordered_windows=tuple(ordered_windows),
    )


def window_contains(local_day: date, window: TimelineWindow) -> bool:
    return window.start_local_date <= local_day < window.end_local_date


def window_label(window: TimelineWindow) -> str:
    end_inclusive = window.end_local_date - timedelta(days=1)
    return f"{window.start_local_date.isoformat()} to {end_inclusive.isoformat()}"


def _window(
    start_local_date: date, duration_days: int, *, order_index: int, is_active: bool = False, is_prior: bool = False
) -> TimelineWindow:
    end_local_date = start_local_date + timedelta(days=duration_days)
    token = f"w{order_index}:{start_local_date.isoformat()}:{(end_local_date - timedelta(days=1)).isoformat()}"
    return TimelineWindow(
        token=token,
        label=f"{start_local_date.isoformat()} to {(end_local_date - timedelta(days=1)).isoformat()}",
        start_local_date=start_local_date,
        end_local_date=end_local_date,
        order_index=order_index,
        is_active=is_active,
        is_prior=is_prior,
    )


__all__ = [
    "DEFAULT_TIMEZONE_TOKEN",
    "SOURCE_KIND_PRIORITY",
    "WINDOW_SPEC_VERSION",
    "build_window_spec",
    "isoformat_utc",
    "local_date_from_datetime",
    "local_date_from_value",
    "local_datetime",
    "resolve_timezone_token",
    "timezone_info",
    "utc_aware",
    "window_contains",
    "window_label",
]

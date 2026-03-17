"""Deterministic private-alpha access, scope, and readiness helpers."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

from flask import current_app, has_app_context

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.inquiry_cross_domain.pairs import PAIR_PROFILES
from lifeos.core.observability import record_private_alpha_readiness

_ALLOWED_ALPHA_DOMAINS = {"calendar", "habits", "projects", "skills", "finance", "journal"}
_ALLOWED_FEEDBACK_TYPES = (
    "helpful",
    "unclear",
    "too_technical",
    "too_long",
    "incorrect",
    "not_useful_yet",
    "other",
)
_ALLOWED_FEEDBACK_SURFACES = ("humanized", "technical")
_READINESS_WINDOW_DAYS = 30


class AlphaGateError(ValueError):
    def __init__(self, code: str, *, details: dict[str, object] | None = None):
        super().__init__(code)
        self.code = code
        self.details = details or {}


@dataclass(frozen=True)
class AlphaReadinessStatus:
    ready: bool
    blocking_reason: str | None
    next_step: str | None
    recent_window_days: int
    as_of_ts: datetime
    ready_domains: tuple[str, ...]
    ready_pairs: tuple[str, ...]
    domain_event_counts: dict[str, int]

    def to_payload(self) -> dict[str, object]:
        return {
            "ready": self.ready,
            "blocking_reason": self.blocking_reason,
            "next_step": self.next_step,
            "recent_window_days": self.recent_window_days,
            "as_of_ts": self.as_of_ts.isoformat(),
            "ready_domains": list(self.ready_domains),
            "ready_pairs": list(self.ready_pairs),
            "domain_event_counts": dict(self.domain_event_counts),
        }


@dataclass(frozen=True)
class AlphaInviteValidation:
    normalized_email: str
    token_hash: str


@dataclass(frozen=True)
class AlphaFlags:
    enabled: bool
    invite_only: bool
    max_users: int
    visible_domains: tuple[str, ...]
    enabled_pair_profiles: tuple[str, ...]
    technical_brief_enabled: bool
    history_enabled: bool
    inquiry_feedback_enabled: bool
    hide_domain_crud: bool
    require_data_readiness: bool
    calendar_sync_enabled: bool

    def to_bootstrap_payload(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "invite_only": self.invite_only,
            "max_users": self.max_users,
            "visible_domains": list(self.visible_domains),
            "enabled_pair_profiles": list(self.enabled_pair_profiles),
            "technical_brief_enabled": self.technical_brief_enabled,
            "history_enabled": self.history_enabled,
            "inquiry_feedback_enabled": self.inquiry_feedback_enabled,
            "hide_domain_crud": self.hide_domain_crud,
            "require_data_readiness": self.require_data_readiness,
            "calendar_sync_enabled": self.calendar_sync_enabled,
        }


def _is_truthy(value: object) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _normalize_sequence(values: Iterable[str] | str | None) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        return [item.strip() for item in values.split(",") if item.strip()]
    return [str(item).strip() for item in list(values or []) if str(item).strip()]


def _normalize_domains(values: Iterable[str] | str | None) -> tuple[str, ...]:
    normalized = sorted({str(item).strip().lower() for item in _normalize_sequence(values)})
    return tuple(item for item in normalized if item in _ALLOWED_ALPHA_DOMAINS)


def _pair_profile_map() -> dict[str, tuple[str, str]]:
    mapping: dict[str, tuple[str, str]] = {}
    for profile in PAIR_PROFILES:
        mapping[str(profile.profile)] = tuple(sorted(str(item).strip().lower() for item in profile.domains))
    return mapping


def alpha_flags() -> AlphaFlags:
    if not has_app_context():
        return AlphaFlags(
            enabled=False,
            invite_only=False,
            max_users=0,
            visible_domains=(),
            enabled_pair_profiles=(),
            technical_brief_enabled=True,
            history_enabled=True,
            inquiry_feedback_enabled=True,
            hide_domain_crud=False,
            require_data_readiness=False,
            calendar_sync_enabled=True,
        )
    config = current_app.config
    visible_domains = _normalize_domains(config.get("ALPHA_VISIBLE_DOMAINS"))
    enabled_pair_profiles = tuple(
        item.strip()
        for item in _normalize_sequence(config.get("ALPHA_ENABLED_CROSS_DOMAIN_PAIR_PROFILES"))
        if str(item).strip() in _pair_profile_map()
    )
    return AlphaFlags(
        enabled=bool(config.get("ENABLE_PRIVATE_ALPHA", False)),
        invite_only=bool(config.get("ALPHA_INVITE_ONLY", False)),
        max_users=max(int(config.get("ALPHA_MAX_USERS", 0) or 0), 0),
        visible_domains=visible_domains,
        enabled_pair_profiles=enabled_pair_profiles,
        technical_brief_enabled=bool(config.get("ALPHA_ENABLE_TECHNICAL_BRIEF", True)),
        history_enabled=bool(config.get("ALPHA_ENABLE_HISTORY", True)),
        inquiry_feedback_enabled=bool(config.get("ALPHA_ENABLE_INQUIRY_FEEDBACK", True)),
        hide_domain_crud=bool(config.get("ALPHA_HIDE_DOMAIN_CRUD", False)),
        require_data_readiness=bool(config.get("ALPHA_REQUIRE_DATA_READINESS", False)),
        calendar_sync_enabled=bool(config.get("ALPHA_ENABLE_CALENDAR_SYNC", True)),
    )


def alpha_enabled() -> bool:
    return alpha_flags().enabled


def alpha_visible_domains() -> tuple[str, ...]:
    return alpha_flags().visible_domains


def alpha_enabled_pair_profiles() -> tuple[str, ...]:
    return alpha_flags().enabled_pair_profiles


def alpha_allowed_pairs() -> dict[str, tuple[str, str]]:
    pair_map = _pair_profile_map()
    allowed: dict[str, tuple[str, str]] = {}
    flags = alpha_flags()
    for profile_name in flags.enabled_pair_profiles:
        domains = pair_map.get(profile_name)
        if not domains:
            continue
        if all(domain in flags.visible_domains for domain in domains):
            allowed[profile_name] = domains
    return allowed


def alpha_pair_domains() -> set[tuple[str, str]]:
    return set(alpha_allowed_pairs().values())


def alpha_history_enabled() -> bool:
    flags = alpha_flags()
    return (not flags.enabled) or flags.history_enabled


def alpha_technical_brief_enabled() -> bool:
    flags = alpha_flags()
    return (not flags.enabled) or flags.technical_brief_enabled


def alpha_inquiry_feedback_enabled() -> bool:
    flags = alpha_flags()
    return (not flags.enabled) or flags.inquiry_feedback_enabled


def enforce_alpha_inquiry_scope(lens: str, domains: Iterable[str]) -> None:
    flags = alpha_flags()
    if not flags.enabled:
        return
    normalized_domains = tuple(sorted({str(item).strip().lower() for item in domains if str(item).strip()}))
    if lens == "domain":
        if len(normalized_domains) != 1:
            raise AlphaGateError("alpha_single_domain_required")
        if normalized_domains[0] not in flags.visible_domains:
            raise AlphaGateError(
                "alpha_domain_not_visible",
                details={"visible_domains": list(flags.visible_domains), "requested_domains": list(normalized_domains)},
            )
        return
    if lens != "cross_domain":
        raise AlphaGateError("alpha_invalid_lens")
    if len(normalized_domains) != 2:
        raise AlphaGateError("alpha_pair_required")
    if any(domain not in flags.visible_domains for domain in normalized_domains):
        raise AlphaGateError(
            "alpha_domain_not_visible",
            details={"visible_domains": list(flags.visible_domains), "requested_domains": list(normalized_domains)},
        )
    if tuple(sorted(normalized_domains)) not in alpha_pair_domains():
        raise AlphaGateError(
            "alpha_pair_not_enabled",
            details={
                "enabled_pair_profiles": list(flags.enabled_pair_profiles),
                "requested_domains": list(normalized_domains),
            },
        )


def inquiry_visible_in_alpha(lens: str, domains: Iterable[str]) -> bool:
    try:
        enforce_alpha_inquiry_scope(lens, domains)
    except AlphaGateError:
        return False
    return True


def evaluate_alpha_readiness(user_id: int, *, as_of_ts: datetime | None = None) -> AlphaReadinessStatus:
    effective_as_of = (as_of_ts or datetime.utcnow()).replace(microsecond=0)
    flags = alpha_flags()
    visible_domains = flags.visible_domains
    window_start = effective_as_of - timedelta(days=_READINESS_WINDOW_DAYS)
    domain_event_counts: dict[str, int] = {}
    ready_domains: list[str] = []
    for domain in visible_domains:
        count = EventRecord.query.filter(
            EventRecord.user_id == user_id,
            EventRecord.created_at >= window_start,
            EventRecord.created_at <= effective_as_of,
            EventRecord.event_type.like(f"{domain}.%"),
        ).count()
        domain_event_counts[domain] = count
        if count > 0:
            ready_domains.append(domain)
    ready_pairs = sorted(
        profile_name
        for profile_name, domains in alpha_allowed_pairs().items()
        if all(domain in ready_domains for domain in domains)
    )
    ready = bool(ready_domains or ready_pairs)
    next_step = None
    blocking_reason = None
    if not ready:
        blocking_reason = "alpha_readiness_not_met"
        if "calendar" in visible_domains and flags.calendar_sync_enabled:
            next_step = (
                "Connect or sync calendar, or add recent records in one visible alpha domain before running inquiry."
            )
        else:
            next_step = "Add recent records in one visible alpha domain before running inquiry."
    readiness = AlphaReadinessStatus(
        ready=ready,
        blocking_reason=blocking_reason,
        next_step=next_step,
        recent_window_days=_READINESS_WINDOW_DAYS,
        as_of_ts=effective_as_of,
        ready_domains=tuple(sorted(ready_domains)),
        ready_pairs=tuple(ready_pairs),
        domain_event_counts=domain_event_counts,
    )
    record_private_alpha_readiness(ready=readiness.ready, blocking_reason=readiness.blocking_reason)
    return readiness


def enforce_alpha_readiness(user_id: int, *, as_of_ts: datetime | None = None) -> AlphaReadinessStatus:
    flags = alpha_flags()
    readiness = evaluate_alpha_readiness(user_id, as_of_ts=as_of_ts)
    if flags.enabled and flags.require_data_readiness and not readiness.ready:
        raise AlphaGateError(readiness.blocking_reason or "alpha_readiness_not_met", details=readiness.to_payload())
    return readiness


def validate_alpha_feedback_type(feedback_type: str) -> str:
    normalized = str(feedback_type or "").strip().lower()
    if normalized not in _ALLOWED_FEEDBACK_TYPES:
        raise AlphaGateError("invalid_alpha_feedback_type")
    return normalized


def validate_alpha_feedback_surface(surface: str) -> str:
    normalized = str(surface or "").strip().lower() or "humanized"
    if normalized not in _ALLOWED_FEEDBACK_SURFACES:
        raise AlphaGateError("invalid_alpha_feedback_surface")
    if normalized == "technical" and not alpha_technical_brief_enabled():
        raise AlphaGateError("alpha_technical_brief_disabled")
    return normalized


def normalize_invite_email(email: str) -> str:
    return str(email or "").strip().lower()


def hash_invite_token(raw_token: str) -> str:
    return hashlib.sha256(str(raw_token or "").encode("utf-8")).hexdigest()


__all__ = [
    "AlphaFlags",
    "AlphaGateError",
    "AlphaInviteValidation",
    "AlphaReadinessStatus",
    "alpha_allowed_pairs",
    "alpha_enabled",
    "alpha_enabled_pair_profiles",
    "alpha_flags",
    "alpha_history_enabled",
    "alpha_inquiry_feedback_enabled",
    "alpha_pair_domains",
    "alpha_technical_brief_enabled",
    "alpha_visible_domains",
    "enforce_alpha_inquiry_scope",
    "enforce_alpha_readiness",
    "evaluate_alpha_readiness",
    "hash_invite_token",
    "inquiry_visible_in_alpha",
    "normalize_invite_email",
    "validate_alpha_feedback_surface",
    "validate_alpha_feedback_type",
]

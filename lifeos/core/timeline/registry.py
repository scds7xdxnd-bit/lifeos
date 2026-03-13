"""Allowlisted Phase 9 timeline profiles."""

from __future__ import annotations

from flask import current_app, has_app_context

from lifeos.core.timeline.contracts import TimelineProfile

FIRST_WAVE_TIMELINE_DOMAINS = ("calendar", "finance", "habits", "projects", "skills")
APPROVED_PHASE8_PAIRS = (
    ("calendar", "projects"),
    ("finance", "habits"),
    ("habits", "health"),
    ("habits", "journal"),
    ("journal", "relationships"),
    ("projects", "skills"),
)

DOMAIN_TIMELINE_PROFILES: dict[str, TimelineProfile] = {
    "calendar": TimelineProfile(
        profile_id="calendar_timeline_v1",
        profile_version="1.0.0",
        scope="domain",
        domains=("calendar",),
        adapter_key="calendar",
        baseline_window_count=3,
        min_recurrence_windows=2,
        min_trend_windows=3,
        max_findings=4,
        baseline_policy_token="fixed_prior_windows_v1:b3",
        value_label="scheduled activity",
        observation_label="calendar events",
    ),
    "finance": TimelineProfile(
        profile_id="finance_timeline_v1",
        profile_version="1.0.0",
        scope="domain",
        domains=("finance",),
        adapter_key="finance",
        baseline_window_count=3,
        min_recurrence_windows=2,
        min_trend_windows=3,
        max_findings=4,
        baseline_policy_token="fixed_prior_windows_v1:b3",
        value_label="activity volume",
        observation_label="finance activity",
    ),
    "habits": TimelineProfile(
        profile_id="habits_timeline_v1",
        profile_version="1.0.0",
        scope="domain",
        domains=("habits",),
        adapter_key="habits",
        baseline_window_count=3,
        min_recurrence_windows=2,
        min_trend_windows=3,
        max_findings=5,
        baseline_policy_token="fixed_prior_windows_v1:b3",
        value_label="logged activity",
        observation_label="habit logs",
        supports_streaks=True,
    ),
    "projects": TimelineProfile(
        profile_id="projects_timeline_v1",
        profile_version="1.0.0",
        scope="domain",
        domains=("projects",),
        adapter_key="projects",
        baseline_window_count=3,
        min_recurrence_windows=2,
        min_trend_windows=3,
        max_findings=4,
        baseline_policy_token="fixed_prior_windows_v1:b3",
        value_label="recorded activity",
        observation_label="project activity",
    ),
    "skills": TimelineProfile(
        profile_id="skills_timeline_v1",
        profile_version="1.0.0",
        scope="domain",
        domains=("skills",),
        adapter_key="skills",
        baseline_window_count=3,
        min_recurrence_windows=2,
        min_trend_windows=3,
        max_findings=5,
        baseline_policy_token="fixed_prior_windows_v1:b3",
        value_label="practice minutes",
        observation_label="practice sessions",
        supports_streaks=True,
    ),
}

PAIR_TIMELINE_PROFILES: dict[str, TimelineProfile] = {
    "calendar__projects": TimelineProfile(
        profile_id="projects_calendar_timeline_v1",
        profile_version="1.0.0",
        scope="pair",
        domains=("calendar", "projects"),
        adapter_key="calendar__projects",
        baseline_window_count=3,
        min_recurrence_windows=2,
        min_trend_windows=3,
        max_findings=3,
        baseline_policy_token="fixed_prior_windows_v1:b3",
        value_label="alignment windows",
        observation_label="calendar/project alignment",
    ),
    "finance__habits": TimelineProfile(
        profile_id="finance_habits_timeline_v1",
        profile_version="1.0.0",
        scope="pair",
        domains=("finance", "habits"),
        adapter_key="finance__habits",
        baseline_window_count=3,
        min_recurrence_windows=2,
        min_trend_windows=3,
        max_findings=3,
        baseline_policy_token="fixed_prior_windows_v1:b3",
        value_label="alignment windows",
        observation_label="finance/habit alignment",
    ),
    "habits__health": TimelineProfile(
        profile_id="health_habits_timeline_v1",
        profile_version="1.0.0",
        scope="pair",
        domains=("habits", "health"),
        adapter_key="habits__health",
        baseline_window_count=3,
        min_recurrence_windows=2,
        min_trend_windows=3,
        max_findings=3,
        baseline_policy_token="fixed_prior_windows_v1:b3",
        value_label="alignment windows",
        observation_label="health/habit alignment",
    ),
    "habits__journal": TimelineProfile(
        profile_id="journal_habits_timeline_v1",
        profile_version="1.0.0",
        scope="pair",
        domains=("habits", "journal"),
        adapter_key="habits__journal",
        baseline_window_count=3,
        min_recurrence_windows=2,
        min_trend_windows=3,
        max_findings=3,
        baseline_policy_token="fixed_prior_windows_v1:b3",
        value_label="alignment windows",
        observation_label="journal/habit alignment",
    ),
    "journal__relationships": TimelineProfile(
        profile_id="relationships_journal_timeline_v1",
        profile_version="1.0.0",
        scope="pair",
        domains=("journal", "relationships"),
        adapter_key="journal__relationships",
        baseline_window_count=3,
        min_recurrence_windows=2,
        min_trend_windows=3,
        max_findings=3,
        baseline_policy_token="fixed_prior_windows_v1:b3",
        value_label="alignment windows",
        observation_label="relationship/journal alignment",
    ),
    "projects__skills": TimelineProfile(
        profile_id="projects_skills_timeline_v1",
        profile_version="1.0.0",
        scope="pair",
        domains=("projects", "skills"),
        adapter_key="projects__skills",
        baseline_window_count=3,
        min_recurrence_windows=2,
        min_trend_windows=3,
        max_findings=3,
        baseline_policy_token="fixed_prior_windows_v1:b3",
        value_label="alignment windows",
        observation_label="project/skill alignment",
    ),
}


def timeline_enabled() -> bool:
    if not has_app_context():
        return False
    return bool(current_app.config.get("ENABLE_PHASE9_TIMELINE_INTELLIGENCE", False))


def _profile_allowlist() -> set[str] | None:
    if not has_app_context():
        return None
    configured = current_app.config.get("PHASE9_ENABLED_TIMELINE_PROFILES")
    if not configured:
        return None
    if isinstance(configured, str):
        raw_items = configured.split(",")
    else:
        raw_items = list(configured)
    allowed = {str(item).strip() for item in raw_items if str(item).strip()}
    return allowed or None


def _allowed_profile(profile: TimelineProfile) -> bool:
    if not timeline_enabled():
        return False
    allowlist = _profile_allowlist()
    if allowlist is None:
        return True
    return profile.profile_id in allowlist


def get_domain_timeline_profile(domain: str) -> TimelineProfile | None:
    profile = DOMAIN_TIMELINE_PROFILES.get(str(domain or "").strip().lower())
    if profile is None:
        return None
    if profile.domains[0] not in FIRST_WAVE_TIMELINE_DOMAINS:
        return None
    return profile if _allowed_profile(profile) else None


def get_pair_timeline_profile(domains: list[str] | tuple[str, ...]) -> TimelineProfile | None:
    pair = tuple(sorted(str(domain or "").strip().lower() for domain in domains))
    if len(pair) != 2 or pair not in APPROVED_PHASE8_PAIRS:
        return None
    key = "__".join(pair)
    profile = PAIR_TIMELINE_PROFILES.get(key)
    if profile is None:
        return None
    if any(domain not in FIRST_WAVE_TIMELINE_DOMAINS for domain in pair):
        return None
    return profile if _allowed_profile(profile) else None


__all__ = [
    "APPROVED_PHASE8_PAIRS",
    "DOMAIN_TIMELINE_PROFILES",
    "FIRST_WAVE_TIMELINE_DOMAINS",
    "PAIR_TIMELINE_PROFILES",
    "get_domain_timeline_profile",
    "get_pair_timeline_profile",
    "timeline_enabled",
]

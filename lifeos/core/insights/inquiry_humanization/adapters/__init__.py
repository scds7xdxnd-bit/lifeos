"""Bounded domain and approved-pair phrasing adapters for inquiry humanization."""

from __future__ import annotations

import re

from lifeos.core.insights.inquiry_humanization.adapters.base import HumanizationAdapter
from lifeos.core.insights.inquiry_humanization.adapters.calendar import ADAPTER as CALENDAR_ADAPTER
from lifeos.core.insights.inquiry_humanization.adapters.finance import ADAPTER as FINANCE_ADAPTER
from lifeos.core.insights.inquiry_humanization.adapters.habits import ADAPTER as HABITS_ADAPTER
from lifeos.core.insights.inquiry_humanization.adapters.health import ADAPTER as HEALTH_ADAPTER
from lifeos.core.insights.inquiry_humanization.adapters.journal import ADAPTER as JOURNAL_ADAPTER
from lifeos.core.insights.inquiry_humanization.adapters.pairs import PAIR_ADAPTERS
from lifeos.core.insights.inquiry_humanization.adapters.projects import ADAPTER as PROJECTS_ADAPTER
from lifeos.core.insights.inquiry_humanization.adapters.relationships import ADAPTER as RELATIONSHIPS_ADAPTER
from lifeos.core.insights.inquiry_humanization.adapters.skills import ADAPTER as SKILLS_ADAPTER

_DOMAIN_ADAPTERS = {
    "finance": FINANCE_ADAPTER,
    "habits": HABITS_ADAPTER,
    "projects": PROJECTS_ADAPTER,
    "skills": SKILLS_ADAPTER,
    "calendar": CALENDAR_ADAPTER,
    "health": HEALTH_ADAPTER,
    "journal": JOURNAL_ADAPTER,
    "relationships": RELATIONSHIPS_ADAPTER,
}
_DOMAIN_ALIASES = {
    "calendar": "calendar",
    "finance": "finance",
    "financial": "finance",
    "habit": "habits",
    "habits": "habits",
    "health": "health",
    "journal": "journal",
    "journaling": "journal",
    "project": "projects",
    "projects": "projects",
    "relationship": "relationships",
    "relationships": "relationships",
    "skill": "skills",
    "skills": "skills",
}
_LENS_ALIASES = {
    "cross_domain": "cross_domain",
    "crossdomain": "cross_domain",
    "domain": "domain",
}
_DEFAULT_ADAPTER = HumanizationAdapter(key="default")


def _normalize_token(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(value or "").strip().lower()).strip("_")


def _normalize_lens(value: object) -> str:
    return _LENS_ALIASES.get(_normalize_token(value), "")


def _normalize_domains(values: object) -> tuple[str, ...]:
    normalized: list[str] = []
    seen: set[str] = set()
    for item in list(values or []):
        domain = _DOMAIN_ALIASES.get(_normalize_token(item), "")
        if not domain or domain in seen:
            continue
        seen.add(domain)
        normalized.append(domain)
    return tuple(normalized)


def resolve_adapter(brief: dict) -> HumanizationAdapter:
    lens = _normalize_lens(brief.get("lens"))
    domains = _normalize_domains(brief.get("domains") or [])
    if lens == "cross_domain" and len(domains) == 2:
        pair_key = "__".join(sorted(domains))
        return PAIR_ADAPTERS.get(pair_key, _DEFAULT_ADAPTER)
    if domains:
        return _DOMAIN_ADAPTERS.get(domains[0], _DEFAULT_ADAPTER)
    return _DEFAULT_ADAPTER


__all__ = ["HumanizationAdapter", "resolve_adapter"]

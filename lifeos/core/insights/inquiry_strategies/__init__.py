"""Focused inquiry domain expert strategy registry."""

from __future__ import annotations

from lifeos.core.insights.inquiry_strategies.base import DomainStrategyProfile, enforce_claim_guardrail
from lifeos.core.insights.inquiry_strategies.finance import FINANCE_STRATEGY
from lifeos.core.insights.inquiry_strategies.habits import HABITS_STRATEGY
from lifeos.core.insights.inquiry_strategies.health import HEALTH_STRATEGY
from lifeos.core.insights.inquiry_strategies.journal import JOURNAL_STRATEGY
from lifeos.core.insights.inquiry_strategies.projects import PROJECTS_STRATEGY
from lifeos.core.insights.inquiry_strategies.relationships import RELATIONSHIPS_STRATEGY
from lifeos.core.insights.inquiry_strategies.skills import SKILLS_STRATEGY

FIRST_WAVE_DOMAIN_STRATEGIES: dict[str, DomainStrategyProfile] = {
    "finance": FINANCE_STRATEGY,
    "habits": HABITS_STRATEGY,
    "projects": PROJECTS_STRATEGY,
    "skills": SKILLS_STRATEGY,
}

LATER_WAVE_DOMAIN_STRATEGIES: dict[str, DomainStrategyProfile] = {
    "journal": JOURNAL_STRATEGY,
    "relationships": RELATIONSHIPS_STRATEGY,
    "health": HEALTH_STRATEGY,
}

DOMAIN_STRATEGIES: dict[str, DomainStrategyProfile] = {
    **FIRST_WAVE_DOMAIN_STRATEGIES,
    **LATER_WAVE_DOMAIN_STRATEGIES,
}

GENERIC_BRIEF_PROFILE = {
    "profile": "generic_inquiry_brief",
    "profile_version": "1.0.0",
    "strategy": "generic_rules_v1",
    "strategy_version": "1.0.0",
}


def get_first_wave_strategy(domain: str) -> DomainStrategyProfile | None:
    return FIRST_WAVE_DOMAIN_STRATEGIES.get(str(domain or "").lower())


def get_domain_strategy(domain: str) -> DomainStrategyProfile | None:
    return DOMAIN_STRATEGIES.get(str(domain or "").lower())


def strategy_token_for_scope(*, lens: str, primary_domain: str, domains: list[str]) -> str:
    if lens == "domain" and len(domains) == 1:
        strategy = get_domain_strategy(primary_domain)
        if strategy:
            return f"{strategy.profile}:{strategy.profile_version}:{strategy.strategy_version}"
    return (
        f"{GENERIC_BRIEF_PROFILE['profile']}:"
        f"{GENERIC_BRIEF_PROFILE['profile_version']}:"
        f"{GENERIC_BRIEF_PROFILE['strategy_version']}"
    )


__all__ = [
    "DomainStrategyProfile",
    "FIRST_WAVE_DOMAIN_STRATEGIES",
    "LATER_WAVE_DOMAIN_STRATEGIES",
    "DOMAIN_STRATEGIES",
    "GENERIC_BRIEF_PROFILE",
    "get_domain_strategy",
    "get_first_wave_strategy",
    "strategy_token_for_scope",
    "enforce_claim_guardrail",
]

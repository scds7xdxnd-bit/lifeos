"""Cross-domain strategy registry."""

from __future__ import annotations

from lifeos.core.insights.inquiry_cross_domain.pairs import PAIR_PROFILES
from lifeos.core.insights.inquiry_cross_domain.pairs.base import CrossDomainPairProfile


class CrossDomainStrategyRegistry:
    """Deterministic pair strategy registry."""

    def __init__(self) -> None:
        self._by_pair: dict[tuple[str, str], CrossDomainPairProfile] = {}
        for profile in PAIR_PROFILES:
            pair = tuple(sorted(profile.domains))
            self._by_pair[pair] = profile

    def get(self, domains: list[str] | tuple[str, ...]) -> CrossDomainPairProfile | None:
        pair = tuple(sorted(str(domain).strip().lower() for domain in domains))
        if len(pair) != 2:
            return None
        return self._by_pair.get((pair[0], pair[1]))

    def contains(self, domains: list[str] | tuple[str, ...]) -> bool:
        return self.get(domains) is not None


CROSS_DOMAIN_STRATEGY_REGISTRY = CrossDomainStrategyRegistry()


def get_cross_domain_strategy(domains: list[str] | tuple[str, ...]) -> CrossDomainPairProfile | None:
    return CROSS_DOMAIN_STRATEGY_REGISTRY.get(domains)


__all__ = [
    "CrossDomainStrategyRegistry",
    "CROSS_DOMAIN_STRATEGY_REGISTRY",
    "get_cross_domain_strategy",
]

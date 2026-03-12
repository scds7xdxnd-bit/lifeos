"""Domain expert strategy profiles for focused inquiry."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DomainStrategyProfile:
    domain: str
    profile: str
    profile_version: str
    strategy: str
    strategy_version: str
    finding_categories: tuple[str, ...]
    coverage_category: str
    signal_category: str
    gap_category: str
    limitation_language: tuple[str, str]
    refine_guidance: tuple[str, ...]
    allowed_claim_prefixes: tuple[str, ...]
    forbidden_claim_tokens: tuple[str, ...]
    event_priority_prefixes: tuple[str, ...]
    insight_priority_kinds: tuple[str, ...]

    def event_priority(self, event_type: str | None) -> int:
        value = str(event_type or "")
        for idx, prefix in enumerate(self.event_priority_prefixes):
            if value.startswith(prefix):
                return idx
        return len(self.event_priority_prefixes) + 1

    def insight_priority(self, insight_kind: str | None) -> int:
        value = str(insight_kind or "")
        for idx, kind in enumerate(self.insight_priority_kinds):
            if value == kind:
                return idx
        return len(self.insight_priority_kinds) + 1


def enforce_claim_guardrail(
    claim: str,
    *,
    allowed_prefixes: tuple[str, ...],
    forbidden_tokens: tuple[str, ...],
    fallback: str,
) -> str:
    normalized = claim.strip()
    lowered = normalized.lower()
    if not any(lowered.startswith(prefix.lower()) for prefix in allowed_prefixes):
        return fallback
    lowered = claim.lower()
    for token in forbidden_tokens:
        if token in lowered:
            return fallback
    return normalized


__all__ = ["DomainStrategyProfile", "enforce_claim_guardrail"]

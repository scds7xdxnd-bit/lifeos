"""Phase 5b ML contracts for deterministic cross-domain insights (rules-only)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

FEATURE_VERSION = "v1"
ALLOWED_WINDOW_DAYS: Tuple[int, ...] = (7, 14, 30)
ALLOWED_DELIVERY_POLICIES: Tuple[str, ...] = ("feed",)
ALLOWED_SEVERITIES: Tuple[str, ...] = ("info",)

PHASE5B_FORBIDDEN_CAPABILITIES = (
    "ml_models",
    "embeddings",
    "personalization",
    "notifications",
    "autonomous_actions",
    "ranking_learning",
)

PHASE5B_REQUIRED_INVARIANTS = (
    "deterministic_rules_only",
    "explainable_outputs",
    "feed_only_delivery",
    "no_hidden_state",
)


@dataclass(frozen=True)
class FeatureContract:
    """Feature definition contract for deterministic features."""

    key: str
    source_domain: str
    description: str
    version: str = FEATURE_VERSION


@dataclass(frozen=True)
class InsightTypeContract:
    """Phase 5b insight type contract."""

    insight_type: str
    required_features: List[str]
    window_days: int
    delivery_policy: str
    severity: str
    confidence_range: Tuple[float, float]
    priority_range: Tuple[int, int]


PHASE5B_FEATURE_CONTRACTS: dict[str, FeatureContract] = {
    "calendar.event.count": FeatureContract(
        key="calendar.event.count",
        source_domain="calendar",
        description="Count of calendar events created.",
    ),
    "calendar.event.late_night.count": FeatureContract(
        key="calendar.event.late_night.count",
        source_domain="calendar",
        description="Count of late-night calendar events (21:00-04:59).",
    ),
    "calendar.obligation.count": FeatureContract(
        key="calendar.obligation.count",
        source_domain="calendar",
        description="Count of calendar events that look like obligations.",
    ),
    "finance.transaction.count": FeatureContract(
        key="finance.transaction.count",
        source_domain="finance",
        description="Count of finance transactions recorded.",
    ),
    "finance.spend.total": FeatureContract(
        key="finance.spend.total",
        source_domain="finance",
        description="Total absolute spend from finance transactions.",
    ),
    "journal.entry.count": FeatureContract(
        key="journal.entry.count",
        source_domain="journal",
        description="Count of journal entries recorded.",
    ),
    "journal.stress.count": FeatureContract(
        key="journal.stress.count",
        source_domain="journal",
        description="Count of journal entries tagged as stress/low mood.",
    ),
    "habits.log.count": FeatureContract(
        key="habits.log.count",
        source_domain="habits",
        description="Count of habit logs recorded.",
    ),
    "health.sleep_low.count": FeatureContract(
        key="health.sleep_low.count",
        source_domain="health",
        description="Count of low-sleep health metrics.",
    ),
    "relationships.interaction.count": FeatureContract(
        key="relationships.interaction.count",
        source_domain="relationships",
        description="Count of relationship interactions logged.",
    ),
    "projects.task.completed.count": FeatureContract(
        key="projects.task.completed.count",
        source_domain="projects",
        description="Count of project tasks completed.",
    ),
}


PHASE5B_INSIGHT_TYPE_CONTRACTS: dict[str, InsightTypeContract] = {
    "finance_calendar_obligation_risk": InsightTypeContract(
        insight_type="finance_calendar_obligation_risk",
        required_features=["calendar.obligation.count", "finance.spend.total"],
        window_days=30,
        delivery_policy="feed",
        severity="info",
        confidence_range=(0.4, 0.9),
        priority_range=(70, 70),
    ),
    "finance_journal_stress_spike": InsightTypeContract(
        insight_type="finance_journal_stress_spike",
        required_features=["journal.stress.count", "finance.spend.total"],
        window_days=7,
        delivery_policy="feed",
        severity="info",
        confidence_range=(0.4, 0.9),
        priority_range=(65, 65),
    ),
    "journal_habit_reflection_link": InsightTypeContract(
        insight_type="journal_habit_reflection_link",
        required_features=["journal.entry.count", "habits.log.count"],
        window_days=7,
        delivery_policy="feed",
        severity="info",
        confidence_range=(0.55, 0.55),
        priority_range=(55, 55),
    ),
    "calendar_relationship_gap": InsightTypeContract(
        insight_type="calendar_relationship_gap",
        required_features=["calendar.event.count", "relationships.interaction.count"],
        window_days=30,
        delivery_policy="feed",
        severity="info",
        confidence_range=(0.5, 0.5),
        priority_range=(60, 60),
    ),
    "calendar_project_late_night_slippage": InsightTypeContract(
        insight_type="calendar_project_late_night_slippage",
        required_features=["calendar.event.late_night.count", "projects.task.completed.count"],
        window_days=14,
        delivery_policy="feed",
        severity="info",
        confidence_range=(0.5, 0.5),
        priority_range=(60, 60),
    ),
    "habits_health_sleep_consistency": InsightTypeContract(
        insight_type="habits_health_sleep_consistency",
        required_features=["habits.log.count", "health.sleep_low.count"],
        window_days=7,
        delivery_policy="feed",
        severity="info",
        confidence_range=(0.55, 0.55),
        priority_range=(55, 55),
    ),
}


def get_feature_contract(feature_key: str) -> FeatureContract | None:
    return PHASE5B_FEATURE_CONTRACTS.get(feature_key)


def list_feature_contracts() -> Iterable[FeatureContract]:
    return PHASE5B_FEATURE_CONTRACTS.values()


def get_insight_type_contract(insight_type: str) -> InsightTypeContract | None:
    return PHASE5B_INSIGHT_TYPE_CONTRACTS.get(insight_type)


def list_insight_type_contracts() -> Iterable[InsightTypeContract]:
    return PHASE5B_INSIGHT_TYPE_CONTRACTS.values()


def alignment_report() -> dict[str, object]:
    """Return a diff report against the Phase 5b registry/feature definitions."""
    from lifeos.core.insights.feature_service import FEATURE_DEFINITIONS
    from lifeos.core.insights.registry import PHASE5B_INSIGHT_DEFINITIONS

    feature_keys = set(FEATURE_DEFINITIONS.keys())
    contract_feature_keys = set(PHASE5B_FEATURE_CONTRACTS.keys())

    registry_insights = {definition.insight_type for definition in PHASE5B_INSIGHT_DEFINITIONS}
    contract_insights = set(PHASE5B_INSIGHT_TYPE_CONTRACTS.keys())

    invalid_window_days = {
        key: contract.window_days
        for key, contract in PHASE5B_INSIGHT_TYPE_CONTRACTS.items()
        if contract.window_days not in ALLOWED_WINDOW_DAYS
    }
    invalid_delivery_policies = {
        key: contract.delivery_policy
        for key, contract in PHASE5B_INSIGHT_TYPE_CONTRACTS.items()
        if contract.delivery_policy not in ALLOWED_DELIVERY_POLICIES
    }
    invalid_severities = {
        key: contract.severity
        for key, contract in PHASE5B_INSIGHT_TYPE_CONTRACTS.items()
        if contract.severity not in ALLOWED_SEVERITIES
    }

    return {
        "missing_feature_contracts": sorted(feature_keys - contract_feature_keys),
        "extra_feature_contracts": sorted(contract_feature_keys - feature_keys),
        "missing_insight_contracts": sorted(registry_insights - contract_insights),
        "extra_insight_contracts": sorted(contract_insights - registry_insights),
        "invalid_window_days": invalid_window_days,
        "invalid_delivery_policies": invalid_delivery_policies,
        "invalid_severities": invalid_severities,
    }


__all__ = [
    "FEATURE_VERSION",
    "ALLOWED_WINDOW_DAYS",
    "ALLOWED_DELIVERY_POLICIES",
    "ALLOWED_SEVERITIES",
    "PHASE5B_FORBIDDEN_CAPABILITIES",
    "PHASE5B_REQUIRED_INVARIANTS",
    "FeatureContract",
    "InsightTypeContract",
    "PHASE5B_FEATURE_CONTRACTS",
    "PHASE5B_INSIGHT_TYPE_CONTRACTS",
    "get_feature_contract",
    "list_feature_contracts",
    "get_insight_type_contract",
    "list_insight_type_contracts",
    "alignment_report",
]

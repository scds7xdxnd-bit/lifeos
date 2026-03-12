"""Cross-domain inquiry strategy modules."""

from lifeos.core.insights.inquiry_cross_domain.aggregator import (
    NormalizedCrossDomainEvidence,
    aggregate_cross_domain_evidence,
)
from lifeos.core.insights.inquiry_cross_domain.engine import (
    CrossDomainSynthesisResult,
    synthesize_cross_domain_brief,
)
from lifeos.core.insights.inquiry_cross_domain.registry import (
    CROSS_DOMAIN_STRATEGY_REGISTRY,
    CrossDomainStrategyRegistry,
    get_cross_domain_strategy,
)

__all__ = [
    "CrossDomainSynthesisResult",
    "CrossDomainStrategyRegistry",
    "CROSS_DOMAIN_STRATEGY_REGISTRY",
    "NormalizedCrossDomainEvidence",
    "aggregate_cross_domain_evidence",
    "get_cross_domain_strategy",
    "synthesize_cross_domain_brief",
]

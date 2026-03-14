"""Phase 6 inquiry ML contracts (scaffolding only, no runtime ML decisioning)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from lifeos.core.insights.contracts import CONFIDENCE_VOCABULARY

PHASE6_INQUIRY_V1_NON_RUNTIME_DECLARATION = (
    "Focused Inquiry v1 is deterministic and rules-only. ML is non-runtime and non-decisioning "
    "for inquiry brief generation, confidence labels, and evidence selection."
)
PHASE8_CROSS_DOMAIN_NON_RUNTIME_DECLARATION = (
    "Phase 8 cross-domain inquiry profiles are deterministic, rules-only, non-runtime scaffolding. "
    "Cross-domain profile metadata is structured contract output, not model inference."
)
PHASE8_1_PRODUCTIZATION_NON_RUNTIME_DECLARATION = (
    "Phase 8.1 inquiry productization is deterministic and non-runtime for ML decisioning. "
    "Answerability and usefulness metadata are bounded contract descriptors, not probabilistic truth scores."
)
PHASE8_1_PRODUCTIZATION_VERSION = "phase8_1_productization_v1"
PHASE6_INQUIRY_RUNTIME_DECISIONING_ENABLED = False
PHASE6_INQUIRY_FORBIDDEN_RUNTIME_CAPABILITIES = (
    "runtime_model_scoring",
    "runtime_ranking",
    "runtime_embeddings",
    "runtime_nlp_generation",
    "confidence_relabeling",
    "evidence_override",
    "free_form_answer_generation",
)
PHASE8_1_FORBIDDEN_RUNTIME_CAPABILITIES = (
    "runtime_answerability_scoring",
    "runtime_helpfulness_probability",
    "personalized_finding_ranking",
    "free_form_productized_generation",
)

INQUIRY_LENS_TYPES = ("domain", "cross_domain")
ALLOWED_INQUIRY_ACTIONS = ("display", "refine_only")
FIRST_WAVE_EXPERT_DOMAINS = ("finance", "habits", "projects", "skills")
LATER_WAVE_EXPERT_DOMAINS = ("journal", "relationships", "health")
ALL_EXPERT_DOMAINS = tuple(sorted({*FIRST_WAVE_EXPERT_DOMAINS, *LATER_WAVE_EXPERT_DOMAINS}))
LATER_WAVE_DOMAIN_METADATA_CONTRACTS = {
    "journal": {
        "profile": "focused_inquiry_journal_expert_brief",
        "profile_version": "1.0.0",
        "strategy": "journal_rules_v1",
        "strategy_version": "1.0.0",
        "finding_categories": ("reflection_cadence", "mood_tag_pattern", "evidence_gap"),
    },
    "relationships": {
        "profile": "focused_inquiry_relationships_expert_brief",
        "profile_version": "1.0.0",
        "strategy": "relationships_rules_v1",
        "strategy_version": "1.0.0",
        "finding_categories": ("interaction_cadence", "channel_distribution", "evidence_gap"),
    },
    "health": {
        "profile": "focused_inquiry_health_expert_brief",
        "profile_version": "1.0.0",
        "strategy": "health_rules_v1",
        "strategy_version": "1.0.0",
        "finding_categories": ("metric_coverage", "trend_signal", "evidence_gap"),
    },
}
LATER_WAVE_FORBIDDEN_TOKEN_REQUIREMENTS = {
    "journal": ("diagnosis", "therapy", "hidden intent", "personality"),
    "relationships": ("intent", "emotion of", "moral", "toxic"),
    "health": ("diagnosis", "treatment", "clinical", "medical risk"),
}
REQUIRED_INQUIRY_QUALITY_FIELDS = (
    "findings_total",
    "findings_with_evidence",
    "evidence_coverage_ratio",
    "structure_gaps",
    "sparse_domains",
    "refine_guidance",
)

REQUIRED_INQUIRY_BRIEF_FIELDS = (
    "summary",
    "findings",
    "direct_answer",
    "answerability",
    "context_non_evidence",
    "uncertainty_note",
    "limits",
    "refine_guidance",
    "bounded_patterns",
    "productization_metadata",
    "question",
    "lens",
    "domains",
    "timeframe",
    "as_of_ts",
    "generated_at",
    "brief_profile",
    "quality_metadata",
)
REQUIRED_INQUIRY_FINDING_FIELDS = (
    "claim",
    "finding_category",
    "evidence_refs",
    "relevance_rank",
    "relevance_reason",
    "confidence_label",
    "uncertainty_note",
    "source_domains",
)
DISALLOWED_INQUIRY_OUTPUT_FIELDS = (
    "confidence_score",
    "model_output",
    "generated_text",
    "embedding",
    "rank_score",
    "autonomous_action",
    "answer",
)
DISALLOWED_QUALITY_METADATA_FIELDS = (
    "confidence",
    "confidence_score",
    "probability",
    "model_score",
    "truth_score",
)
REQUIRED_DIRECT_ANSWER_FIELDS = ("text", "supporting_claims", "note")
REQUIRED_ANSWERABILITY_FIELDS = ("classification", "reason", "evidence_coverage_ratio", "supporting_finding_count")
REQUIRED_BOUNDED_PATTERN_FIELDS = ("pattern_category", "finding_count", "note")
REQUIRED_PRODUCTIZATION_METADATA_FIELDS = (
    "version",
    "limitation_count_before",
    "limitation_count_after",
    "limitation_redundancy_removed",
    "direct_answer_present",
)
REQUIRED_TIMELINE_METADATA_FIELDS = (
    "timeline_profile_id",
    "timeline_profile_version",
    "window_spec_token",
    "baseline_policy_token",
    "timezone_token",
    "as_of_ts",
    "evidence_manifest_hash",
    "timeline_summary_hash",
    "comparison_coverage",
    "finding_count",
    "insufficiency_count",
)
REQUIRED_TIMELINE_CONTEXT_FIELDS = (
    "claim_type",
    "active_window_label",
    "comparison_label",
    "window_spec_token",
    "baseline_policy_token",
    "coverage_status",
)
REQUIRED_TIMELINE_COVERAGE_FIELDS = (
    "prior_window_available",
    "baseline_windows_available",
    "baseline_windows_required",
    "recurrence_windows_available",
    "trend_windows_available",
)
REQUIRED_LIMITATION_ITEM_FIELDS = ("limitation_id", "text")
REQUIRED_HUMANIZED_METADATA_FIELDS = (
    "canonical_brief_hash",
    "humanization_version",
    "humanized_brief_hash",
    "technical_view_available",
)
REQUIRED_HUMANIZED_ANSWER_FIELDS = ("text", "source_finding_ids", "source_limitation_ids")
REQUIRED_HUMANIZED_BLOCK_FIELDS = (
    "block_id",
    "text",
    "source_finding_ids",
    "source_limitation_ids",
    "evidence_refs",
    "confidence_label",
)
REQUIRED_HUMANIZED_SECTION_FIELDS = ("section_id", "title", "blocks")
TIMELINE_CLAIM_TYPES = (
    "recurrence_observation",
    "continuity_or_break",
    "prior_window_comparison",
    "baseline_relative_change",
    "trend_direction",
    "volatility_description",
    "episodic_vs_sustained",
    "approved_pair_alignment_persistence",
)
PHASE8_1_ALLOWED_ANSWERABILITY_CLASSES = (
    "strong_answerable",
    "partial_answerable",
    "weak_answerable",
)
DISALLOWED_ANSWERABILITY_FIELDS = (
    "confidence",
    "confidence_score",
    "probability",
    "model_score",
    "truth_score",
    "helpfulness_score",
)
DISALLOWED_PRODUCTIZATION_METADATA_FIELDS = (
    "confidence",
    "confidence_score",
    "probability",
    "model_score",
    "truth_score",
    "helpfulness_score",
    "answerability_score",
)
REQUIRED_BRIEF_PROFILE_FIELDS = (
    "profile",
    "profile_version",
    "strategy",
    "strategy_version",
    "domain",
    "expert_mode",
    "finding_categories",
)
DISALLOWED_BRIEF_PROFILE_FIELDS = (
    "confidence",
    "confidence_score",
    "probability",
    "model_score",
    "rank_score",
)
FORBIDDEN_CROSS_DOMAIN_CLAIM_CATEGORIES = (
    "psychological_interpretation",
    "medical_inference",
    "moral_judgment",
    "intent_inference",
    "unsupported_causality",
)
PHASE8_APPROVED_CROSS_DOMAIN_PAIR_CONTRACTS = {
    "finance__habits": {
        "profile": "finance_habits_v1",
        "profile_version": "1.0.0",
        "strategy": "cross_domain_pair_rules_v1",
        "strategy_version": "1.0.0",
        "domains": ("finance", "habits"),
    },
    "projects__skills": {
        "profile": "projects_skills_v1",
        "profile_version": "1.0.0",
        "strategy": "cross_domain_pair_rules_v1",
        "strategy_version": "1.0.0",
        "domains": ("projects", "skills"),
    },
    "habits__journal": {
        "profile": "journal_habits_v1",
        "profile_version": "1.0.0",
        "strategy": "cross_domain_pair_rules_v1",
        "strategy_version": "1.0.0",
        "domains": ("journal", "habits"),
    },
    "habits__health": {
        "profile": "health_habits_v1",
        "profile_version": "1.0.0",
        "strategy": "cross_domain_pair_rules_v1",
        "strategy_version": "1.0.0",
        "domains": ("health", "habits"),
    },
    "calendar__projects": {
        "profile": "projects_calendar_v1",
        "profile_version": "1.0.0",
        "strategy": "cross_domain_pair_rules_v1",
        "strategy_version": "1.0.0",
        "domains": ("projects", "calendar"),
    },
    "journal__relationships": {
        "profile": "relationships_journal_v1",
        "profile_version": "1.0.0",
        "strategy": "cross_domain_pair_rules_v1",
        "strategy_version": "1.0.0",
        "domains": ("journal", "relationships"),
    },
}
PHASE8_APPROVED_PAIR_PROFILE_NAMES = tuple(
    sorted({str(item["profile"]) for item in PHASE8_APPROVED_CROSS_DOMAIN_PAIR_CONTRACTS.values()})
)
PHASE8_REQUIRED_CROSS_DOMAIN_STORAGE_FIELDS = (
    "cross_domain_profile",
    "cross_domain_profile_version",
    "selected_domains",
    "selected_domains_key",
    "blocked_claim_count",
)
PHASE8_REQUIRED_SELECTED_DOMAIN_CONTRACT_KEYS = (
    "InquiryItem.domains",
    "InquiryBriefItem.domains",
)
PHASE8_REQUIRED_CROSS_DOMAIN_PROFILE_DSD_KEYS = (
    "InquiryBriefProfile.profile",
    "InquiryBriefProfile.profile_version",
    "InquiryBriefProfile.strategy",
    "InquiryBriefProfile.strategy_version",
    "InquiryBriefProfile.domain",
    "InquiryBriefProfile.finding_categories",
)


@dataclass(frozen=True)
class InquiryBriefTypeContract:
    """Bounded contract for inquiry brief types exposed in v1 surfaces."""

    inquiry_type: str
    lens: str
    allowed_actions: tuple[str, ...]
    allowed_confidence_labels: tuple[str, ...]
    required_brief_fields: tuple[str, ...]
    required_finding_fields: tuple[str, ...]


@dataclass(frozen=True)
class InquiryFutureSupportContract:
    """Future ML support stubs; these are not active in v1 runtime."""

    name: str
    scope: str
    required_inputs: tuple[str, ...]
    preserved_contracts: tuple[str, ...]
    runtime_allowed_in_v1: bool = False


@dataclass(frozen=True)
class InquiryDataRequirement:
    """Data that should be preserved now for safe future ML phases."""

    name: str
    required_fields: tuple[str, ...]
    purpose: str


INQUIRY_BRIEF_TYPE_CONTRACTS: dict[str, InquiryBriefTypeContract] = {
    "focused_inquiry_domain_brief": InquiryBriefTypeContract(
        inquiry_type="focused_inquiry_domain_brief",
        lens="domain",
        allowed_actions=ALLOWED_INQUIRY_ACTIONS,
        allowed_confidence_labels=("informational", "needs_review"),
        required_brief_fields=REQUIRED_INQUIRY_BRIEF_FIELDS,
        required_finding_fields=REQUIRED_INQUIRY_FINDING_FIELDS,
    ),
    "focused_inquiry_cross_domain_brief": InquiryBriefTypeContract(
        inquiry_type="focused_inquiry_cross_domain_brief",
        lens="cross_domain",
        allowed_actions=ALLOWED_INQUIRY_ACTIONS,
        allowed_confidence_labels=("informational", "needs_review"),
        required_brief_fields=REQUIRED_INQUIRY_BRIEF_FIELDS,
        required_finding_fields=REQUIRED_INQUIRY_FINDING_FIELDS,
    ),
    "focused_inquiry_timeline_domain_brief": InquiryBriefTypeContract(
        inquiry_type="focused_inquiry_timeline_domain_brief",
        lens="domain",
        allowed_actions=ALLOWED_INQUIRY_ACTIONS,
        allowed_confidence_labels=("informational", "needs_review"),
        required_brief_fields=REQUIRED_INQUIRY_BRIEF_FIELDS,
        required_finding_fields=REQUIRED_INQUIRY_FINDING_FIELDS,
    ),
    "focused_inquiry_timeline_cross_domain_brief": InquiryBriefTypeContract(
        inquiry_type="focused_inquiry_timeline_cross_domain_brief",
        lens="cross_domain",
        allowed_actions=ALLOWED_INQUIRY_ACTIONS,
        allowed_confidence_labels=("informational", "needs_review"),
        required_brief_fields=REQUIRED_INQUIRY_BRIEF_FIELDS,
        required_finding_fields=REQUIRED_INQUIRY_FINDING_FIELDS,
    ),
}


INQUIRY_FUTURE_SUPPORT_CONTRACTS: dict[str, InquiryFutureSupportContract] = {
    "domain_expert_brief_enhancement": InquiryFutureSupportContract(
        name="domain_expert_brief_enhancement",
        scope="Potential domain-specific brief refinement over existing deterministic evidence.",
        required_inputs=(
            "inquiry_brief_version",
            "evidence_refs",
            "uncertainty_note",
            "confidence_label",
        ),
        preserved_contracts=(
            "context_non_evidence_must_remain_separate",
            "canonical_confidence_vocabulary_only",
            "no_evidence_override",
        ),
    ),
    "cross_domain_pattern_support": InquiryFutureSupportContract(
        name="cross_domain_pattern_support",
        scope="Potential support for cross-domain pattern summarization using explicit evidence links.",
        required_inputs=(
            "selected_domains",
            "source_domains",
            "evidence_refs",
            "timeframe",
            "as_of_ts",
        ),
        preserved_contracts=(
            "explicit_cross_domain_scope_required",
            "traceable_evidence_refs_per_finding",
            "bounded_timeframe_and_as_of",
        ),
    ),
    "timeline_intelligence_support": InquiryFutureSupportContract(
        name="timeline_intelligence_support",
        scope="Potential support for temporal sequencing and trend interpretation over inquiry histories.",
        required_inputs=(
            "event_record.created_at",
            "inquiry_request.timeframe_start",
            "inquiry_request.timeframe_end",
            "inquiry_brief_version.as_of_ts",
            "inquiry_brief_version.version_number",
        ),
        preserved_contracts=(
            "deterministic_replay_identity",
            "version_lineage_integrity",
            "no_free_form_answer_generation",
        ),
    ),
}


INQUIRY_FUTURE_DATA_REQUIREMENTS: dict[str, InquiryDataRequirement] = {
    "temporal_features": InquiryDataRequirement(
        name="temporal_features",
        required_fields=(
            "timeframe_start",
            "timeframe_end",
            "as_of_ts",
            "created_at",
            "generated_at",
        ),
        purpose="Enable deterministic temporal reasoning and replay-safe comparisons.",
    ),
    "cross_domain_cooccurrence_features": InquiryDataRequirement(
        name="cross_domain_cooccurrence_features",
        required_fields=(
            "domains",
            "source_domains",
            "event_type",
            "domain",
            "source_kind",
        ),
        purpose="Preserve explicit co-occurrence signals across selected inquiry domains.",
    ),
    "inquiry_refinement_history": InquiryDataRequirement(
        name="inquiry_refinement_history",
        required_fields=(
            "inquiry_id",
            "version_number",
            "parent_version_id",
            "normalized_hash",
            "brief_hash",
        ),
        purpose="Support lineage-aware evaluation and safe regression analysis.",
    ),
    "evidence_coverage_uncertainty_structure": InquiryDataRequirement(
        name="evidence_coverage_uncertainty_structure",
        required_fields=(
            "evidence_refs",
            "uncertainty_note",
            "limits",
            "confidence_label",
            "context_non_evidence",
            "quality_metadata.findings_total",
            "quality_metadata.findings_with_evidence",
            "quality_metadata.evidence_coverage_ratio",
            "quality_metadata.structure_gaps",
            "quality_metadata.sparse_domains",
            "quality_metadata.refine_guidance",
            "brief_profile.profile",
            "brief_profile.profile_version",
            "brief_profile.strategy",
            "brief_profile.strategy_version",
            "brief_profile.domain",
            "brief_profile.expert_mode",
            "brief_profile.finding_categories",
            "finding_category",
            "relevance_rank",
            "relevance_reason",
            "direct_answer.text",
            "direct_answer.supporting_claims",
            "answerability.classification",
            "answerability.evidence_coverage_ratio",
            "bounded_patterns.pattern_category",
            "bounded_patterns.finding_count",
            "productization_metadata.version",
            "productization_metadata.limitation_redundancy_removed",
        ),
        purpose="Keep epistemic boundaries and evidence coverage measurable in future phases.",
    ),
}


def get_inquiry_brief_contract(inquiry_type: str) -> InquiryBriefTypeContract | None:
    return INQUIRY_BRIEF_TYPE_CONTRACTS.get(inquiry_type)


def list_inquiry_brief_contracts() -> Iterable[InquiryBriefTypeContract]:
    return INQUIRY_BRIEF_TYPE_CONTRACTS.values()


def list_inquiry_future_support_contracts() -> Iterable[InquiryFutureSupportContract]:
    return INQUIRY_FUTURE_SUPPORT_CONTRACTS.values()


def list_inquiry_future_data_requirements() -> Iterable[InquiryDataRequirement]:
    return INQUIRY_FUTURE_DATA_REQUIREMENTS.values()


def alignment_report() -> dict[str, object]:
    """Return alignment checks between inquiry runtime contracts and ML stubs."""
    from lifeos.core.contracts import api_contracts
    from lifeos.core.contracts.api_dsd_mappings import DSD_FIELD_MAPPINGS
    from lifeos.core.insights.inquiry_cross_domain.pairs import PAIR_PROFILES
    from lifeos.core.insights.inquiry_cross_domain.pairs.base import ALLOWED_CROSS_DOMAIN_CLAIM_CATEGORIES
    from lifeos.core.insights.inquiry_productization import ANSWERABILITY_CLASSES, productize_inquiry_brief
    from lifeos.core.insights.inquiry_strategies import (
        DOMAIN_STRATEGIES,
        FIRST_WAVE_DOMAIN_STRATEGIES,
        LATER_WAVE_DOMAIN_STRATEGIES,
    )
    from lifeos.core.insights.models import InquiryBriefVersion
    from lifeos.core.ux.domain_surface_contracts import DOMAIN_SURFACE_CONTRACTS

    inquiry_surface = DOMAIN_SURFACE_CONTRACTS.get("insights:inquiry")
    surface_inquiry_types = set(inquiry_surface.insight_contracts if inquiry_surface else [])
    ml_inquiry_types = set(INQUIRY_BRIEF_TYPE_CONTRACTS.keys())

    inquiry_fields = {field.name for field in api_contracts.INQUIRY_ITEM.fields}
    brief_fields = {field.name for field in api_contracts.INQUIRY_BRIEF_ITEM.fields}
    finding_fields = {field.name for field in api_contracts.INQUIRY_FINDING_ITEM.fields}
    brief_profile_fields = {field.name for field in api_contracts.INQUIRY_BRIEF_PROFILE.fields}
    quality_fields = {field.name for field in api_contracts.INQUIRY_QUALITY_METADATA.fields}
    direct_answer_fields = {field.name for field in api_contracts.INQUIRY_DIRECT_ANSWER.fields}
    answerability_fields = {field.name for field in api_contracts.INQUIRY_ANSWERABILITY.fields}
    bounded_pattern_fields = {field.name for field in api_contracts.INQUIRY_BOUNDED_PATTERN.fields}
    productization_fields = {field.name for field in api_contracts.INQUIRY_PRODUCTIZATION_METADATA.fields}
    context_fields = {field.name for field in api_contracts.INQUIRY_CONTEXT_BLOCK.fields}
    disallowed_present = sorted((brief_fields | finding_fields) & set(DISALLOWED_INQUIRY_OUTPUT_FIELDS))
    disallowed_profile_present = sorted(brief_profile_fields & set(DISALLOWED_BRIEF_PROFILE_FIELDS))
    disallowed_quality_present = sorted(quality_fields & set(DISALLOWED_QUALITY_METADATA_FIELDS))
    disallowed_answerability_present = sorted(answerability_fields & set(DISALLOWED_ANSWERABILITY_FIELDS))
    disallowed_productization_present = sorted(productization_fields & set(DISALLOWED_PRODUCTIZATION_METADATA_FIELDS))

    dsd_mapping = DSD_FIELD_MAPPINGS.get("insights:inquiry", {})
    required_quality_dsd_keys = {"InquiryBriefItem.quality_metadata"} | {
        f"InquiryQualityMetadata.{field_name}" for field_name in REQUIRED_INQUIRY_QUALITY_FIELDS
    }
    required_profile_dsd_keys = {"InquiryBriefItem.brief_profile", "InquiryFindingItem.finding_category"} | {
        f"InquiryBriefProfile.{field_name}" for field_name in REQUIRED_BRIEF_PROFILE_FIELDS
    }
    required_productization_dsd_keys = {
        "InquiryBriefItem.direct_answer",
        "InquiryBriefItem.answerability",
        "InquiryBriefItem.refine_guidance",
        "InquiryBriefItem.bounded_patterns",
        "InquiryBriefItem.productization_metadata",
        "InquiryFindingItem.relevance_rank",
        "InquiryFindingItem.relevance_reason",
    }
    required_productization_dsd_keys |= {
        f"InquiryDirectAnswer.{field_name}" for field_name in REQUIRED_DIRECT_ANSWER_FIELDS
    }
    required_productization_dsd_keys |= {
        f"InquiryAnswerability.{field_name}" for field_name in REQUIRED_ANSWERABILITY_FIELDS
    }
    required_productization_dsd_keys |= {
        f"InquiryBoundedPattern.{field_name}" for field_name in REQUIRED_BOUNDED_PATTERN_FIELDS
    }
    required_productization_dsd_keys |= {
        f"InquiryProductizationMetadata.{field_name}" for field_name in REQUIRED_PRODUCTIZATION_METADATA_FIELDS
    }
    required_phase8_dsd_keys = set(PHASE8_REQUIRED_CROSS_DOMAIN_PROFILE_DSD_KEYS) | set(
        PHASE8_REQUIRED_SELECTED_DOMAIN_CONTRACT_KEYS
    )
    missing_quality_dsd_mappings = sorted(required_quality_dsd_keys - set(dsd_mapping.keys()))
    missing_profile_dsd_mappings = sorted(required_profile_dsd_keys - set(dsd_mapping.keys()))
    missing_productization_dsd_mappings = sorted(required_productization_dsd_keys - set(dsd_mapping.keys()))
    missing_phase8_dsd_mappings = sorted(required_phase8_dsd_keys - set(dsd_mapping.keys()))

    productization_probe = productize_inquiry_brief(
        question="",
        domains=[],
        findings=[],
        limits=[],
        incoming_refine_guidance=[],
    )
    productization_runtime_version = str(productization_probe.metadata.get("version") or "")

    missing_selected_domains_contract_fields: list[str] = []
    if "domains" not in inquiry_fields:
        missing_selected_domains_contract_fields.append("InquiryItem.domains")
    if "domains" not in brief_fields:
        missing_selected_domains_contract_fields.append("InquiryBriefItem.domains")

    storage_columns = {column.name for column in InquiryBriefVersion.__table__.columns}
    missing_cross_domain_storage_fields = sorted(set(PHASE8_REQUIRED_CROSS_DOMAIN_STORAGE_FIELDS) - storage_columns)

    expected_pair_contracts = PHASE8_APPROVED_CROSS_DOMAIN_PAIR_CONTRACTS
    expected_pair_keys = set(expected_pair_contracts.keys())
    registry_profiles = {profile.pair_key: profile for profile in PAIR_PROFILES}
    registry_pair_keys = set(registry_profiles.keys())
    allowed_categories = set(ALLOWED_CROSS_DOMAIN_CLAIM_CATEGORIES)
    forbidden_categories = set(FORBIDDEN_CROSS_DOMAIN_CLAIM_CATEGORIES)
    phase8_pair_profile_mismatches: dict[str, dict[str, str]] = {}
    phase8_pair_version_mismatches: dict[str, dict[str, str]] = {}
    phase8_pair_domain_mismatches: dict[str, dict[str, list[str]]] = {}
    phase8_pair_allowed_category_mismatches: dict[str, dict[str, list[str]]] = {}
    phase8_pair_forbidden_category_overlaps: dict[str, list[str]] = {}
    for pair_key in sorted(expected_pair_keys & registry_pair_keys):
        expected = expected_pair_contracts[pair_key]
        actual = registry_profiles[pair_key]

        profile_mismatch: dict[str, str] = {}
        if actual.profile != expected["profile"]:
            profile_mismatch["profile"] = actual.profile
        if actual.strategy != expected["strategy"]:
            profile_mismatch["strategy"] = actual.strategy
        if profile_mismatch:
            phase8_pair_profile_mismatches[pair_key] = profile_mismatch

        version_mismatch: dict[str, str] = {}
        if actual.profile_version != expected["profile_version"]:
            version_mismatch["profile_version"] = actual.profile_version
        if actual.strategy_version != expected["strategy_version"]:
            version_mismatch["strategy_version"] = actual.strategy_version
        if version_mismatch:
            phase8_pair_version_mismatches[pair_key] = version_mismatch

        expected_domains = sorted(expected["domains"])
        actual_domains = sorted(actual.domains)
        if expected_domains != actual_domains:
            phase8_pair_domain_mismatches[pair_key] = {
                "expected_only": sorted(set(expected_domains) - set(actual_domains)),
                "actual_only": sorted(set(actual_domains) - set(expected_domains)),
            }

        actual_categories = set(actual.allowed_claim_categories)
        if actual_categories != allowed_categories:
            phase8_pair_allowed_category_mismatches[pair_key] = {
                "expected_only": sorted(allowed_categories - actual_categories),
                "actual_only": sorted(actual_categories - allowed_categories),
            }
        overlap = sorted(actual_categories & forbidden_categories)
        if overlap:
            phase8_pair_forbidden_category_overlaps[pair_key] = overlap

    strategy_domains = set(DOMAIN_STRATEGIES.keys())
    expected_domains = set(ALL_EXPERT_DOMAINS)
    first_wave_strategy_domains = set(FIRST_WAVE_DOMAIN_STRATEGIES.keys())
    expected_first_wave_domains = set(FIRST_WAVE_EXPERT_DOMAINS)
    later_wave_strategy_domains = set(LATER_WAVE_DOMAIN_STRATEGIES.keys())
    expected_later_wave_domains = set(LATER_WAVE_EXPERT_DOMAINS)

    later_wave_profile_mismatches: dict[str, dict[str, str]] = {}
    later_wave_category_mismatches: dict[str, dict[str, list[str]]] = {}
    later_wave_missing_forbidden_tokens: dict[str, list[str]] = {}
    later_wave_invalid_versions: dict[str, dict[str, str]] = {}
    for domain in sorted(expected_later_wave_domains & later_wave_strategy_domains):
        strategy = LATER_WAVE_DOMAIN_STRATEGIES[domain]
        expected = LATER_WAVE_DOMAIN_METADATA_CONTRACTS[domain]
        profile_mismatch: dict[str, str] = {}
        if strategy.profile != expected["profile"]:
            profile_mismatch["profile"] = strategy.profile
        if strategy.strategy != expected["strategy"]:
            profile_mismatch["strategy"] = strategy.strategy
        if profile_mismatch:
            later_wave_profile_mismatches[domain] = profile_mismatch

        version_mismatch: dict[str, str] = {}
        if strategy.profile_version != expected["profile_version"]:
            version_mismatch["profile_version"] = strategy.profile_version
        if strategy.strategy_version != expected["strategy_version"]:
            version_mismatch["strategy_version"] = strategy.strategy_version
        if version_mismatch:
            later_wave_invalid_versions[domain] = version_mismatch

        expected_categories = set(expected["finding_categories"])
        actual_categories = set(strategy.finding_categories)
        if expected_categories != actual_categories:
            later_wave_category_mismatches[domain] = {
                "expected_only": sorted(expected_categories - actual_categories),
                "actual_only": sorted(actual_categories - expected_categories),
            }

        required_tokens = {item.lower() for item in LATER_WAVE_FORBIDDEN_TOKEN_REQUIREMENTS[domain]}
        actual_tokens = {item.lower() for item in strategy.forbidden_claim_tokens}
        missing_tokens = sorted(required_tokens - actual_tokens)
        if missing_tokens:
            later_wave_missing_forbidden_tokens[domain] = missing_tokens

    confidence_labels = set()
    invalid_lenses: dict[str, str] = {}
    invalid_actions: dict[str, list[str]] = {}
    for inquiry_type, contract in INQUIRY_BRIEF_TYPE_CONTRACTS.items():
        confidence_labels.update(contract.allowed_confidence_labels)
        if contract.lens not in INQUIRY_LENS_TYPES:
            invalid_lenses[inquiry_type] = contract.lens
        extras = sorted(set(contract.allowed_actions) - set(ALLOWED_INQUIRY_ACTIONS))
        if extras:
            invalid_actions[inquiry_type] = extras

    return {
        "runtime_decisioning_enabled": PHASE6_INQUIRY_RUNTIME_DECISIONING_ENABLED,
        "missing_inquiry_type_contracts": sorted(surface_inquiry_types - ml_inquiry_types),
        "extra_inquiry_type_contracts": sorted(ml_inquiry_types - surface_inquiry_types),
        "invalid_lenses": invalid_lenses,
        "invalid_actions": invalid_actions,
        "non_canonical_confidence_labels": sorted(confidence_labels - set(CONFIDENCE_VOCABULARY)),
        "missing_required_brief_fields": sorted(set(REQUIRED_INQUIRY_BRIEF_FIELDS) - brief_fields),
        "missing_required_finding_fields": sorted(set(REQUIRED_INQUIRY_FINDING_FIELDS) - finding_fields),
        "missing_required_brief_profile_fields": sorted(set(REQUIRED_BRIEF_PROFILE_FIELDS) - brief_profile_fields),
        "missing_required_quality_fields": sorted(set(REQUIRED_INQUIRY_QUALITY_FIELDS) - quality_fields),
        "missing_required_direct_answer_fields": sorted(set(REQUIRED_DIRECT_ANSWER_FIELDS) - direct_answer_fields),
        "missing_required_answerability_fields": sorted(set(REQUIRED_ANSWERABILITY_FIELDS) - answerability_fields),
        "missing_required_bounded_pattern_fields": sorted(
            set(REQUIRED_BOUNDED_PATTERN_FIELDS) - bounded_pattern_fields
        ),
        "missing_required_productization_metadata_fields": sorted(
            set(REQUIRED_PRODUCTIZATION_METADATA_FIELDS) - productization_fields
        ),
        "disallowed_output_fields_present": disallowed_present,
        "disallowed_brief_profile_fields_present": disallowed_profile_present,
        "disallowed_quality_fields_present": disallowed_quality_present,
        "disallowed_answerability_fields_present": disallowed_answerability_present,
        "disallowed_productization_fields_present": disallowed_productization_present,
        "missing_context_non_evidence_fields": sorted({"label", "text"} - context_fields),
        "missing_quality_dsd_mappings": missing_quality_dsd_mappings,
        "missing_profile_dsd_mappings": missing_profile_dsd_mappings,
        "missing_productization_dsd_mappings": missing_productization_dsd_mappings,
        "non_contract_answerability_classes": sorted(
            set(PHASE8_1_ALLOWED_ANSWERABILITY_CLASSES) - set(ANSWERABILITY_CLASSES)
        ),
        "extra_runtime_answerability_classes": sorted(
            set(ANSWERABILITY_CLASSES) - set(PHASE8_1_ALLOWED_ANSWERABILITY_CLASSES)
        ),
        "productization_version_mismatch": (
            productization_runtime_version
            if productization_runtime_version != PHASE8_1_PRODUCTIZATION_VERSION
            else None
        ),
        "missing_selected_domains_contract_fields": missing_selected_domains_contract_fields,
        "missing_phase8_dsd_mappings": missing_phase8_dsd_mappings,
        "missing_cross_domain_storage_fields": missing_cross_domain_storage_fields,
        "missing_phase8_pair_profiles": sorted(expected_pair_keys - registry_pair_keys),
        "extra_phase8_pair_profiles": sorted(registry_pair_keys - expected_pair_keys),
        "phase8_pair_profile_mismatches": phase8_pair_profile_mismatches,
        "phase8_pair_version_mismatches": phase8_pair_version_mismatches,
        "phase8_pair_domain_mismatches": phase8_pair_domain_mismatches,
        "phase8_pair_allowed_category_mismatches": phase8_pair_allowed_category_mismatches,
        "phase8_pair_forbidden_category_overlaps": phase8_pair_forbidden_category_overlaps,
        "missing_first_wave_domains": sorted(expected_first_wave_domains - first_wave_strategy_domains),
        "extra_first_wave_domains": sorted(first_wave_strategy_domains - expected_first_wave_domains),
        "missing_expert_domains": sorted(expected_domains - strategy_domains),
        "extra_expert_domains": sorted(strategy_domains - expected_domains),
        "missing_later_wave_domains": sorted(expected_later_wave_domains - later_wave_strategy_domains),
        "extra_later_wave_domains": sorted(later_wave_strategy_domains - expected_later_wave_domains),
        "later_wave_profile_mismatches": later_wave_profile_mismatches,
        "later_wave_invalid_versions": later_wave_invalid_versions,
        "later_wave_category_mismatches": later_wave_category_mismatches,
        "later_wave_missing_forbidden_tokens": later_wave_missing_forbidden_tokens,
    }


def validate_contract_payload(payload: Mapping[str, object]) -> list[str]:
    """Validate inquiry brief payload keys against the v1 bounded contract."""
    errors: list[str] = []
    if not isinstance(payload, Mapping):
        return ["payload_not_mapping"]

    payload_keys = set(payload.keys())
    missing = sorted(set(REQUIRED_INQUIRY_BRIEF_FIELDS) - payload_keys)
    disallowed = sorted(payload_keys & set(DISALLOWED_INQUIRY_OUTPUT_FIELDS))
    if missing:
        errors.append(f"missing_brief_fields:{','.join(missing)}")
    if disallowed:
        errors.append(f"disallowed_brief_fields:{','.join(disallowed)}")

    findings = payload.get("findings")
    findings_categories: list[str] = []
    finding_ids: set[str] = set()
    if isinstance(findings, list):
        for idx, finding in enumerate(findings):
            if not isinstance(finding, Mapping):
                errors.append(f"invalid_finding_mapping:{idx}")
                continue
            keys = set(finding.keys())
            missing_finding = sorted(set(REQUIRED_INQUIRY_FINDING_FIELDS) - keys)
            disallowed_finding = sorted(keys & set(DISALLOWED_INQUIRY_OUTPUT_FIELDS))
            if missing_finding:
                errors.append(f"missing_finding_fields:{idx}:{','.join(missing_finding)}")
            if disallowed_finding:
                errors.append(f"disallowed_finding_fields:{idx}:{','.join(disallowed_finding)}")
            finding_id = str(finding.get("finding_id") or "")
            if finding_id.strip():
                if finding_id in finding_ids:
                    errors.append(f"duplicate_finding_id:{idx}:{finding_id}")
                else:
                    finding_ids.add(finding_id)
            category = finding.get("finding_category")
            if not isinstance(category, str) or not category.strip():
                errors.append(f"invalid_finding_category:{idx}")
            else:
                findings_categories.append(category.strip())
            relevance_rank = finding.get("relevance_rank")
            if not isinstance(relevance_rank, int) or relevance_rank < 1:
                errors.append(f"invalid_relevance_rank:{idx}")
            relevance_reason = finding.get("relevance_reason")
            if not isinstance(relevance_reason, str) or not relevance_reason.strip():
                errors.append(f"invalid_relevance_reason:{idx}")
            confidence = str(finding.get("confidence_label") or "")
            if confidence and confidence not in CONFIDENCE_VOCABULARY:
                errors.append(f"invalid_confidence_label:{idx}:{confidence}")
            timeline_context = finding.get("timeline_context")
            if timeline_context is not None:
                if not isinstance(timeline_context, Mapping):
                    errors.append(f"invalid_timeline_context:{idx}")
                else:
                    timeline_keys = set(timeline_context.keys())
                    missing_timeline = sorted(set(REQUIRED_TIMELINE_CONTEXT_FIELDS) - timeline_keys)
                    if missing_timeline:
                        errors.append(f"missing_timeline_context_fields:{idx}:{','.join(missing_timeline)}")
                    claim_type = str(timeline_context.get("claim_type") or "")
                    if claim_type not in TIMELINE_CLAIM_TYPES:
                        errors.append(f"invalid_timeline_claim_type:{idx}:{claim_type or 'missing'}")

    limitation_items = payload.get("limitation_items")
    limitation_ids: set[str] = set()
    if limitation_items is not None:
        if not isinstance(limitation_items, list):
            errors.append("invalid_limitation_items")
        else:
            for idx, item in enumerate(limitation_items):
                if not isinstance(item, Mapping):
                    errors.append(f"invalid_limitation_item:{idx}")
                    continue
                keys = set(item.keys())
                missing_limitation = sorted(set(REQUIRED_LIMITATION_ITEM_FIELDS) - keys)
                if missing_limitation:
                    errors.append(f"missing_limitation_item_fields:{idx}:{','.join(missing_limitation)}")
                limitation_id = str(item.get("limitation_id") or "")
                if not limitation_id.strip():
                    errors.append(f"invalid_limitation_id:{idx}")
                elif limitation_id in limitation_ids:
                    errors.append(f"duplicate_limitation_id:{idx}:{limitation_id}")
                else:
                    limitation_ids.add(limitation_id)
                text = str(item.get("text") or "")
                if not text.strip():
                    errors.append(f"invalid_limitation_text:{idx}")

    quality_metadata = payload.get("quality_metadata")
    if not isinstance(quality_metadata, Mapping):
        errors.append("invalid_quality_metadata")
    else:
        quality_keys = set(quality_metadata.keys())
        missing_quality = sorted(set(REQUIRED_INQUIRY_QUALITY_FIELDS) - quality_keys)
        if missing_quality:
            errors.append(f"missing_quality_fields:{','.join(missing_quality)}")
        disallowed_quality = sorted(quality_keys & set(DISALLOWED_QUALITY_METADATA_FIELDS))
        if disallowed_quality:
            errors.append(f"disallowed_quality_fields:{','.join(disallowed_quality)}")

        findings_total = quality_metadata.get("findings_total")
        findings_with_evidence = quality_metadata.get("findings_with_evidence")
        evidence_coverage_ratio = quality_metadata.get("evidence_coverage_ratio")
        if not isinstance(findings_total, int) or findings_total < 0:
            errors.append("invalid_quality_findings_total")
        if not isinstance(findings_with_evidence, int) or findings_with_evidence < 0:
            errors.append("invalid_quality_findings_with_evidence")
        if (
            isinstance(findings_total, int)
            and isinstance(findings_with_evidence, int)
            and findings_with_evidence > findings_total
        ):
            errors.append("invalid_quality_findings_consistency")
        try:
            ratio = float(evidence_coverage_ratio)
        except (TypeError, ValueError):
            ratio = None
        if ratio is None or ratio < 0.0 or ratio > 1.0:
            errors.append("invalid_quality_evidence_coverage_ratio")

        for key in ("structure_gaps", "sparse_domains", "refine_guidance"):
            value = quality_metadata.get(key)
            if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
                errors.append(f"invalid_quality_{key}")

    direct_answer = payload.get("direct_answer")
    if not isinstance(direct_answer, Mapping):
        errors.append("invalid_direct_answer")
    else:
        direct_keys = set(direct_answer.keys())
        missing_direct = sorted(set(REQUIRED_DIRECT_ANSWER_FIELDS) - direct_keys)
        if missing_direct:
            errors.append(f"missing_direct_answer_fields:{','.join(missing_direct)}")
        disallowed_direct = sorted(direct_keys & set(DISALLOWED_ANSWERABILITY_FIELDS))
        if disallowed_direct:
            errors.append(f"disallowed_direct_answer_fields:{','.join(disallowed_direct)}")
        text = direct_answer.get("text")
        note = direct_answer.get("note")
        supporting_claims = direct_answer.get("supporting_claims")
        if not isinstance(text, str) or not text.strip():
            errors.append("invalid_direct_answer_text")
        if not isinstance(note, str) or not note.strip():
            errors.append("invalid_direct_answer_note")
        if not isinstance(supporting_claims, list) or any(
            not isinstance(item, str) or not item.strip() for item in supporting_claims
        ):
            errors.append("invalid_direct_answer_supporting_claims")

    answerability = payload.get("answerability")
    if not isinstance(answerability, Mapping):
        errors.append("invalid_answerability")
    else:
        answerability_keys = set(answerability.keys())
        missing_answerability = sorted(set(REQUIRED_ANSWERABILITY_FIELDS) - answerability_keys)
        if missing_answerability:
            errors.append(f"missing_answerability_fields:{','.join(missing_answerability)}")
        disallowed_answerability = sorted(answerability_keys & set(DISALLOWED_ANSWERABILITY_FIELDS))
        if disallowed_answerability:
            errors.append(f"disallowed_answerability_fields:{','.join(disallowed_answerability)}")
        classification = str(answerability.get("classification") or "")
        if classification not in PHASE8_1_ALLOWED_ANSWERABILITY_CLASSES:
            errors.append("invalid_answerability_classification")
        reason = answerability.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            errors.append("invalid_answerability_reason")
        supporting_count = answerability.get("supporting_finding_count")
        if not isinstance(supporting_count, int) or supporting_count < 0:
            errors.append("invalid_answerability_supporting_finding_count")
        try:
            answerability_ratio = float(answerability.get("evidence_coverage_ratio"))
        except (TypeError, ValueError):
            answerability_ratio = None
        if answerability_ratio is None or answerability_ratio < 0.0 or answerability_ratio > 1.0:
            errors.append("invalid_answerability_evidence_coverage_ratio")

    refine_guidance = payload.get("refine_guidance")
    if not isinstance(refine_guidance, list) or any(
        not isinstance(item, str) or not item.strip() for item in refine_guidance
    ):
        errors.append("invalid_refine_guidance")

    bounded_patterns = payload.get("bounded_patterns")
    if not isinstance(bounded_patterns, list):
        errors.append("invalid_bounded_patterns")
    else:
        for idx, item in enumerate(bounded_patterns):
            if not isinstance(item, Mapping):
                errors.append(f"invalid_bounded_pattern_mapping:{idx}")
                continue
            pattern_keys = set(item.keys())
            missing_pattern_fields = sorted(set(REQUIRED_BOUNDED_PATTERN_FIELDS) - pattern_keys)
            if missing_pattern_fields:
                errors.append(f"missing_bounded_pattern_fields:{idx}:{','.join(missing_pattern_fields)}")
            disallowed_pattern_fields = sorted(pattern_keys & set(DISALLOWED_ANSWERABILITY_FIELDS))
            if disallowed_pattern_fields:
                errors.append(f"disallowed_bounded_pattern_fields:{idx}:{','.join(disallowed_pattern_fields)}")
            category = item.get("pattern_category")
            note = item.get("note")
            count = item.get("finding_count")
            if not isinstance(category, str) or not category.strip():
                errors.append(f"invalid_bounded_pattern_category:{idx}")
            if category in FORBIDDEN_CROSS_DOMAIN_CLAIM_CATEGORIES:
                errors.append(f"forbidden_bounded_pattern_category:{idx}")
            if not isinstance(note, str) or not note.strip():
                errors.append(f"invalid_bounded_pattern_note:{idx}")
            if not isinstance(count, int) or count < 0:
                errors.append(f"invalid_bounded_pattern_count:{idx}")

    productization_metadata = payload.get("productization_metadata")
    if not isinstance(productization_metadata, Mapping):
        errors.append("invalid_productization_metadata")
    else:
        productization_keys = set(productization_metadata.keys())
        missing_productization_fields = sorted(set(REQUIRED_PRODUCTIZATION_METADATA_FIELDS) - productization_keys)
        if missing_productization_fields:
            errors.append(f"missing_productization_metadata_fields:{','.join(missing_productization_fields)}")
        disallowed_productization_fields = sorted(productization_keys & set(DISALLOWED_PRODUCTIZATION_METADATA_FIELDS))
        if disallowed_productization_fields:
            errors.append(f"disallowed_productization_metadata_fields:{','.join(disallowed_productization_fields)}")
        version = str(productization_metadata.get("version") or "")
        if version != PHASE8_1_PRODUCTIZATION_VERSION:
            errors.append("invalid_productization_version")
        before = productization_metadata.get("limitation_count_before")
        after = productization_metadata.get("limitation_count_after")
        removed = productization_metadata.get("limitation_redundancy_removed")
        present = productization_metadata.get("direct_answer_present")
        if not isinstance(before, int) or before < 0:
            errors.append("invalid_productization_limitation_count_before")
        if not isinstance(after, int) or after < 0:
            errors.append("invalid_productization_limitation_count_after")
        if not isinstance(removed, int) or removed < 0:
            errors.append("invalid_productization_limitation_redundancy_removed")
        if (
            isinstance(before, int)
            and isinstance(after, int)
            and isinstance(removed, int)
            and before - after != removed
        ):
            errors.append("invalid_productization_limitation_consistency")
        if not isinstance(present, bool):
            errors.append("invalid_productization_direct_answer_present")
        elif isinstance(direct_answer, Mapping):
            expected_present = bool(str(direct_answer.get("text") or "").strip())
            if present != expected_present:
                errors.append("invalid_productization_direct_answer_consistency")

    timeline_metadata = payload.get("timeline_metadata")
    if timeline_metadata is not None:
        if not isinstance(timeline_metadata, Mapping):
            errors.append("invalid_timeline_metadata")
        else:
            timeline_keys = set(timeline_metadata.keys())
            missing_timeline = sorted(set(REQUIRED_TIMELINE_METADATA_FIELDS) - timeline_keys)
            if missing_timeline:
                errors.append(f"missing_timeline_metadata_fields:{','.join(missing_timeline)}")
            coverage = timeline_metadata.get("comparison_coverage")
            if not isinstance(coverage, Mapping):
                errors.append("invalid_timeline_comparison_coverage")
            else:
                coverage_keys = set(coverage.keys())
                missing_coverage = sorted(set(REQUIRED_TIMELINE_COVERAGE_FIELDS) - coverage_keys)
                if missing_coverage:
                    errors.append(f"missing_timeline_coverage_fields:{','.join(missing_coverage)}")

    humanized_brief = payload.get("humanized_brief")
    if humanized_brief is not None:
        if not isinstance(humanized_brief, Mapping):
            errors.append("invalid_humanized_brief")
        else:
            metadata = humanized_brief.get("metadata")
            answer = humanized_brief.get("answer")
            sections = humanized_brief.get("sections")
            if not isinstance(metadata, Mapping):
                errors.append("invalid_humanized_metadata")
            else:
                missing_metadata = sorted(set(REQUIRED_HUMANIZED_METADATA_FIELDS) - set(metadata.keys()))
                if missing_metadata:
                    errors.append(f"missing_humanized_metadata_fields:{','.join(missing_metadata)}")
            if not isinstance(answer, Mapping):
                errors.append("invalid_humanized_answer")
            else:
                missing_answer = sorted(set(REQUIRED_HUMANIZED_ANSWER_FIELDS) - set(answer.keys()))
                if missing_answer:
                    errors.append(f"missing_humanized_answer_fields:{','.join(missing_answer)}")
            if not isinstance(sections, list):
                errors.append("invalid_humanized_sections")
            else:
                for idx, section in enumerate(sections):
                    if not isinstance(section, Mapping):
                        errors.append(f"invalid_humanized_section:{idx}")
                        continue
                    missing_section = sorted(set(REQUIRED_HUMANIZED_SECTION_FIELDS) - set(section.keys()))
                    if missing_section:
                        errors.append(f"missing_humanized_section_fields:{idx}:{','.join(missing_section)}")
                    blocks = section.get("blocks")
                    if not isinstance(blocks, list):
                        errors.append(f"invalid_humanized_section_blocks:{idx}")
                        continue
                    for block_idx, block in enumerate(blocks):
                        if not isinstance(block, Mapping):
                            errors.append(f"invalid_humanized_block:{idx}:{block_idx}")
                            continue
                        missing_block = sorted(set(REQUIRED_HUMANIZED_BLOCK_FIELDS) - set(block.keys()))
                        if missing_block:
                            errors.append(f"missing_humanized_block_fields:{idx}:{block_idx}:{','.join(missing_block)}")
                        for ref_key in ("source_finding_ids", "source_limitation_ids"):
                            refs = block.get(ref_key)
                            if not isinstance(refs, list) or any(
                                not isinstance(item, str) or not item.strip() for item in refs
                            ):
                                errors.append(f"invalid_humanized_block_traceability:{idx}:{block_idx}:{ref_key}")
                            elif ref_key == "source_finding_ids":
                                missing_refs = sorted(item for item in refs if item not in finding_ids)
                                if missing_refs:
                                    errors.append(
                                        f"invalid_humanized_block_finding_refs:{idx}:{block_idx}:{','.join(missing_refs)}"
                                    )
                            else:
                                missing_refs = sorted(item for item in refs if item not in limitation_ids)
                                if missing_refs:
                                    errors.append(
                                        f"invalid_humanized_block_limitation_refs:{idx}:{block_idx}:{','.join(missing_refs)}"
                                    )

    brief_profile = payload.get("brief_profile")
    if not isinstance(brief_profile, Mapping):
        errors.append("invalid_brief_profile")
    else:
        profile_keys = set(brief_profile.keys())
        missing_profile = sorted(set(REQUIRED_BRIEF_PROFILE_FIELDS) - profile_keys)
        if missing_profile:
            errors.append(f"missing_brief_profile_fields:{','.join(missing_profile)}")
        disallowed_profile = sorted(profile_keys & set(DISALLOWED_BRIEF_PROFILE_FIELDS))
        if disallowed_profile:
            errors.append(f"disallowed_brief_profile_fields:{','.join(disallowed_profile)}")
        if not isinstance(brief_profile.get("profile"), str) or not str(brief_profile.get("profile")).strip():
            errors.append("invalid_brief_profile_profile")
        if (
            not isinstance(brief_profile.get("profile_version"), str)
            or not str(brief_profile.get("profile_version")).strip()
        ):
            errors.append("invalid_brief_profile_profile_version")
        if not isinstance(brief_profile.get("strategy"), str) or not str(brief_profile.get("strategy")).strip():
            errors.append("invalid_brief_profile_strategy")
        if (
            not isinstance(brief_profile.get("strategy_version"), str)
            or not str(brief_profile.get("strategy_version")).strip()
        ):
            errors.append("invalid_brief_profile_strategy_version")
        domain = brief_profile.get("domain")
        if not isinstance(domain, str) or not domain.strip():
            errors.append("invalid_brief_profile_domain")
        if not isinstance(brief_profile.get("expert_mode"), bool):
            errors.append("invalid_brief_profile_expert_mode")
        elif (
            brief_profile.get("expert_mode")
            and str(brief_profile.get("domain") or "") not in ALL_EXPERT_DOMAINS
            and str(brief_profile.get("profile") or "") not in PHASE8_APPROVED_PAIR_PROFILE_NAMES
        ):
            errors.append("invalid_brief_profile_expert_domain")
        categories = brief_profile.get("finding_categories")
        if not isinstance(categories, list) or any(
            not isinstance(item, str) or not item.strip() for item in categories
        ):
            errors.append("invalid_brief_profile_finding_categories")
        else:
            normalized_categories = {item.strip() for item in categories}
            domain_value = str(brief_profile.get("domain") or "")
            if domain_value in LATER_WAVE_DOMAIN_METADATA_CONTRACTS:
                allowed_categories = set(LATER_WAVE_DOMAIN_METADATA_CONTRACTS[domain_value]["finding_categories"])
                if not normalized_categories.issubset(allowed_categories):
                    errors.append("invalid_later_wave_finding_categories")
            if findings_categories and not set(findings_categories).issubset(normalized_categories):
                errors.append("invalid_finding_category_scope")

            lens_value = str(payload.get("lens") or "")
            profile_name = str(brief_profile.get("profile") or "")
            pair_contract = next(
                (
                    contract
                    for contract in PHASE8_APPROVED_CROSS_DOMAIN_PAIR_CONTRACTS.values()
                    if str(contract["profile"]) == profile_name
                ),
                None,
            )
            if pair_contract is not None:
                if lens_value != "cross_domain":
                    errors.append("invalid_cross_domain_profile_lens")
                domains_raw = payload.get("domains")
                if not isinstance(domains_raw, list):
                    errors.append("invalid_selected_domains")
                else:
                    normalized_domains = sorted({str(item).strip() for item in domains_raw if str(item).strip()})
                    expected_domains = sorted(pair_contract["domains"])
                    if len(normalized_domains) != 2:
                        errors.append("invalid_selected_domains_length")
                    if normalized_domains != expected_domains:
                        errors.append("invalid_cross_domain_profile_domains")

                if str(brief_profile.get("profile_version") or "") != str(pair_contract["profile_version"]):
                    errors.append("invalid_cross_domain_profile_version")
                if str(brief_profile.get("strategy") or "") != str(pair_contract["strategy"]):
                    errors.append("invalid_cross_domain_profile_strategy")
                if str(brief_profile.get("strategy_version") or "") != str(pair_contract["strategy_version"]):
                    errors.append("invalid_cross_domain_strategy_version")
                if str(brief_profile.get("domain") or "") != "+".join(sorted(pair_contract["domains"])):
                    errors.append("invalid_cross_domain_profile_domain")

                allowed_cross_domain_categories = {
                    "co_occurrence_observation",
                    "temporal_alignment",
                    "trend_alignment",
                    "coverage_gap",
                    "structural_dependency_observation",
                    "inconsistency_flag",
                    "approved_pair_alignment_persistence",
                }
                forbidden_cross_domain_categories = set(FORBIDDEN_CROSS_DOMAIN_CLAIM_CATEGORIES)
                if not normalized_categories.issubset(allowed_cross_domain_categories):
                    errors.append("invalid_cross_domain_profile_categories")
                if normalized_categories & forbidden_cross_domain_categories:
                    errors.append("forbidden_cross_domain_profile_categories")
                if findings_categories and not set(findings_categories).issubset(allowed_cross_domain_categories):
                    errors.append("invalid_cross_domain_finding_categories")
    return errors


__all__ = [
    "PHASE6_INQUIRY_V1_NON_RUNTIME_DECLARATION",
    "PHASE8_CROSS_DOMAIN_NON_RUNTIME_DECLARATION",
    "PHASE8_1_PRODUCTIZATION_NON_RUNTIME_DECLARATION",
    "PHASE8_1_PRODUCTIZATION_VERSION",
    "PHASE6_INQUIRY_RUNTIME_DECISIONING_ENABLED",
    "PHASE6_INQUIRY_FORBIDDEN_RUNTIME_CAPABILITIES",
    "PHASE8_1_FORBIDDEN_RUNTIME_CAPABILITIES",
    "INQUIRY_LENS_TYPES",
    "ALLOWED_INQUIRY_ACTIONS",
    "FIRST_WAVE_EXPERT_DOMAINS",
    "LATER_WAVE_EXPERT_DOMAINS",
    "ALL_EXPERT_DOMAINS",
    "LATER_WAVE_DOMAIN_METADATA_CONTRACTS",
    "LATER_WAVE_FORBIDDEN_TOKEN_REQUIREMENTS",
    "REQUIRED_BRIEF_PROFILE_FIELDS",
    "REQUIRED_INQUIRY_QUALITY_FIELDS",
    "REQUIRED_DIRECT_ANSWER_FIELDS",
    "REQUIRED_ANSWERABILITY_FIELDS",
    "REQUIRED_BOUNDED_PATTERN_FIELDS",
    "REQUIRED_PRODUCTIZATION_METADATA_FIELDS",
    "PHASE8_1_ALLOWED_ANSWERABILITY_CLASSES",
    "REQUIRED_INQUIRY_BRIEF_FIELDS",
    "REQUIRED_INQUIRY_FINDING_FIELDS",
    "DISALLOWED_INQUIRY_OUTPUT_FIELDS",
    "DISALLOWED_BRIEF_PROFILE_FIELDS",
    "DISALLOWED_QUALITY_METADATA_FIELDS",
    "DISALLOWED_ANSWERABILITY_FIELDS",
    "DISALLOWED_PRODUCTIZATION_METADATA_FIELDS",
    "FORBIDDEN_CROSS_DOMAIN_CLAIM_CATEGORIES",
    "PHASE8_APPROVED_CROSS_DOMAIN_PAIR_CONTRACTS",
    "PHASE8_APPROVED_PAIR_PROFILE_NAMES",
    "PHASE8_REQUIRED_CROSS_DOMAIN_STORAGE_FIELDS",
    "PHASE8_REQUIRED_SELECTED_DOMAIN_CONTRACT_KEYS",
    "PHASE8_REQUIRED_CROSS_DOMAIN_PROFILE_DSD_KEYS",
    "InquiryBriefTypeContract",
    "InquiryFutureSupportContract",
    "InquiryDataRequirement",
    "INQUIRY_BRIEF_TYPE_CONTRACTS",
    "INQUIRY_FUTURE_SUPPORT_CONTRACTS",
    "INQUIRY_FUTURE_DATA_REQUIREMENTS",
    "get_inquiry_brief_contract",
    "list_inquiry_brief_contracts",
    "list_inquiry_future_support_contracts",
    "list_inquiry_future_data_requirements",
    "alignment_report",
    "validate_contract_payload",
]

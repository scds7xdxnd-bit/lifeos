"""Phase 6 inquiry ML contracts (scaffolding only, no runtime ML decisioning)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from lifeos.core.insights.contracts import CONFIDENCE_VOCABULARY

PHASE6_INQUIRY_V1_NON_RUNTIME_DECLARATION = (
    "Focused Inquiry v1 is deterministic and rules-only. ML is non-runtime and non-decisioning "
    "for inquiry brief generation, confidence labels, and evidence selection."
)
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

INQUIRY_LENS_TYPES = ("domain", "cross_domain")
ALLOWED_INQUIRY_ACTIONS = ("display", "refine_only")
FIRST_WAVE_EXPERT_DOMAINS = ("finance", "habits", "projects", "skills")
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
    "context_non_evidence",
    "uncertainty_note",
    "limits",
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
    from lifeos.core.insights.inquiry_strategies import FIRST_WAVE_DOMAIN_STRATEGIES
    from lifeos.core.ux.domain_surface_contracts import DOMAIN_SURFACE_CONTRACTS

    inquiry_surface = DOMAIN_SURFACE_CONTRACTS.get("insights:inquiry")
    surface_inquiry_types = set(inquiry_surface.insight_contracts if inquiry_surface else [])
    ml_inquiry_types = set(INQUIRY_BRIEF_TYPE_CONTRACTS.keys())

    brief_fields = {field.name for field in api_contracts.INQUIRY_BRIEF_ITEM.fields}
    finding_fields = {field.name for field in api_contracts.INQUIRY_FINDING_ITEM.fields}
    brief_profile_fields = {field.name for field in api_contracts.INQUIRY_BRIEF_PROFILE.fields}
    quality_fields = {field.name for field in api_contracts.INQUIRY_QUALITY_METADATA.fields}
    context_fields = {field.name for field in api_contracts.INQUIRY_CONTEXT_BLOCK.fields}
    disallowed_present = sorted((brief_fields | finding_fields) & set(DISALLOWED_INQUIRY_OUTPUT_FIELDS))
    disallowed_profile_present = sorted(brief_profile_fields & set(DISALLOWED_BRIEF_PROFILE_FIELDS))
    disallowed_quality_present = sorted(quality_fields & set(DISALLOWED_QUALITY_METADATA_FIELDS))

    dsd_mapping = DSD_FIELD_MAPPINGS.get("insights:inquiry", {})
    required_quality_dsd_keys = {"InquiryBriefItem.quality_metadata"} | {
        f"InquiryQualityMetadata.{field_name}" for field_name in REQUIRED_INQUIRY_QUALITY_FIELDS
    }
    required_profile_dsd_keys = {"InquiryBriefItem.brief_profile", "InquiryFindingItem.finding_category"} | {
        f"InquiryBriefProfile.{field_name}" for field_name in REQUIRED_BRIEF_PROFILE_FIELDS
    }
    missing_quality_dsd_mappings = sorted(required_quality_dsd_keys - set(dsd_mapping.keys()))
    missing_profile_dsd_mappings = sorted(required_profile_dsd_keys - set(dsd_mapping.keys()))

    strategy_domains = set(FIRST_WAVE_DOMAIN_STRATEGIES.keys())
    expected_domains = set(FIRST_WAVE_EXPERT_DOMAINS)

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
        "disallowed_output_fields_present": disallowed_present,
        "disallowed_brief_profile_fields_present": disallowed_profile_present,
        "disallowed_quality_fields_present": disallowed_quality_present,
        "missing_context_non_evidence_fields": sorted({"label", "text"} - context_fields),
        "missing_quality_dsd_mappings": missing_quality_dsd_mappings,
        "missing_profile_dsd_mappings": missing_profile_dsd_mappings,
        "missing_first_wave_domains": sorted(expected_domains - strategy_domains),
        "extra_first_wave_domains": sorted(strategy_domains - expected_domains),
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
            category = finding.get("finding_category")
            if not isinstance(category, str) or not category.strip():
                errors.append(f"invalid_finding_category:{idx}")
            else:
                findings_categories.append(category.strip())
            confidence = str(finding.get("confidence_label") or "")
            if confidence and confidence not in CONFIDENCE_VOCABULARY:
                errors.append(f"invalid_confidence_label:{idx}:{confidence}")

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
            brief_profile.get("expert_mode") and str(brief_profile.get("domain") or "") not in FIRST_WAVE_EXPERT_DOMAINS
        ):
            errors.append("invalid_brief_profile_expert_domain")
        categories = brief_profile.get("finding_categories")
        if not isinstance(categories, list) or any(
            not isinstance(item, str) or not item.strip() for item in categories
        ):
            errors.append("invalid_brief_profile_finding_categories")
        else:
            normalized_categories = {item.strip() for item in categories}
            if findings_categories and not set(findings_categories).issubset(normalized_categories):
                errors.append("invalid_finding_category_scope")
    return errors


__all__ = [
    "PHASE6_INQUIRY_V1_NON_RUNTIME_DECLARATION",
    "PHASE6_INQUIRY_RUNTIME_DECISIONING_ENABLED",
    "PHASE6_INQUIRY_FORBIDDEN_RUNTIME_CAPABILITIES",
    "INQUIRY_LENS_TYPES",
    "ALLOWED_INQUIRY_ACTIONS",
    "FIRST_WAVE_EXPERT_DOMAINS",
    "REQUIRED_BRIEF_PROFILE_FIELDS",
    "REQUIRED_INQUIRY_QUALITY_FIELDS",
    "REQUIRED_INQUIRY_BRIEF_FIELDS",
    "REQUIRED_INQUIRY_FINDING_FIELDS",
    "DISALLOWED_INQUIRY_OUTPUT_FIELDS",
    "DISALLOWED_BRIEF_PROFILE_FIELDS",
    "DISALLOWED_QUALITY_METADATA_FIELDS",
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

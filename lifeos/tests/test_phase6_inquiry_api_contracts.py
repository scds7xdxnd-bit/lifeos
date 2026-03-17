"""Phase 6 inquiry API contract freeze tests."""

from __future__ import annotations

import pytest

from lifeos.core.contracts.api_contracts import API_CONTRACTS, compute_schema_hash
from lifeos.core.contracts.api_dsd_mappings import DSD_FIELD_MAPPINGS

pytestmark = pytest.mark.unit


INQUIRY_CONTRACT_KEYS = {
    "inquiries.create.v1",
    "inquiries.list.v1",
    "inquiries.detail.v1",
    "inquiries.refine.v1",
    "inquiries.readiness.v1",
    "inquiries.feedback.v1",
}


def _contract_object_fields(contract_name: str) -> set[str]:
    contract = API_CONTRACTS[contract_name]
    fields: set[str] = set()
    for obj in contract.schema.objects:
        for field in obj.fields:
            fields.add(field.name)
    return fields


def test_inquiry_contracts_exist_with_expected_paths_and_methods():
    expected = {
        "inquiries.create.v1": ("POST", "/api/v1/inquiries"),
        "inquiries.list.v1": ("GET", "/api/v1/inquiries"),
        "inquiries.detail.v1": ("GET", "/api/v1/inquiries/<id>"),
        "inquiries.refine.v1": ("POST", "/api/v1/inquiries/<id>/refine"),
        "inquiries.readiness.v1": ("GET", "/api/v1/inquiries/readiness"),
        "inquiries.feedback.v1": ("POST", "/api/v1/inquiries/<id>/feedback"),
    }
    assert INQUIRY_CONTRACT_KEYS.issubset(API_CONTRACTS.keys())
    for name, (method, path) in expected.items():
        contract = API_CONTRACTS[name]
        assert contract.method == method
        assert contract.path == path
        assert contract.surface_key == "insights:inquiry"


def test_inquiry_routes_are_registered(app):
    rule_map: dict[str, set[str]] = {}
    for rule in app.url_map.iter_rules():
        methods = rule_map.setdefault(rule.rule, set())
        methods.update(rule.methods)
    base = "/api/v1/inquiries"
    base_slash = "/api/v1/inquiries/"
    assert any(path in rule_map for path in (base, base_slash))
    base_methods = rule_map.get(base) or rule_map.get(base_slash) or set()
    assert "GET" in base_methods
    assert "POST" in base_methods
    assert "GET" in (rule_map.get("/api/v1/inquiries/readiness") or set())
    assert "GET" in (rule_map.get("/api/v1/inquiries/<int:inquiry_id>") or set())
    assert "POST" in (rule_map.get("/api/v1/inquiries/<int:inquiry_id>/refine") or set())
    assert "POST" in (rule_map.get("/api/v1/inquiries/<int:inquiry_id>/feedback") or set())


def test_inquiry_contract_schema_hashes_match():
    for name in INQUIRY_CONTRACT_KEYS:
        contract = API_CONTRACTS[name]
        assert compute_schema_hash(contract.schema) == contract.schema_hash


def test_inquiry_contracts_include_canonical_brief_fields():
    fields = set()
    for name in INQUIRY_CONTRACT_KEYS:
        fields.update(_contract_object_fields(name))
    required = {
        "finding_id",
        "claim",
        "finding_category",
        "evidence_refs",
        "relevance_rank",
        "relevance_reason",
        "confidence_label",
        "uncertainty_note",
        "context_non_evidence",
        "direct_answer",
        "answerability",
        "limitation_items",
        "bounded_patterns",
        "productization_metadata",
        "brief_profile",
        "timeline_metadata",
        "humanized_brief",
        "quality_metadata",
        "profile",
        "profile_version",
        "strategy",
        "strategy_version",
        "expert_mode",
        "finding_categories",
        "timeline_context",
        "timeline_profile_id",
        "timeline_profile_version",
        "timeline_engine_version",
        "window_spec_token",
        "active_window_token",
        "comparison_window_token",
        "baseline_policy_token",
        "timezone_token",
        "evidence_manifest_hash",
        "timeline_summary_hash",
        "comparison_coverage",
        "canonical_brief_hash",
        "humanization_version",
        "humanized_brief_hash",
        "technical_view_available",
        "limitation_id",
        "text",
        "metadata",
        "sections",
        "block_id",
        "source_finding_ids",
        "source_limitation_ids",
        "section_id",
        "title",
        "blocks",
        "claim_type",
        "active_window_label",
        "comparison_label",
        "coverage_status",
        "prior_window_available",
        "baseline_windows_available",
        "baseline_windows_required",
        "recurrence_windows_available",
        "trend_windows_available",
        "findings_total",
        "findings_with_evidence",
        "evidence_coverage_ratio",
        "structure_gaps",
        "sparse_domains",
        "refine_guidance",
        "classification",
        "supporting_claims",
        "limitation_redundancy_removed",
        "ready",
        "blocking_reason",
        "next_step",
        "recent_window_days",
        "ready_domains",
        "ready_pairs",
        "domain_event_counts",
        "enabled",
        "invite_only",
        "max_users",
        "visible_domains",
        "enabled_pair_profiles",
        "technical_brief_enabled",
        "history_enabled",
        "inquiry_feedback_enabled",
        "hide_domain_crud",
        "require_data_readiness",
        "calendar_sync_enabled",
    }
    assert required.issubset(fields)


def test_inquiry_dsd_mappings_exist():
    mapping = DSD_FIELD_MAPPINGS.get("insights:inquiry")
    assert mapping
    required = {
        "InquiryFindingItem.finding_id",
        "InquiryFindingItem.claim",
        "InquiryFindingItem.evidence_refs",
        "InquiryFindingItem.relevance_rank",
        "InquiryFindingItem.relevance_reason",
        "InquiryFindingItem.confidence_label",
        "InquiryFindingItem.uncertainty_note",
        "InquiryBriefItem.context_non_evidence",
        "InquiryBriefItem.direct_answer",
        "InquiryBriefItem.answerability",
        "InquiryBriefItem.limitation_items",
        "InquiryBriefItem.bounded_patterns",
        "InquiryBriefItem.productization_metadata",
        "InquiryBriefItem.brief_profile",
        "InquiryBriefItem.timeline_metadata",
        "InquiryBriefItem.humanized_brief",
        "InquiryBriefItem.quality_metadata",
        "InquiryLimitationItem.limitation_id",
        "InquiryLimitationItem.text",
        "InquiryFindingItem.finding_category",
        "InquiryFindingItem.timeline_context",
        "InquiryBriefProfile.profile",
        "InquiryBriefProfile.profile_version",
        "InquiryBriefProfile.strategy",
        "InquiryBriefProfile.strategy_version",
        "InquiryBriefProfile.domain",
        "InquiryBriefProfile.expert_mode",
        "InquiryBriefProfile.finding_categories",
        "InquiryTimelineContext.claim_type",
        "InquiryTimelineContext.active_window_label",
        "InquiryTimelineContext.comparison_label",
        "InquiryTimelineContext.window_spec_token",
        "InquiryTimelineContext.baseline_policy_token",
        "InquiryTimelineContext.coverage_status",
        "InquiryTimelineMetadata.timeline_profile_id",
        "InquiryTimelineMetadata.timeline_profile_version",
        "InquiryTimelineMetadata.timeline_engine_version",
        "InquiryTimelineMetadata.window_spec_token",
        "InquiryTimelineMetadata.active_window_token",
        "InquiryTimelineMetadata.comparison_window_token",
        "InquiryTimelineMetadata.baseline_policy_token",
        "InquiryTimelineMetadata.timezone_token",
        "InquiryTimelineMetadata.evidence_manifest_hash",
        "InquiryTimelineMetadata.timeline_summary_hash",
        "InquiryTimelineMetadata.comparison_coverage",
        "InquiryHumanizedMetadata.canonical_brief_hash",
        "InquiryHumanizedMetadata.humanization_version",
        "InquiryHumanizedMetadata.humanized_brief_hash",
        "InquiryHumanizedMetadata.technical_view_available",
        "InquiryHumanizedAnswer.text",
        "InquiryHumanizedAnswer.source_finding_ids",
        "InquiryHumanizedAnswer.source_limitation_ids",
        "InquiryHumanizedBlock.block_id",
        "InquiryHumanizedBlock.text",
        "InquiryHumanizedBlock.source_finding_ids",
        "InquiryHumanizedBlock.source_limitation_ids",
        "InquiryHumanizedBlock.evidence_refs",
        "InquiryHumanizedBlock.confidence_label",
        "InquiryHumanizedSection.section_id",
        "InquiryHumanizedSection.title",
        "InquiryHumanizedSection.blocks",
        "InquiryHumanizedBrief.metadata",
        "InquiryHumanizedBrief.answer",
        "InquiryHumanizedBrief.sections",
        "InquiryReadinessItem.ready",
        "InquiryReadinessItem.blocking_reason",
        "InquiryReadinessItem.next_step",
        "InquiryReadinessItem.recent_window_days",
        "InquiryReadinessItem.as_of_ts",
        "InquiryReadinessItem.ready_domains",
        "InquiryReadinessItem.ready_pairs",
        "InquiryReadinessItem.domain_event_counts",
        "InquiryAlphaFlagsItem.enabled",
        "InquiryAlphaFlagsItem.invite_only",
        "InquiryAlphaFlagsItem.max_users",
        "InquiryAlphaFlagsItem.visible_domains",
        "InquiryAlphaFlagsItem.enabled_pair_profiles",
        "InquiryAlphaFlagsItem.technical_brief_enabled",
        "InquiryAlphaFlagsItem.history_enabled",
        "InquiryAlphaFlagsItem.inquiry_feedback_enabled",
        "InquiryAlphaFlagsItem.hide_domain_crud",
        "InquiryAlphaFlagsItem.require_data_readiness",
        "InquiryAlphaFlagsItem.calendar_sync_enabled",
        "Response.feedback_id",
        "Response.readiness",
        "Response.alpha",
        "InquiryTimelineCoverage.prior_window_available",
        "InquiryTimelineCoverage.baseline_windows_available",
        "InquiryTimelineCoverage.baseline_windows_required",
        "InquiryTimelineCoverage.recurrence_windows_available",
        "InquiryTimelineCoverage.trend_windows_available",
        "InquiryQualityMetadata.findings_total",
        "InquiryQualityMetadata.findings_with_evidence",
        "InquiryQualityMetadata.evidence_coverage_ratio",
        "InquiryQualityMetadata.structure_gaps",
        "InquiryQualityMetadata.sparse_domains",
        "InquiryQualityMetadata.refine_guidance",
        "InquiryDirectAnswer.text",
        "InquiryAnswerability.classification",
        "InquiryProductizationMetadata.limitation_redundancy_removed",
    }
    assert required.issubset(mapping.keys())

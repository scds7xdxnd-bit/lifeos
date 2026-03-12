"""Phase 6 inquiry ML contract scaffolding checks."""

from __future__ import annotations

import pytest

from lifeos.core.insights.ml.phase6_inquiry_contracts import (
    ALLOWED_INQUIRY_ACTIONS,
    PHASE8_1_ALLOWED_ANSWERABILITY_CLASSES,
    PHASE8_1_PRODUCTIZATION_NON_RUNTIME_DECLARATION,
    PHASE8_1_PRODUCTIZATION_VERSION,
    FIRST_WAVE_EXPERT_DOMAINS,
    LATER_WAVE_EXPERT_DOMAINS,
    PHASE8_APPROVED_CROSS_DOMAIN_PAIR_CONTRACTS,
    PHASE8_CROSS_DOMAIN_NON_RUNTIME_DECLARATION,
    INQUIRY_FUTURE_DATA_REQUIREMENTS,
    INQUIRY_FUTURE_SUPPORT_CONTRACTS,
    PHASE6_INQUIRY_RUNTIME_DECISIONING_ENABLED,
    PHASE6_INQUIRY_V1_NON_RUNTIME_DECLARATION,
    alignment_report,
    validate_contract_payload,
)

pytestmark = pytest.mark.unit


def _productized_fields(*, answerability: str = "partial_answerable") -> dict[str, object]:
    return {
        "direct_answer": {
            "text": "Bounded direct answer derived from existing findings.",
            "supporting_claims": ["Primary finding claim."],
            "note": "Derived only from evidence-bounded findings; no new inference classes were introduced.",
        },
        "answerability": {
            "classification": answerability,
            "reason": "Evidence coverage and finding support are bounded for this scope.",
            "evidence_coverage_ratio": 0.75,
            "supporting_finding_count": 1,
        },
        "refine_guidance": ["Narrow scope to improve directness. Likely gain: improve answerability clarity."],
        "bounded_patterns": [
            {
                "pattern_category": "coverage_gap",
                "finding_count": 1,
                "note": "Descriptive pattern synthesized from canonical findings only.",
            }
        ],
        "productization_metadata": {
            "version": PHASE8_1_PRODUCTIZATION_VERSION,
            "limitation_count_before": 1,
            "limitation_count_after": 1,
            "limitation_redundancy_removed": 0,
            "direct_answer_present": True,
        },
    }


def test_phase6_inquiry_ml_alignment_report_is_clean():
    report = alignment_report()
    assert report["runtime_decisioning_enabled"] is False
    assert report["missing_inquiry_type_contracts"] == []
    assert report["extra_inquiry_type_contracts"] == []
    assert report["invalid_lenses"] == {}
    assert report["invalid_actions"] == {}
    assert report["non_canonical_confidence_labels"] == []
    assert report["missing_required_brief_fields"] == []
    assert report["missing_required_finding_fields"] == []
    assert report["missing_required_brief_profile_fields"] == []
    assert report["missing_required_quality_fields"] == []
    assert report["missing_required_direct_answer_fields"] == []
    assert report["missing_required_answerability_fields"] == []
    assert report["missing_required_bounded_pattern_fields"] == []
    assert report["missing_required_productization_metadata_fields"] == []
    assert report["disallowed_output_fields_present"] == []
    assert report["disallowed_brief_profile_fields_present"] == []
    assert report["disallowed_quality_fields_present"] == []
    assert report["disallowed_answerability_fields_present"] == []
    assert report["disallowed_productization_fields_present"] == []
    assert report["missing_context_non_evidence_fields"] == []
    assert report["missing_quality_dsd_mappings"] == []
    assert report["missing_profile_dsd_mappings"] == []
    assert report["missing_productization_dsd_mappings"] == []
    assert report["non_contract_answerability_classes"] == []
    assert report["extra_runtime_answerability_classes"] == []
    assert report["productization_version_mismatch"] is None
    assert report["missing_selected_domains_contract_fields"] == []
    assert report["missing_phase8_dsd_mappings"] == []
    assert report["missing_cross_domain_storage_fields"] == []
    assert report["missing_phase8_pair_profiles"] == []
    assert report["extra_phase8_pair_profiles"] == []
    assert report["phase8_pair_profile_mismatches"] == {}
    assert report["phase8_pair_version_mismatches"] == {}
    assert report["phase8_pair_domain_mismatches"] == {}
    assert report["phase8_pair_allowed_category_mismatches"] == {}
    assert report["phase8_pair_forbidden_category_overlaps"] == {}
    assert report["missing_first_wave_domains"] == []
    assert report["extra_first_wave_domains"] == []
    assert report["missing_expert_domains"] == []
    assert report["extra_expert_domains"] == []
    assert report["missing_later_wave_domains"] == []
    assert report["extra_later_wave_domains"] == []
    assert report["later_wave_profile_mismatches"] == {}
    assert report["later_wave_invalid_versions"] == {}
    assert report["later_wave_category_mismatches"] == {}
    assert report["later_wave_missing_forbidden_tokens"] == {}


def test_phase6_inquiry_ml_runtime_boundary_is_explicit():
    assert PHASE6_INQUIRY_RUNTIME_DECISIONING_ENABLED is False
    assert "non-runtime" in PHASE6_INQUIRY_V1_NON_RUNTIME_DECLARATION.lower()
    assert "deterministic" in PHASE6_INQUIRY_V1_NON_RUNTIME_DECLARATION.lower()
    assert "non-runtime" in PHASE8_CROSS_DOMAIN_NON_RUNTIME_DECLARATION.lower()
    assert "deterministic" in PHASE8_CROSS_DOMAIN_NON_RUNTIME_DECLARATION.lower()
    assert "non-runtime" in PHASE8_1_PRODUCTIZATION_NON_RUNTIME_DECLARATION.lower()
    assert "deterministic" in PHASE8_1_PRODUCTIZATION_NON_RUNTIME_DECLARATION.lower()
    assert ALLOWED_INQUIRY_ACTIONS == ("display", "refine_only")
    assert set(PHASE8_1_ALLOWED_ANSWERABILITY_CLASSES) == {
        "strong_answerable",
        "partial_answerable",
        "weak_answerable",
    }
    assert set(FIRST_WAVE_EXPERT_DOMAINS) == {"finance", "habits", "projects", "skills"}
    assert set(LATER_WAVE_EXPERT_DOMAINS) == {"journal", "relationships", "health"}
    assert set(PHASE8_APPROVED_CROSS_DOMAIN_PAIR_CONTRACTS) == {
        "finance__habits",
        "projects__skills",
        "habits__journal",
        "habits__health",
        "calendar__projects",
        "journal__relationships",
    }


def test_phase6_inquiry_ml_payload_validator_enforces_bounds():
    valid_payload = {
        "summary": "Scoped inquiry summary.",
        "findings": [
            {
                "claim": "Finance has records in range.",
                "finding_category": "cashflow_coverage",
                "evidence_refs": [{"source_kind": "event_record"}],
                "relevance_rank": 1,
                "relevance_reason": "Moderate relevance: claim is supported by canonical evidence.",
                "confidence_label": "informational",
                "uncertainty_note": "Bounded to selected timeframe.",
                "source_domains": ["finance"],
            }
        ],
        "context_non_evidence": {"label": "Context (not evidence)", "text": "", "note": ""},
        "uncertainty_note": "Bounded evidence window.",
        "limits": [],
        "question": "What changed in finance this week?",
        "lens": "domain",
        "domains": ["finance"],
        "timeframe": {"start": "2026-01-01", "end": "2026-01-31"},
        "as_of_ts": "2026-01-31T23:59:59",
        "generated_at": "2026-01-31T23:59:59",
        **_productized_fields(),
        "brief_profile": {
            "profile": "finance_domain_expert_brief",
            "profile_version": "1.0.0",
            "strategy": "finance_rules_v1",
            "strategy_version": "1.0.0",
            "domain": "finance",
            "expert_mode": True,
            "finding_categories": ["cashflow_coverage"],
        },
        "quality_metadata": {
            "findings_total": 1,
            "findings_with_evidence": 1,
            "evidence_coverage_ratio": 1.0,
            "structure_gaps": [],
            "sparse_domains": [],
            "refine_guidance": ["Current brief structure has sufficient evidence coverage for this scope."],
        },
    }
    assert validate_contract_payload(valid_payload) == []

    invalid_payload = dict(valid_payload)
    invalid_payload["answer"] = "auto-generated answer"
    invalid_payload["findings"] = [dict(valid_payload["findings"][0], confidence_score=0.99)]
    errors = validate_contract_payload(invalid_payload)
    assert any(error.startswith("disallowed_brief_fields") for error in errors)
    assert any(error.startswith("disallowed_finding_fields") for error in errors)


def test_phase6_inquiry_ml_payload_validator_rejects_invalid_quality_metadata():
    payload = {
        "summary": "Scoped inquiry summary.",
        "findings": [
            {
                "claim": "Finance has records in range.",
                "evidence_refs": [{"source_kind": "event_record"}],
                "confidence_label": "informational",
                "uncertainty_note": "Bounded to selected timeframe.",
                "source_domains": ["finance"],
            }
        ],
        "context_non_evidence": {"label": "Context (not evidence)", "text": "", "note": ""},
        "uncertainty_note": "Bounded evidence window.",
        "limits": [],
        "question": "What changed in finance this week?",
        "lens": "domain",
        "domains": ["finance"],
        "timeframe": {"start": "2026-01-01", "end": "2026-01-31"},
        "as_of_ts": "2026-01-31T23:59:59",
        "generated_at": "2026-01-31T23:59:59",
        **_productized_fields(),
        "quality_metadata": {
            "findings_total": 1,
            "findings_with_evidence": 2,
            "evidence_coverage_ratio": 1.2,
            "structure_gaps": "not-a-list",
            "sparse_domains": [],
            "refine_guidance": [],
            "confidence_score": 0.97,
        },
    }
    errors = validate_contract_payload(payload)
    assert "invalid_quality_findings_consistency" in errors
    assert "invalid_quality_evidence_coverage_ratio" in errors
    assert "invalid_quality_structure_gaps" in errors
    assert any(error.startswith("disallowed_quality_fields") for error in errors)


def test_phase6_inquiry_ml_payload_validator_rejects_invalid_brief_profile():
    payload = {
        "summary": "Scoped inquiry summary.",
        "findings": [
            {
                "claim": "Finance has records in range.",
                "finding_category": "cashflow_coverage",
                "evidence_refs": [{"source_kind": "event_record"}],
                "relevance_rank": 1,
                "relevance_reason": "Moderate relevance: claim is supported by canonical evidence.",
                "confidence_label": "informational",
                "uncertainty_note": "Bounded to selected timeframe.",
                "source_domains": ["finance"],
            }
        ],
        "context_non_evidence": {"label": "Context (not evidence)", "text": "", "note": ""},
        "uncertainty_note": "Bounded evidence window.",
        "limits": [],
        "question": "What changed in finance this week?",
        "lens": "domain",
        "domains": ["finance"],
        "timeframe": {"start": "2026-01-01", "end": "2026-01-31"},
        "as_of_ts": "2026-01-31T23:59:59",
        "generated_at": "2026-01-31T23:59:59",
        **_productized_fields(),
        "quality_metadata": {
            "findings_total": 1,
            "findings_with_evidence": 1,
            "evidence_coverage_ratio": 1.0,
            "structure_gaps": [],
            "sparse_domains": [],
            "refine_guidance": [],
        },
        "brief_profile": {
            "profile": "other_profile",
            "profile_version": "1.0.0",
            "strategy": "other_rules",
            "strategy_version": "1.0.0",
            "domain": "calendar",
            "expert_mode": True,
            "finding_categories": ["other_category"],
            "confidence_score": 0.91,
        },
    }
    errors = validate_contract_payload(payload)
    assert any(error.startswith("disallowed_brief_profile_fields") for error in errors)
    assert "invalid_brief_profile_expert_domain" in errors
    assert "invalid_finding_category_scope" in errors


def test_phase6_inquiry_ml_payload_validator_accepts_later_wave_profile():
    payload = {
        "summary": "Scoped inquiry summary.",
        "findings": [
            {
                "claim": "Journal evidence includes explicit entry cadence signals in this timeframe.",
                "finding_category": "reflection_cadence",
                "evidence_refs": [{"source_kind": "event_record"}],
                "relevance_rank": 1,
                "relevance_reason": "High relevance: claim matches inquiry wording and has canonical evidence.",
                "confidence_label": "informational",
                "uncertainty_note": "Bounded to selected timeframe.",
                "source_domains": ["journal"],
            }
        ],
        "context_non_evidence": {"label": "Context (not evidence)", "text": "", "note": ""},
        "uncertainty_note": "Bounded evidence window.",
        "limits": [],
        "question": "What happened in journal this week?",
        "lens": "domain",
        "domains": ["journal"],
        "timeframe": {"start": "2026-01-01", "end": "2026-01-31"},
        "as_of_ts": "2026-01-31T23:59:59",
        "generated_at": "2026-01-31T23:59:59",
        **_productized_fields(),
        "brief_profile": {
            "profile": "focused_inquiry_journal_expert_brief",
            "profile_version": "1.0.0",
            "strategy": "journal_rules_v1",
            "strategy_version": "1.0.0",
            "domain": "journal",
            "expert_mode": True,
            "finding_categories": ["reflection_cadence", "mood_tag_pattern", "evidence_gap"],
        },
        "quality_metadata": {
            "findings_total": 1,
            "findings_with_evidence": 1,
            "evidence_coverage_ratio": 1.0,
            "structure_gaps": [],
            "sparse_domains": [],
            "refine_guidance": [],
        },
    }
    assert validate_contract_payload(payload) == []


def test_phase6_inquiry_ml_payload_validator_accepts_phase8_cross_domain_profile():
    payload = {
        "summary": "Cross-domain scope summary.",
        "findings": [
            {
                "claim": "Cross-domain evidence shows observed alignment between selected records.",
                "finding_category": "co_occurrence_observation",
                "evidence_refs": [{"source_kind": "event_record"}],
                "relevance_rank": 1,
                "relevance_reason": "High relevance: claim matches inquiry wording and has canonical evidence.",
                "confidence_label": "needs_review",
                "uncertainty_note": "Bounded to selected timeframe and explicit scope.",
                "source_domains": ["finance", "habits"],
            }
        ],
        "context_non_evidence": {"label": "Context (not evidence)", "text": "", "note": ""},
        "uncertainty_note": "Bounded evidence window.",
        "limits": [],
        "question": "How do finance and habits align?",
        "lens": "cross_domain",
        "domains": ["finance", "habits"],
        "timeframe": {"start": "2026-01-01", "end": "2026-01-31"},
        "as_of_ts": "2026-01-31T23:59:59",
        "generated_at": "2026-01-31T23:59:59",
        **_productized_fields(answerability="weak_answerable"),
        "brief_profile": {
            "profile": "finance_habits_v1",
            "profile_version": "1.0.0",
            "strategy": "cross_domain_pair_rules_v1",
            "strategy_version": "1.0.0",
            "domain": "finance+habits",
            "expert_mode": True,
            "finding_categories": ["co_occurrence_observation", "coverage_gap"],
        },
        "quality_metadata": {
            "findings_total": 1,
            "findings_with_evidence": 1,
            "evidence_coverage_ratio": 1.0,
            "structure_gaps": [],
            "sparse_domains": [],
            "refine_guidance": [],
        },
    }
    assert validate_contract_payload(payload) == []


def test_phase6_inquiry_ml_payload_validator_rejects_phase8_cross_domain_contract_violations():
    payload = {
        "summary": "Cross-domain scope summary.",
        "findings": [
            {
                "claim": "Cross-domain evidence shows observed alignment between selected records.",
                "finding_category": "psychological_interpretation",
                "evidence_refs": [{"source_kind": "event_record"}],
                "relevance_rank": 1,
                "relevance_reason": "Lower relevance: limited direct wording alignment or sparse canonical evidence.",
                "confidence_label": "needs_review",
                "uncertainty_note": "Bounded to selected timeframe and explicit scope.",
                "source_domains": ["finance", "habits"],
            }
        ],
        "context_non_evidence": {"label": "Context (not evidence)", "text": "", "note": ""},
        "uncertainty_note": "Bounded evidence window.",
        "limits": [],
        "question": "How do finance and habits align?",
        "lens": "cross_domain",
        "domains": ["finance", "projects"],
        "timeframe": {"start": "2026-01-01", "end": "2026-01-31"},
        "as_of_ts": "2026-01-31T23:59:59",
        "generated_at": "2026-01-31T23:59:59",
        **_productized_fields(answerability="weak_answerable"),
        "brief_profile": {
            "profile": "finance_habits_v1",
            "profile_version": "1.0.0",
            "strategy": "cross_domain_pair_rules_v1",
            "strategy_version": "1.0.0",
            "domain": "finance+projects",
            "expert_mode": True,
            "finding_categories": ["psychological_interpretation"],
        },
        "quality_metadata": {
            "findings_total": 1,
            "findings_with_evidence": 1,
            "evidence_coverage_ratio": 1.0,
            "structure_gaps": [],
            "sparse_domains": [],
            "refine_guidance": [],
        },
    }
    errors = validate_contract_payload(payload)
    assert "invalid_cross_domain_profile_domains" in errors
    assert "invalid_cross_domain_profile_domain" in errors
    assert "invalid_cross_domain_profile_categories" in errors
    assert "forbidden_cross_domain_profile_categories" in errors
    assert "invalid_cross_domain_finding_categories" in errors


def test_phase6_inquiry_ml_payload_validator_rejects_score_like_productization_semantics():
    payload = {
        "summary": "Scoped inquiry summary.",
        "findings": [
            {
                "claim": "Finance has records in range.",
                "finding_category": "cashflow_coverage",
                "evidence_refs": [{"source_kind": "event_record"}],
                "relevance_rank": 1,
                "relevance_reason": "Moderate relevance: claim is supported by canonical evidence.",
                "confidence_label": "informational",
                "uncertainty_note": "Bounded to selected timeframe.",
                "source_domains": ["finance"],
            }
        ],
        "direct_answer": {
            "text": "Bounded direct answer derived from existing findings.",
            "supporting_claims": ["Primary finding claim."],
            "note": "Derived only from evidence-bounded findings.",
            "probability": 0.91,
        },
        "answerability": {
            "classification": "partial_answerable",
            "reason": "Evidence coverage and finding support are bounded for this scope.",
            "evidence_coverage_ratio": 0.75,
            "supporting_finding_count": 1,
            "helpfulness_score": 0.88,
        },
        "context_non_evidence": {"label": "Context (not evidence)", "text": "", "note": ""},
        "uncertainty_note": "Bounded evidence window.",
        "limits": [],
        "refine_guidance": ["Narrow scope to improve directness. Likely gain: improve answerability clarity."],
        "bounded_patterns": [
            {
                "pattern_category": "coverage_gap",
                "finding_count": 1,
                "note": "Descriptive pattern synthesized from canonical findings only.",
            }
        ],
        "productization_metadata": {
            "version": PHASE8_1_PRODUCTIZATION_VERSION,
            "limitation_count_before": 1,
            "limitation_count_after": 1,
            "limitation_redundancy_removed": 0,
            "direct_answer_present": True,
            "helpfulness_score": 0.91,
        },
        "question": "What changed in finance this week?",
        "lens": "domain",
        "domains": ["finance"],
        "timeframe": {"start": "2026-01-01", "end": "2026-01-31"},
        "as_of_ts": "2026-01-31T23:59:59",
        "generated_at": "2026-01-31T23:59:59",
        "brief_profile": {
            "profile": "finance_domain_expert_brief",
            "profile_version": "1.0.0",
            "strategy": "finance_rules_v1",
            "strategy_version": "1.0.0",
            "domain": "finance",
            "expert_mode": True,
            "finding_categories": ["cashflow_coverage"],
        },
        "quality_metadata": {
            "findings_total": 1,
            "findings_with_evidence": 1,
            "evidence_coverage_ratio": 1.0,
            "structure_gaps": [],
            "sparse_domains": [],
            "refine_guidance": [],
        },
    }
    errors = validate_contract_payload(payload)
    assert any(error.startswith("disallowed_direct_answer_fields") for error in errors)
    assert any(error.startswith("disallowed_answerability_fields") for error in errors)
    assert any(error.startswith("disallowed_productization_metadata_fields") for error in errors)


def test_phase6_inquiry_ml_future_scaffolds_remain_non_runtime():
    assert all(not contract.runtime_allowed_in_v1 for contract in INQUIRY_FUTURE_SUPPORT_CONTRACTS.values())
    assert set(INQUIRY_FUTURE_DATA_REQUIREMENTS.keys()) == {
        "temporal_features",
        "cross_domain_cooccurrence_features",
        "inquiry_refinement_history",
        "evidence_coverage_uncertainty_structure",
    }

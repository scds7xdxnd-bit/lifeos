"""Phase 6 inquiry ML contract scaffolding checks."""

from __future__ import annotations

import pytest

from lifeos.core.insights.ml.phase6_inquiry_contracts import (
    ALLOWED_INQUIRY_ACTIONS,
    INQUIRY_FUTURE_DATA_REQUIREMENTS,
    INQUIRY_FUTURE_SUPPORT_CONTRACTS,
    PHASE6_INQUIRY_RUNTIME_DECISIONING_ENABLED,
    PHASE6_INQUIRY_V1_NON_RUNTIME_DECLARATION,
    alignment_report,
    validate_contract_payload,
)

pytestmark = pytest.mark.unit


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
    assert report["disallowed_output_fields_present"] == []
    assert report["missing_context_non_evidence_fields"] == []


def test_phase6_inquiry_ml_runtime_boundary_is_explicit():
    assert PHASE6_INQUIRY_RUNTIME_DECISIONING_ENABLED is False
    assert "non-runtime" in PHASE6_INQUIRY_V1_NON_RUNTIME_DECLARATION.lower()
    assert "deterministic" in PHASE6_INQUIRY_V1_NON_RUNTIME_DECLARATION.lower()
    assert ALLOWED_INQUIRY_ACTIONS == ("display", "refine_only")


def test_phase6_inquiry_ml_payload_validator_enforces_bounds():
    valid_payload = {
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
    }
    assert validate_contract_payload(valid_payload) == []

    invalid_payload = dict(valid_payload)
    invalid_payload["answer"] = "auto-generated answer"
    invalid_payload["findings"] = [dict(valid_payload["findings"][0], confidence_score=0.99)]
    errors = validate_contract_payload(invalid_payload)
    assert any(error.startswith("disallowed_brief_fields") for error in errors)
    assert any(error.startswith("disallowed_finding_fields") for error in errors)


def test_phase6_inquiry_ml_future_scaffolds_remain_non_runtime():
    assert all(not contract.runtime_allowed_in_v1 for contract in INQUIRY_FUTURE_SUPPORT_CONTRACTS.values())
    assert set(INQUIRY_FUTURE_DATA_REQUIREMENTS.keys()) == {
        "temporal_features",
        "cross_domain_cooccurrence_features",
        "inquiry_refinement_history",
        "evidence_coverage_uncertainty_structure",
    }

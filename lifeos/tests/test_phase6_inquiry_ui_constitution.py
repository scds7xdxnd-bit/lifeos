"""Phase 6 inquiry UI constitutional backend guard tests."""

from __future__ import annotations

import pytest

from lifeos.core.contracts.api_contracts import API_CONTRACTS
from lifeos.core.ux.domain_surface_contracts import DOMAIN_SURFACE_CONTRACTS

pytestmark = pytest.mark.unit


def _contract_field_names(name: str) -> set[str]:
    contract = API_CONTRACTS[name]
    names = {field.name for field in contract.schema.fields}
    for obj in contract.schema.objects:
        for field in obj.fields:
            names.add(field.name)
    return names


def test_inquiry_surface_contract_matches_read_first_structure():
    surface = DOMAIN_SURFACE_CONTRACTS.get("insights:inquiry")
    assert surface is not None
    assert surface.primary_question == "What exactly am I trying to understand right now?"
    assert surface.primary_action == "Generate brief"
    assert any(section.name == "Inquiry brief findings" for section in surface.read_only_sections)
    assert any(section.name == "Inquiry scope form" for section in surface.editable_sections)


def test_inquiry_contracts_expose_evidence_and_confidence_fields():
    names = set()
    for key in (
        "inquiries.create.v1",
        "inquiries.detail.v1",
        "inquiries.refine.v1",
        "inquiries.readiness.v1",
        "inquiries.feedback.v1",
    ):
        names.update(_contract_field_names(key))
    assert {
        "claim",
        "finding_category",
        "evidence_refs",
        "relevance_rank",
        "relevance_reason",
        "confidence_label",
        "uncertainty_note",
        "direct_answer",
        "answerability",
        "brief_profile",
        "profile",
        "profile_version",
        "strategy",
        "strategy_version",
        "expert_mode",
        "finding_categories",
        "bounded_patterns",
        "productization_metadata",
        "quality_metadata",
        "findings_total",
        "findings_with_evidence",
        "evidence_coverage_ratio",
        "structure_gaps",
        "sparse_domains",
        "refine_guidance",
        "ready",
        "blocking_reason",
        "next_step",
        "visible_domains",
        "enabled_pair_profiles",
        "feedback_id",
    }.issubset(names)


def test_inquiry_contracts_do_not_expose_chat_transcript_fields():
    banned = {"chat_messages", "assistant_reply", "conversation_id", "transcript", "prompt"}
    names = set()
    for key in (
        "inquiries.create.v1",
        "inquiries.list.v1",
        "inquiries.detail.v1",
        "inquiries.refine.v1",
        "inquiries.readiness.v1",
        "inquiries.feedback.v1",
    ):
        names.update(_contract_field_names(key))
    assert names.isdisjoint(banned)

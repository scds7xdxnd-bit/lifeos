"""Phase 3a.5 domain surface contract tests (Tier 0)."""

from __future__ import annotations

import pytest

from lifeos.core.ux.domain_surface_contracts import DOMAIN_SURFACE_CONTRACTS

pytestmark = pytest.mark.unit


def test_tier0_surface_contracts_present():
    required = {"profile:settings", "journal:entries"}
    assert required.issubset(DOMAIN_SURFACE_CONTRACTS.keys())


def test_surface_contracts_have_required_fields():
    for key, contract in DOMAIN_SURFACE_CONTRACTS.items():
        assert contract.purpose
        assert contract.primary_question
        assert contract.data_fields
        assert contract.read_only_sections is not None
        assert contract.editable_sections is not None


def test_read_write_boundary_is_explicit():
    for key, contract in DOMAIN_SURFACE_CONTRACTS.items():
        read_only_names = {section.name for section in contract.read_only_sections}
        editable_names = {section.name for section in contract.editable_sections}
        assert read_only_names.isdisjoint(editable_names)
        for section in contract.read_only_sections:
            assert section.editable is False
            assert section.edit_entry is None
        for section in contract.editable_sections:
            assert section.editable is True
            assert section.edit_entry is not None


def test_data_field_stability_and_source_constraints():
    allowed_sources = {"user_entered", "system_derived", "imported"}
    allowed_stability = {"stable", "likely_to_change"}
    for key, contract in DOMAIN_SURFACE_CONTRACTS.items():
        for field in contract.data_fields:
            assert field.source in allowed_sources
            assert field.stability in allowed_stability

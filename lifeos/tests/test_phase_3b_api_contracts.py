"""Phase 3b API contract freeze tests."""

from __future__ import annotations

import re

import pytest

from lifeos.core.contracts.api_contracts import (
    ALLOWED_SOURCES,
    ALLOWED_STABILITY,
    API_CONTRACTS,
    compute_schema_hash,
)
from lifeos.core.ux.domain_surface_contracts import DOMAIN_SURFACE_CONTRACTS

pytestmark = pytest.mark.unit


def _iter_fields(contract):
    for field in contract.schema.fields:
        yield field
    for obj in contract.schema.objects:
        for field in obj.fields:
            yield field


def test_api_contract_hashes_match():
    for name, contract in API_CONTRACTS.items():
        assert compute_schema_hash(contract.schema) == contract.schema_hash, f"{name} hash mismatch"


def test_api_contract_fields_use_allowed_vocab():
    for contract in API_CONTRACTS.values():
        for field in _iter_fields(contract):
            assert field.source in ALLOWED_SOURCES
            assert field.stability in ALLOWED_STABILITY
            assert field.type
            assert field.meaning


def test_api_contracts_reference_valid_surface_authority():
    for contract in API_CONTRACTS.values():
        if not contract.surface_key:
            continue
        surface = DOMAIN_SURFACE_CONTRACTS.get(contract.surface_key)
        assert surface is not None, f"missing surface {contract.surface_key}"
        requires_editable = any(field.source == "user" for field in _iter_fields(contract))
        if requires_editable:
            assert surface.editable_sections, f"{contract.surface_key} missing editable sections"


def test_api_contracts_are_versioned_and_read_only():
    semver = re.compile(r"^\d+\.\d+\.\d+$")
    for contract in API_CONTRACTS.values():
        assert semver.match(contract.version)
        assert contract.method == "GET"
        assert contract.read_only is True

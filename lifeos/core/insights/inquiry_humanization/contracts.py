"""Deterministic contracts for Phase 10 inquiry humanization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

HUMANIZATION_VERSION = "phase10_humanization_v1"


@dataclass(frozen=True)
class CanonicalFinding:
    finding_id: str
    claim: str
    finding_category: str
    confidence_label: str
    uncertainty_note: str
    source_domains: tuple[str, ...]
    evidence_refs: tuple[dict[str, object], ...]


@dataclass(frozen=True)
class CanonicalLimitation:
    limitation_id: str
    text: str


@dataclass(frozen=True)
class HumanizationRequest:
    canonical_brief: Mapping[str, object]
    canonical_brief_hash: str


@dataclass(frozen=True)
class HumanizedBlock:
    block_id: str
    text: str
    source_finding_ids: tuple[str, ...]
    source_limitation_ids: tuple[str, ...]
    evidence_refs: tuple[dict[str, object], ...]
    confidence_label: str | None = None


@dataclass(frozen=True)
class HumanizedSection:
    section_id: str
    title: str
    blocks: tuple[HumanizedBlock, ...]


@dataclass(frozen=True)
class HumanizedAnswer:
    text: str
    source_finding_ids: tuple[str, ...]
    source_limitation_ids: tuple[str, ...]


@dataclass(frozen=True)
class HumanizationMetadata:
    canonical_brief_hash: str
    humanization_version: str
    humanized_brief_hash: str
    technical_view_available: bool


@dataclass(frozen=True)
class HumanizedBrief:
    metadata: HumanizationMetadata
    answer: HumanizedAnswer
    sections: tuple[HumanizedSection, ...]


__all__ = [
    "CanonicalFinding",
    "CanonicalLimitation",
    "HumanizationMetadata",
    "HumanizationRequest",
    "HumanizedAnswer",
    "HumanizedBlock",
    "HumanizedBrief",
    "HumanizedSection",
    "HUMANIZATION_VERSION",
]

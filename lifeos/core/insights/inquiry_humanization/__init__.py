"""Shared deterministic inquiry humanization layer."""

from lifeos.core.insights.inquiry_humanization.assembler import humanize_inquiry_brief, serialize_humanized_brief
from lifeos.core.insights.inquiry_humanization.contracts import HUMANIZATION_VERSION, HumanizationRequest

__all__ = ["HUMANIZATION_VERSION", "HumanizationRequest", "humanize_inquiry_brief", "serialize_humanized_brief"]

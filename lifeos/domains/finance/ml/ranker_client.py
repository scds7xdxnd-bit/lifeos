"""Stub ML ranker client for account prediction."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from lifeos.core.insights.ml.embeddings import embed_text
from lifeos.core.insights.ml.ranking import rank_candidates

# Simple metadata to keep track of which ranker produced the response.
RANKER_MODEL_NAME = "embed-ranker"
RANKER_MODEL_VERSION = "v1"
RANKER_PAYLOAD_VERSION = "v1"


@dataclass
class RankerResult:
    """Structured output for account ranking adapters."""

    suggestions: List[int]
    model: str = RANKER_MODEL_NAME
    model_version: str | None = RANKER_MODEL_VERSION
    payload_version: str = RANKER_PAYLOAD_VERSION
    context: Dict[str, Any] = field(default_factory=dict)


def predict_account(description: str, candidates: List[Tuple[int, str]]) -> RankerResult:
    """Return account IDs ranked by semantic similarity to the description."""
    query_vec = embed_text(description)
    candidate_vecs = [(account_id, embed_text(label)) for account_id, label in candidates]
    ranked = rank_candidates(query_vec, candidate_vecs)
    suggestions = [account_id for account_id in ranked]
    return RankerResult(suggestions=suggestions, context={"candidate_count": len(candidates)})

"""Load legacy finance ML assets from the original app."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from lifeos.domains.finance.ml.ranker_client import RankerResult

try:
    import joblib
except ImportError:  # pragma: no cover - optional dependency
    joblib = None  # type: ignore

logger = logging.getLogger(__name__)


LEGACY_MODEL_FILENAMES = {
    "debit_model": "debit_account_suggester.joblib",
    "credit_model": "credit_account_suggester.joblib",
    "debit_encoder": "debit_account_label_encoder.joblib",
    "credit_encoder": "credit_account_label_encoder.joblib",
    "credit_vectorizer": "credit_account_label_vectorizer.joblib",
    "debit_vectorizer": "debit_account_tfidf.joblib",
}


def load_legacy_models(model_dir: str) -> Dict[str, Any]:
    """Load legacy joblib artifacts if available."""
    models: Dict[str, Any] = {}
    if not joblib:
        logger.info("joblib not installed; skipping legacy model load")
        return models
    base = Path(model_dir)
    for key, filename in LEGACY_MODEL_FILENAMES.items():
        path = base / filename
        if path.exists():
            try:
                models[key] = joblib.load(path)
                logger.info("Loaded legacy model %s from %s", key, path)
            except Exception as exc:  # pragma: no cover - load errors
                logger.warning("Failed to load %s: %s", path, exc)
    return models


def predict_account_with_legacy(description: str, models: Dict[str, Any]) -> Optional[RankerResult]:
    """Placeholder: adapt legacy models if available (returns None when not usable)."""
    # Without the original pipeline wiring, we simply return None to fall back to current flow.
    if not models:
        return None
    logger.info("Legacy models present; falling back to embed-based ranking for now.")
    return None

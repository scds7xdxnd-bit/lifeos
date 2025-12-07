"""ML-powered account suggestion flows."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from flask import current_app

from lifeos.core.events.event_service import log_event
from lifeos.domains.finance.events import EVENT_CATALOG, FINANCE_ML_SUGGEST_ACCOUNTS
from lifeos.domains.finance.models.accounting_models import Account
from lifeos.domains.finance.ml.legacy_models import load_legacy_models, predict_account_with_legacy
from lifeos.domains.finance.ml.ranker_client import RANKER_PAYLOAD_VERSION, RankerResult, predict_account


def suggest_accounts(user_id: int, description: str) -> List[int]:
    """Return ranked account IDs for a transaction description."""
    app = current_app._get_current_object()  # type: ignore[attr-defined]
    legacy_result = _maybe_rank_with_legacy(app, description)
    if legacy_result and legacy_result.suggestions:
        _log_ranker_event(user_id, description, legacy_result)
        return legacy_result.suggestions

    embed_result = _rank_with_embeddings(user_id, description)
    _log_ranker_event(user_id, description, embed_result)
    return embed_result.suggestions


def _event_payload_version() -> Optional[str]:
    catalog_entry = EVENT_CATALOG.get(FINANCE_ML_SUGGEST_ACCOUNTS) or {}
    return catalog_entry.get("version")


def _maybe_rank_with_legacy(app, description: str) -> Optional[RankerResult]:
    if not app.config.get("ENABLE_ML", True):
        return None
    cache = app.extensions.setdefault("legacy_ml_cache", {})
    if "models" not in cache:
        cache["models"] = load_legacy_models(app.config.get("MLSUGGESTER_MODEL_DIR") or "flask_app")
    legacy_models: Dict[str, Any] = cache.get("models") or {}
    if not legacy_models:
        return None
    result = predict_account_with_legacy(description, legacy_models)
    if result:
        result.payload_version = result.payload_version or _event_payload_version() or RANKER_PAYLOAD_VERSION
    return result


def _rank_with_embeddings(user_id: int, description: str) -> RankerResult:
    accounts = Account.query.filter_by(user_id=user_id, is_active=True).all()
    candidates = [(acct.id, f"{acct.name} {acct.code or ''}") for acct in accounts]
    result = predict_account(description, candidates)
    result.payload_version = result.payload_version or _event_payload_version() or RANKER_PAYLOAD_VERSION
    if not result.context:
        result.context = {}
    result.context.setdefault("candidate_count", len(candidates))
    return result


def _log_ranker_event(user_id: int, description: str, result: RankerResult) -> None:
    payload = {
        "user_id": user_id,
        "description": description,
        "suggestions": result.suggestions[:3],
        "model": result.model,
        "payload_version": result.payload_version or _event_payload_version(),
    }
    if result.model_version:
        payload["model_version"] = result.model_version
    if result.context:
        payload["context"] = result.context
    log_event(FINANCE_ML_SUGGEST_ACCOUNTS, payload, user_id=user_id)

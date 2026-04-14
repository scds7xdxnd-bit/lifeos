"""Exchange rate and currency API controller."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.utils.decorators import csrf_protected, require_roles
from lifeos.domains.finance.schemas.finance_schemas import ExchangeRateCreate
from lifeos.domains.finance.services.currency_service import (
    create_exchange_rate,
    get_latest_rate,
    get_user_base_currency,
    list_currencies,
    list_exchange_rates,
    set_user_base_currency,
)
from lifeos.extensions import limiter

exchange_rate_api_bp = Blueprint("exchange_rate_api", __name__)


# ---------------------------------------------------------------------------
# Currencies
# ---------------------------------------------------------------------------


@exchange_rate_api_bp.get("/currencies")
@jwt_required()
@limiter.limit("600/minute")
def list_currencies_endpoint():
    """List all supported ISO 4217 currencies."""
    currencies = list_currencies()
    return jsonify(
        {
            "ok": True,
            "currencies": [
                {
                    "code": c.code,
                    "symbol": c.symbol,
                    "name": c.name,
                    "decimal_places": c.decimal_places,
                    "is_base": bool(c.is_base),
                }
                for c in currencies
            ],
        }
    )


# ---------------------------------------------------------------------------
# User base currency preference
# ---------------------------------------------------------------------------


@exchange_rate_api_bp.get("/currencies/base")
@jwt_required()
@limiter.limit("240/minute")
def get_base_currency_endpoint():
    """Return the authenticated user's base currency code."""
    user_id = int(get_jwt_identity())
    code = get_user_base_currency(user_id)
    return jsonify({"ok": True, "currency_code": code})


@exchange_rate_api_bp.put("/currencies/base")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
@limiter.limit("60/minute")
def set_base_currency_endpoint():
    """Set the authenticated user's base currency.

    Request body: ``{"currency_code": "KRW"}``
    """
    user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}
    currency_code = (payload.get("currency_code") or "").strip()

    if not currency_code:
        return jsonify({"ok": False, "error": "validation_error"}), 400

    try:
        code = set_user_base_currency(user_id, currency_code)
    except ValueError as exc:
        err = str(exc)
        if err == "invalid_currency":
            return jsonify({"ok": False, "error": "invalid_currency"}), 400
        return jsonify({"ok": False, "error": "validation_error"}), 400

    return jsonify({"ok": True, "currency_code": code})


# ---------------------------------------------------------------------------
# Exchange rates
# ---------------------------------------------------------------------------


@exchange_rate_api_bp.get("/exchange-rates")
@jwt_required()
@limiter.limit("240/minute")
def list_exchange_rates_endpoint():
    """List manual exchange rates for the authenticated user.

    Query params (optional): ``from_currency``, ``to_currency``
    """
    user_id = int(get_jwt_identity())
    from_currency = request.args.get("from_currency")
    to_currency = request.args.get("to_currency")

    rates = list_exchange_rates(user_id, from_currency=from_currency, to_currency=to_currency)

    return jsonify(
        {
            "ok": True,
            "rates": [
                {
                    "id": r.id,
                    "from_currency": r.from_currency,
                    "to_currency": r.to_currency,
                    "rate": str(r.rate),
                    "effective_date": r.effective_date.isoformat(),
                    "source": r.source,
                }
                for r in rates
            ],
        }
    )


@exchange_rate_api_bp.post("/exchange-rates")
@jwt_required()
@csrf_protected
@require_roles({"finance:write"})
@limiter.limit("120/minute")
def create_exchange_rate_endpoint():
    """Create or overwrite a manual exchange rate.

    Request body::

        {
          "from_currency": "USD",
          "to_currency": "KRW",
          "rate": "1316.50",
          "effective_date": "2026-03-29"
        }
    """
    user_id = int(get_jwt_identity())
    payload = request.get_json(silent=True) or {}

    try:
        data = ExchangeRateCreate.model_validate(payload)
    except ValidationError:
        return jsonify({"ok": False, "error": "validation_error"}), 400

    try:
        fx_row = create_exchange_rate(
            user_id=user_id,
            from_currency=data.from_currency,
            to_currency=data.to_currency,
            rate=data.rate,
            effective_date=data.effective_date,
        )
    except ValueError as exc:
        err = str(exc)
        if err in {"same_currency", "invalid_currency", "invalid_rate"}:
            return jsonify({"ok": False, "error": err}), 400
        return jsonify({"ok": False, "error": "validation_error"}), 400

    return (
        jsonify(
            {
                "ok": True,
                "rate": {
                    "id": fx_row.id,
                    "from_currency": fx_row.from_currency,
                    "to_currency": fx_row.to_currency,
                    "rate": str(fx_row.rate),
                    "effective_date": fx_row.effective_date.isoformat(),
                    "source": fx_row.source,
                },
            }
        ),
        201,
    )


@exchange_rate_api_bp.get("/exchange-rates/latest")
@jwt_required()
@limiter.limit("240/minute")
def get_latest_rate_endpoint():
    """Return the most recent rate for a currency pair on or before ``as_of``.

    Query params:
      - ``from_currency`` (required)
      - ``to_currency`` (required)
      - ``as_of`` (optional, ISO date, defaults to today)
    """
    user_id = int(get_jwt_identity())
    from_currency = (request.args.get("from_currency") or "").strip().upper()
    to_currency = (request.args.get("to_currency") or "").strip().upper()

    if not from_currency or not to_currency:
        return jsonify({"ok": False, "error": "validation_error"}), 400

    as_of_raw = request.args.get("as_of")
    as_of = None
    if as_of_raw:
        try:
            from datetime import date as _date

            as_of = _date.fromisoformat(as_of_raw)
        except ValueError:
            return jsonify({"ok": False, "error": "validation_error"}), 400

    rate = get_latest_rate(user_id, from_currency, to_currency, as_of=as_of)
    if rate is None:
        return jsonify({"ok": False, "error": "not_found"}), 404

    return jsonify(
        {
            "ok": True,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": str(rate),
        }
    )

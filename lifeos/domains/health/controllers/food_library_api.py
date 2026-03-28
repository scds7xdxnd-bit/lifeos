"""Food library CRUD API controller."""

from __future__ import annotations

import requests as _requests
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.utils.decorators import csrf_protected
from lifeos.domains.health import services
from lifeos.domains.health.mappers import map_food_item
from lifeos.domains.health.schemas.food_library_schemas import (
    FoodItemCreate,
    FoodItemUpdate,
    Pagination,
)

food_library_api_bp = Blueprint("food_library_api", __name__)


@food_library_api_bp.get("")
@jwt_required()
def list_foods():
    user_id = int(get_jwt_identity())
    try:
        params = Pagination.model_validate(dict(request.args))
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    items, total = services.list_food_items(user_id, page=params.page, per_page=params.per_page)
    pages = (total + params.per_page - 1) // params.per_page if params.per_page else 1
    return jsonify(
        {
            "ok": True,
            "items": [map_food_item(f) for f in items],
            "page": params.page,
            "pages": pages,
            "total": total,
        }
    )


@food_library_api_bp.get("/<int:food_id>")
@jwt_required()
def get_food(food_id: int):
    user_id = int(get_jwt_identity())
    item = services.get_food_item(user_id, food_id)
    if not item:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "item": map_food_item(item)})


@food_library_api_bp.post("")
@jwt_required()
@csrf_protected
def create_food():
    payload = request.get_json(silent=True) or {}
    try:
        data = FoodItemCreate.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    user_id = int(get_jwt_identity())
    try:
        item = services.create_food_item(
            user_id,
            name=data.name,
            cost_per_100g=data.cost_per_100g,
            calories_per_100g=data.calories_per_100g,
            protein_per_100g=data.protein_per_100g,
            carbohydrate_per_100g=data.carbohydrate_per_100g,
            fat_per_100g=data.fat_per_100g,
            fiber_per_100g=data.fiber_per_100g,
        )
    except ValueError as exc:
        if str(exc) == "duplicate":
            return jsonify({"ok": False, "error": "duplicate"}), 409
        return jsonify({"ok": False, "error": "validation_error"}), 400
    return jsonify({"ok": True, "item": map_food_item(item)}), 201


@food_library_api_bp.patch("/<int:food_id>")
@jwt_required()
@csrf_protected
def update_food(food_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = FoodItemUpdate.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    user_id = int(get_jwt_identity())
    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        return jsonify({"ok": False, "error": "no_fields"}), 400
    try:
        item = services.update_food_item(user_id, food_id, **fields)
    except ValueError as exc:
        if str(exc) == "duplicate":
            return jsonify({"ok": False, "error": "duplicate"}), 409
        return jsonify({"ok": False, "error": "validation_error"}), 400
    if not item:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "item": map_food_item(item)})


@food_library_api_bp.delete("/<int:food_id>")
@jwt_required()
@csrf_protected
def delete_food(food_id: int):
    user_id = int(get_jwt_identity())
    deleted = services.delete_food_item(user_id, food_id)
    if not deleted:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True})


_OFF_HEADERS = {
    "User-Agent": "LifeOS/1.0 (lifeos-app)",
    "Accept": "application/json",
}
_OFF_FIELDS = "product_name,brands,nutriments"

# Regional OFF databases for better local product coverage.
# world.openfoodfacts.org is used as the global fallback.
_OFF_REGIONAL: dict[str, dict] = {
    "ko": {
        "url": "https://kr.openfoodfacts.org/cgi/search.pl",
        "lc": "ko",
        "cc": "kr",
    },
    "zh": {
        "url": "https://cn.openfoodfacts.org/cgi/search.pl",
        "lc": "zh",
        "cc": "cn",
    },
}
_OFF_WORLD_URL = "https://world.openfoodfacts.org/cgi/search.pl"


def _normalise_product(p: dict) -> dict | None:
    """Return a normalised product dict, or None if the entry has no name."""
    name = p.get("product_name", "").strip()
    if not name:
        return None
    nutriments = p.get("nutriments") or {}
    return {
        "product_name": name,
        "brands": p.get("brands") or None,
        # OFF stores per-100g values under the _100g suffix — no conversion needed.
        "calories_per_100g": float(nutriments.get("energy-kcal_100g") or 0),
        "protein_per_100g": float(nutriments.get("proteins_100g") or 0),
        "carbohydrate_per_100g": float(nutriments.get("carbohydrates_100g") or 0),
        "fat_per_100g": float(nutriments.get("fat_100g") or 0),
        "fiber_per_100g": (float(nutriments["fiber_100g"]) if nutriments.get("fiber_100g") is not None else None),
    }


def _fetch_off(url: str, q: str, limit: int, extra_params: dict | None = None) -> list[dict]:
    """Fetch and normalise results from an OFF search endpoint. Returns [] on any error."""
    params = {
        "search_terms": q,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": limit,
        "fields": _OFF_FIELDS,
    }
    if extra_params:
        params.update(extra_params)
    try:
        resp = _requests.get(url, params=params, headers=_OFF_HEADERS, timeout=6)
        if not resp.ok:
            return []
        products = []
        for p in resp.json().get("products", []):
            normalised = _normalise_product(p)
            if normalised:
                products.append(normalised)
        return products
    except Exception:  # noqa: BLE001
        return []


@food_library_api_bp.get("/search")
@jwt_required()
def search_foods():
    """Proxy Open Food Facts name search — avoids browser CORS restrictions.

    Accepts optional ``lang`` param (e.g. ``ko``, ``zh``, ``en``) to route
    queries to the regional OFF database for better local product coverage.
    When a regional database returns fewer than ``limit`` results the world
    database is queried and the two lists are merged (regional results first,
    duplicates removed by product name).
    """
    q = request.args.get("q", "").strip()
    if len(q) < 3:
        return jsonify({"ok": True, "products": []})

    limit = min(int(request.args.get("limit", 8)), 20)
    lang = request.args.get("lang", "en").lower()[:5]

    regional = _OFF_REGIONAL.get(lang)

    if regional:
        # Query the regional database first.
        results = _fetch_off(
            regional["url"],
            q,
            limit,
            extra_params={"lc": regional["lc"], "cc": regional["cc"]},
        )
        # If regional returns fewer than requested, supplement with world results.
        if len(results) < limit:
            world_results = _fetch_off(_OFF_WORLD_URL, q, limit)
            seen = {r["product_name"].lower() for r in results}
            for item in world_results:
                if item["product_name"].lower() not in seen and len(results) < limit:
                    results.append(item)
                    seen.add(item["product_name"].lower())
    else:
        results = _fetch_off(_OFF_WORLD_URL, q, limit)

    return jsonify({"ok": True, "products": results})

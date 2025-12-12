"""Relationships JSON API."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.utils.decorators import csrf_protected
from lifeos.domains.relationships import services
from lifeos.domains.relationships.mappers import map_interaction, map_person
from lifeos.domains.relationships.schemas.rel_schemas import (
    InteractionCreate,
    InteractionUpdate,
    PersonCreate,
    PersonUpdate,
)

rel_api_bp = Blueprint("relationships_api", __name__)


@rel_api_bp.get("/people")
@jwt_required()
def list_people():
    user_id = int(get_jwt_identity())
    args = request.args
    tag = args.get("tag")
    relationship_type = args.get("relationship_type")
    importance_level = args.get("importance_level")
    importance_level = int(importance_level) if importance_level is not None else None
    search = args.get("search")
    people = services.list_people(
        user_id,
        tag=tag,
        relationship_type=relationship_type,
        importance_level=importance_level,
        search=search,
    )
    return jsonify({"ok": True, "people": [map_person(p) for p in people]})


@rel_api_bp.post("/people")
@jwt_required()
@csrf_protected
def create_person():
    payload = request.get_json(silent=True) or {}
    try:
        data = PersonCreate.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify(
                {"ok": False, "error": "validation_error", "details": exc.errors()}
            ),
            400,
        )
    user_id = int(get_jwt_identity())
    try:
        person = services.create_person(user_id=user_id, **data.model_dump())
    except ValueError as exc:
        code = str(exc)
        if code == "duplicate":
            return jsonify({"ok": False, "error": "duplicate"}), 409
        return jsonify({"ok": False, "error": "validation_error"}), 400
    return jsonify({"ok": True, "person": map_person(person)}), 201


@rel_api_bp.get("/people/<int:person_id>")
@jwt_required()
def get_person(person_id: int):
    user_id = int(get_jwt_identity())
    person = services.get_person(user_id, person_id)
    if not person:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "person": map_person(person)})


@rel_api_bp.patch("/people/<int:person_id>")
@jwt_required()
@csrf_protected
def update_person(person_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = PersonUpdate.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify(
                {"ok": False, "error": "validation_error", "details": exc.errors()}
            ),
            400,
        )
    user_id = int(get_jwt_identity())
    person = services.update_person(
        user_id,
        person_id,
        **{k: v for k, v in data.model_dump().items() if v is not None},
    )
    if not person:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "person": map_person(person)})


@rel_api_bp.delete("/people/<int:person_id>")
@jwt_required()
@csrf_protected
def delete_person(person_id: int):
    user_id = int(get_jwt_identity())
    deleted = services.delete_person(user_id, person_id)
    if not deleted:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True})


@rel_api_bp.get("/people/<int:person_id>/interactions")
@jwt_required()
def list_interactions(person_id: int):
    user_id = int(get_jwt_identity())
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    try:
        interactions = services.list_interactions(
            user_id, person_id, page=page, per_page=per_page
        )
    except ValueError as exc:
        if str(exc) == "not_found":
            return jsonify({"ok": False, "error": "not_found"}), 404
        raise
    return jsonify(
        {"ok": True, "interactions": [map_interaction(i) for i in interactions]}
    )


@rel_api_bp.post("/people/<int:person_id>/interactions")
@jwt_required()
@csrf_protected
def log_interaction(person_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = InteractionCreate.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify(
                {"ok": False, "error": "validation_error", "details": exc.errors()}
            ),
            400,
        )
    user_id = int(get_jwt_identity())
    try:
        interaction = services.log_interaction(
            user_id,
            person_id,
            date_value=data.date,
            method=data.method,
            notes=data.notes,
            sentiment=data.sentiment,
        )
    except ValueError as exc:
        if str(exc) == "not_found":
            return jsonify({"ok": False, "error": "not_found"}), 404
        return jsonify({"ok": False, "error": "validation_error"}), 400
    return jsonify({"ok": True, "interaction": map_interaction(interaction)}), 201


@rel_api_bp.patch("/interactions/<int:interaction_id>")
@jwt_required()
@csrf_protected
def update_interaction(interaction_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = InteractionUpdate.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify(
                {"ok": False, "error": "validation_error", "details": exc.errors()}
            ),
            400,
        )
    user_id = int(get_jwt_identity())
    interaction = services.edit_interaction(
        user_id,
        interaction_id,
        **{k: v for k, v in data.model_dump().items() if v is not None},
    )
    if not interaction:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "interaction": map_interaction(interaction)})


@rel_api_bp.delete("/interactions/<int:interaction_id>")
@jwt_required()
@csrf_protected
def delete_interaction(interaction_id: int):
    user_id = int(get_jwt_identity())
    deleted = services.delete_interaction(user_id, interaction_id)
    if not deleted:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True})


@rel_api_bp.get("/reconnect")
@jwt_required()
def reconnect():
    user_id = int(get_jwt_identity())
    limit = int(request.args.get("limit", 20))
    cutoff_days = int(request.args.get("cutoff_days", 30))
    candidates = services.compute_reconnect_candidates(
        user_id, limit=limit, cutoff_days=cutoff_days
    )
    payload = [
        {
            "person": map_person(item["person"]),
            "last_interaction_date": (
                item["last_interaction_date"].isoformat()
                if item["last_interaction_date"]
                else None
            ),
            "days_since": item["days_since"],
        }
        for item in candidates
    ]
    return jsonify({"ok": True, "candidates": payload})

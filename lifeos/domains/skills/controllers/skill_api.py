"""Skill API controllers (thin, service-backed)."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.utils.decorators import csrf_protected
from lifeos.domains.skills.mappers import map_session_response, map_skill_summary
from lifeos.domains.skills.schemas.skill_schemas import (
    PracticeSessionCreate,
    PracticeSessionUpdate,
    SkillCreate,
    SkillUpdate,
)
from lifeos.domains.skills.services.skill_service import (
    create_skill,
    delete_practice_session,
    delete_skill,
    get_skill_summary,
    list_skills_with_aggregates,
    log_practice_session,
    update_practice_session,
    update_skill,
)

skill_api_bp = Blueprint("skill_api", __name__)


@skill_api_bp.post("")
@jwt_required()
@csrf_protected
def create_skill_endpoint():
    payload = request.get_json(silent=True) or {}
    try:
        data = SkillCreate.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}),
            400,
        )
    user_id = int(get_jwt_identity())
    try:
        skill = create_skill(user_id=user_id, **data.model_dump())
    except ValueError as exc:
        code = str(exc)
        if code == "duplicate":
            return jsonify({"ok": False, "error": "duplicate"}), 409
        return jsonify({"ok": False, "error": "validation_error"}), 400
    return jsonify({"ok": True, "skill_id": skill.id}), 201


@skill_api_bp.get("")
@jwt_required()
def list_skills_endpoint():
    user_id = int(get_jwt_identity())
    records = list_skills_with_aggregates(user_id=user_id)
    payload = [map_skill_summary(rec).model_dump() for rec in records]
    return jsonify({"ok": True, "skills": payload})


@skill_api_bp.get("/<int:skill_id>")
@jwt_required()
def get_skill_detail(skill_id: int):
    user_id = int(get_jwt_identity())
    summary = get_skill_summary(user_id, skill_id)
    if not summary:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "skill": map_skill_summary(summary).model_dump()})


@skill_api_bp.patch("/<int:skill_id>")
@jwt_required()
@csrf_protected
def update_skill_endpoint(skill_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = SkillUpdate.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}),
            400,
        )
    user_id = int(get_jwt_identity())
    skill = update_skill(
        user_id,
        skill_id,
        **{k: v for k, v in data.model_dump().items() if v is not None},
    )
    if not skill:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True})


@skill_api_bp.delete("/<int:skill_id>")
@jwt_required()
@csrf_protected
def delete_skill_endpoint(skill_id: int):
    user_id = int(get_jwt_identity())
    deleted = delete_skill(user_id, skill_id)
    if not deleted:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True})


@skill_api_bp.post("/<int:skill_id>/practice")
@jwt_required()
@csrf_protected
def log_practice_endpoint(skill_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = PracticeSessionCreate.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}),
            400,
        )
    user_id = int(get_jwt_identity())
    try:
        session = log_practice_session(user_id, skill_id, **data.model_dump())
    except ValueError as exc:
        code = str(exc)
        if code == "not_found":
            return jsonify({"ok": False, "error": "not_found"}), 404
        return jsonify({"ok": False, "error": "validation_error"}), 400
    return jsonify({"ok": True, "session": map_session_response(session).model_dump()})


@skill_api_bp.patch("/practice/<int:session_id>")
@jwt_required()
@csrf_protected
def update_practice_endpoint(session_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = PracticeSessionUpdate.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}),
            400,
        )
    user_id = int(get_jwt_identity())
    session = update_practice_session(
        user_id,
        session_id,
        **{k: v for k, v in data.model_dump().items() if v is not None},
    )
    if not session:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "session": map_session_response(session).model_dump()})


@skill_api_bp.delete("/practice/<int:session_id>")
@jwt_required()
@csrf_protected
def delete_practice_endpoint(session_id: int):
    user_id = int(get_jwt_identity())
    deleted = delete_practice_session(user_id, session_id)
    if not deleted:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True})

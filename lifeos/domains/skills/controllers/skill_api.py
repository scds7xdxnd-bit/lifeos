"""Skill API controllers (thin, service-backed)."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.utils.decorators import csrf_protected
from lifeos.domains.skills.mappers import map_session_response, map_skill_summary
from lifeos.domains.skills.schemas.skill_schemas import (
    PracticeSessionCreate,
    PracticeSessionUpdate,
    SkillCreate,
    SkillOverviewCardResponse,
    SkillPathResponse,
    SkillUpdate,
)
from lifeos.domains.skills.services.skill_service import (
    create_skill,
    delete_practice_session,
    delete_skill,
    get_skill_path,
    get_skill_summary,
    list_skill_overview_cards,
    list_skills_with_aggregates,
    log_practice_session,
    resolve_next_recommended_step,
    update_practice_session,
    update_skill,
)

skill_api_bp = Blueprint("skill_api", __name__)


def _phase12_skills_goals_enabled() -> bool:
    return bool(current_app.config.get("ENABLE_PHASE12_SKILLS_GOALS", False))


def _phase12_skills_goals_strict_enabled() -> bool:
    return bool(current_app.config.get("ENABLE_PHASE12_SKILLS_GOALS_STRICT", False))


def _phase12_skills_path_enabled() -> bool:
    return bool(current_app.config.get("ENABLE_PHASE12_SKILLS_PATH", False))


def _feature_disabled_response():
    return jsonify({"ok": False, "error": "not_found"}), 404


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
    if (
        _phase12_skills_goals_enabled()
        and _phase12_skills_goals_strict_enabled()
        and (data.goal_type is None or data.goal_target_value is None)
    ):
        return jsonify({"ok": False, "error": "goal_required"}), 400
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


@skill_api_bp.get("/overview")
@jwt_required()
def list_skills_overview_endpoint():
    if not _phase12_skills_goals_enabled():
        return _feature_disabled_response()

    user_id = int(get_jwt_identity())
    cards = list_skill_overview_cards(user_id=user_id)
    payload = [SkillOverviewCardResponse.model_validate(card).model_dump() for card in cards]
    summary = {
        "total_hours": round(sum(float(item["total_minutes"]) for item in payload) / 60.0, 1),
        "total_sessions": int(sum(int(item["session_count"]) for item in payload)),
        "at_risk": int(sum(1 for item in payload if item["progress_state"] == "at_risk")),
        "active": int(len(payload)),
    }
    groups = {
        "at_risk": [item for item in payload if item["progress_state"] == "at_risk"],
        "on_track": [item for item in payload if item["progress_state"] == "on_track"],
        "completed": [item for item in payload if item["progress_state"] == "completed"],
    }
    return jsonify({"ok": True, "summary": summary, "groups": groups, "skills": payload})


@skill_api_bp.get("/<int:skill_id>")
@jwt_required()
def get_skill_detail(skill_id: int):
    user_id = int(get_jwt_identity())
    summary = get_skill_summary(user_id, skill_id)
    if not summary:
        return jsonify({"ok": False, "error": "not_found"}), 404

    skill_payload = map_skill_summary(summary).model_dump()
    path_payload = get_skill_path(user_id=user_id, skill_id=skill_id) if _phase12_skills_path_enabled() else None
    goal_payload = path_payload.get("goal") if path_payload else None
    path_steps = path_payload.get("steps") if path_payload else None
    current_step = path_payload.get("next_recommended_step") if path_payload else None

    history_payload = {
        "recent_sessions_count": len(skill_payload.get("recent_sessions") or []),
        "last_practiced_at": skill_payload.get("last_practiced_at"),
    }
    return jsonify(
        {
            "ok": True,
            "skill": skill_payload,
            "goal": goal_payload,
            "path": path_payload,
            "path_steps": path_steps,
            "current_step": current_step,
            "history": history_payload,
        }
    )


@skill_api_bp.get("/<int:skill_id>/path")
@jwt_required()
def get_skill_path_endpoint(skill_id: int):
    if not _phase12_skills_path_enabled():
        return _feature_disabled_response()

    user_id = int(get_jwt_identity())
    path_payload = get_skill_path(user_id=user_id, skill_id=skill_id)
    if not path_payload:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "path": SkillPathResponse.model_validate(path_payload).model_dump()})


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
    next_step = None
    path_payload = get_skill_path(user_id=user_id, skill_id=skill_id) if _phase12_skills_path_enabled() else None
    if path_payload:
        next_step = path_payload.get("next_recommended_step") or resolve_next_recommended_step(
            path_payload.get("steps") or []
        )

    return jsonify(
        {"ok": True, "session": map_session_response(session).model_dump(), "next_recommended_step": next_step}
    )


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

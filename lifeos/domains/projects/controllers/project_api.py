"""Project API controllers."""

from __future__ import annotations

import math

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.utils.decorators import csrf_protected
from lifeos.domains.projects import services
from lifeos.domains.projects.mappers import map_project, map_task, map_task_log
from lifeos.domains.projects.models.project_models import ProjectTask
from lifeos.domains.projects.schemas.project_schemas import (
    ProjectCreate,
    ProjectListFilter,
    ProjectUpdate,
    TaskCreate,
    TaskListFilter,
    TaskLogCreate,
    TaskUpdate,
)

project_api_bp = Blueprint("project_api", __name__)


def _parse_query(schema_cls):
    data = {k: v for k, v in request.args.items()}
    try:
        return schema_cls.model_validate(data), None
    except ValidationError as exc:
        return None, exc


@project_api_bp.get("")
@jwt_required()
def list_projects():
    user_id = int(get_jwt_identity())
    params, err = _parse_query(ProjectListFilter)
    if err:
        return (
            jsonify({"ok": False, "error": "validation_error", "details": err.errors()}),
            400,
        )
    items, total = services.list_projects(user_id, status=params.status, page=params.page, per_page=params.per_page)
    pages = math.ceil(total / params.per_page) if params.per_page else 1
    return jsonify(
        {
            "ok": True,
            "items": [map_project(p) for p in items],
            "page": params.page,
            "pages": pages,
            "total": total,
        }
    )


@project_api_bp.post("")
@jwt_required()
@csrf_protected
def create_project():
    payload = request.get_json(silent=True) or {}
    try:
        data = ProjectCreate.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}),
            400,
        )
    user_id = int(get_jwt_identity())
    try:
        project = services.create_project(
            user_id,
            name=data.name,
            description=data.description,
            target_date=data.target_date,
        )
    except ValueError as exc:
        if str(exc) == "duplicate":
            return jsonify({"ok": False, "error": "duplicate"}), 409
        return jsonify({"ok": False, "error": "validation_error"}), 400
    return jsonify({"ok": True, "project": map_project(project)}), 201


@project_api_bp.get("/<int:project_id>")
@jwt_required()
def get_project(project_id: int):
    user_id = int(get_jwt_identity())
    project = services.get_project(user_id, project_id)
    if not project:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "project": map_project(project)})


@project_api_bp.patch("/<int:project_id>")
@jwt_required()
@csrf_protected
def update_project(project_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = ProjectUpdate.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}),
            400,
        )
    user_id = int(get_jwt_identity())
    try:
        project = services.update_project(
            user_id,
            project_id,
            **{k: v for k, v in data.model_dump().items() if v is not None},
        )
    except ValueError:
        return jsonify({"ok": False, "error": "validation_error"}), 400
    if not project:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "project": map_project(project)})


@project_api_bp.post("/<int:project_id>/archive")
@jwt_required()
@csrf_protected
def archive_project(project_id: int):
    user_id = int(get_jwt_identity())
    project = services.archive_project(user_id, project_id)
    if not project:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "project": map_project(project)})


@project_api_bp.post("/<int:project_id>/complete")
@jwt_required()
@csrf_protected
def complete_project(project_id: int):
    user_id = int(get_jwt_identity())
    project = services.complete_project(user_id, project_id)
    if not project:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "project": map_project(project)})


@project_api_bp.delete("/<int:project_id>")
@jwt_required()
@csrf_protected
def delete_project(project_id: int):
    user_id = int(get_jwt_identity())
    deleted = services.delete_project(user_id, project_id)
    if not deleted:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True})


@project_api_bp.get("/<int:project_id>/tasks")
@jwt_required()
def list_tasks(project_id: int):
    user_id = int(get_jwt_identity())
    params, err = _parse_query(TaskListFilter)
    if err:
        return (
            jsonify({"ok": False, "error": "validation_error", "details": err.errors()}),
            400,
        )
    items, total = services.list_tasks(
        user_id,
        project_id=project_id,
        status=params.status,
        due_before=params.due_before,
        page=params.page,
        per_page=params.per_page,
    )
    pages = math.ceil(total / params.per_page) if params.per_page else 1
    return jsonify(
        {
            "ok": True,
            "items": [map_task(t) for t in items],
            "page": params.page,
            "pages": pages,
            "total": total,
        }
    )


@project_api_bp.post("/<int:project_id>/tasks")
@jwt_required()
@csrf_protected
def create_task(project_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = TaskCreate.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}),
            400,
        )
    user_id = int(get_jwt_identity())
    try:
        task = services.create_task(
            user_id,
            project_id,
            title=data.title,
            due_date=data.due_date,
            priority=data.priority,
            notes=data.notes,
        )
    except ValueError as exc:
        if str(exc) == "not_found":
            return jsonify({"ok": False, "error": "not_found"}), 404
        return jsonify({"ok": False, "error": "validation_error"}), 400
    return jsonify({"ok": True, "task": map_task(task)}), 201


@project_api_bp.get("/tasks/<int:task_id>")
@jwt_required()
def get_task(task_id: int):
    user_id = int(get_jwt_identity())
    task = ProjectTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "task": map_task(task)})


@project_api_bp.patch("/tasks/<int:task_id>")
@jwt_required()
@csrf_protected
def update_task(task_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = TaskUpdate.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}),
            400,
        )
    user_id = int(get_jwt_identity())
    try:
        task = services.update_task(
            user_id,
            task_id,
            **{k: v for k, v in data.model_dump().items() if v is not None},
        )
    except ValueError:
        return jsonify({"ok": False, "error": "validation_error"}), 400
    if not task:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "task": map_task(task)})


@project_api_bp.post("/tasks/<int:task_id>/complete")
@jwt_required()
@csrf_protected
def complete_task(task_id: int):
    user_id = int(get_jwt_identity())
    task = services.complete_task(user_id, task_id)
    if not task:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "task": map_task(task)})


@project_api_bp.delete("/tasks/<int:task_id>")
@jwt_required()
@csrf_protected
def delete_task(task_id: int):
    user_id = int(get_jwt_identity())
    deleted = services.delete_task(user_id, task_id)
    if not deleted:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True})


@project_api_bp.get("/tasks/<int:task_id>/logs")
@jwt_required()
def list_task_logs(task_id: int):
    user_id = int(get_jwt_identity())
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 100))
    try:
        items, total = services.list_task_logs(user_id, task_id, page=page, per_page=per_page)
    except ValueError as exc:
        if str(exc) == "not_found":
            return jsonify({"ok": False, "error": "not_found"}), 404
        raise
    pages = math.ceil(total / per_page) if per_page else 1
    return jsonify(
        {
            "ok": True,
            "items": [map_task_log(log_item) for log_item in items],
            "page": page,
            "pages": pages,
            "total": total,
        }
    )


@project_api_bp.post("/tasks/<int:task_id>/logs")
@jwt_required()
@csrf_protected
def log_task(task_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        data = TaskLogCreate.model_validate(payload)
    except ValidationError as exc:
        return (
            jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}),
            400,
        )
    user_id = int(get_jwt_identity())
    try:
        log = services.log_task_activity(
            user_id,
            task_id,
            note=data.note,
            status_snapshot=data.status_snapshot,
        )
    except ValueError as exc:
        if str(exc) == "not_found":
            return jsonify({"ok": False, "error": "not_found"}), 404
        return jsonify({"ok": False, "error": "validation_error"}), 400
    return jsonify({"ok": True, "log": map_task_log(log)}), 201

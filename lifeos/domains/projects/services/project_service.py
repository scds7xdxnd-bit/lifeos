"""Project service layer."""

from __future__ import annotations

from datetime import datetime
from typing import List, Tuple

from lifeos.domains.projects.events import (
    PROJECT_ARCHIVED,
    PROJECT_COMPLETED,
    PROJECT_CREATED,
    PROJECT_UPDATED,
)
from lifeos.domains.projects.models.project_models import Project
from lifeos.extensions import db
from lifeos.platform.outbox import enqueue as enqueue_outbox

_PROJECT_STATUSES = {"active", "archived", "completed"}


def create_project(user_id: int, *, name: str, description: str | None = None, target_date=None) -> Project:
    existing = Project.query.filter_by(user_id=user_id, name=name).first()
    if existing:
        raise ValueError("duplicate")
    project = Project(
        user_id=user_id,
        name=name.strip(),
        description=(description or "").strip() or None,
        target_date=target_date,
        status="active",
    )
    db.session.add(project)
    db.session.flush()
    enqueue_outbox(
        PROJECT_CREATED,
        {
            "project_id": project.id,
            "user_id": user_id,
            "name": project.name,
            "status": project.status,
            "target_date": (project.target_date.isoformat() if project.target_date else None),
            "created_at": project.created_at.isoformat(),
        },
        user_id=user_id,
    )
    db.session.commit()
    return project


def update_project(user_id: int, project_id: int, **fields) -> Project | None:
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return None
    changed = {}
    for key in ("name", "description", "status", "target_date"):
        if key in fields and fields[key] is not None:
            if key == "status" and fields[key] not in _PROJECT_STATUSES:
                raise ValueError("validation_error")
            val = fields[key].strip() if isinstance(fields[key], str) else fields[key]
            setattr(project, key, val)
            changed[key] = val
    enqueue_outbox(
        PROJECT_UPDATED,
        {
            "project_id": project.id,
            "user_id": user_id,
            "fields": changed,
            "updated_at": (project.updated_at.isoformat() if project.updated_at else datetime.utcnow().isoformat()),
        },
        user_id=user_id,
    )
    db.session.commit()
    return project


def archive_project(user_id: int, project_id: int) -> Project | None:
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return None
    project.status = "archived"
    enqueue_outbox(
        PROJECT_ARCHIVED,
        {
            "project_id": project.id,
            "user_id": user_id,
            "archived_at": datetime.utcnow().isoformat(),
        },
        user_id=user_id,
    )
    db.session.commit()
    return project


def complete_project(user_id: int, project_id: int) -> Project | None:
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return None
    project.status = "completed"
    enqueue_outbox(
        PROJECT_COMPLETED,
        {
            "project_id": project.id,
            "user_id": user_id,
            "completed_at": datetime.utcnow().isoformat(),
        },
        user_id=user_id,
    )
    db.session.commit()
    return project


def get_project(user_id: int, project_id: int) -> Project | None:
    return Project.query.filter_by(id=project_id, user_id=user_id).first()


def list_projects(
    user_id: int, *, status: str | None = None, page: int = 1, per_page: int = 50
) -> Tuple[List[Project], int]:
    query = Project.query.filter_by(user_id=user_id)
    if status:
        query = query.filter(Project.status == status)
    query = query.order_by(Project.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def delete_project(user_id: int, project_id: int) -> bool:
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        return False
    db.session.delete(project)
    db.session.commit()
    return True

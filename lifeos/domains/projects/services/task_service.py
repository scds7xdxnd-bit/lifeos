"""Task service."""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Tuple

from lifeos.domains.projects.events import TASK_COMPLETED, TASK_CREATED, TASK_LOGGED, TASK_UPDATED
from lifeos.domains.projects.models.project_models import Project, ProjectTask, ProjectTaskLog
from lifeos.extensions import db
from lifeos.platform.outbox import enqueue as enqueue_outbox

_TASK_STATUSES = {"open", "in_progress", "completed", "blocked", "archived"}


def create_task(
    user_id: int,
    project_id: int,
    *,
    title: str,
    due_date: date | None = None,
    priority: int | None = None,
    notes: str | None = None,
) -> ProjectTask:
    project = Project.query.filter_by(id=project_id, user_id=user_id).first()
    if not project:
        raise ValueError("not_found")
    task = ProjectTask(
        user_id=user_id,
        project_id=project_id,
        title=title.strip(),
        status="open",
        due_date=due_date,
        priority=priority,
        notes=(notes or "").strip() or None,
    )
    db.session.add(task)
    db.session.flush()
    enqueue_outbox(
        TASK_CREATED,
        {
            "task_id": task.id,
            "project_id": project_id,
            "user_id": user_id,
            "title": task.title,
            "status": task.status,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "priority": task.priority,
        },
        user_id=user_id,
    )
    db.session.commit()
    return task


def update_task(user_id: int, task_id: int, **fields) -> ProjectTask | None:
    task = ProjectTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return None
    changed = {}
    for key in ("title", "status", "due_date", "priority", "notes"):
        if key in fields and fields[key] is not None:
            if key == "status" and fields[key] not in _TASK_STATUSES:
                raise ValueError("validation_error")
            val = fields[key].strip() if isinstance(fields[key], str) else fields[key]
            setattr(task, key, val)
            changed[key] = val
    enqueue_outbox(
        TASK_UPDATED,
        {
            "task_id": task.id,
            "project_id": task.project_id,
            "user_id": user_id,
            "fields": changed,
            "updated_at": task.updated_at.isoformat() if task.updated_at else datetime.utcnow().isoformat(),
        },
        user_id=user_id,
    )
    db.session.commit()
    return task


def complete_task(user_id: int, task_id: int) -> ProjectTask | None:
    task = ProjectTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return None
    task.status = "completed"
    enqueue_outbox(
        TASK_COMPLETED,
        {
            "task_id": task.id,
            "project_id": task.project_id,
            "user_id": user_id,
            "completed_at": datetime.utcnow().isoformat(),
        },
        user_id=user_id,
    )
    db.session.commit()
    return task


def list_tasks(
    user_id: int,
    project_id: int | None = None,
    *,
    status: str | None = None,
    due_before: date | None = None,
    page: int = 1,
    per_page: int = 100,
) -> Tuple[List[ProjectTask], int]:
    query = ProjectTask.query.filter_by(user_id=user_id)
    if project_id:
        query = query.filter(ProjectTask.project_id == project_id)
    if status:
        query = query.filter(ProjectTask.status == status)
    if due_before:
        query = query.filter(ProjectTask.due_date != None, ProjectTask.due_date <= due_before)  # noqa: E711
    query = query.order_by(ProjectTask.due_date.asc().nullsfirst(), ProjectTask.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def log_task_activity(
    user_id: int,
    task_id: int,
    *,
    note: str | None = None,
    status_snapshot: str | None = None,
    logged_at: datetime | None = None,
) -> ProjectTaskLog:
    task = ProjectTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        raise ValueError("not_found")
    log = ProjectTaskLog(
        user_id=user_id,
        task_id=task_id,
        note=(note or "").strip() or None,
        status_snapshot=status_snapshot or task.status,
        logged_at=logged_at or datetime.utcnow(),
    )
    db.session.add(log)
    db.session.flush()
    enqueue_outbox(
        TASK_LOGGED,
        {
            "log_id": log.id,
            "task_id": task_id,
            "project_id": task.project_id,
            "user_id": user_id,
            "status_snapshot": log.status_snapshot,
            "logged_at": log.logged_at.isoformat(),
        },
        user_id=user_id,
    )
    db.session.commit()
    return log


def list_task_logs(user_id: int, task_id: int, page: int = 1, per_page: int = 100) -> Tuple[List[ProjectTaskLog], int]:
    task = ProjectTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        raise ValueError("not_found")
    query = ProjectTaskLog.query.filter_by(user_id=user_id, task_id=task_id).order_by(ProjectTaskLog.logged_at.desc())
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def delete_task(user_id: int, task_id: int) -> bool:
    task = ProjectTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return False
    db.session.delete(task)
    db.session.commit()
    return True

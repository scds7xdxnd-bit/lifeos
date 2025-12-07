"""DTO mappers for projects."""

from __future__ import annotations

from lifeos.domains.projects.models.project_models import Project, ProjectTask, ProjectTaskLog


def map_project(project: Project) -> dict:
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "target_date": project.target_date.isoformat() if project.target_date else None,
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "updated_at": project.updated_at.isoformat() if project.updated_at else None,
    }


def map_task(task: ProjectTask) -> dict:
    return {
        "id": task.id,
        "project_id": task.project_id,
        "title": task.title,
        "status": task.status,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "priority": task.priority,
        "notes": task.notes,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


def map_task_log(log: ProjectTaskLog) -> dict:
    return {
        "id": log.id,
        "task_id": log.task_id,
        "note": log.note,
        "status_snapshot": log.status_snapshot,
        "logged_at": log.logged_at.isoformat() if log.logged_at else None,
        "created_at": log.created_at.isoformat() if log.created_at else None,
    }

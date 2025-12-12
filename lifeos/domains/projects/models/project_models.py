"""Project domain models."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from lifeos.extensions import db


class Project(db.Model):
    __tablename__ = "project"
    __table_args__ = (
        db.Index("ix_project_user_name", "user_id", "name"),
        db.Index("ix_project_user_status", "user_id", "status"),
        db.Index("ix_project_user_target_date", "user_id", "target_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        db.ForeignKey("user.id"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(db.Text)
    status: Mapped[str] = mapped_column(db.String(32), default="active", nullable=False)
    target_date: Mapped[date | None] = mapped_column(db.Date)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    tasks: Mapped[list["ProjectTask"]] = relationship(
        "ProjectTask", back_populates="project", cascade="all, delete-orphan"
    )


class ProjectTask(db.Model):
    __tablename__ = "project_task"
    __table_args__ = (
        db.Index(
            "ix_project_task_user_project_status", "user_id", "project_id", "status"
        ),
        db.Index("ix_project_task_user_due_date", "user_id", "due_date"),
        db.Index(
            "ix_project_task_user_project_due_date", "user_id", "project_id", "due_date"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        db.ForeignKey("user.id"), index=True, nullable=False
    )
    project_id: Mapped[int] = mapped_column(
        db.ForeignKey("project.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(db.String(255), nullable=False)
    status: Mapped[str] = mapped_column(db.String(32), default="open", nullable=False)
    due_date: Mapped[date | None] = mapped_column(db.Date)
    priority: Mapped[int | None] = mapped_column(db.Integer)
    notes: Mapped[str | None] = mapped_column(db.Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    project: Mapped[Project] = relationship(Project, back_populates="tasks")
    logs: Mapped[list["ProjectTaskLog"]] = relationship(
        "ProjectTaskLog", back_populates="task", cascade="all, delete-orphan"
    )


class ProjectTaskLog(db.Model):
    __tablename__ = "project_task_log"
    __table_args__ = (
        db.Index(
            "ix_project_task_log_user_task_logged_at", "user_id", "task_id", "logged_at"
        ),
        db.Index("ix_project_task_log_user_logged_at", "user_id", "logged_at"),
        db.Index("ix_project_task_log_calendar_event", "calendar_event_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        db.ForeignKey("user.id"), index=True, nullable=False
    )
    task_id: Mapped[int] = mapped_column(
        db.ForeignKey("project_task.id", ondelete="CASCADE"), index=True, nullable=False
    )
    note: Mapped[str | None] = mapped_column(db.Text)
    logged_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    status_snapshot: Mapped[str | None] = mapped_column(db.String(32))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Calendar inference fields
    source: Mapped[str] = mapped_column(db.String(32), default="manual", nullable=False)
    calendar_event_id: Mapped[int | None] = mapped_column(
        db.ForeignKey("calendar_event.id", ondelete="SET NULL"), nullable=True
    )
    confidence_score: Mapped[float | None] = mapped_column(
        db.Numeric(3, 2), nullable=True
    )
    inference_status: Mapped[str | None] = mapped_column(db.String(16), nullable=True)

    task: Mapped[ProjectTask] = relationship(ProjectTask, back_populates="logs")


__all__ = ["Project", "ProjectTask", "ProjectTaskLog"]

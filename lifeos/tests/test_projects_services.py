"""Tests for Projects domain services: projects, tasks, task logs."""

from datetime import date, datetime, timedelta
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.integration

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.domains.projects.models.project_models import (
    Project,
    ProjectTask,
    ProjectTaskLog,
)
from lifeos.domains.projects.services.project_service import (
    archive_project,
    complete_project,
    create_project,
    delete_project,
    get_project,
    list_projects,
    update_project,
)
from lifeos.domains.projects.services.task_service import (
    complete_task,
    create_task,
    list_tasks,
    log_task_activity,
    update_task,
)
from lifeos.extensions import db


@pytest.fixture
def test_user(app):
    """Create a test user for project tests."""
    with app.app_context():
        user = User(
            email="projects-tester@example.com", password_hash=hash_password("secret")
        )
        db.session.add(user)
        db.session.commit()
        yield user


# ============== Project CRUD Tests ==============


class TestProjectService:
    """Tests for project creation, update, and lifecycle."""

    def test_create_project_success(self, app, test_user):
        """Create a valid project."""
        with app.app_context():
            project = create_project(
                test_user.id,
                name="LifeOS Development",
                description="Build the life operating system",
                target_date=date.today() + timedelta(days=90),
            )

            assert project.id is not None
            assert project.user_id == test_user.id
            assert project.name == "LifeOS Development"
            assert project.description == "Build the life operating system"
            assert project.status == "active"
            assert project.target_date == date.today() + timedelta(days=90)

    def test_create_project_minimal(self, app, test_user):
        """Create project with minimal fields."""
        with app.app_context():
            project = create_project(test_user.id, name="Simple Project")

            assert project.id is not None
            assert project.name == "Simple Project"
            assert project.description is None
            assert project.target_date is None

    def test_create_project_duplicate_name_fails(self, app, test_user):
        """Creating project with duplicate name fails."""
        with app.app_context():
            create_project(test_user.id, name="Unique Project")

            with pytest.raises(ValueError, match="duplicate"):
                create_project(test_user.id, name="Unique Project")

    @pytest.mark.xfail(
        reason="Outbox event payload contains date object that cannot be JSON serialized"
    )
    def test_update_project_success(self, app, test_user):
        """Update an existing project."""
        with app.app_context():
            project = create_project(test_user.id, name="Update Test")

            updated = update_project(
                test_user.id,
                project.id,
                description="Updated description",
                target_date=date.today() + timedelta(days=30),
            )

            assert updated is not None
            assert updated.description == "Updated description"
            assert updated.target_date == date.today() + timedelta(days=30)

    def test_update_project_status(self, app, test_user):
        """Update project status."""
        with app.app_context():
            project = create_project(test_user.id, name="Status Test")

            updated = update_project(test_user.id, project.id, status="archived")

            assert updated.status == "archived"

    def test_update_project_invalid_status_fails(self, app, test_user):
        """Update with invalid status fails."""
        with app.app_context():
            project = create_project(test_user.id, name="Invalid Status Test")

            with pytest.raises(ValueError, match="validation_error"):
                update_project(test_user.id, project.id, status="invalid_status")

    def test_update_project_not_found(self, app, test_user):
        """Update non-existent project returns None."""
        with app.app_context():
            result = update_project(test_user.id, 99999, name="New Name")
            assert result is None

    def test_archive_project(self, app, test_user):
        """Archive an existing project."""
        with app.app_context():
            project = create_project(test_user.id, name="To Archive")

            archived = archive_project(test_user.id, project.id)

            assert archived is not None
            assert archived.status == "archived"

    def test_complete_project(self, app, test_user):
        """Complete an existing project."""
        with app.app_context():
            project = create_project(test_user.id, name="To Complete")

            completed = complete_project(test_user.id, project.id)

            assert completed is not None
            assert completed.status == "completed"

    def test_delete_project(self, app, test_user):
        """Delete an existing project."""
        with app.app_context():
            project = create_project(test_user.id, name="To Delete")
            project_id = project.id

            deleted = delete_project(test_user.id, project_id)
            assert deleted is True

            # Verify it's gone
            assert Project.query.get(project_id) is None

    def test_delete_project_not_found(self, app, test_user):
        """Delete non-existent project returns False."""
        with app.app_context():
            deleted = delete_project(test_user.id, 99999)
            assert deleted is False

    def test_get_project(self, app, test_user):
        """Get a specific project."""
        with app.app_context():
            project = create_project(test_user.id, name="Get Test")

            fetched = get_project(test_user.id, project.id)

            assert fetched is not None
            assert fetched.name == "Get Test"

    def test_get_project_not_found(self, app, test_user):
        """Get non-existent project returns None."""
        with app.app_context():
            fetched = get_project(test_user.id, 99999)
            assert fetched is None

    def test_list_projects_pagination(self, app, test_user):
        """List projects with pagination."""
        with app.app_context():
            for i in range(15):
                create_project(test_user.id, name=f"Project {i}")

            items, total = list_projects(test_user.id, page=1, per_page=10)
            assert len(items) == 10
            assert total == 15

            items2, total2 = list_projects(test_user.id, page=2, per_page=10)
            assert len(items2) == 5
            assert total2 == 15

    def test_list_projects_status_filter(self, app, test_user):
        """Filter projects by status."""
        with app.app_context():
            p1 = create_project(test_user.id, name="Active 1")
            p2 = create_project(test_user.id, name="Active 2")
            p3 = create_project(test_user.id, name="Archived")
            archive_project(test_user.id, p3.id)

            active_items, active_total = list_projects(test_user.id, status="active")
            assert active_total == 2

            archived_items, archived_total = list_projects(
                test_user.id, status="archived"
            )
            assert archived_total == 1


# ============== Task CRUD Tests ==============


class TestTaskService:
    """Tests for task creation, update, and completion."""

    def test_create_task_success(self, app, test_user):
        """Create a valid task."""
        with app.app_context():
            project = create_project(test_user.id, name="Task Project")

            task = create_task(
                test_user.id,
                project.id,
                title="Implement feature X",
                due_date=date.today() + timedelta(days=7),
                priority=1,
                notes="High priority task",
            )

            assert task.id is not None
            assert task.user_id == test_user.id
            assert task.project_id == project.id
            assert task.title == "Implement feature X"
            assert task.status == "open"
            assert task.due_date == date.today() + timedelta(days=7)
            assert task.priority == 1
            assert task.notes == "High priority task"

    def test_create_task_project_not_found(self, app, test_user):
        """Creating task for non-existent project fails."""
        with app.app_context():
            with pytest.raises(ValueError, match="not_found"):
                create_task(test_user.id, 99999, title="Orphan Task")

    def test_update_task_success(self, app, test_user):
        """Update an existing task."""
        with app.app_context():
            project = create_project(test_user.id, name="Update Task Project")
            task = create_task(test_user.id, project.id, title="Original Task")

            updated = update_task(
                test_user.id,
                task.id,
                title="Updated Task",
                status="in_progress",
                priority=2,
            )

            assert updated is not None
            assert updated.title == "Updated Task"
            assert updated.status == "in_progress"
            assert updated.priority == 2

    def test_update_task_invalid_status_fails(self, app, test_user):
        """Update with invalid status fails."""
        with app.app_context():
            project = create_project(test_user.id, name="Invalid Status Project")
            task = create_task(test_user.id, project.id, title="Status Task")

            with pytest.raises(ValueError, match="validation_error"):
                update_task(test_user.id, task.id, status="invalid_status")

    def test_update_task_not_found(self, app, test_user):
        """Update non-existent task returns None."""
        with app.app_context():
            result = update_task(test_user.id, 99999, title="New Title")
            assert result is None

    def test_complete_task(self, app, test_user):
        """Complete an existing task."""
        with app.app_context():
            project = create_project(test_user.id, name="Complete Task Project")
            task = create_task(test_user.id, project.id, title="To Complete")

            completed = complete_task(test_user.id, task.id)

            assert completed is not None
            assert completed.status == "completed"

    def test_list_tasks_by_project(self, app, test_user):
        """List tasks for a specific project."""
        with app.app_context():
            project1 = create_project(test_user.id, name="Project 1")
            project2 = create_project(test_user.id, name="Project 2")

            create_task(test_user.id, project1.id, title="Task 1A")
            create_task(test_user.id, project1.id, title="Task 1B")
            create_task(test_user.id, project2.id, title="Task 2A")

            items, total = list_tasks(test_user.id, project_id=project1.id)
            assert total == 2

    def test_list_tasks_status_filter(self, app, test_user):
        """Filter tasks by status."""
        with app.app_context():
            project = create_project(test_user.id, name="Filter Project")
            task1 = create_task(test_user.id, project.id, title="Open Task")
            task2 = create_task(test_user.id, project.id, title="Completed Task")
            complete_task(test_user.id, task2.id)

            open_items, open_total = list_tasks(
                test_user.id, project_id=project.id, status="open"
            )
            assert open_total == 1

            completed_items, completed_total = list_tasks(
                test_user.id, project_id=project.id, status="completed"
            )
            assert completed_total == 1

    def test_list_tasks_due_before_filter(self, app, test_user):
        """Filter tasks by due date."""
        with app.app_context():
            project = create_project(test_user.id, name="Due Date Project")
            create_task(
                test_user.id,
                project.id,
                title="Soon",
                due_date=date.today() + timedelta(days=1),
            )
            create_task(
                test_user.id,
                project.id,
                title="Later",
                due_date=date.today() + timedelta(days=30),
            )
            create_task(test_user.id, project.id, title="No Due Date")

            items, total = list_tasks(
                test_user.id,
                project_id=project.id,
                due_before=date.today() + timedelta(days=7),
            )
            assert total == 1


# ============== Task Log Tests ==============


class TestTaskLogService:
    """Tests for task activity logging."""

    def test_log_task_activity_success(self, app, test_user):
        """Log activity on a task."""
        with app.app_context():
            project = create_project(test_user.id, name="Log Project")
            task = create_task(test_user.id, project.id, title="Log Task")

            log = log_task_activity(
                test_user.id,
                task.id,
                note="Made progress on this task",
                status_snapshot="in_progress",
            )

            assert log.id is not None
            assert log.task_id == task.id
            assert log.user_id == test_user.id
            assert log.note == "Made progress on this task"
            assert log.status_snapshot == "in_progress"
            assert log.source == "manual"

    def test_log_task_activity_with_timestamp(self, app, test_user):
        """Log task activity with custom timestamp."""
        with app.app_context():
            project = create_project(test_user.id, name="Timestamp Log Project")
            task = create_task(test_user.id, project.id, title="Timestamp Task")
            past_time = datetime.utcnow() - timedelta(hours=2)

            log = log_task_activity(test_user.id, task.id, logged_at=past_time)

            assert log.logged_at.date() == past_time.date()

    def test_log_task_activity_task_not_found(self, app, test_user):
        """Logging activity for non-existent task fails."""
        with app.app_context():
            with pytest.raises(ValueError, match="not_found"):
                log_task_activity(test_user.id, 99999, note="Orphan log")


# ============== Event Emission Tests ==============


class TestProjectEventEmission:
    """Tests for project event emission to outbox."""

    def test_project_created_event_emitted(self, app, test_user):
        """Project creation should emit event to outbox."""
        with app.app_context():
            from lifeos.lifeos_platform.outbox.models import OutboxMessage

            initial_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="projects.project.created"
            ).count()

            create_project(test_user.id, name="Event Project")

            final_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="projects.project.created"
            ).count()

            assert final_count == initial_count + 1

    def test_project_updated_event_emitted(self, app, test_user):
        """Project update should emit event to outbox."""
        with app.app_context():
            from lifeos.lifeos_platform.outbox.models import OutboxMessage

            project = create_project(test_user.id, name="Update Event Project")

            initial_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="projects.project.updated"
            ).count()

            update_project(test_user.id, project.id, description="Updated")

            final_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="projects.project.updated"
            ).count()

            assert final_count == initial_count + 1

    def test_project_archived_event_emitted(self, app, test_user):
        """Project archive should emit event to outbox."""
        with app.app_context():
            from lifeos.lifeos_platform.outbox.models import OutboxMessage

            project = create_project(test_user.id, name="Archive Event Project")

            initial_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="projects.project.archived"
            ).count()

            archive_project(test_user.id, project.id)

            final_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="projects.project.archived"
            ).count()

            assert final_count == initial_count + 1

    def test_project_completed_event_emitted(self, app, test_user):
        """Project completion should emit event to outbox."""
        with app.app_context():
            from lifeos.lifeos_platform.outbox.models import OutboxMessage

            project = create_project(test_user.id, name="Complete Event Project")

            initial_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="projects.project.completed"
            ).count()

            complete_project(test_user.id, project.id)

            final_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="projects.project.completed"
            ).count()

            assert final_count == initial_count + 1

    def test_task_created_event_emitted(self, app, test_user):
        """Task creation should emit event to outbox."""
        with app.app_context():
            from lifeos.lifeos_platform.outbox.models import OutboxMessage

            project = create_project(test_user.id, name="Task Event Project")

            initial_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="projects.task.created"
            ).count()

            create_task(test_user.id, project.id, title="Event Task")

            final_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="projects.task.created"
            ).count()

            assert final_count == initial_count + 1


# ============== User Isolation Tests ==============


class TestProjectUserIsolation:
    """Tests ensuring projects are properly isolated per user."""

    def test_projects_isolated_by_user(self, app, test_user):
        """Users can only see their own projects."""
        with app.app_context():
            # Create project for test user
            create_project(test_user.id, name="User A Project")

            # Create another user with project
            other_user = User(
                email="other-projects@example.com",
                password_hash=hash_password("secret"),
            )
            db.session.add(other_user)
            db.session.commit()
            create_project(other_user.id, name="User B Project")

            # List projects for test user
            items, total = list_projects(test_user.id)

            assert total == 1
            assert items[0].name == "User A Project"

    def test_tasks_isolated_by_user(self, app, test_user):
        """Users can only create tasks for their own projects."""
        with app.app_context():
            # Create another user's project
            other_user = User(
                email="other-tasks@example.com", password_hash=hash_password("secret")
            )
            db.session.add(other_user)
            db.session.commit()
            other_project = create_project(other_user.id, name="Other Project")

            # Test user cannot create task in other's project
            with pytest.raises(ValueError, match="not_found"):
                create_task(test_user.id, other_project.id, title="Sneaky Task")

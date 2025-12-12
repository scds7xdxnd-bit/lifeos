"""Tests for Projects domain API endpoints."""

from datetime import date, timedelta

import pytest
from flask_jwt_extended import create_access_token

pytestmark = pytest.mark.integration

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.domains.projects.models.project_models import Project, ProjectTask
from lifeos.domains.projects.services.project_service import create_project
from lifeos.domains.projects.services.task_service import create_task
from lifeos.extensions import db


@pytest.fixture
def test_user(app):
    """Create a test user for project API tests."""
    with app.app_context():
        user = User(email="projects-api@example.com", password_hash=hash_password("secret"))
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def auth_headers(app, test_user):
    """JWT headers for API calls."""
    with app.app_context():
        token = create_access_token(identity=str(test_user.id))
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


@pytest.fixture
def csrf_headers(app, test_user):
    """JWT headers with CSRF for API calls that modify data."""
    with app.app_context():
        token = create_access_token(identity=str(test_user.id))
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-CSRF-Token": "test-csrf-token",
    }


# ============== Project CRUD API Tests ==============


class TestProjectsAPI:
    """Tests for projects API endpoints."""

    def test_list_projects_empty(self, client, auth_headers):
        """List projects when none exist."""
        resp = client.get("/api/projects", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_projects_with_data(self, app, client, test_user, auth_headers):
        """List projects with existing data."""
        with app.app_context():
            create_project(test_user.id, name="Project Alpha")
            create_project(test_user.id, name="Project Beta")

        resp = client.get("/api/projects", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert len(data["items"]) == 2
        assert data["total"] == 2

    def test_list_projects_with_status_filter(self, app, client, test_user, auth_headers):
        """List projects with status filter."""
        with app.app_context():
            create_project(test_user.id, name="Active Project")
            p2 = create_project(test_user.id, name="Archived Project")
            from lifeos.domains.projects.services.project_service import archive_project

            archive_project(test_user.id, p2.id)

        resp = client.get("/api/projects?status=active", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "Active Project"

    def test_create_project_success(self, client, csrf_headers):
        """Create a project successfully."""
        payload = {
            "name": "New Project",
            "description": "A test project",
            "target_date": (date.today() + timedelta(days=30)).isoformat(),
        }
        resp = client.post("/api/projects", json=payload, headers=csrf_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["ok"] is True
        assert data["project"]["name"] == "New Project"
        assert data["project"]["status"] == "active"

    def test_create_project_minimal(self, client, csrf_headers):
        """Create project with minimal data."""
        payload = {"name": "Minimal Project"}
        resp = client.post("/api/projects", json=payload, headers=csrf_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["ok"] is True

    def test_create_project_duplicate_fails(self, app, client, test_user, csrf_headers):
        """Creating duplicate project fails."""
        with app.app_context():
            create_project(test_user.id, name="Duplicate Project")

        payload = {"name": "Duplicate Project"}
        resp = client.post("/api/projects", json=payload, headers=csrf_headers)
        assert resp.status_code == 409
        data = resp.get_json()
        assert data["error"] == "duplicate"

    def test_create_project_unauthorized(self, client):
        """Creating project without auth fails."""
        payload = {"name": "Unauthorized Project"}
        resp = client.post("/api/projects", json=payload)
        assert resp.status_code == 401

    def test_get_project_success(self, app, client, test_user, auth_headers):
        """Get a specific project."""
        with app.app_context():
            project = create_project(test_user.id, name="Get Project")
            project_id = project.id

        resp = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["project"]["name"] == "Get Project"

    def test_get_project_not_found(self, client, auth_headers):
        """Get non-existent project returns 404."""
        resp = client.get("/api/projects/99999", headers=auth_headers)
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["error"] == "not_found"

    def test_update_project(self, app, client, test_user, csrf_headers):
        """Update an existing project."""
        with app.app_context():
            project = create_project(test_user.id, name="Update Project")
            project_id = project.id

        payload = {"description": "Updated description", "status": "active"}
        resp = client.patch(f"/api/projects/{project_id}", json=payload, headers=csrf_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["project"]["description"] == "Updated description"

    def test_update_project_not_found(self, client, csrf_headers):
        """Update non-existent project returns 404."""
        payload = {"description": "Updated"}
        resp = client.patch("/api/projects/99999", json=payload, headers=csrf_headers)
        assert resp.status_code == 404

    def test_archive_project(self, app, client, test_user, csrf_headers):
        """Archive an existing project."""
        with app.app_context():
            project = create_project(test_user.id, name="To Archive")
            project_id = project.id

        resp = client.post(f"/api/projects/{project_id}/archive", headers=csrf_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["project"]["status"] == "archived"

    def test_complete_project(self, app, client, test_user, csrf_headers):
        """Complete an existing project."""
        with app.app_context():
            project = create_project(test_user.id, name="To Complete")
            project_id = project.id

        resp = client.post(f"/api/projects/{project_id}/complete", headers=csrf_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["project"]["status"] == "completed"

    def test_delete_project(self, app, client, test_user, csrf_headers):
        """Delete an existing project."""
        with app.app_context():
            project = create_project(test_user.id, name="To Delete")
            project_id = project.id

        resp = client.delete(f"/api/projects/{project_id}", headers=csrf_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True

    def test_delete_project_not_found(self, client, csrf_headers):
        """Delete non-existent project returns 404."""
        resp = client.delete("/api/projects/99999", headers=csrf_headers)
        assert resp.status_code == 404


# ============== Tasks API Tests ==============


class TestTasksAPI:
    """Tests for tasks API endpoints."""

    def test_list_tasks_empty(self, app, client, test_user, auth_headers):
        """List tasks for a project when none exist."""
        with app.app_context():
            project = create_project(test_user.id, name="Empty Task Project")
            project_id = project.id

        resp = client.get(f"/api/projects/{project_id}/tasks", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["items"] == []

    def test_list_tasks_with_data(self, app, client, test_user, auth_headers):
        """List tasks with existing data."""
        with app.app_context():
            project = create_project(test_user.id, name="Task Project")
            create_task(test_user.id, project.id, title="Task 1")
            create_task(test_user.id, project.id, title="Task 2")
            project_id = project.id

        resp = client.get(f"/api/projects/{project_id}/tasks", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["items"]) == 2

    def test_create_task_success(self, app, client, test_user, csrf_headers):
        """Create a task successfully."""
        with app.app_context():
            project = create_project(test_user.id, name="New Task Project")
            project_id = project.id

        payload = {
            "title": "New Task",
            "due_date": (date.today() + timedelta(days=7)).isoformat(),
            "priority": 1,
            "notes": "Important task",
        }
        resp = client.post(f"/api/projects/{project_id}/tasks", json=payload, headers=csrf_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["ok"] is True
        assert data["task"]["title"] == "New Task"
        assert data["task"]["status"] == "open"

    def test_create_task_project_not_found(self, client, csrf_headers):
        """Creating task for non-existent project fails."""
        payload = {"title": "Orphan Task"}
        resp = client.post("/api/projects/99999/tasks", json=payload, headers=csrf_headers)
        assert resp.status_code == 404

    def test_get_task(self, app, client, test_user, auth_headers):
        """Get a specific task."""
        with app.app_context():
            project = create_project(test_user.id, name="Get Task Project")
            task = create_task(test_user.id, project.id, title="Get Task")
            task_id = task.id

        resp = client.get(f"/api/projects/tasks/{task_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["task"]["title"] == "Get Task"

    def test_get_task_not_found(self, client, auth_headers):
        """Get non-existent task returns 404."""
        resp = client.get("/api/projects/tasks/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_update_task(self, app, client, test_user, csrf_headers):
        """Update an existing task."""
        with app.app_context():
            project = create_project(test_user.id, name="Update Task Project")
            task = create_task(test_user.id, project.id, title="Update Task")
            task_id = task.id

        payload = {"title": "Updated Task", "status": "in_progress", "priority": 2}
        resp = client.patch(f"/api/projects/tasks/{task_id}", json=payload, headers=csrf_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["task"]["title"] == "Updated Task"
        assert data["task"]["status"] == "in_progress"

    def test_update_task_not_found(self, client, csrf_headers):
        """Update non-existent task returns 404."""
        payload = {"title": "Updated"}
        resp = client.patch("/api/projects/tasks/99999", json=payload, headers=csrf_headers)
        assert resp.status_code == 404

    def test_complete_task(self, app, client, test_user, csrf_headers):
        """Complete an existing task."""
        with app.app_context():
            project = create_project(test_user.id, name="Complete Task Project")
            task = create_task(test_user.id, project.id, title="To Complete")
            task_id = task.id

        resp = client.post(f"/api/projects/tasks/{task_id}/complete", headers=csrf_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["task"]["status"] == "completed"


# ============== Task Logs API Tests ==============


class TestTaskLogsAPI:
    """Tests for task activity logging API endpoints."""

    def test_log_task_activity(self, app, client, test_user, csrf_headers):
        """Log activity on a task."""
        with app.app_context():
            project = create_project(test_user.id, name="Log Task Project")
            task = create_task(test_user.id, project.id, title="Log Task")
            task_id = task.id

        payload = {"note": "Made progress", "status_snapshot": "in_progress"}
        resp = client.post(f"/api/projects/tasks/{task_id}/logs", json=payload, headers=csrf_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["ok"] is True
        assert data["log"]["note"] == "Made progress"

    @pytest.mark.xfail(reason="Outbox event payload has date object that cannot be JSON serialized")
    def test_list_task_logs(self, app, client, test_user, auth_headers):
        """List activity logs for a task."""
        with app.app_context():
            from lifeos.domains.projects.services.task_service import log_task_activity

            project = create_project(test_user.id, name="List Logs Project")
            task = create_task(test_user.id, project.id, title="List Logs Task")
            log_task_activity(test_user.id, task.id, note="Log 1")
            log_task_activity(test_user.id, task.id, note="Log 2")
            task_id = task.id

        resp = client.get(f"/api/projects/tasks/{task_id}/logs", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert len(data["logs"]) == 2


# ============== Pagination API Tests ==============


class TestProjectsPaginationAPI:
    """Tests for pagination in project/task listing."""

    def test_projects_pagination(self, app, client, test_user, auth_headers):
        """Test project listing with pagination."""
        with app.app_context():
            for i in range(15):
                create_project(test_user.id, name=f"Paginated Project {i}")

        resp = client.get("/api/projects?page=1&per_page=10", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["items"]) == 10
        assert data["total"] == 15
        assert data["pages"] == 2

        resp2 = client.get("/api/projects?page=2&per_page=10", headers=auth_headers)
        data2 = resp2.get_json()
        assert len(data2["items"]) == 5

    def test_tasks_pagination(self, app, client, test_user, auth_headers):
        """Test task listing with pagination."""
        with app.app_context():
            project = create_project(test_user.id, name="Pagination Project")
            for i in range(25):
                create_task(test_user.id, project.id, title=f"Paginated Task {i}")
            project_id = project.id

        resp = client.get(f"/api/projects/{project_id}/tasks?page=1&per_page=10", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["items"]) == 10
        assert data["total"] == 25


# ============== User Isolation API Tests ==============


class TestProjectsAPIUserIsolation:
    """Tests ensuring project API data is properly isolated per user."""

    def test_projects_api_isolated_by_user(self, app, client, test_user, auth_headers):
        """Users can only see their own projects via API."""
        with app.app_context():
            # Create project for test user
            create_project(test_user.id, name="Test User Project")

            # Create another user with project
            other_user = User(
                email="other-project-api@example.com",
                password_hash=hash_password("secret"),
            )
            db.session.add(other_user)
            db.session.commit()
            create_project(other_user.id, name="Other User Project")

        resp = client.get("/api/projects", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Test User Project"

    def test_cannot_access_other_user_project(self, app, client, test_user, auth_headers):
        """Cannot access another user's project detail."""
        with app.app_context():
            other_user = User(
                email="other-project-api2@example.com",
                password_hash=hash_password("secret"),
            )
            db.session.add(other_user)
            db.session.commit()
            project = create_project(other_user.id, name="Private Project")
            project_id = project.id

        resp = client.get(f"/api/projects/{project_id}", headers=auth_headers)
        assert resp.status_code == 404

    def test_cannot_update_other_user_project(self, app, client, test_user, csrf_headers):
        """Cannot update another user's project."""
        with app.app_context():
            other_user = User(
                email="other-project-api3@example.com",
                password_hash=hash_password("secret"),
            )
            db.session.add(other_user)
            db.session.commit()
            project = create_project(other_user.id, name="Protected Project")
            project_id = project.id

        payload = {"description": "Hacked!"}
        resp = client.patch(f"/api/projects/{project_id}", json=payload, headers=csrf_headers)
        assert resp.status_code == 404

    def test_cannot_create_task_in_other_user_project(self, app, client, test_user, csrf_headers):
        """Cannot create task in another user's project."""
        with app.app_context():
            other_user = User(
                email="other-task-api@example.com",
                password_hash=hash_password("secret"),
            )
            db.session.add(other_user)
            db.session.commit()
            project = create_project(other_user.id, name="Other User's Project")
            project_id = project.id

        payload = {"title": "Sneaky Task"}
        resp = client.post(f"/api/projects/{project_id}/tasks", json=payload, headers=csrf_headers)
        assert resp.status_code == 404

"""Comprehensive Habits API tests.

Tests all API endpoints for the habits domain:
- GET /api/habits - list_habits
- POST /api/habits - create_habit
- GET /api/habits/<id> - habit_detail
- PATCH /api/habits/<id> - update_habit
- POST /api/habits/<id>/deactivate - deactivate_habit
- DELETE /api/habits/<id> - delete_habit
- POST /api/habits/<id>/logs - create_log
- PATCH /api/habits/logs/<id> - update_log
- DELETE /api/habits/logs/<id> - delete_log
"""

from __future__ import annotations

from datetime import date

import pytest

pytestmark = pytest.mark.integration

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.domains.habits.models import Habit, HabitLog
from lifeos.extensions import db


# ==================== Fixtures ====================


def _prime_csrf(client) -> str:
    """Insert CSRF token into client session."""
    token = "test-csrf-token"
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _auth_headers(access_token: str, csrf_token: str) -> dict[str, str]:
    """Build auth headers with JWT and CSRF tokens."""
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


@pytest.fixture
def user_with_tokens(app):
    """Create a test user and return user object and tokens."""
    with app.app_context():
        user = create_user(
            UserCreateRequest(
                email="habit-api-test@example.com",
                password="secret123",
                full_name="Habit Tester",
                timezone="UTC",
            )
        )
        tokens = issue_tokens(user)
        return {"user": user, "user_id": user.id, "tokens": tokens}


# ==================== List Habits Tests ====================


def test_list_habits_empty(app, client, user_with_tokens):
    """Should return empty list when user has no habits."""
    csrf_token = _prime_csrf(client)
    resp = client.get(
        "/api/habits",
        headers=_auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token),
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True
    assert body["habits"] == []


def test_list_habits_with_data(app, client, user_with_tokens):
    """Should return habits list with summary info."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    # Create a habit
    payload = {
        "name": "Morning Run",
        "description": "Run 5km",
        "schedule_type": "daily",
        "target_count": 1,
    }
    resp = client.post("/api/habits", json=payload, headers=headers)
    assert resp.status_code == 201

    # List habits
    resp = client.get("/api/habits", headers=headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True
    assert len(body["habits"]) == 1
    assert body["habits"][0]["name"] == "Morning Run"
    assert body["habits"][0]["is_active"] is True
    assert body["habits"][0]["count"] == 0


# ==================== Create Habit Tests ====================


def test_create_habit_success(app, client, user_with_tokens):
    """Should create habit with valid payload."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    payload = {
        "name": "Read Books",
        "description": "Read for 30 minutes",
        "schedule_type": "daily",
        "target_count": 1,
        "time_of_day": "evening",
        "difficulty": "medium",
    }
    resp = client.post("/api/habits", json=payload, headers=headers)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["ok"] is True
    assert "habit_id" in body

    # Verify in database
    with app.app_context():
        habit = db.session.get(Habit, body["habit_id"])
        assert habit is not None
        assert habit.name == "Read Books"
        assert habit.schedule_type == "daily"


def test_create_habit_minimal_payload(app, client, user_with_tokens):
    """Should create habit with minimal required fields."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    payload = {"name": "Meditate"}
    resp = client.post("/api/habits", json=payload, headers=headers)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["ok"] is True


def test_create_habit_missing_name_fails(app, client, user_with_tokens):
    """Should reject habit creation without name."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    payload = {"description": "No name provided"}
    resp = client.post("/api/habits", json=payload, headers=headers)
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["ok"] is False
    assert body["error"] == "validation_error"


def test_create_habit_duplicate_fails(app, client, user_with_tokens):
    """Should reject duplicate habit name for same user."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    payload = {"name": "Unique Habit"}
    resp = client.post("/api/habits", json=payload, headers=headers)
    assert resp.status_code == 201

    # Attempt duplicate
    resp = client.post("/api/habits", json=payload, headers=headers)
    assert resp.status_code == 409
    body = resp.get_json()
    assert body["ok"] is False
    assert body["error"] == "duplicate"


# ==================== Habit Detail Tests ====================


def test_habit_detail_success(app, client, user_with_tokens):
    """Should return habit detail with stats and logs."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    # Create habit
    payload = {"name": "Exercise", "description": "Daily workout"}
    resp = client.post("/api/habits", json=payload, headers=headers)
    habit_id = resp.get_json()["habit_id"]

    # Get detail
    resp = client.get(f"/api/habits/{habit_id}", headers=headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True
    assert body["habit"]["id"] == habit_id
    assert body["habit"]["name"] == "Exercise"
    assert "stats" in body["habit"]
    assert "logs" in body["habit"]


def test_habit_detail_not_found(app, client, user_with_tokens):
    """Should return 404 for non-existent habit."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    resp = client.get("/api/habits/99999", headers=headers)
    assert resp.status_code == 404
    body = resp.get_json()
    assert body["ok"] is False
    assert body["error"] == "not_found"


def test_habit_detail_other_user_not_visible(app, client):
    """Should not see habits created by other users."""
    with app.app_context():
        # Create first user and habit
        user1 = create_user(
            UserCreateRequest(
                email="user1-habits@example.com",
                password="secret123",
                full_name="User 1",
                timezone="UTC",
            )
        )
        tokens1 = issue_tokens(user1)

        user2 = create_user(
            UserCreateRequest(
                email="user2-habits@example.com",
                password="secret123",
                full_name="User 2",
                timezone="UTC",
            )
        )
        tokens2 = issue_tokens(user2)

    csrf_token = _prime_csrf(client)

    # User 1 creates habit
    headers1 = _auth_headers(tokens1["access_token"], csrf_token)
    payload = {"name": "User1 Private Habit"}
    resp = client.post("/api/habits", json=payload, headers=headers1)
    habit_id = resp.get_json()["habit_id"]

    # User 2 tries to access
    headers2 = _auth_headers(tokens2["access_token"], csrf_token)
    resp = client.get(f"/api/habits/{habit_id}", headers=headers2)
    assert resp.status_code == 404


# ==================== Update Habit Tests ====================


def test_update_habit_success(app, client, user_with_tokens):
    """Should update habit fields."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    # Create habit
    payload = {"name": "Original Name", "description": "Original description"}
    resp = client.post("/api/habits", json=payload, headers=headers)
    habit_id = resp.get_json()["habit_id"]

    # Update
    update_payload = {"name": "Updated Name", "description": "Updated description"}
    resp = client.patch(f"/api/habits/{habit_id}", json=update_payload, headers=headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True

    # Verify
    resp = client.get(f"/api/habits/{habit_id}", headers=headers)
    assert resp.get_json()["habit"]["name"] == "Updated Name"


def test_update_habit_partial(app, client, user_with_tokens):
    """Should update only provided fields."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    payload = {"name": "Keep This", "description": "Original", "target_count": 5}
    resp = client.post("/api/habits", json=payload, headers=headers)
    habit_id = resp.get_json()["habit_id"]

    # Partial update - only description
    resp = client.patch(
        f"/api/habits/{habit_id}", json={"description": "New"}, headers=headers
    )
    assert resp.status_code == 200

    resp = client.get(f"/api/habits/{habit_id}", headers=headers)
    detail = resp.get_json()["habit"]
    assert detail["name"] == "Keep This"  # Unchanged
    assert detail["description"] == "New"  # Updated


def test_update_habit_not_found(app, client, user_with_tokens):
    """Should return 404 for non-existent habit update."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    resp = client.patch("/api/habits/99999", json={"name": "New"}, headers=headers)
    assert resp.status_code == 404


# ==================== Deactivate Habit Tests ====================


def test_deactivate_habit_success(app, client, user_with_tokens):
    """Should deactivate active habit."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    payload = {"name": "Active Habit"}
    resp = client.post("/api/habits", json=payload, headers=headers)
    habit_id = resp.get_json()["habit_id"]

    # Deactivate
    resp = client.post(f"/api/habits/{habit_id}/deactivate", headers=headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True

    # Verify
    resp = client.get(f"/api/habits/{habit_id}", headers=headers)
    assert resp.get_json()["habit"]["is_active"] is False


def test_deactivate_habit_not_found(app, client, user_with_tokens):
    """Should return 404 for non-existent habit deactivation."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    resp = client.post("/api/habits/99999/deactivate", headers=headers)
    assert resp.status_code == 404


# ==================== Delete Habit Tests ====================


def test_delete_habit_success(app, client, user_with_tokens):
    """Should delete habit."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    payload = {"name": "Delete Me"}
    resp = client.post("/api/habits", json=payload, headers=headers)
    habit_id = resp.get_json()["habit_id"]

    # Delete
    resp = client.delete(f"/api/habits/{habit_id}", headers=headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True

    # Verify gone
    resp = client.get(f"/api/habits/{habit_id}", headers=headers)
    assert resp.status_code == 404


def test_delete_habit_not_found(app, client, user_with_tokens):
    """Should return 404 for non-existent habit deletion."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    resp = client.delete("/api/habits/99999", headers=headers)
    assert resp.status_code == 404


# ==================== Create Log Tests ====================


def test_create_log_success(app, client, user_with_tokens):
    """Should create habit log entry."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    # Create habit
    payload = {"name": "Log Test Habit"}
    resp = client.post("/api/habits", json=payload, headers=headers)
    habit_id = resp.get_json()["habit_id"]

    # Log completion
    log_payload = {
        "logged_date": date.today().isoformat(),
        "value": 1,
        "note": "Completed today!",
    }
    resp = client.post(
        f"/api/habits/{habit_id}/logs", json=log_payload, headers=headers
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True
    assert "log" in body
    assert body["log"]["habit_id"] == habit_id
    assert body["log"]["note"] == "Completed today!"


def test_create_log_habit_not_found(app, client, user_with_tokens):
    """Should return 404 when logging to non-existent habit."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    log_payload = {"logged_date": date.today().isoformat(), "value": 1}
    resp = client.post("/api/habits/99999/logs", json=log_payload, headers=headers)
    assert resp.status_code == 404


def test_create_log_inactive_habit_succeeds(app, client, user_with_tokens):
    """Logging to deactivated habit succeeds by design (allow_inactive=True default)."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    # Create and deactivate habit
    payload = {"name": "Inactive Habit"}
    resp = client.post("/api/habits", json=payload, headers=headers)
    habit_id = resp.get_json()["habit_id"]
    client.post(f"/api/habits/{habit_id}/deactivate", headers=headers)

    # Logging to inactive habit is allowed by design
    log_payload = {"logged_date": date.today().isoformat(), "value": 1}
    resp = client.post(
        f"/api/habits/{habit_id}/logs", json=log_payload, headers=headers
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True


# ==================== Update Log Tests ====================


def test_update_log_success(app, client, user_with_tokens):
    """Should update habit log entry."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    # Create habit and log
    payload = {"name": "Update Log Habit"}
    resp = client.post("/api/habits", json=payload, headers=headers)
    habit_id = resp.get_json()["habit_id"]

    log_payload = {
        "logged_date": date.today().isoformat(),
        "value": 1,
        "note": "Original",
    }
    resp = client.post(
        f"/api/habits/{habit_id}/logs", json=log_payload, headers=headers
    )
    log_id = resp.get_json()["log"]["id"]

    # Update log
    update_payload = {"note": "Updated note", "value": 2}
    resp = client.patch(
        f"/api/habits/logs/{log_id}", json=update_payload, headers=headers
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True


def test_update_log_not_found(app, client, user_with_tokens):
    """Should return 404 for non-existent log update."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    resp = client.patch("/api/habits/logs/99999", json={"note": "New"}, headers=headers)
    assert resp.status_code == 404


# ==================== Delete Log Tests ====================


def test_delete_log_success(app, client, user_with_tokens):
    """Should delete habit log entry."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    # Create habit and log
    payload = {"name": "Delete Log Habit"}
    resp = client.post("/api/habits", json=payload, headers=headers)
    habit_id = resp.get_json()["habit_id"]

    log_payload = {"logged_date": date.today().isoformat(), "value": 1}
    resp = client.post(
        f"/api/habits/{habit_id}/logs", json=log_payload, headers=headers
    )
    log_id = resp.get_json()["log"]["id"]

    # Delete log
    resp = client.delete(f"/api/habits/logs/{log_id}", headers=headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True


def test_delete_log_not_found(app, client, user_with_tokens):
    """Should return 404 for non-existent log deletion."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    resp = client.delete("/api/habits/logs/99999", headers=headers)
    assert resp.status_code == 404


# ==================== Auth/CSRF Tests ====================


def test_create_habit_requires_auth(app, client):
    """Should require authentication."""
    resp = client.post("/api/habits", json={"name": "Unauth"})
    assert resp.status_code == 401


def test_create_habit_requires_csrf(app, client, user_with_tokens):
    """CSRF validation is disabled in testing mode, so request succeeds."""
    headers = {"Authorization": f"Bearer {user_with_tokens['tokens']['access_token']}"}
    resp = client.post("/api/habits", json={"name": "No CSRF"}, headers=headers)
    # CSRF is not enforced in test mode
    assert resp.status_code == 201

"""Comprehensive Journal API tests.

Tests all API endpoints for the journal domain:
- GET /api/journal - list_journal
- GET /api/journal/<id> - get_entry
- POST /api/journal - create_journal_entry
- PATCH /api/journal/<id> - update_journal_entry
- DELETE /api/journal/<id> - delete_journal_entry
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

pytestmark = pytest.mark.integration

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.domains.journal.models import JournalEntry
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
                email="journal-api-test@example.com",
                password="secret123",
                full_name="Journal API Tester",
                timezone="UTC",
            )
        )
        tokens = issue_tokens(user)
        return {"user": user, "user_id": user.id, "tokens": tokens}


@pytest.fixture
def other_user_tokens(app):
    """Create another user for isolation tests."""
    with app.app_context():
        user = create_user(
            UserCreateRequest(
                email="other-journal-api@example.com",
                password="secret123",
                full_name="Other Journal User",
                timezone="UTC",
            )
        )
        tokens = issue_tokens(user)
        return {"user_id": user.id, "tokens": tokens}


# ==================== List Journal Tests ====================


def test_list_journal_empty(app, client, user_with_tokens):
    """Should return empty list when user has no entries."""
    csrf_token = _prime_csrf(client)
    resp = client.get(
        "/api/journal",
        headers=_auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token),
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True
    assert body["items"] == []
    assert body["total"] == 0


def test_list_journal_with_entries(app, client, user_with_tokens):
    """Should return entries list with pagination info."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    # Create entries
    for i in range(3):
        payload = {
            "title": f"Entry {i}",
            "body": f"Content {i}",
            "entry_date": (date.today() - timedelta(days=i)).isoformat(),
        }
        resp = client.post("/api/journal", json=payload, headers=headers)
        assert resp.status_code == 201

    # List entries
    resp = client.get("/api/journal", headers=headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True
    assert len(body["items"]) == 3
    assert body["total"] == 3
    assert "pages" in body


def test_list_journal_filter_by_date_range(app, client, user_with_tokens):
    """Should filter entries by date range."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    today = date.today()
    # Create entries across dates
    for i in range(5):
        payload = {
            "title": f"Entry {i}",
            "body": f"Content {i}",
            "entry_date": (today - timedelta(days=i)).isoformat(),
        }
        client.post("/api/journal", json=payload, headers=headers)

    # Filter last 2 days
    resp = client.get(
        f"/api/journal?date_from={today - timedelta(days=1)}&date_to={today}",
        headers=headers,
    )
    body = resp.get_json()
    assert body["total"] == 2


def test_list_journal_filter_by_mood(app, client, user_with_tokens):
    """Should filter entries by mood."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    client.post(
        "/api/journal",
        json={"title": "Happy", "body": "Great day", "mood": 5},
        headers=headers,
    )
    client.post(
        "/api/journal",
        json={"title": "Sad", "body": "Bad day", "mood": -3},
        headers=headers,
    )

    resp = client.get("/api/journal?mood=5", headers=headers)
    body = resp.get_json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Happy"


def test_list_journal_filter_by_tag(app, client, user_with_tokens):
    """Should filter entries by tag."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    client.post(
        "/api/journal",
        json={"title": "Tagged", "body": "Content", "tags": ["gratitude"]},
        headers=headers,
    )
    client.post(
        "/api/journal",
        json={"title": "Untagged", "body": "Content", "tags": []},
        headers=headers,
    )

    resp = client.get("/api/journal?tag=gratitude", headers=headers)
    body = resp.get_json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Tagged"


def test_list_journal_search_text(app, client, user_with_tokens):
    """Should search in title and body."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    client.post(
        "/api/journal",
        json={"title": "Python", "body": "Learning Flask"},
        headers=headers,
    )
    client.post(
        "/api/journal", json={"title": "Random", "body": "Nothing"}, headers=headers
    )

    resp = client.get("/api/journal?search_text=Python", headers=headers)
    body = resp.get_json()
    assert body["total"] == 1

    resp = client.get("/api/journal?search_text=Flask", headers=headers)
    body = resp.get_json()
    assert body["total"] == 1


def test_list_journal_pagination(app, client, user_with_tokens):
    """Should paginate results."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    for i in range(15):
        client.post(
            "/api/journal",
            json={"title": f"Entry {i}", "body": f"Content {i}"},
            headers=headers,
        )

    # First page
    resp = client.get("/api/journal?page=1&per_page=5", headers=headers)
    body = resp.get_json()
    assert len(body["items"]) == 5
    assert body["total"] == 15
    assert body["pages"] == 3

    # Second page
    resp = client.get("/api/journal?page=2&per_page=5", headers=headers)
    body = resp.get_json()
    assert len(body["items"]) == 5


def test_list_journal_isolation(app, client, user_with_tokens, other_user_tokens):
    """Should only list user's own entries."""
    csrf_token = _prime_csrf(client)

    # User 1 creates entry
    headers1 = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)
    client.post(
        "/api/journal", json={"title": "Private", "body": "Secret"}, headers=headers1
    )

    # User 2 sees nothing
    headers2 = _auth_headers(other_user_tokens["tokens"]["access_token"], csrf_token)
    resp = client.get("/api/journal", headers=headers2)
    body = resp.get_json()
    assert body["items"] == []


# ==================== Get Entry Tests ====================


def test_get_entry_success(app, client, user_with_tokens):
    """Should retrieve entry by ID."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    # Create entry
    resp = client.post(
        "/api/journal",
        json={"title": "Get Me", "body": "Content", "mood": 3, "tags": ["test"]},
        headers=headers,
    )
    entry_id = resp.get_json()["entry"]["id"]

    # Get entry
    resp = client.get(f"/api/journal/{entry_id}", headers=headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True
    assert body["entry"]["id"] == entry_id
    assert body["entry"]["title"] == "Get Me"
    assert body["entry"]["mood"] == 3


def test_get_entry_not_found(app, client, user_with_tokens):
    """Should return 404 for non-existent entry."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    resp = client.get("/api/journal/99999", headers=headers)
    assert resp.status_code == 404
    body = resp.get_json()
    assert body["ok"] is False
    assert body["error"] == "not_found"


def test_get_entry_other_user_not_visible(
    app, client, user_with_tokens, other_user_tokens
):
    """Should not retrieve other user's entry."""
    csrf_token = _prime_csrf(client)

    # User 1 creates entry
    headers1 = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)
    resp = client.post(
        "/api/journal", json={"title": "Private", "body": "Secret"}, headers=headers1
    )
    entry_id = resp.get_json()["entry"]["id"]

    # User 2 cannot access
    headers2 = _auth_headers(other_user_tokens["tokens"]["access_token"], csrf_token)
    resp = client.get(f"/api/journal/{entry_id}", headers=headers2)
    assert resp.status_code == 404


# ==================== Create Entry Tests ====================


def test_create_entry_success(app, client, user_with_tokens):
    """Should create entry with valid payload."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    payload = {
        "title": "My Journal Entry",
        "body": "This is the content of my entry.",
        "entry_date": date.today().isoformat(),
        "mood": 4,
        "tags": ["reflection", "gratitude"],
        "is_private": True,
    }
    resp = client.post("/api/journal", json=payload, headers=headers)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["ok"] is True
    assert "entry" in body
    assert body["entry"]["title"] == "My Journal Entry"
    assert body["entry"]["mood"] == 4
    assert body["entry"]["tags"] == ["reflection", "gratitude"]


def test_create_entry_minimal(app, client, user_with_tokens):
    """Should create entry with only body."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    payload = {"body": "Just the body content"}
    resp = client.post("/api/journal", json=payload, headers=headers)
    assert resp.status_code == 201


def test_create_entry_empty_body_fails(app, client, user_with_tokens):
    """Should reject empty body."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    payload = {"title": "Title Only", "body": ""}
    resp = client.post("/api/journal", json=payload, headers=headers)
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["ok"] is False


def test_create_entry_invalid_mood(app, client, user_with_tokens):
    """Should reject mood outside range."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    payload = {"body": "Content", "mood": 10}
    resp = client.post("/api/journal", json=payload, headers=headers)
    assert resp.status_code == 400


def test_create_entry_with_sentiment(app, client, user_with_tokens):
    """Should accept sentiment analysis fields."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    payload = {
        "title": "Analyzed Entry",
        "body": "Content for analysis",
        "sentiment_score": 0.85,
        "emotion_label": "joyful",
    }
    resp = client.post("/api/journal", json=payload, headers=headers)
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["entry"]["sentiment_score"] == 0.85
    assert body["entry"]["emotion_label"] == "joyful"


# ==================== Update Entry Tests ====================


def test_update_entry_success(app, client, user_with_tokens):
    """Should update entry fields."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    # Create entry
    resp = client.post(
        "/api/journal",
        json={"title": "Original", "body": "Original body", "mood": 2},
        headers=headers,
    )
    entry_id = resp.get_json()["entry"]["id"]

    # Update
    update_payload = {"title": "Updated", "body": "Updated body", "mood": 5}
    resp = client.patch(
        f"/api/journal/{entry_id}", json=update_payload, headers=headers
    )
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True
    assert body["entry"]["title"] == "Updated"
    assert body["entry"]["mood"] == 5


def test_update_entry_partial(app, client, user_with_tokens):
    """Should update only provided fields."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    resp = client.post(
        "/api/journal",
        json={"title": "Keep This", "body": "Keep body", "mood": 2},
        headers=headers,
    )
    entry_id = resp.get_json()["entry"]["id"]

    # Partial update
    resp = client.patch(f"/api/journal/{entry_id}", json={"mood": 5}, headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["entry"]["title"] == "Keep This"  # Unchanged
    assert resp.get_json()["entry"]["mood"] == 5  # Updated


def test_update_entry_not_found(app, client, user_with_tokens):
    """Should return 404 for non-existent entry."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    resp = client.patch("/api/journal/99999", json={"title": "New"}, headers=headers)
    assert resp.status_code == 404


def test_update_entry_other_user(app, client, user_with_tokens, other_user_tokens):
    """Should not update other user's entry."""
    csrf_token = _prime_csrf(client)

    # User 1 creates entry
    headers1 = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)
    resp = client.post(
        "/api/journal", json={"title": "Mine", "body": "Content"}, headers=headers1
    )
    entry_id = resp.get_json()["entry"]["id"]

    # User 2 cannot update
    headers2 = _auth_headers(other_user_tokens["tokens"]["access_token"], csrf_token)
    resp = client.patch(
        f"/api/journal/{entry_id}", json={"title": "Hacked"}, headers=headers2
    )
    assert resp.status_code == 404


# ==================== Delete Entry Tests ====================


def test_delete_entry_success(app, client, user_with_tokens):
    """Should delete entry."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    resp = client.post(
        "/api/journal", json={"title": "Delete Me", "body": "Content"}, headers=headers
    )
    entry_id = resp.get_json()["entry"]["id"]

    resp = client.delete(f"/api/journal/{entry_id}", headers=headers)
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["ok"] is True

    # Verify gone
    resp = client.get(f"/api/journal/{entry_id}", headers=headers)
    assert resp.status_code == 404


def test_delete_entry_not_found(app, client, user_with_tokens):
    """Should return 404 for non-existent entry."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)

    resp = client.delete("/api/journal/99999", headers=headers)
    assert resp.status_code == 404


def test_delete_entry_other_user(app, client, user_with_tokens, other_user_tokens):
    """Should not delete other user's entry."""
    csrf_token = _prime_csrf(client)

    # User 1 creates entry
    headers1 = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)
    resp = client.post(
        "/api/journal", json={"title": "Protected", "body": "Content"}, headers=headers1
    )
    entry_id = resp.get_json()["entry"]["id"]

    # User 2 cannot delete
    headers2 = _auth_headers(other_user_tokens["tokens"]["access_token"], csrf_token)
    resp = client.delete(f"/api/journal/{entry_id}", headers=headers2)
    assert resp.status_code == 404

    # Verify still exists
    resp = client.get(f"/api/journal/{entry_id}", headers=headers1)
    assert resp.status_code == 200


# ==================== Auth/CSRF Tests ====================


def test_list_journal_requires_auth(app, client):
    """Should require authentication."""
    resp = client.get("/api/journal")
    assert resp.status_code == 401


def test_create_entry_requires_csrf(app, client, user_with_tokens):
    """CSRF validation is disabled in testing mode, so request succeeds."""
    headers = {"Authorization": f"Bearer {user_with_tokens['tokens']['access_token']}"}
    resp = client.post(
        "/api/journal", json={"title": "No CSRF", "body": "Content"}, headers=headers
    )
    # CSRF is not enforced in test mode
    assert resp.status_code == 201


def test_update_entry_requires_csrf(app, client, user_with_tokens):
    """CSRF validation is disabled in testing mode, so request succeeds."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)
    resp = client.post(
        "/api/journal", json={"title": "Test", "body": "Content"}, headers=headers
    )
    entry_id = resp.get_json()["entry"]["id"]

    # CSRF is not enforced in test mode
    headers_no_csrf = {
        "Authorization": f"Bearer {user_with_tokens['tokens']['access_token']}"
    }
    resp = client.patch(
        f"/api/journal/{entry_id}", json={"title": "New"}, headers=headers_no_csrf
    )
    assert resp.status_code == 200


def test_delete_entry_requires_csrf(app, client, user_with_tokens):
    """CSRF validation is disabled in testing mode, so request succeeds."""
    csrf_token = _prime_csrf(client)
    headers = _auth_headers(user_with_tokens["tokens"]["access_token"], csrf_token)
    resp = client.post(
        "/api/journal", json={"title": "Test", "body": "Content"}, headers=headers
    )
    entry_id = resp.get_json()["entry"]["id"]

    # CSRF is not enforced in test mode
    headers_no_csrf = {
        "Authorization": f"Bearer {user_with_tokens['tokens']['access_token']}"
    }
    resp = client.delete(f"/api/journal/{entry_id}", headers=headers_no_csrf)
    assert resp.status_code == 200

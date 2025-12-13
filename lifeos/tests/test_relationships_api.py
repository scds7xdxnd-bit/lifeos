"""Tests for Relationships domain API endpoints."""

from datetime import date, timedelta
from uuid import uuid4

import pytest
from flask_jwt_extended import create_access_token

pytestmark = pytest.mark.integration

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.domains.relationships.models.interaction_models import Interaction
from lifeos.domains.relationships.models.person_models import Person
from lifeos.domains.relationships.services import create_person, log_interaction
from lifeos.extensions import db


@pytest.fixture
def test_user(app):
    """Create a test user for relationships API tests."""
    with app.app_context():
        unique_email = f"relationships-api+{uuid4().hex}@example.com"
        user = User(email=unique_email, password_hash=hash_password("secret"))
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


# ============== People CRUD API Tests ==============


class TestPeopleAPI:
    """Tests for people API endpoints."""

    def test_list_people_empty(self, client, auth_headers):
        """List people when none exist."""
        resp = client.get("/api/relationships/people", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["people"] == []

    def test_list_people_with_data(self, app, client, test_user, auth_headers):
        """List people with existing data."""
        with app.app_context():
            create_person(test_user.id, name="Alice")
            create_person(test_user.id, name="Bob")

        resp = client.get("/api/relationships/people", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert len(data["people"]) == 2

    def test_list_people_with_filters(self, app, client, test_user, auth_headers):
        """List people with filters."""
        with app.app_context():
            create_person(
                test_user.id,
                name="Work Friend",
                relationship_type="colleague",
                tags=["work"],
            )
            create_person(
                test_user.id,
                name="School Friend",
                relationship_type="friend",
                tags=["school"],
            )

        # Filter by relationship_type
        resp = client.get(
            "/api/relationships/people?relationship_type=colleague",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["people"]) == 1
        assert data["people"][0]["name"] == "Work Friend"

    def test_list_people_search(self, app, client, test_user, auth_headers):
        """Search people by name."""
        with app.app_context():
            create_person(test_user.id, name="John Smith")
            create_person(test_user.id, name="Jane Doe")

        resp = client.get("/api/relationships/people?search=John", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["people"]) == 1
        assert data["people"][0]["name"] == "John Smith"

    def test_create_person_success(self, client, csrf_headers):
        """Create a person successfully."""
        payload = {
            "name": "New Person",
            "relationship_type": "friend",
            "importance_level": 4,
            "tags": ["college", "tech"],
            "notes": "Met at hackathon",
        }
        resp = client.post("/api/relationships/people", json=payload, headers=csrf_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["ok"] is True
        assert data["person"]["name"] == "New Person"
        assert data["person"]["relationship_type"] == "friend"

    def test_create_person_minimal(self, client, csrf_headers):
        """Create person with minimal data."""
        payload = {"name": "Minimal Person"}
        resp = client.post("/api/relationships/people", json=payload, headers=csrf_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["ok"] is True

    def test_create_person_empty_name_fails(self, client, csrf_headers):
        """Creating person with empty name fails."""
        payload = {"name": ""}
        resp = client.post("/api/relationships/people", json=payload, headers=csrf_headers)
        assert resp.status_code == 400

    def test_create_person_duplicate_fails(self, app, client, test_user, csrf_headers):
        """Creating duplicate person fails."""
        with app.app_context():
            create_person(test_user.id, name="Duplicate Person")

        payload = {"name": "Duplicate Person"}
        resp = client.post("/api/relationships/people", json=payload, headers=csrf_headers)
        assert resp.status_code == 409
        data = resp.get_json()
        assert data["error"] == "duplicate"

    def test_create_person_unauthorized(self, client):
        """Creating person without auth fails."""
        payload = {"name": "Unauthorized Person"}
        resp = client.post("/api/relationships/people", json=payload)
        assert resp.status_code == 401

    def test_get_person_success(self, app, client, test_user, auth_headers):
        """Get a specific person."""
        with app.app_context():
            person = create_person(test_user.id, name="Get Person")
            person_id = person.id

        resp = client.get(f"/api/relationships/people/{person_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["person"]["name"] == "Get Person"

    def test_get_person_not_found(self, client, auth_headers):
        """Get non-existent person returns 404."""
        resp = client.get("/api/relationships/people/99999", headers=auth_headers)
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["error"] == "not_found"

    def test_update_person(self, app, client, test_user, csrf_headers):
        """Update an existing person."""
        with app.app_context():
            person = create_person(test_user.id, name="Update Person")
            person_id = person.id

        payload = {
            "relationship_type": "family",
            "importance_level": 5,
            "notes": "Updated notes",
        }
        resp = client.patch(f"/api/relationships/people/{person_id}", json=payload, headers=csrf_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["person"]["relationship_type"] == "family"

    def test_update_person_not_found(self, client, csrf_headers):
        """Update non-existent person returns 404."""
        payload = {"notes": "Updated"}
        resp = client.patch("/api/relationships/people/99999", json=payload, headers=csrf_headers)
        assert resp.status_code == 404

    def test_delete_person(self, app, client, test_user, csrf_headers):
        """Delete an existing person."""
        with app.app_context():
            person = create_person(test_user.id, name="To Delete")
            person_id = person.id

        resp = client.delete(f"/api/relationships/people/{person_id}", headers=csrf_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True

    def test_delete_person_not_found(self, client, csrf_headers):
        """Delete non-existent person returns 404."""
        resp = client.delete("/api/relationships/people/99999", headers=csrf_headers)
        assert resp.status_code == 404


# ============== Interactions API Tests ==============


class TestInteractionsAPI:
    """Tests for interactions API endpoints."""

    def test_list_interactions_empty(self, app, client, test_user, auth_headers):
        """List interactions for a person when none exist."""
        with app.app_context():
            person = create_person(test_user.id, name="Empty Interactions Person")
            person_id = person.id

        resp = client.get(f"/api/relationships/people/{person_id}/interactions", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["interactions"] == []

    def test_list_interactions_with_data(self, app, client, test_user, auth_headers):
        """List interactions with existing data."""
        with app.app_context():
            person = create_person(test_user.id, name="Interaction Person")
            log_interaction(test_user.id, person.id, date_value=date.today(), method="call")
            log_interaction(
                test_user.id,
                person.id,
                date_value=date.today() - timedelta(days=1),
                method="message",
            )
            person_id = person.id

        resp = client.get(f"/api/relationships/people/{person_id}/interactions", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["interactions"]) == 2

    def test_list_interactions_person_not_found(self, client, auth_headers):
        """List interactions for non-existent person fails."""
        resp = client.get("/api/relationships/people/99999/interactions", headers=auth_headers)
        assert resp.status_code == 404

    def test_log_interaction_success(self, app, client, test_user, csrf_headers):
        """Log an interaction successfully."""
        with app.app_context():
            person = create_person(test_user.id, name="Log Interaction Person")
            person_id = person.id

        payload = {
            "date": date.today().isoformat(),
            "method": "meeting",
            "notes": "Had lunch together",
            "sentiment": "positive",
        }
        resp = client.post(
            f"/api/relationships/people/{person_id}/interactions",
            json=payload,
            headers=csrf_headers,
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["ok"] is True
        assert data["interaction"]["method"] == "meeting"

    def test_log_interaction_minimal(self, app, client, test_user, csrf_headers):
        """Log interaction with minimal data."""
        with app.app_context():
            person = create_person(test_user.id, name="Minimal Log Person")
            person_id = person.id

        payload = {"date": date.today().isoformat()}
        resp = client.post(
            f"/api/relationships/people/{person_id}/interactions",
            json=payload,
            headers=csrf_headers,
        )
        assert resp.status_code == 201

    def test_log_interaction_person_not_found(self, client, csrf_headers):
        """Logging interaction for non-existent person fails."""
        payload = {"date": date.today().isoformat(), "method": "call"}
        resp = client.post(
            "/api/relationships/people/99999/interactions",
            json=payload,
            headers=csrf_headers,
        )
        assert resp.status_code == 404

    def test_update_interaction(self, app, client, test_user, csrf_headers):
        """Update an existing interaction."""
        with app.app_context():
            person = create_person(test_user.id, name="Update Interaction Person")
            interaction = log_interaction(test_user.id, person.id, date_value=date.today(), method="call")
            interaction_id = interaction.id

        payload = {"notes": "Updated notes", "sentiment": "neutral"}
        resp = client.patch(
            f"/api/relationships/interactions/{interaction_id}",
            json=payload,
            headers=csrf_headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["interaction"]["notes"] == "Updated notes"

    def test_update_interaction_not_found(self, client, csrf_headers):
        """Update non-existent interaction returns 404."""
        payload = {"notes": "Updated"}
        resp = client.patch("/api/relationships/interactions/99999", json=payload, headers=csrf_headers)
        assert resp.status_code == 404

    def test_delete_interaction(self, app, client, test_user, csrf_headers):
        """Delete an interaction."""
        with app.app_context():
            person = create_person(test_user.id, name="Delete Interaction Person")
            interaction = log_interaction(test_user.id, person.id, date_value=date.today())
            interaction_id = interaction.id

        resp = client.delete(f"/api/relationships/interactions/{interaction_id}", headers=csrf_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True

    def test_delete_interaction_not_found(self, client, csrf_headers):
        """Delete non-existent interaction returns 404."""
        resp = client.delete("/api/relationships/interactions/99999", headers=csrf_headers)
        assert resp.status_code == 404


# ============== Reconnect API Tests ==============


class TestReconnectAPI:
    """Tests for reconnect candidates API."""

    def test_reconnect_empty(self, client, auth_headers):
        """Get reconnect candidates when no people exist."""
        resp = client.get("/api/relationships/reconnect", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["candidates"] == []

    def test_reconnect_with_candidates(self, app, client, test_user, auth_headers):
        """Get reconnect candidates with data."""
        with app.app_context():
            # Person with no interaction
            create_person(test_user.id, name="No Contact")

            # Person with old interaction
            old_contact = create_person(test_user.id, name="Old Contact")
            log_interaction(
                test_user.id,
                old_contact.id,
                date_value=date.today() - timedelta(days=60),
            )

            # Person with recent interaction (should not be candidate)
            recent_contact = create_person(test_user.id, name="Recent Contact")
            log_interaction(
                test_user.id,
                recent_contact.id,
                date_value=date.today() - timedelta(days=5),
            )

        resp = client.get("/api/relationships/reconnect?cutoff_days=30", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        # Should have 2 candidates: No Contact and Old Contact
        assert len(data["candidates"]) == 2
        names = [c["person"]["name"] for c in data["candidates"]]
        assert "Recent Contact" not in names

    def test_reconnect_with_limit(self, app, client, test_user, auth_headers):
        """Reconnect respects limit parameter."""
        with app.app_context():
            for i in range(10):
                create_person(test_user.id, name=f"Contact {i}")

        resp = client.get("/api/relationships/reconnect?limit=5", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["candidates"]) == 5


# ============== Pagination API Tests ==============


class TestRelationshipsPaginationAPI:
    """Tests for pagination in relationship endpoints."""

    def test_interactions_pagination(self, app, client, test_user, auth_headers):
        """Test interaction listing with pagination."""
        with app.app_context():
            person = create_person(test_user.id, name="Pagination Person")
            for i in range(25):
                log_interaction(
                    test_user.id,
                    person.id,
                    date_value=date.today() - timedelta(days=i),
                    method="call",
                )
            person_id = person.id

        resp = client.get(
            f"/api/relationships/people/{person_id}/interactions?page=1&per_page=10",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["interactions"]) == 10


# ============== User Isolation API Tests ==============


class TestRelationshipsAPIUserIsolation:
    """Tests ensuring relationship API data is properly isolated per user."""

    def test_people_api_isolated_by_user(self, app, client, test_user, auth_headers):
        """Users can only see their own people via API."""
        with app.app_context():
            # Create person for test user
            create_person(test_user.id, name="Test User Person")

            # Create another user with person
            other_user = User(email="other-rel-api@example.com", password_hash=hash_password("secret"))
            db.session.add(other_user)
            db.session.commit()
            create_person(other_user.id, name="Other User Person")

        resp = client.get("/api/relationships/people", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["people"]) == 1
        assert data["people"][0]["name"] == "Test User Person"

    def test_cannot_access_other_user_person(self, app, client, test_user, auth_headers):
        """Cannot access another user's person detail."""
        with app.app_context():
            other_user = User(
                email="other-rel-api2@example.com",
                password_hash=hash_password("secret"),
            )
            db.session.add(other_user)
            db.session.commit()
            person = create_person(other_user.id, name="Private Person")
            person_id = person.id

        resp = client.get(f"/api/relationships/people/{person_id}", headers=auth_headers)
        assert resp.status_code == 404

    def test_cannot_update_other_user_person(self, app, client, test_user, csrf_headers):
        """Cannot update another user's person."""
        with app.app_context():
            other_user = User(
                email="other-rel-api3@example.com",
                password_hash=hash_password("secret"),
            )
            db.session.add(other_user)
            db.session.commit()
            person = create_person(other_user.id, name="Protected Person")
            person_id = person.id

        payload = {"notes": "Hacked!"}
        resp = client.patch(f"/api/relationships/people/{person_id}", json=payload, headers=csrf_headers)
        assert resp.status_code == 404

    def test_cannot_log_interaction_other_user_person(self, app, client, test_user, csrf_headers):
        """Cannot log interaction for another user's person."""
        with app.app_context():
            other_user = User(
                email="other-rel-api4@example.com",
                password_hash=hash_password("secret"),
            )
            db.session.add(other_user)
            db.session.commit()
            person = create_person(other_user.id, name="Other's Person")
            person_id = person.id

        payload = {"date": date.today().isoformat(), "method": "call"}
        resp = client.post(
            f"/api/relationships/people/{person_id}/interactions",
            json=payload,
            headers=csrf_headers,
        )
        assert resp.status_code == 404

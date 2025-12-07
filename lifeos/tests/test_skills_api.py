"""Tests for Skills domain API endpoints."""

from datetime import datetime, timedelta

import pytest
from flask_jwt_extended import create_access_token

pytestmark = pytest.mark.integration

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.domains.skills.models.skill_models import PracticeSession, Skill
from lifeos.domains.skills.services.skill_service import create_skill, log_practice_session
from lifeos.extensions import db


@pytest.fixture
def test_user(app):
    """Create a test user for skills API tests."""
    with app.app_context():
        user = User(email="skills-api@example.com", password_hash=hash_password("secret"))
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


# ============== Skills CRUD API Tests ==============


class TestSkillsAPI:
    """Tests for skills API endpoints."""

    def test_list_skills_empty(self, client, auth_headers):
        """List skills when none exist."""
        resp = client.get("/api/skills", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["skills"] == []

    def test_list_skills_with_data(self, app, client, test_user, auth_headers):
        """List skills with existing data."""
        with app.app_context():
            create_skill(test_user.id, name="Python", category="Programming")
            create_skill(test_user.id, name="Piano", category="Music")

        resp = client.get("/api/skills", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert len(data["skills"]) == 2

    def test_create_skill_success(self, client, csrf_headers):
        """Create a skill successfully."""
        payload = {
            "name": "Machine Learning",
            "category": "AI",
            "difficulty": "advanced",
            "target_level": 5,
            "current_level": 1,
            "description": "Deep learning and neural networks",
        }
        resp = client.post("/api/skills", json=payload, headers=csrf_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["ok"] is True
        assert "skill_id" in data

    def test_create_skill_minimal(self, client, csrf_headers):
        """Create skill with minimal data."""
        payload = {"name": "Rust Programming"}
        resp = client.post("/api/skills", json=payload, headers=csrf_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["ok"] is True

    def test_create_skill_empty_name_fails(self, client, csrf_headers):
        """Creating skill with empty name fails."""
        payload = {"name": ""}
        resp = client.post("/api/skills", json=payload, headers=csrf_headers)
        assert resp.status_code == 400

    def test_create_skill_duplicate_fails(self, app, client, test_user, csrf_headers):
        """Creating duplicate skill fails."""
        with app.app_context():
            create_skill(test_user.id, name="Docker")

        payload = {"name": "Docker"}
        resp = client.post("/api/skills", json=payload, headers=csrf_headers)
        assert resp.status_code == 409
        data = resp.get_json()
        assert data["error"] == "duplicate"

    def test_create_skill_unauthorized(self, client):
        """Creating skill without auth fails."""
        payload = {"name": "Kubernetes"}
        resp = client.post("/api/skills", json=payload)
        assert resp.status_code == 401

    def test_get_skill_detail(self, app, client, test_user, auth_headers):
        """Get detailed skill information."""
        with app.app_context():
            skill = create_skill(test_user.id, name="GraphQL", category="API")
            skill_id = skill.id

        resp = client.get(f"/api/skills/{skill_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["skill"]["name"] == "GraphQL"

    def test_get_skill_not_found(self, client, auth_headers):
        """Get non-existent skill returns 404."""
        resp = client.get("/api/skills/99999", headers=auth_headers)
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["error"] == "not_found"

    def test_update_skill(self, app, client, test_user, csrf_headers):
        """Update an existing skill."""
        with app.app_context():
            skill = create_skill(test_user.id, name="React")
            skill_id = skill.id

        payload = {"description": "React.js frontend development", "current_level": 3}
        resp = client.patch(f"/api/skills/{skill_id}", json=payload, headers=csrf_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True

    def test_update_skill_not_found(self, client, csrf_headers):
        """Update non-existent skill returns 404."""
        payload = {"description": "Updated"}
        resp = client.patch("/api/skills/99999", json=payload, headers=csrf_headers)
        assert resp.status_code == 404

    def test_delete_skill(self, app, client, test_user, csrf_headers):
        """Delete an existing skill."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Vue.js")
            skill_id = skill.id

        resp = client.delete(f"/api/skills/{skill_id}", headers=csrf_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True

    def test_delete_skill_not_found(self, client, csrf_headers):
        """Delete non-existent skill returns 404."""
        resp = client.delete("/api/skills/99999", headers=csrf_headers)
        assert resp.status_code == 404


# ============== Practice Session API Tests ==============


class TestPracticeSessionAPI:
    """Tests for practice session API endpoints."""

    def test_log_practice_success(self, app, client, test_user, csrf_headers):
        """Log a practice session successfully."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Angular")
            skill_id = skill.id

        payload = {
            "duration_minutes": 60,
            "intensity": 4,
            "notes": "Learned about directives",
        }
        resp = client.post(f"/api/skills/{skill_id}/practice", json=payload, headers=csrf_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["session"]["duration_minutes"] == 60

    def test_log_practice_with_timestamp(self, app, client, test_user, csrf_headers):
        """Log practice session with custom timestamp."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Svelte")
            skill_id = skill.id

        past_time = (datetime.utcnow() - timedelta(days=1)).isoformat()
        payload = {"duration_minutes": 45, "practiced_at": past_time}
        resp = client.post(f"/api/skills/{skill_id}/practice", json=payload, headers=csrf_headers)
        assert resp.status_code == 200

    def test_log_practice_skill_not_found(self, client, csrf_headers):
        """Logging practice for non-existent skill fails."""
        payload = {"duration_minutes": 30}
        resp = client.post("/api/skills/99999/practice", json=payload, headers=csrf_headers)
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["error"] == "not_found"

    def test_log_practice_invalid_duration(self, app, client, test_user, csrf_headers):
        """Logging practice with invalid duration fails."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Next.js")
            skill_id = skill.id

        payload = {"duration_minutes": 0}
        resp = client.post(f"/api/skills/{skill_id}/practice", json=payload, headers=csrf_headers)
        assert resp.status_code == 400

    def test_update_practice_session(self, app, client, test_user, csrf_headers):
        """Update an existing practice session."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Nuxt")
            session = log_practice_session(test_user.id, skill.id, duration_minutes=30)
            session_id = session.id

        payload = {"duration_minutes": 45, "notes": "Extended session"}
        resp = client.patch(f"/api/skills/practice/{session_id}", json=payload, headers=csrf_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["session"]["duration_minutes"] == 45

    def test_update_practice_not_found(self, client, csrf_headers):
        """Update non-existent practice session returns 404."""
        payload = {"duration_minutes": 60}
        resp = client.patch("/api/skills/practice/99999", json=payload, headers=csrf_headers)
        assert resp.status_code == 404

    def test_delete_practice_session(self, app, client, test_user, csrf_headers):
        """Delete a practice session."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Remix")
            session = log_practice_session(test_user.id, skill.id, duration_minutes=30)
            session_id = session.id

        resp = client.delete(f"/api/skills/practice/{session_id}", headers=csrf_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True

    def test_delete_practice_not_found(self, client, csrf_headers):
        """Delete non-existent practice session returns 404."""
        resp = client.delete("/api/skills/practice/99999", headers=csrf_headers)
        assert resp.status_code == 404


# ============== Skill with Aggregates API Tests ==============


class TestSkillAggregatesAPI:
    """Tests for skills listing with practice aggregates."""

    def test_list_skills_includes_aggregates(self, app, client, test_user, auth_headers):
        """Skills list includes practice aggregates."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Elixir")
            log_practice_session(test_user.id, skill.id, duration_minutes=60)
            log_practice_session(test_user.id, skill.id, duration_minutes=45)

        resp = client.get("/api/skills", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["skills"]) == 1
        skill_data = data["skills"][0]
        assert skill_data["total_minutes"] == 105
        assert skill_data["session_count"] == 2

    def test_skill_detail_includes_stats(self, app, client, test_user, auth_headers):
        """Skill detail includes practice statistics."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Erlang")
            now = datetime.utcnow()
            for i in range(5):
                log_practice_session(
                    test_user.id,
                    skill.id,
                    duration_minutes=30,
                    practiced_at=now - timedelta(days=i),
                )
            skill_id = skill.id

        resp = client.get(f"/api/skills/{skill_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert "total_minutes" in data["skill"]
        assert data["skill"]["total_minutes"] == 150


# ============== User Isolation API Tests ==============


class TestSkillAPIUserIsolation:
    """Tests ensuring skill API data is properly isolated per user."""

    def test_skills_api_isolated_by_user(self, app, client, test_user, auth_headers):
        """Users can only see their own skills via API."""
        with app.app_context():
            # Create skill for test user
            create_skill(test_user.id, name="Test User Skill")

            # Create another user with skill
            other_user = User(email="other-api@example.com", password_hash=hash_password("secret"))
            db.session.add(other_user)
            db.session.commit()
            create_skill(other_user.id, name="Other User Skill")

        resp = client.get("/api/skills", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["skills"]) == 1
        assert data["skills"][0]["name"] == "Test User Skill"

    def test_cannot_access_other_user_skill(self, app, client, test_user, auth_headers):
        """Cannot access another user's skill detail."""
        with app.app_context():
            other_user = User(email="other-api2@example.com", password_hash=hash_password("secret"))
            db.session.add(other_user)
            db.session.commit()
            skill = create_skill(other_user.id, name="Private Skill")
            skill_id = skill.id

        resp = client.get(f"/api/skills/{skill_id}", headers=auth_headers)
        assert resp.status_code == 404

    def test_cannot_update_other_user_skill(self, app, client, test_user, csrf_headers):
        """Cannot update another user's skill."""
        with app.app_context():
            other_user = User(email="other-api3@example.com", password_hash=hash_password("secret"))
            db.session.add(other_user)
            db.session.commit()
            skill = create_skill(other_user.id, name="Protected Skill")
            skill_id = skill.id

        payload = {"description": "Hacked!"}
        resp = client.patch(f"/api/skills/{skill_id}", json=payload, headers=csrf_headers)
        assert resp.status_code == 404

    def test_cannot_delete_other_user_skill(self, app, client, test_user, csrf_headers):
        """Cannot delete another user's skill."""
        with app.app_context():
            other_user = User(email="other-api4@example.com", password_hash=hash_password("secret"))
            db.session.add(other_user)
            db.session.commit()
            skill = create_skill(other_user.id, name="Untouchable Skill")
            skill_id = skill.id

        resp = client.delete(f"/api/skills/{skill_id}", headers=csrf_headers)
        assert resp.status_code == 404

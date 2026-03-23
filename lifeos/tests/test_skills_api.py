"""Tests for Skills domain API endpoints."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from flask_jwt_extended import create_access_token

pytestmark = pytest.mark.integration

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.domains.skills.models.skill_models import PracticeSession, Skill
from lifeos.domains.skills.services.skill_service import (
    create_skill,
    log_practice_session,
)
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

    def test_list_skills_overview_feature_disabled(self, client, auth_headers):
        """Overview endpoint is hidden when Phase 12 goals flag is disabled."""
        client.application.config["ENABLE_PHASE12_SKILLS_GOALS"] = False
        resp = client.get("/api/skills/overview", headers=auth_headers)
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["ok"] is False
        assert data["error"] == "not_found"

    def test_list_skills_overview_enabled(self, app, client, test_user, auth_headers):
        """Overview endpoint returns deterministic progress state payloads."""
        app.config["ENABLE_PHASE12_SKILLS_GOALS"] = True
        with app.app_context():
            completed = create_skill(
                test_user.id,
                name="Completed Skill",
                target_level=3,
                current_level=3,
            )
            at_risk = create_skill(
                test_user.id,
                name="At Risk Skill",
                target_level=5,
                current_level=2,
            )
            log_practice_session(
                test_user.id,
                completed.id,
                duration_minutes=45,
                practiced_at=datetime.utcnow() - timedelta(days=1),
            )
            log_practice_session(
                test_user.id,
                at_risk.id,
                duration_minutes=20,
                practiced_at=datetime.utcnow() - timedelta(days=14),
            )

        resp = client.get("/api/skills/overview", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert len(data["skills"]) == 2
        assert data["summary"]["active"] == 2
        assert "groups" in data

        by_name = {item["name"]: item for item in data["skills"]}
        completed_card = by_name["Completed Skill"]
        assert completed_card["progress_state"] == "completed"
        assert completed_card["primary_action"] == "continue_practice"
        assert completed_card["goal"]["goal_type"] == "milestones"
        assert completed_card["requires_goal_setup"] is False

        at_risk_card = by_name["At Risk Skill"]
        assert at_risk_card["progress_state"] == "at_risk"
        assert at_risk_card["risk_reason"] == "no_recent_sessions"

    def test_get_skill_path_feature_disabled(self, app, client, test_user, auth_headers):
        """Path endpoint is hidden when Phase 12 path flag is disabled."""
        app.config["ENABLE_PHASE12_SKILLS_PATH"] = False
        with app.app_context():
            skill = create_skill(test_user.id, name="Path Hidden Skill")

        resp = client.get(f"/api/skills/{skill.id}/path", headers=auth_headers)
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["ok"] is False
        assert data["error"] == "not_found"

    def test_get_skill_path_enabled(self, app, client, test_user, auth_headers):
        """Path endpoint returns deterministic training steps when enabled."""
        app.config["ENABLE_PHASE12_SKILLS_PATH"] = True
        with app.app_context():
            skill = create_skill(
                test_user.id,
                name="Path Ready Skill",
                target_level=4,
                current_level=1,
            )
            log_practice_session(
                test_user.id,
                skill.id,
                duration_minutes=25,
                practiced_at=datetime.utcnow() - timedelta(days=15),
            )

        resp = client.get(f"/api/skills/{skill.id}/path", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        path = data["path"]
        assert path["skill_id"] == skill.id
        assert path["progress_state"] == "at_risk"
        assert path["risk_reason"] == "no_recent_sessions"
        assert len(path["steps"]) >= 2
        assert path["steps"][0]["action"] == "continue_practice"
        assert path["next_recommended_step"] is not None
        assert path["next_recommended_step"]["action"] in {"continue_practice", "setup_goal", "review_goal"}

    def test_get_skill_path_not_found_when_enabled(self, app, client, auth_headers):
        """Path endpoint returns not_found when feature is enabled but skill does not exist."""
        app.config["ENABLE_PHASE12_SKILLS_PATH"] = True

        resp = client.get("/api/skills/99999/path", headers=auth_headers)
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["ok"] is False
        assert data["error"] == "not_found"

    def test_get_skill_forecast_feature_disabled(self, app, client, test_user, auth_headers):
        """Forecast endpoint is hidden when Phase 12 forecast flag is disabled."""
        app.config["ENABLE_PHASE12_SKILLS_FORECAST"] = False
        with app.app_context():
            skill = create_skill(test_user.id, name="Forecast Hidden Skill")

        resp = client.get(f"/api/skills/{skill.id}/forecast", headers=auth_headers)
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["ok"] is False
        assert data["error"] == "not_found"

    def test_get_skill_forecast_not_found_when_enabled(self, app, client, auth_headers):
        """Forecast endpoint returns not_found when flag is enabled but skill does not exist."""
        app.config["ENABLE_PHASE12_SKILLS_FORECAST"] = True

        resp = client.get("/api/skills/99999/forecast", headers=auth_headers)
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["ok"] is False
        assert data["error"] == "not_found"

    def test_get_skill_forecast_enabled_payload(self, app, client, test_user, auth_headers):
        """Forecast endpoint returns deterministic baseline and projection payload."""
        app.config["ENABLE_PHASE12_SKILLS_FORECAST"] = True
        with app.app_context():
            skill = create_skill(
                test_user.id,
                name="Forecast Ready Skill",
                goal_type="sessions",
                goal_target_value=8,
            )
            now = datetime.utcnow()
            log_practice_session(test_user.id, skill.id, duration_minutes=30, practiced_at=now - timedelta(days=2))
            log_practice_session(test_user.id, skill.id, duration_minutes=25, practiced_at=now - timedelta(days=5))

        resp = client.get(f"/api/skills/{skill.id}/forecast?horizon_days=7", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        forecast = data["forecast"]
        assert forecast["skill_id"] == skill.id
        assert forecast["horizon_days"] == 7
        assert forecast["goal"] is not None
        assert forecast["baseline"]["sessions_last_14"] >= 2
        assert forecast["projection"]["projected_minutes_next_window"] >= 0
        assert forecast["projection"]["projected_sessions_next_window"] >= 0
        assert forecast["forecast_state"] in {"on_track", "at_risk", "completed", "insufficient_data"}

    def test_get_skill_forecast_horizon_clamped(self, app, client, test_user, auth_headers):
        """Forecast horizon is clamped to a safe max range."""
        app.config["ENABLE_PHASE12_SKILLS_FORECAST"] = True
        with app.app_context():
            skill = create_skill(test_user.id, name="Forecast Clamp Skill")

        resp = client.get(f"/api/skills/{skill.id}/forecast?horizon_days=999", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["forecast"]["horizon_days"] == 90

    def test_get_skill_forecast_horizon_min_clamped(self, app, client, test_user, auth_headers):
        """Forecast horizon clamps explicit zero requests to minimum range."""
        app.config["ENABLE_PHASE12_SKILLS_FORECAST"] = True
        with app.app_context():
            skill = create_skill(test_user.id, name="Forecast Min Clamp Skill")

        resp = client.get(f"/api/skills/{skill.id}/forecast?horizon_days=0", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["forecast"]["horizon_days"] == 1

    def test_get_skill_forecast_invalid_horizon_defaults_to_7(self, app, client, test_user, auth_headers):
        """Invalid horizon query should resolve through typed arg parsing and default to 7."""
        app.config["ENABLE_PHASE12_SKILLS_FORECAST"] = True
        with app.app_context():
            skill = create_skill(test_user.id, name="Forecast Invalid Horizon Skill")

        resp = client.get(f"/api/skills/{skill.id}/forecast?horizon_days=abc", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["forecast"]["horizon_days"] == 7

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

    def test_create_skill_requires_goal_when_phase12_goals_enabled(self, app, client, csrf_headers):
        """When goals flag is enabled, creating skill without goal fails."""
        app.config["ENABLE_PHASE12_SKILLS_GOALS"] = True
        app.config["ENABLE_PHASE12_SKILLS_GOALS_STRICT"] = True
        payload = {"name": "No Goal Skill"}
        resp = client.post("/api/skills", json=payload, headers=csrf_headers)
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"] == "goal_required"

    def test_create_skill_allows_missing_goal_when_not_strict(self, app, client, csrf_headers):
        """Goals rollout allows missing goal until strict mode is enabled."""
        app.config["ENABLE_PHASE12_SKILLS_GOALS"] = True
        app.config["ENABLE_PHASE12_SKILLS_GOALS_STRICT"] = False
        payload = {"name": "Legacy Client Skill"}
        resp = client.post("/api/skills", json=payload, headers=csrf_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["ok"] is True

    def test_create_skill_with_goal_when_phase12_goals_enabled(self, app, client, csrf_headers):
        """When goals flag is enabled, creating skill with goal fields succeeds."""
        app.config["ENABLE_PHASE12_SKILLS_GOALS"] = True
        payload = {
            "name": "Goal Ready Skill",
            "goal_type": "sessions",
            "goal_target_value": 12,
        }
        resp = client.post("/api/skills", json=payload, headers=csrf_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["ok"] is True

    def test_create_skill_unauthorized(self, client):
        """Creating skill without auth fails."""
        payload = {"name": "Kubernetes"}
        resp = client.post("/api/skills", json=payload)
        assert resp.status_code == 401

    def test_get_skill_detail(self, app, client, test_user, auth_headers):
        """Get detailed skill information."""
        app.config["ENABLE_PHASE12_SKILLS_PATH"] = True
        with app.app_context():
            skill = create_skill(test_user.id, name="GraphQL", category="API")
            skill_id = skill.id

        resp = client.get(f"/api/skills/{skill_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["skill"]["name"] == "GraphQL"
        assert "goal" in data
        assert "path" in data
        assert "path_steps" in data
        assert "current_step" in data
        assert "history" in data
        assert isinstance(data["path"], dict)
        assert "steps" in data["path"]
        assert data["path_steps"] == data["path"]["steps"]

    def test_get_skill_detail_when_path_disabled_returns_null_path_fields(self, app, client, test_user, auth_headers):
        """Detail endpoint preserves shape and returns null path fields when path flag is disabled."""
        app.config["ENABLE_PHASE12_SKILLS_PATH"] = False
        with app.app_context():
            skill = create_skill(test_user.id, name="Detail No Path")

        resp = client.get(f"/api/skills/{skill.id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["goal"] is None
        assert data["path"] is None
        assert data["path_steps"] is None
        assert data["current_step"] is None

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

    def test_update_skill_validation_error(self, app, client, test_user, csrf_headers):
        """Invalid payload for update returns validation_error."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Validation Skill")

        payload = {"goal_target_value": 0}
        resp = client.patch(f"/api/skills/{skill.id}", json=payload, headers=csrf_headers)
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"] == "validation_error"

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
        app.config["ENABLE_PHASE12_SKILLS_PATH"] = True
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
        assert "next_recommended_step" in data

    def test_log_practice_with_step_id(self, app, client, test_user, csrf_headers):
        """Practice logging supports optional step_id."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Typed Step Skill")
            skill_id = skill.id

        payload = {
            "duration_minutes": 30,
            "step_id": 2,
            "notes": "Worked on step 2",
        }
        resp = client.post(f"/api/skills/{skill_id}/practice", json=payload, headers=csrf_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["session"]["step_id"] == 2

    def test_log_practice_with_path_disabled_returns_null_next_step(self, app, client, test_user, csrf_headers):
        """When path feature is disabled, practice response returns explicit null next step."""
        app.config["ENABLE_PHASE12_SKILLS_PATH"] = False
        with app.app_context():
            skill = create_skill(test_user.id, name="No Path Next Step")

        payload = {"duration_minutes": 30}
        resp = client.post(f"/api/skills/{skill.id}/practice", json=payload, headers=csrf_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["next_recommended_step"] is None

    def test_log_practice_uses_resolver_when_path_missing_recommended_step(self, app, client, test_user, csrf_headers):
        """Practice endpoint falls back to resolver when path payload omits next_recommended_step."""
        app.config["ENABLE_PHASE12_SKILLS_PATH"] = True
        with app.app_context():
            skill = create_skill(test_user.id, name="Resolver Fallback Skill")

        payload = {"duration_minutes": 30}
        mocked_path = {
            "skill_id": skill.id,
            "progress_state": "on_track",
            "risk_reason": None,
            "goal": None,
            "steps": [
                {
                    "step_id": "continue_practice",
                    "label": "Continue Practice",
                    "status": "ready",
                    "action": "continue_practice",
                }
            ],
            "next_recommended_step": None,
        }
        with patch("lifeos.domains.skills.controllers.skill_api.get_skill_path", return_value=mocked_path):
            resp = client.post(f"/api/skills/{skill.id}/practice", json=payload, headers=csrf_headers)

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["next_recommended_step"] is not None
        assert data["next_recommended_step"]["step_id"] == "continue_practice"

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

    def test_update_practice_validation_error(self, app, client, test_user, csrf_headers):
        """Invalid payload for practice update returns validation_error."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Update Practice Validation")
            session = log_practice_session(test_user.id, skill.id, duration_minutes=20)

        payload = {"duration_minutes": 0}
        resp = client.patch(f"/api/skills/practice/{session.id}", json=payload, headers=csrf_headers)
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"] == "validation_error"

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

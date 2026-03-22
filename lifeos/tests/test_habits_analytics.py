"""HAB-019: Integration tests for habits analytics endpoints.

Tests /stats, /history, /heatmap response shape and user-scoping.
"""

from datetime import date, timedelta

import pytest

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.domains.habits.models.habit_models import Habit, HabitLog, HabitStat
from lifeos.domains.habits.services import create_habit, log_habit_completion
from lifeos.domains.habits.services.stat_service import recompute_habit_stat
from lifeos.extensions import db

pytestmark = pytest.mark.integration


@pytest.fixture
def analytics_user(app):
    """Create a test user for analytics tests."""
    with app.app_context():
        user = User(
            email="analytics-tester@example.com",
            password_hash=hash_password("secret"),
        )
        db.session.add(user)
        db.session.commit()
        yield user


@pytest.fixture
def analytics_other_user(app):
    """Second user to verify scoping."""
    with app.app_context():
        user = User(
            email="other-analytics@example.com",
            password_hash=hash_password("secret"),
        )
        db.session.add(user)
        db.session.commit()
        yield user


@pytest.fixture
def habit_with_logs(app, analytics_user):
    """Create a habit with 10 days of logs and a materialized stat."""
    with app.app_context():
        habit = create_habit(
            analytics_user.id,
            name="Analytics Test Habit",
            schedule_type="daily",
        )
        today = date.today()
        for i in range(10):
            log_habit_completion(
                analytics_user.id,
                habit.id,
                logged_date=today - timedelta(days=i),
            )
        recompute_habit_stat(analytics_user.id, habit.id)
        db.session.commit()
        yield habit


def _auth_headers(user_id: int) -> dict:
    """Build JWT auth headers for test requests."""
    from flask_jwt_extended import create_access_token

    token = create_access_token(identity=str(user_id))
    return {"Authorization": f"Bearer {token}"}


class TestHabitStatsEndpoint:
    """GET /api/habits/<id>/stats"""

    def test_stats_response_shape(self, app, client, analytics_user, habit_with_logs):
        with app.app_context():
            resp = client.get(
                f"/api/habits/{habit_with_logs.id}/stats",
                headers=_auth_headers(analytics_user.id),
            )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        stats = data["stats"]
        assert "current_streak" in stats
        assert "longest_streak" in stats
        assert "completion_rate_30d" in stats
        assert "total_logs" in stats
        assert "last_logged_at" in stats
        assert isinstance(stats["current_streak"], int)
        assert stats["current_streak"] >= 1
        assert stats["total_logs"] == 10

    def test_stats_user_scoping(self, app, client, analytics_other_user, habit_with_logs):
        """Other user cannot access habit stats."""
        with app.app_context():
            resp = client.get(
                f"/api/habits/{habit_with_logs.id}/stats",
                headers=_auth_headers(analytics_other_user.id),
            )
        assert resp.status_code == 404

    def test_stats_not_found(self, app, client, analytics_user):
        with app.app_context():
            resp = client.get(
                "/api/habits/99999/stats",
                headers=_auth_headers(analytics_user.id),
            )
        assert resp.status_code == 404


class TestHabitHistoryEndpoint:
    """GET /api/habits/<id>/history"""

    def test_history_response_shape(self, app, client, analytics_user, habit_with_logs):
        with app.app_context():
            resp = client.get(
                f"/api/habits/{habit_with_logs.id}/history?range=30d",
                headers=_auth_headers(analytics_user.id),
            )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        history = data["history"]
        assert "entries" in history
        assert "range" in history
        assert history["range"] == "30d"
        assert len(history["entries"]) == 30
        # Each entry has date and logged fields
        entry = history["entries"][0]
        assert "date" in entry
        assert "logged" in entry
        assert isinstance(entry["logged"], bool)

    def test_history_7d_range(self, app, client, analytics_user, habit_with_logs):
        with app.app_context():
            resp = client.get(
                f"/api/habits/{habit_with_logs.id}/history?range=7d",
                headers=_auth_headers(analytics_user.id),
            )
        data = resp.get_json()
        assert len(data["history"]["entries"]) == 7

    def test_history_user_scoping(self, app, client, analytics_other_user, habit_with_logs):
        """Other user cannot access another user's habit history."""
        with app.app_context():
            resp = client.get(
                f"/api/habits/{habit_with_logs.id}/history?range=7d",
                headers=_auth_headers(analytics_other_user.id),
            )
        assert resp.status_code == 404


class TestHabitHeatmapEndpoint:
    """GET /api/habits/<id>/heatmap"""

    def test_heatmap_response_shape(self, app, client, analytics_user, habit_with_logs):
        year = date.today().year
        with app.app_context():
            resp = client.get(
                f"/api/habits/{habit_with_logs.id}/heatmap?year={year}",
                headers=_auth_headers(analytics_user.id),
            )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        heatmap = data["heatmap"]
        assert heatmap["year"] == year
        assert "entries" in heatmap
        # Should have entries for every day of the year
        entries = heatmap["entries"]
        assert len(entries) >= 365
        entry = entries[0]
        assert "date" in entry
        assert "logged" in entry

    def test_heatmap_user_scoping(self, app, client, analytics_other_user, habit_with_logs):
        year = date.today().year
        with app.app_context():
            resp = client.get(
                f"/api/habits/{habit_with_logs.id}/heatmap?year={year}",
                headers=_auth_headers(analytics_other_user.id),
            )
        assert resp.status_code == 404


class TestMigrationConsistency:
    """HAB-019: Verify migration chain has single head."""

    def test_single_alembic_head(self, app):
        """Ensure no migration branch conflicts."""
        import os
        from pathlib import Path

        from alembic import command
        from alembic.config import Config as AlembicConfig

        root = Path(__file__).resolve().parents[2]
        cfg = AlembicConfig(str(root / "alembic.ini"))
        cfg.set_main_option("script_location", str(root / "lifeos" / "migrations"))
        db_url = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")
        if db_url:
            cfg.set_main_option("sqlalchemy.url", db_url)

        from alembic.script import ScriptDirectory

        script = ScriptDirectory.from_config(cfg)
        heads = script.get_heads()
        assert len(heads) == 1, f"Expected single head, found {len(heads)}: {heads}"

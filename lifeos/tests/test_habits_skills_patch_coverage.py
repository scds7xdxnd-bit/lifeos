"""Unit coverage tests for recent habits/skills patch branches."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from unittest.mock import patch
from uuid import uuid4

import pytest

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.domains.habits.services import (
    _user_local_today,
    create_habit,
    list_habits,
    log_habit_completion,
)
from lifeos.domains.skills.services.skill_service import (
    create_skill,
    get_skill_forecast,
    log_practice_session,
)
from lifeos.extensions import db

pytestmark = pytest.mark.unit


@pytest.fixture
def unit_user(app):
    with app.app_context():
        user = User(
            email=f"patch-coverage+{uuid4().hex}@example.com",
            password_hash=hash_password("secret"),
            timezone="Asia/Seoul",
        )
        db.session.add(user)
        db.session.commit()
        return user


def test__user_local_today_returns_date(app, unit_user):
    with app.app_context():
        today_value = _user_local_today(unit_user.id)
        assert isinstance(today_value, date)


def test_log_habit_completion_uses_user_local_today_when_date_missing(app, unit_user):
    with app.app_context():
        habit = create_habit(unit_user.id, name="Patch Habit")
        fixed_today = date(2026, 3, 23)

        with patch("lifeos.domains.habits.services._user_local_today", return_value=fixed_today):
            log = log_habit_completion(unit_user.id, habit.id)

        assert log.logged_date == fixed_today


def test_list_habits_uses_user_local_today_for_today_log_lookup(app, unit_user):
    with app.app_context():
        habit = create_habit(unit_user.id, name="Patch Habit Today Lookup")
        fixed_today = date(2026, 3, 23)
        log_habit_completion(unit_user.id, habit.id, logged_date=fixed_today)

        with patch("lifeos.domains.habits.services._user_local_today", return_value=fixed_today):
            payload = list_habits(unit_user.id)

        assert len(payload) == 1
        assert payload[0]["completed_today"] is True
        assert payload[0]["today_log_id"] is not None


def test_get_skill_forecast_sessions_goal_projects_ratio(app, unit_user):
    with app.app_context():
        skill = create_skill(
            unit_user.id,
            name="Patch Sessions Forecast",
            goal_type="sessions",
            goal_target_value=6,
        )
        now = datetime.utcnow()
        log_practice_session(unit_user.id, skill.id, duration_minutes=20, practiced_at=now - timedelta(days=2))
        log_practice_session(unit_user.id, skill.id, duration_minutes=30, practiced_at=now - timedelta(days=5))

        payload = get_skill_forecast(unit_user.id, skill.id, horizon_days=7)

        assert payload is not None
        assert payload["forecast_state"] == "on_track"
        assert payload["projection"]["projected_goal_progress_ratio"] is not None


def test_get_skill_forecast_non_projectable_goal_type_reason(app, unit_user):
    with app.app_context():
        skill = create_skill(
            unit_user.id,
            name="Patch Benchmark Forecast",
            goal_type="benchmark",
            goal_target_value=10,
            current_level=1,
        )
        now = datetime.utcnow()
        log_practice_session(unit_user.id, skill.id, duration_minutes=20, practiced_at=now - timedelta(days=2))
        log_practice_session(unit_user.id, skill.id, duration_minutes=25, practiced_at=now - timedelta(days=4))

        payload = get_skill_forecast(unit_user.id, skill.id, horizon_days=7)

        assert payload is not None
        assert payload["forecast_state"] == "insufficient_data"
        assert payload["risk_reason"] == "non_projectable_goal_type"

"""Tests for HAB-015: Habit stat recomputation service."""

from datetime import date, timedelta

import pytest

pytestmark = pytest.mark.integration

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.domains.habits.models.habit_models import HabitStat
from lifeos.domains.habits.services import (
    create_habit,
    delete_habit_log,
    log_habit_completion,
    update_habit_log,
)
from lifeos.domains.habits.services.stat_service import (
    STREAK_MILESTONES,
    compute_streaks,
    recompute_habit_stat,
)
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox.models import OutboxMessage


@pytest.fixture
def stat_user(app):
    """Create a test user for stat service tests."""
    with app.app_context():
        user = User(
            email="stat-tester@example.com",
            password_hash=hash_password("secret"),
        )
        db.session.add(user)
        db.session.commit()
        yield user


# ============== compute_streaks unit tests ==============


class TestComputeStreaks:
    """Pure-function tests for the streak algorithm."""

    def test_empty_logs(self, app):
        with app.app_context():
            current, best = compute_streaks([])
            assert current == 0
            assert best == 0

    def test_single_log(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Single")
            log_habit_completion(stat_user.id, habit.id, logged_date=date.today())
            from lifeos.domains.habits.models.habit_models import HabitLog

            logs = HabitLog.query.filter_by(habit_id=habit.id).order_by(HabitLog.logged_date.desc()).all()
            current, best = compute_streaks(logs)
            assert current == 1
            assert best == 1

    def test_consecutive_days(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Consecutive")
            today = date.today()
            for i in range(7):
                log_habit_completion(stat_user.id, habit.id, logged_date=today - timedelta(days=i))
            from lifeos.domains.habits.models.habit_models import HabitLog

            logs = HabitLog.query.filter_by(habit_id=habit.id).order_by(HabitLog.logged_date.desc()).all()
            current, best = compute_streaks(logs)
            assert current == 7
            assert best == 7

    def test_gap_resets_streak(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Gap")
            today = date.today()
            # 3 consecutive days, then 2-day gap, then 2 days
            for i in range(3):
                log_habit_completion(stat_user.id, habit.id, logged_date=today - timedelta(days=i))
            for i in range(2):
                log_habit_completion(stat_user.id, habit.id, logged_date=today - timedelta(days=5 + i))
            from lifeos.domains.habits.models.habit_models import HabitLog

            logs = HabitLog.query.filter_by(habit_id=habit.id).order_by(HabitLog.logged_date.desc()).all()
            current, best = compute_streaks(logs)
            assert current == 3
            assert best == 3


# ============== recompute_habit_stat tests ==============


class TestRecomputeHabitStat:
    """Tests for the recompute_habit_stat service function."""

    def test_creates_stat_on_first_log(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="First Stat")
            # log_habit_completion already calls recompute_habit_stat
            log_habit_completion(stat_user.id, habit.id, logged_date=date.today())

            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            assert stat is not None
            assert stat.current_streak == 1
            assert stat.total_logs == 1
            assert stat.last_logged_at == date.today()

    def test_updates_stat_on_subsequent_logs(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Multi Stat")
            today = date.today()
            log_habit_completion(stat_user.id, habit.id, logged_date=today)
            log_habit_completion(stat_user.id, habit.id, logged_date=today - timedelta(days=1))

            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            assert stat.current_streak == 2
            assert stat.total_logs == 2

    def test_stat_decrements_on_log_delete(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Delete Stat")
            today = date.today()
            log1 = log_habit_completion(stat_user.id, habit.id, logged_date=today)
            log_habit_completion(stat_user.id, habit.id, logged_date=today - timedelta(days=1))

            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            assert stat.total_logs == 2

            delete_habit_log(stat_user.id, log1.id)

            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            assert stat.total_logs == 1
            assert stat.current_streak == 1

    def test_stat_updates_on_log_date_change(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Update Date Stat")
            today = date.today()
            log_habit_completion(stat_user.id, habit.id, logged_date=today)
            log2 = log_habit_completion(stat_user.id, habit.id, logged_date=today - timedelta(days=1))

            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            assert stat.current_streak == 2

            # Move log2 to create a gap
            update_habit_log(stat_user.id, log2.id, logged_date=today - timedelta(days=5))

            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            assert stat.current_streak == 1

    def test_completion_rate_30d(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Rate Stat")
            today = date.today()
            # Log 15 out of last 30 days
            for i in range(0, 30, 2):
                log_habit_completion(stat_user.id, habit.id, logged_date=today - timedelta(days=i))

            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            assert stat.completion_rate_30d is not None
            assert stat.completion_rate_30d == pytest.approx(15 / 30.0)

    def test_longest_streak_preserved(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Longest Streak")
            today = date.today()
            # Build a 5-day streak in the past
            for i in range(5):
                log_habit_completion(
                    stat_user.id,
                    habit.id,
                    logged_date=today - timedelta(days=10 + i),
                )
            # Now a 2-day streak recently
            for i in range(2):
                log_habit_completion(stat_user.id, habit.id, logged_date=today - timedelta(days=i))

            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            assert stat.current_streak == 2
            assert stat.longest_streak == 5


# ============== Event emission tests ==============


class TestStatEventEmission:
    """Tests that stat recomputation emits the correct events."""

    def test_stat_recomputed_event_emitted(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Event Stat")

            initial = OutboxMessage.query.filter_by(user_id=stat_user.id, event_type="habits.stat.recomputed").count()

            log_habit_completion(stat_user.id, habit.id, logged_date=date.today())

            final = OutboxMessage.query.filter_by(user_id=stat_user.id, event_type="habits.stat.recomputed").count()
            assert final == initial + 1

    def test_stat_recomputed_on_delete(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Delete Event Stat")
            log = log_habit_completion(stat_user.id, habit.id, logged_date=date.today())

            initial = OutboxMessage.query.filter_by(user_id=stat_user.id, event_type="habits.stat.recomputed").count()

            delete_habit_log(stat_user.id, log.id)

            final = OutboxMessage.query.filter_by(user_id=stat_user.id, event_type="habits.stat.recomputed").count()
            assert final == initial + 1

    def test_streak_milestone_7_emitted(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Milestone 7")
            today = date.today()
            # Log 7 consecutive days
            for i in range(7):
                log_habit_completion(stat_user.id, habit.id, logged_date=today - timedelta(days=i))

            milestones = OutboxMessage.query.filter_by(
                user_id=stat_user.id,
                event_type="habits.habit.streak_milestone",
            ).all()
            assert len(milestones) >= 1
            payloads = [m.payload for m in milestones]
            assert any(p.get("milestone_type") == 7 for p in payloads)

    def test_no_milestone_below_threshold(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="No Milestone")
            today = date.today()
            # Log only 3 consecutive days — below 7 threshold
            for i in range(3):
                log_habit_completion(stat_user.id, habit.id, logged_date=today - timedelta(days=i))

            milestones = OutboxMessage.query.filter_by(
                user_id=stat_user.id,
                event_type="habits.habit.streak_milestone",
            ).count()
            assert milestones == 0

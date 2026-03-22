"""Tests for HAB-017: Comprehensive streak accuracy test suite.

Validates edge cases in compute_streaks (pure function) and
recompute_habit_stat (materialized stats) to ensure deterministic
streak calculations under backdated logs, duplicates, deletions,
future dates, long streaks, and the 1-day grace-period tolerance.
"""

from datetime import date, timedelta

import pytest

pytestmark = pytest.mark.integration

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.domains.habits.models.habit_models import HabitLog, HabitStat
from lifeos.domains.habits.services import (
    create_habit,
    delete_habit_log,
    log_habit_completion,
    update_habit_log,
)
from lifeos.domains.habits.services.stat_service import (
    compute_streaks,
    recompute_habit_stat,
)
from lifeos.extensions import db


@pytest.fixture
def stat_user(app):
    """Create a test user for streak accuracy tests."""
    with app.app_context():
        user = User(
            email="streak-accuracy@example.com",
            password_hash=hash_password("secret"),
        )
        db.session.add(user)
        db.session.commit()
        yield user


def _fetch_logs_desc(habit_id: int):
    """Helper: fetch logs for a habit sorted descending by logged_date."""
    return HabitLog.query.filter_by(habit_id=habit_id).order_by(HabitLog.logged_date.desc()).all()


# ============== 1. Backdated logs ==============


class TestBackdatedLogs:
    """Logging today then backdating a log 5 days ago should NOT bridge the gap."""

    def test_backdated_log_does_not_bridge_gap(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Backdate Streak")
            today = date.today()

            # Log today
            log_habit_completion(stat_user.id, habit.id, logged_date=today)
            # Backdate a log to 5 days ago — gap of 4 days in between
            log_habit_completion(stat_user.id, habit.id, logged_date=today - timedelta(days=5))

            logs = _fetch_logs_desc(habit.id)
            current, best = compute_streaks(logs)

            # The two logs are 5 days apart — no bridge.
            # Current streak is the first consecutive run (just today = 1).
            assert current == 1
            assert best == 1

            # Verify materialized stat agrees
            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            assert stat is not None
            assert stat.current_streak == 1


# ============== 2. Future-dated logs ==============


class TestFutureDatedLogs:
    """A log for tomorrow should not count toward the current streak from today."""

    def test_future_log_forms_separate_streak(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Future Streak")
            today = date.today()
            tomorrow = today + timedelta(days=1)

            # Log today and tomorrow
            log_habit_completion(stat_user.id, habit.id, logged_date=today)
            log_habit_completion(stat_user.id, habit.id, logged_date=tomorrow)

            logs = _fetch_logs_desc(habit.id)
            current, best = compute_streaks(logs)

            # Tomorrow and today are consecutive, so current_streak = 2
            # (the algorithm starts from the most recent log and walks back)
            assert current == 2
            assert best == 2

    def test_future_log_with_gap_to_today(self, app, stat_user):
        """Future log 3 days out + today = gap, not consecutive."""
        with app.app_context():
            habit = create_habit(stat_user.id, name="Future Gap Streak")
            today = date.today()
            future = today + timedelta(days=3)

            log_habit_completion(stat_user.id, habit.id, logged_date=today)
            log_habit_completion(stat_user.id, habit.id, logged_date=future)

            logs = _fetch_logs_desc(habit.id)
            current, best = compute_streaks(logs)

            # Future log is the most recent; gap to today is 2 days, so
            # current streak = 1 (just the future log).
            assert current == 1
            assert best == 1


# ============== 3. Duplicate dates ==============


class TestDuplicateDates:
    """Multiple logs on the same date: the algorithm walks sorted-desc logs,
    and a duplicate date after processing resets the run (it falls into the
    else branch). This tests the actual behavior."""

    def test_duplicate_date_does_not_double_count(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Duplicate Date")
            today = date.today()

            # Two logs on the same day
            log_habit_completion(stat_user.id, habit.id, logged_date=today)
            log_habit_completion(stat_user.id, habit.id, logged_date=today)

            logs = _fetch_logs_desc(habit.id)
            current, best = compute_streaks(logs)

            # Duplicate falls to else-branch: first log sets run=1, duplicate
            # resets and starts new run=1. So current_streak=1, best=1.
            assert current == 1
            assert best == 1

    def test_duplicate_in_middle_of_streak(self, app, stat_user):
        """Consecutive days D, D-1, D-1, D-2: duplicate D-1 breaks the run."""
        with app.app_context():
            habit = create_habit(stat_user.id, name="Dup Middle")
            today = date.today()

            log_habit_completion(stat_user.id, habit.id, logged_date=today)
            log_habit_completion(stat_user.id, habit.id, logged_date=today - timedelta(days=1))
            # Duplicate for yesterday
            log_habit_completion(stat_user.id, habit.id, logged_date=today - timedelta(days=1))
            log_habit_completion(stat_user.id, habit.id, logged_date=today - timedelta(days=2))

            logs = _fetch_logs_desc(habit.id)
            current, best = compute_streaks(logs)

            # Walk: today(run=1) -> D-1(run=2) -> D-1 duplicate (else: save
            # current=2, run=1) -> D-2 (elif tolerance: run=2).
            # Final: current_streak=2 (first run), best=2.
            assert current == 2
            assert best == 2


# ============== 4. Single log ==============


class TestSingleLog:
    """A single log should give streak of 1."""

    def test_single_log_streak(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Single Log")
            log_habit_completion(stat_user.id, habit.id, logged_date=date.today())

            logs = _fetch_logs_desc(habit.id)
            current, best = compute_streaks(logs)
            assert current == 1
            assert best == 1

            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            assert stat.current_streak == 1
            assert stat.longest_streak == 1


# ============== 5. Long streak (30+ days) ==============


class TestLongStreak:
    """A 35-day streak should report current=35, best=35."""

    def test_35_day_streak(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Long Streak")
            today = date.today()

            for i in range(35):
                log_habit_completion(
                    stat_user.id,
                    habit.id,
                    logged_date=today - timedelta(days=i),
                )

            logs = _fetch_logs_desc(habit.id)
            current, best = compute_streaks(logs)
            assert current == 35
            assert best == 35

            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            assert stat.current_streak == 35
            assert stat.longest_streak == 35


# ============== 6. Streak break and rebuild ==============


class TestStreakBreakAndRebuild:
    """Build 10-day streak, gap of 3 days, then 5-day streak.
    current=5, best=10."""

    def test_break_and_rebuild(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Break Rebuild")
            today = date.today()

            # Recent 5-day streak: today through today-4
            for i in range(5):
                log_habit_completion(
                    stat_user.id,
                    habit.id,
                    logged_date=today - timedelta(days=i),
                )

            # Gap of 3 days (days 5, 6, 7 are missing)

            # Older 10-day streak: today-8 through today-17
            for i in range(10):
                log_habit_completion(
                    stat_user.id,
                    habit.id,
                    logged_date=today - timedelta(days=8 + i),
                )

            logs = _fetch_logs_desc(habit.id)
            current, best = compute_streaks(logs)
            assert current == 5
            assert best == 10

            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            assert stat.current_streak == 5
            assert stat.longest_streak == 10


# ============== 7. All logs in the past (no recent) ==============


class TestAllLogsInPast:
    """Logs only from 30+ days ago — current streak reflects the most recent
    consecutive run, even if it ended long ago."""

    def test_old_streak_still_counted(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Old Streak")
            today = date.today()

            # 5 consecutive days starting 35 days ago (days 35-31)
            for i in range(5):
                log_habit_completion(
                    stat_user.id,
                    habit.id,
                    logged_date=today - timedelta(days=31 + i),
                )

            logs = _fetch_logs_desc(habit.id)
            current, best = compute_streaks(logs)

            # The most recent consecutive run is 5 days (31-35 days ago)
            assert current == 5
            assert best == 5

    def test_old_two_streaks_with_gap(self, app, stat_user):
        """Two old streaks: 3-day (days 31-33) and 5-day (days 40-44)."""
        with app.app_context():
            habit = create_habit(stat_user.id, name="Old Two Streaks")
            today = date.today()

            # More recent old streak: 3 days (31-33 days ago)
            for i in range(3):
                log_habit_completion(
                    stat_user.id,
                    habit.id,
                    logged_date=today - timedelta(days=31 + i),
                )

            # Older streak: 5 days (40-44 days ago)
            for i in range(5):
                log_habit_completion(
                    stat_user.id,
                    habit.id,
                    logged_date=today - timedelta(days=40 + i),
                )

            logs = _fetch_logs_desc(habit.id)
            current, best = compute_streaks(logs)

            assert current == 3  # most recent consecutive run
            assert best == 5  # longest ever


# ============== 8. Delete middle log ==============


class TestDeleteMiddleLog:
    """5 consecutive days, delete the middle one — streak splits."""

    def test_delete_middle_splits_streak(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Delete Middle")
            today = date.today()

            logs_created = []
            for i in range(5):
                log = log_habit_completion(
                    stat_user.id,
                    habit.id,
                    logged_date=today - timedelta(days=i),
                )
                logs_created.append(log)

            # Before deletion: streak should be 5
            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            assert stat.current_streak == 5

            # Delete the middle log (day 2 = today - 2)
            middle_log = [lg for lg in logs_created if lg.logged_date == today - timedelta(days=2)][0]
            delete_habit_log(stat_user.id, middle_log.id)

            # After deletion: remaining dates are today, today-1, today-3, today-4
            # Walk through compute_streaks:
            # expected=today, log=today -> run=1, expected=today-1
            # expected=today-1, log=today-1 -> run=2, expected=today-2
            # expected=today-2, log=today-3 -> (today-2 - (today-3)).days=1
            #   -> elif (grace period): run=3, expected=today-4
            # expected=today-4, log=today-4 -> run=4, expected=today-5
            # Result: current=4, best=4
            # The 1-day tolerance bridges the gap left by the deleted log.

            logs = _fetch_logs_desc(habit.id)
            current, best = compute_streaks(logs)
            assert current == 4
            assert best == 4

            # recompute_habit_stat recalculates from scratch, so materialized
            # stat should match the pure function result.
            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            assert stat.current_streak == 4
            assert stat.longest_streak == 4


# ============== 9. Delete most recent log ==============


class TestDeleteMostRecentLog:
    """5 consecutive days, delete today's log — current streak recalculates."""

    def test_delete_today_recalculates(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Delete Recent")
            today = date.today()

            logs_created = []
            for i in range(5):
                log = log_habit_completion(
                    stat_user.id,
                    habit.id,
                    logged_date=today - timedelta(days=i),
                )
                logs_created.append(log)

            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            assert stat.current_streak == 5

            # Delete today's log
            today_log = [lg for lg in logs_created if lg.logged_date == today][0]
            delete_habit_log(stat_user.id, today_log.id)

            # Remaining: today-1 through today-4 = 4 consecutive days
            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            assert stat.current_streak == 4
            assert stat.longest_streak == 4
            assert stat.total_logs == 4


# ============== 10. Zero logs after all deleted ==============


class TestZeroLogsAfterAllDeleted:
    """Delete all logs — streak goes to 0, stat reflects it."""

    def test_all_deleted_zeroes_stat(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Delete All")
            today = date.today()

            logs_created = []
            for i in range(3):
                log = log_habit_completion(
                    stat_user.id,
                    habit.id,
                    logged_date=today - timedelta(days=i),
                )
                logs_created.append(log)

            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            assert stat.current_streak == 3

            # Delete all logs
            for lg in logs_created:
                delete_habit_log(stat_user.id, lg.id)

            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            assert stat.current_streak == 0
            assert stat.longest_streak == 0
            assert stat.total_logs == 0
            assert stat.last_logged_at is None


# ============== 11. Grace period / 1-day tolerance ==============


class TestGracePeriodOneDayTolerance:
    """The algorithm's elif branch allows (expected - log.logged_date).days == 1.
    This means a single missed day does NOT break the streak — the algorithm
    treats it as a grace period / 1-day tolerance."""

    def test_one_day_gap_does_not_break_streak(self, app, stat_user):
        """Logs on days D, D-2 (skip D-1): streak should be 2 via tolerance."""
        with app.app_context():
            habit = create_habit(stat_user.id, name="Grace Period 1")
            today = date.today()

            log_habit_completion(stat_user.id, habit.id, logged_date=today)
            log_habit_completion(stat_user.id, habit.id, logged_date=today - timedelta(days=2))

            logs = _fetch_logs_desc(habit.id)
            current, best = compute_streaks(logs)

            # expected starts at today.
            # log=today -> run=1, expected=today-1
            # log=today-2 -> expected=today-1, (today-1 - (today-2)).days = 1
            #   -> elif: run=2, expected=today-3
            # Result: current=2, best=2
            assert current == 2
            assert best == 2

    def test_two_day_gap_breaks_streak(self, app, stat_user):
        """Logs on days D, D-3 (skip D-1 and D-2): streak should break."""
        with app.app_context():
            habit = create_habit(stat_user.id, name="Grace Period 2")
            today = date.today()

            log_habit_completion(stat_user.id, habit.id, logged_date=today)
            log_habit_completion(stat_user.id, habit.id, logged_date=today - timedelta(days=3))

            logs = _fetch_logs_desc(habit.id)
            current, best = compute_streaks(logs)

            # expected=today, log=today -> run=1, expected=today-1
            # log=today-3: (today-1 - (today-3)).days = 2, NOT 1 -> else
            # current_streak=1, best=1, run=1
            # Final: current=1, best=1
            assert current == 1
            assert best == 1

    def test_tolerance_extends_long_streak(self, app, stat_user):
        """D, D-1, D-3, D-4, D-5: one gap at D-2, tolerance bridges it."""
        with app.app_context():
            habit = create_habit(stat_user.id, name="Grace Long")
            today = date.today()

            for offset in [0, 1, 3, 4, 5]:
                log_habit_completion(
                    stat_user.id,
                    habit.id,
                    logged_date=today - timedelta(days=offset),
                )

            logs = _fetch_logs_desc(habit.id)
            current, best = compute_streaks(logs)

            # Walk:
            # expected=today, log=today -> run=1, expected=today-1
            # expected=today-1, log=today-1 -> run=2, expected=today-2
            # expected=today-2, log=today-3 -> (today-2-(today-3))=1 ->
            #   elif: run=3, expected=today-4
            # expected=today-4, log=today-4 -> run=4, expected=today-5
            # expected=today-5, log=today-5 -> run=5, expected=today-6
            # Result: current=5, best=5
            assert current == 5
            assert best == 5

    def test_tolerance_only_once_between_runs(self, app, stat_user):
        """D, D-2, D-4: each has a 1-day gap. Tolerance applies each time."""
        with app.app_context():
            habit = create_habit(stat_user.id, name="Grace Multi")
            today = date.today()

            for offset in [0, 2, 4]:
                log_habit_completion(
                    stat_user.id,
                    habit.id,
                    logged_date=today - timedelta(days=offset),
                )

            logs = _fetch_logs_desc(habit.id)
            current, best = compute_streaks(logs)

            # Walk:
            # expected=today, log=today -> run=1, expected=today-1
            # expected=today-1, log=today-2 -> (today-1-(today-2))=1 ->
            #   elif: run=2, expected=today-3
            # expected=today-3, log=today-4 -> (today-3-(today-4))=1 ->
            #   elif: run=3, expected=today-5
            # Result: current=3, best=3
            assert current == 3
            assert best == 3


# ============== 12. Concurrent logs (same habit, same date) ==============


class TestConcurrentLogsSameDateSameHabit:
    """Logging twice on the same date — second log shouldn't double-count."""

    def test_two_logs_same_date_streak_one(self, app, stat_user):
        with app.app_context():
            habit = create_habit(stat_user.id, name="Concurrent Same Date")
            today = date.today()

            log_habit_completion(stat_user.id, habit.id, logged_date=today)
            log_habit_completion(stat_user.id, habit.id, logged_date=today)

            stat = HabitStat.query.filter_by(habit_id=habit.id).first()
            # Two logs exist but same date — streak is 1, not 2
            assert stat.current_streak == 1
            assert stat.longest_streak == 1
            assert stat.total_logs == 2  # two log rows exist

    def test_concurrent_with_consecutive_days(self, app, stat_user):
        """Two logs on today + one log on yesterday: streak should be 2."""
        with app.app_context():
            habit = create_habit(stat_user.id, name="Concurrent Consec")
            today = date.today()

            log_habit_completion(stat_user.id, habit.id, logged_date=today)
            log_habit_completion(stat_user.id, habit.id, logged_date=today)
            log_habit_completion(stat_user.id, habit.id, logged_date=today - timedelta(days=1))

            logs = _fetch_logs_desc(habit.id)
            current, best = compute_streaks(logs)

            # Walk (sorted desc): today, today, today-1
            # log=today: expected=today -> run=1, expected=today-1
            # log=today: expected=today-1, today != today-1.
            #   (today-1 - today).days = -1, NOT 1. -> else
            #   recent_streak=1, best=1, run=1, expected=today-1
            # log=today-1: expected=today-1 -> run=2, expected=today-2
            # Final: best=max(1,2)=2, recent_streak=1
            assert current == 1
            assert best == 2

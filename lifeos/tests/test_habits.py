import pytest
from datetime import date, timedelta

pytestmark = pytest.mark.integration

from lifeos.domains.habits.models.habit import Habit
from lifeos.domains.habits.services import compute_streak, create_habit, log_habit
from lifeos.extensions import db


def test_habit_streak(app):
    with app.app_context():
        habit = create_habit(user_id=1, name="Read", cadence="daily", target=1)
        today = date.today()
        db.session.add(
            Habit(
                user_id=habit.user_id,
                name="Dummy",
                schedule_type="daily",
                target_count=1,
            )
        )  # ensure multiple rows don't interfere
        db.session.commit()

        log_habit(habit.id, today, 1)
        log_habit(habit.id, today - timedelta(days=1), 1)
        log_habit(habit.id, today - timedelta(days=2), 1)

        streak = compute_streak(Habit.query.get(habit.id))
        assert streak >= 3

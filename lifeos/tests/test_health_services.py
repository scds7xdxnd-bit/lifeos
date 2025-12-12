"""Tests for Health domain services: biometrics, workouts, nutrition."""

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.integration

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.domains.health.models.health_models import Biometric, NutritionLog, Workout
from lifeos.domains.health.services.health_service import (
    create_biometric_entry,
    create_nutrition_log,
    create_workout,
    get_daily_summary,
    list_biometrics,
    list_nutrition_logs,
    list_workouts,
)
from lifeos.extensions import db


@pytest.fixture
def test_user(app):
    """Create a test user for health tests."""
    with app.app_context():
        user = User(
            email="health-tester@example.com", password_hash=hash_password("secret")
        )
        db.session.add(user)
        db.session.commit()
        yield user


# ============== Biometrics Service Tests ==============


class TestBiometricsService:
    """Tests for biometric entry creation and retrieval."""

    def test_create_biometric_entry_success(self, app, test_user):
        """Create a valid biometric entry."""
        with app.app_context():
            biometric = create_biometric_entry(
                test_user.id,
                date_value=date.today(),
                weight=75.5,
                body_fat_pct=18.5,
                resting_hr=65,
                energy_level=4,
                stress_level=2,
                notes="Feeling good today",
            )

            assert biometric.id is not None
            assert biometric.user_id == test_user.id
            assert float(biometric.weight) == 75.5
            assert float(biometric.body_fat_pct) == 18.5
            assert biometric.resting_hr == 65
            assert biometric.energy_level == 4
            assert biometric.stress_level == 2
            assert biometric.notes == "Feeling good today"

    def test_create_biometric_entry_minimal(self, app, test_user):
        """Create biometric entry with minimal fields."""
        with app.app_context():
            biometric = create_biometric_entry(
                test_user.id,
                date_value=date.today(),
            )

            assert biometric.id is not None
            assert biometric.weight is None
            assert biometric.body_fat_pct is None

    def test_create_biometric_entry_duplicate_date_fails(self, app, test_user):
        """Cannot create two biometric entries for same date."""
        with app.app_context():
            create_biometric_entry(test_user.id, date_value=date.today(), weight=75.0)

            with pytest.raises(ValueError, match="duplicate"):
                create_biometric_entry(
                    test_user.id, date_value=date.today(), weight=76.0
                )

    def test_create_biometric_entry_invalid_energy_level(self, app, test_user):
        """Energy level must be 1-5."""
        with app.app_context():
            with pytest.raises(ValueError, match="validation_error"):
                create_biometric_entry(
                    test_user.id, date_value=date.today(), energy_level=10
                )

    def test_create_biometric_entry_invalid_stress_level(self, app, test_user):
        """Stress level must be 1-5."""
        with app.app_context():
            with pytest.raises(ValueError, match="validation_error"):
                create_biometric_entry(
                    test_user.id, date_value=date.today(), stress_level=0
                )

    def test_list_biometrics_pagination(self, app, test_user):
        """List biometrics with pagination."""
        with app.app_context():
            # Create multiple entries
            for i in range(5):
                create_biometric_entry(
                    test_user.id,
                    date_value=date.today() - timedelta(days=i),
                    weight=70.0 + i,
                )

            items, total = list_biometrics(test_user.id, page=1, per_page=3)
            assert len(items) == 3
            assert total == 5

            items2, total2 = list_biometrics(test_user.id, page=2, per_page=3)
            assert len(items2) == 2
            assert total2 == 5

    def test_list_biometrics_date_range(self, app, test_user):
        """Filter biometrics by date range."""
        with app.app_context():
            for i in range(10):
                create_biometric_entry(
                    test_user.id,
                    date_value=date.today() - timedelta(days=i),
                )

            start = date.today() - timedelta(days=5)
            end = date.today() - timedelta(days=2)
            items, total = list_biometrics(test_user.id, start_date=start, end_date=end)

            assert total == 4
            for item in items:
                assert start <= item.date <= end


# ============== Workout Service Tests ==============


class TestWorkoutService:
    """Tests for workout creation and retrieval."""

    def test_create_workout_success(self, app, test_user):
        """Create a valid workout entry."""
        with app.app_context():
            workout = create_workout(
                test_user.id,
                date_value=date.today(),
                workout_type="running",
                duration_minutes=45,
                intensity="high",
                calories_est=500.0,
                notes="Morning run in the park",
            )

            assert workout.id is not None
            assert workout.user_id == test_user.id
            assert workout.workout_type == "running"
            assert workout.duration_minutes == 45
            assert workout.intensity == "high"
            assert float(workout.calories_est) == 500.0
            assert workout.notes == "Morning run in the park"
            assert workout.source == "manual"

    def test_create_workout_valid_intensities(self, app, test_user):
        """Workout intensity must be low, medium, or high."""
        with app.app_context():
            for i, intensity in enumerate(["low", "medium", "high"]):
                workout = create_workout(
                    test_user.id,
                    date_value=date.today() - timedelta(days=i),
                    workout_type=f"test_{intensity}",
                    duration_minutes=30,
                    intensity=intensity,
                )
                assert workout.intensity == intensity

    def test_create_workout_invalid_intensity_fails(self, app, test_user):
        """Invalid intensity should raise validation error."""
        with app.app_context():
            with pytest.raises(ValueError, match="validation_error"):
                create_workout(
                    test_user.id,
                    date_value=date.today(),
                    workout_type="running",
                    duration_minutes=30,
                    intensity="extreme",
                )

    def test_create_workout_negative_duration_fails(self, app, test_user):
        """Duration cannot be negative."""
        with app.app_context():
            with pytest.raises(ValueError, match="validation_error"):
                create_workout(
                    test_user.id,
                    date_value=date.today(),
                    workout_type="running",
                    duration_minutes=-10,
                    intensity="medium",
                )

    def test_list_workouts_pagination(self, app, test_user):
        """List workouts with pagination."""
        with app.app_context():
            for i in range(7):
                create_workout(
                    test_user.id,
                    date_value=date.today() - timedelta(days=i),
                    workout_type="running",
                    duration_minutes=30,
                    intensity="medium",
                )

            items, total = list_workouts(test_user.id, page=1, per_page=5)
            assert len(items) == 5
            assert total == 7

    def test_list_workouts_date_filter(self, app, test_user):
        """Filter workouts by date range."""
        with app.app_context():
            for i in range(10):
                create_workout(
                    test_user.id,
                    date_value=date.today() - timedelta(days=i),
                    workout_type="running",
                    duration_minutes=30,
                    intensity="medium",
                )

            start = date.today() - timedelta(days=3)
            items, total = list_workouts(test_user.id, start_date=start)

            assert total == 4


# ============== Nutrition Log Service Tests ==============


class TestNutritionLogService:
    """Tests for nutrition log creation and retrieval."""

    def test_create_nutrition_log_success(self, app, test_user):
        """Create a valid nutrition log entry."""
        with app.app_context():
            log = create_nutrition_log(
                test_user.id,
                date_value=date.today(),
                meal_type="lunch",
                items="Grilled chicken salad with quinoa",
                calories_est=650.0,
                quality_score=4,
            )

            assert log.id is not None
            assert log.user_id == test_user.id
            assert log.meal_type == "lunch"
            assert log.items == "Grilled chicken salad with quinoa"
            assert float(log.calories_est) == 650.0
            assert log.quality_score == 4

    def test_create_nutrition_log_valid_meal_types(self, app, test_user):
        """Meal type must be one of the valid options."""
        with app.app_context():
            valid_types = ["breakfast", "lunch", "dinner", "snack", "other"]
            for i, meal_type in enumerate(valid_types):
                log = create_nutrition_log(
                    test_user.id,
                    date_value=date.today() - timedelta(days=i),
                    meal_type=meal_type,
                    items=f"Test {meal_type}",
                )
                assert log.meal_type == meal_type

    def test_create_nutrition_log_invalid_meal_type_fails(self, app, test_user):
        """Invalid meal type should raise validation error."""
        with app.app_context():
            with pytest.raises(ValueError, match="validation_error"):
                create_nutrition_log(
                    test_user.id,
                    date_value=date.today(),
                    meal_type="brunch",  # Not a valid meal type
                    items="Test meal",
                )

    def test_create_nutrition_log_invalid_quality_score_fails(self, app, test_user):
        """Quality score must be 1-5."""
        with app.app_context():
            with pytest.raises(ValueError, match="validation_error"):
                create_nutrition_log(
                    test_user.id,
                    date_value=date.today(),
                    meal_type="lunch",
                    items="Test meal",
                    quality_score=10,
                )

    def test_list_nutrition_logs_pagination(self, app, test_user):
        """List nutrition logs with pagination."""
        with app.app_context():
            for i in range(8):
                create_nutrition_log(
                    test_user.id,
                    date_value=date.today() - timedelta(days=i),
                    meal_type="lunch",
                    items=f"Meal {i}",
                )

            items, total = list_nutrition_logs(test_user.id, page=1, per_page=5)
            assert len(items) == 5
            assert total == 8


# ============== Daily Summary Tests ==============


class TestDailySummary:
    """Tests for daily health summary."""

    def test_get_daily_summary(self, app, test_user):
        """Get daily summary with all health records."""
        with app.app_context():
            today = date.today()

            # Create biometric entry
            create_biometric_entry(
                test_user.id,
                date_value=today,
                weight=75.0,
                energy_level=4,
                stress_level=2,
            )

            # Create workout
            create_workout(
                test_user.id,
                date_value=today,
                workout_type="running",
                duration_minutes=45,
                intensity="high",
                calories_est=400,
            )

            # Create nutrition logs
            create_nutrition_log(
                test_user.id,
                date_value=today,
                meal_type="breakfast",
                items="Oatmeal",
                calories_est=350,
            )
            create_nutrition_log(
                test_user.id,
                date_value=today,
                meal_type="lunch",
                items="Salad",
                calories_est=500,
            )

            summary = get_daily_summary(test_user.id, today)

            assert summary["date"] == today
            assert summary["biometric"] is not None
            assert float(summary["biometric"].weight) == 75.0
            assert summary["energy_level"] == 4
            assert summary["stress_level"] == 2
            assert summary["workouts"]["count"] == 1
            assert summary["nutrition"]["count"] == 2

    def test_get_daily_summary_empty_day(self, app, test_user):
        """Get daily summary for a day with no records."""
        with app.app_context():
            summary = get_daily_summary(test_user.id, date.today())

            assert summary["biometric"] is None
            assert summary["workouts"]["count"] == 0
            assert summary["nutrition"]["count"] == 0


# ============== Event Emission Tests ==============


class TestHealthEventEmission:
    """Tests for health event emission to outbox."""

    def test_biometric_logged_event_emitted(self, app, test_user):
        """Biometric creation should emit event to outbox."""
        with app.app_context():
            from lifeos.lifeos_platform.outbox.models import OutboxMessage

            initial_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="health.biometric.logged"
            ).count()

            create_biometric_entry(test_user.id, date_value=date.today(), weight=75.0)

            final_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="health.biometric.logged"
            ).count()

            assert final_count == initial_count + 1

    def test_workout_logged_event_emitted(self, app, test_user):
        """Workout creation should emit event to outbox."""
        with app.app_context():
            from lifeos.lifeos_platform.outbox.models import OutboxMessage

            initial_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="health.workout.logged"
            ).count()

            create_workout(
                test_user.id,
                date_value=date.today(),
                workout_type="running",
                duration_minutes=30,
                intensity="medium",
            )

            final_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="health.workout.logged"
            ).count()

            assert final_count == initial_count + 1

    def test_nutrition_logged_event_emitted(self, app, test_user):
        """Nutrition log creation should emit event to outbox."""
        with app.app_context():
            from lifeos.lifeos_platform.outbox.models import OutboxMessage

            initial_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="health.nutrition.logged"
            ).count()

            create_nutrition_log(
                test_user.id,
                date_value=date.today(),
                meal_type="lunch",
                items="Salad",
            )

            final_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="health.nutrition.logged"
            ).count()

            assert final_count == initial_count + 1

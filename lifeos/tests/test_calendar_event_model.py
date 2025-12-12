"""
Comprehensive tests for CalendarEvent and CalendarEventInterpretation models.

Tests cover:
- Unit tests for model properties and methods
- Integration tests for database operations
- Fixtures for reusable test data
- Mock patterns for external dependencies
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from flask_jwt_extended import create_access_token

pytestmark = pytest.mark.integration

from lifeos.core.auth.password import hash_password
from lifeos.core.interpreter.constants import (
    DOMAIN_FINANCE,
    DOMAIN_HEALTH,
    DOMAIN_HABITS,
    DOMAIN_PROJECTS,
    DOMAIN_RELATIONSHIPS,
    DOMAIN_SKILLS,
    RECORD_TYPE_INTERACTION,
    RECORD_TYPE_MEAL,
    RECORD_TYPE_PRACTICE,
    RECORD_TYPE_TRANSACTION,
    RECORD_TYPE_WORK_SESSION,
    RECORD_TYPE_WORKOUT,
    STATUS_CONFIRMED,
    STATUS_INFERRED,
    STATUS_REJECTED,
    STATUS_IGNORED,
)
from lifeos.core.users.models import User
from lifeos.domains.calendar.models.calendar_event import (
    CalendarEvent,
    CalendarEventInterpretation,
)
from lifeos.extensions import db


# ==================== Fixtures ====================


@pytest.fixture
def test_user(app):
    """Create a test user for calendar tests."""
    with app.app_context():
        user = User(
            email="calendar-model-tester@example.com",
            password_hash=hash_password("secure_password_123"),
            full_name="Calendar Tester",
            timezone="America/New_York",
        )
        db.session.add(user)
        db.session.commit()
        yield user


@pytest.fixture
def second_user(app):
    """Create a second user for cross-user isolation tests."""
    with app.app_context():
        user = User(
            email="calendar-model-tester-2@example.com",
            password_hash=hash_password("another_password_456"),
            full_name="Second Tester",
            timezone="Europe/London",
        )
        db.session.add(user)
        db.session.commit()
        yield user


@pytest.fixture
def sample_calendar_event(app, test_user):
    """Create a sample calendar event for testing."""
    with app.app_context():
        event = CalendarEvent(
            user_id=test_user.id,
            title="Team Meeting",
            description="Weekly sync with development team",
            start_time=datetime(2025, 12, 7, 10, 0, 0),
            end_time=datetime(2025, 12, 7, 11, 0, 0),
            location="Conference Room A",
            source="manual",
            all_day=False,
            color="#3498db",
            is_private=False,
            tags=["work", "meeting"],
            metadata_={"organizer": "test_user", "attendees": 5},
        )
        db.session.add(event)
        db.session.commit()
        yield event


@pytest.fixture
def all_day_event(app, test_user):
    """Create an all-day calendar event for testing."""
    with app.app_context():
        event = CalendarEvent(
            user_id=test_user.id,
            title="Company Holiday",
            description="Office closed for holiday",
            start_time=datetime(2025, 12, 25, 0, 0, 0),
            end_time=None,
            all_day=True,
            source="sync_google",
            external_id="google_event_12345",
        )
        db.session.add(event)
        db.session.commit()
        yield event


@pytest.fixture
def recurring_event(app, test_user):
    """Create a recurring calendar event for testing."""
    with app.app_context():
        event = CalendarEvent(
            user_id=test_user.id,
            title="Daily Standup",
            start_time=datetime(2025, 12, 7, 9, 0, 0),
            end_time=datetime(2025, 12, 7, 9, 15, 0),
            recurrence_rule="RRULE:FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR",
            source="manual",
        )
        db.session.add(event)
        db.session.commit()
        yield event


@pytest.fixture
def event_with_interpretation(app, test_user):
    """Create a calendar event with an associated interpretation."""
    with app.app_context():
        event = CalendarEvent(
            user_id=test_user.id,
            title="Gym Workout",
            description="Leg day at the fitness center",
            start_time=datetime(2025, 12, 7, 6, 0, 0),
            end_time=datetime(2025, 12, 7, 7, 30, 0),
            location="Anytime Fitness",
            source="manual",
        )
        db.session.add(event)
        db.session.flush()

        interpretation = CalendarEventInterpretation(
            calendar_event_id=event.id,
            user_id=test_user.id,
            domain=DOMAIN_HEALTH,
            record_type=RECORD_TYPE_WORKOUT,
            confidence_score=0.85,
            status=STATUS_INFERRED,
            classification_data={
                "workout_type": "strength",
                "duration_minutes": 90,
                "intensity": "high",
            },
        )
        db.session.add(interpretation)
        db.session.commit()
        yield event, interpretation


@pytest.fixture
def multiple_events(app, test_user):
    """Create multiple calendar events for listing tests."""
    with app.app_context():
        events = []
        base_date = datetime(2025, 12, 7, 8, 0, 0)

        for i in range(5):
            event = CalendarEvent(
                user_id=test_user.id,
                title=f"Event {i + 1}",
                start_time=base_date + timedelta(hours=i * 2),
                end_time=base_date + timedelta(hours=i * 2 + 1),
                source="manual" if i % 2 == 0 else "sync_google",
            )
            events.append(event)
            db.session.add(event)

        db.session.commit()
        yield events


@pytest.fixture
def auth_headers(app, test_user):
    """Generate JWT headers for authenticated API calls."""
    with app.app_context():
        token = create_access_token(
            identity=str(test_user.id),
            additional_claims={"roles": ["calendar:write", "calendar:read"]},
        )
    return {"Authorization": f"Bearer {token}"}


# ==================== Unit Tests: CalendarEvent Model ====================


class TestCalendarEventModel:
    """Unit tests for the CalendarEvent model class."""

    def test_create_minimal_event(self, app, test_user):
        """Test creating an event with only required fields."""
        with app.app_context():
            event = CalendarEvent(
                user_id=test_user.id,
                title="Minimal Event",
                start_time=datetime.now(),
            )
            db.session.add(event)
            db.session.commit()

            assert event.id is not None
            assert event.title == "Minimal Event"
            assert event.user_id == test_user.id
            assert event.source == "manual"
            assert event.all_day is False
            assert event.is_private is False
            assert event.tags == []
            assert event.metadata_ == {}
            assert event.end_time is None
            assert event.description is None
            assert event.location is None

    def test_create_full_event(self, app, test_user):
        """Test creating an event with all fields populated."""
        with app.app_context():
            start = datetime(2025, 12, 7, 14, 0, 0)
            end = datetime(2025, 12, 7, 15, 30, 0)

            event = CalendarEvent(
                user_id=test_user.id,
                title="Complete Event",
                description="Full description with all details",
                start_time=start,
                end_time=end,
                all_day=False,
                location="123 Main Street, Suite 100",
                source="sync_apple",
                external_id="apple_cal_xyz789",
                recurrence_rule="RRULE:FREQ=WEEKLY;BYDAY=MO",
                color="#e74c3c",
                is_private=True,
                tags=["personal", "important"],
                metadata_={"priority": "high", "reminder_minutes": 30},
            )
            db.session.add(event)
            db.session.commit()

            # Verify all fields were saved correctly
            assert event.id is not None
            assert event.title == "Complete Event"
            assert event.description == "Full description with all details"
            assert event.start_time == start
            assert event.end_time == end
            assert event.all_day is False
            assert event.location == "123 Main Street, Suite 100"
            assert event.source == "sync_apple"
            assert event.external_id == "apple_cal_xyz789"
            assert event.recurrence_rule == "RRULE:FREQ=WEEKLY;BYDAY=MO"
            assert event.color == "#e74c3c"
            assert event.is_private is True
            assert event.tags == ["personal", "important"]
            assert event.metadata_ == {"priority": "high", "reminder_minutes": 30}

    def test_duration_minutes_property(self, app, test_user):
        """Test the duration_minutes computed property."""
        with app.app_context():
            # Event with end_time
            event = CalendarEvent(
                user_id=test_user.id,
                title="Timed Event",
                start_time=datetime(2025, 12, 7, 10, 0, 0),
                end_time=datetime(2025, 12, 7, 12, 30, 0),
            )
            assert event.duration_minutes == 150  # 2.5 hours = 150 minutes

    def test_duration_minutes_without_end_time(self, app, test_user):
        """Test duration_minutes returns None when end_time is not set."""
        with app.app_context():
            event = CalendarEvent(
                user_id=test_user.id,
                title="Open-ended Event",
                start_time=datetime(2025, 12, 7, 10, 0, 0),
                end_time=None,
            )
            assert event.duration_minutes is None

    def test_duration_minutes_zero_duration(self, app, test_user):
        """Test duration_minutes for zero-duration events."""
        with app.app_context():
            same_time = datetime(2025, 12, 7, 10, 0, 0)
            event = CalendarEvent(
                user_id=test_user.id,
                title="Instant Event",
                start_time=same_time,
                end_time=same_time,
            )
            assert event.duration_minutes == 0

    def test_timestamps_auto_populated(self, app, test_user):
        """Test that created_at and updated_at are automatically set."""
        with app.app_context():
            before = datetime.utcnow()

            event = CalendarEvent(
                user_id=test_user.id,
                title="Timestamped Event",
                start_time=datetime.now(),
            )
            db.session.add(event)
            db.session.commit()

            after = datetime.utcnow()

            assert event.created_at is not None
            assert event.updated_at is not None
            assert before <= event.created_at <= after
            assert before <= event.updated_at <= after

    def test_source_values(self, app, test_user):
        """Test valid source values for calendar events."""
        valid_sources = ["manual", "sync_google", "sync_apple", "api"]

        with app.app_context():
            for source in valid_sources:
                event = CalendarEvent(
                    user_id=test_user.id,
                    title=f"Event from {source}",
                    start_time=datetime.now(),
                    source=source,
                )
                db.session.add(event)
                db.session.commit()

                assert event.source == source

    def test_interpretations_relationship(self, app, event_with_interpretation):
        """Test the interpretations relationship on CalendarEvent."""
        event, interpretation = event_with_interpretation

        with app.app_context():
            loaded_event = CalendarEvent.query.get(event.id)
            assert len(loaded_event.interpretations) == 1
            assert loaded_event.interpretations[0].domain == DOMAIN_HEALTH

    def test_event_cascade_delete_interpretations(self, app, event_with_interpretation):
        """Test that deleting an event cascades to delete interpretations."""
        event, interpretation = event_with_interpretation

        with app.app_context():
            event_id = event.id
            interpretation_id = interpretation.id

            loaded_event = CalendarEvent.query.get(event_id)
            db.session.delete(loaded_event)
            db.session.commit()

            # Verify event and interpretation are both deleted
            assert CalendarEvent.query.get(event_id) is None
            assert CalendarEventInterpretation.query.get(interpretation_id) is None


# ==================== Unit Tests: CalendarEventInterpretation Model ====================


class TestCalendarEventInterpretationModel:
    """Unit tests for the CalendarEventInterpretation model class."""

    def test_create_interpretation(self, app, sample_calendar_event):
        """Test creating a calendar event interpretation."""
        with app.app_context():
            interpretation = CalendarEventInterpretation(
                calendar_event_id=sample_calendar_event.id,
                user_id=sample_calendar_event.user_id,
                domain=DOMAIN_PROJECTS,
                record_type=RECORD_TYPE_WORK_SESSION,
                confidence_score=0.75,
                status=STATUS_INFERRED,
                classification_data={"project_name": "LifeOS", "duration_minutes": 60},
            )
            db.session.add(interpretation)
            db.session.commit()

            assert interpretation.id is not None
            assert interpretation.calendar_event_id == sample_calendar_event.id
            assert interpretation.domain == DOMAIN_PROJECTS
            assert interpretation.record_type == RECORD_TYPE_WORK_SESSION
            assert float(interpretation.confidence_score) == 0.75

    def test_interpretation_status_transitions(self, app, sample_calendar_event):
        """Test interpretation status can be updated."""
        with app.app_context():
            interpretation = CalendarEventInterpretation(
                calendar_event_id=sample_calendar_event.id,
                user_id=sample_calendar_event.user_id,
                domain=DOMAIN_HEALTH,
                record_type=RECORD_TYPE_WORKOUT,
                confidence_score=0.80,
                status=STATUS_INFERRED,
            )
            db.session.add(interpretation)
            db.session.commit()

            # Update to confirmed
            interpretation.status = STATUS_CONFIRMED
            interpretation.record_id = 123
            db.session.commit()

            loaded = CalendarEventInterpretation.query.get(interpretation.id)
            assert loaded.status == STATUS_CONFIRMED
            assert loaded.record_id == 123

    def test_interpretation_all_domains(self, app, sample_calendar_event):
        """Test interpretations can be created for all supported domains."""
        domain_record_pairs = [
            (DOMAIN_FINANCE, RECORD_TYPE_TRANSACTION),
            (DOMAIN_HEALTH, RECORD_TYPE_WORKOUT),
            (DOMAIN_HEALTH, RECORD_TYPE_MEAL),
            (DOMAIN_HABITS, "habit_log"),
            (DOMAIN_SKILLS, RECORD_TYPE_PRACTICE),
            (DOMAIN_PROJECTS, RECORD_TYPE_WORK_SESSION),
            (DOMAIN_RELATIONSHIPS, RECORD_TYPE_INTERACTION),
        ]

        with app.app_context():
            for domain, record_type in domain_record_pairs:
                interpretation = CalendarEventInterpretation(
                    calendar_event_id=sample_calendar_event.id,
                    user_id=sample_calendar_event.user_id,
                    domain=domain,
                    record_type=record_type,
                    confidence_score=0.70,
                    status=STATUS_INFERRED,
                )
                db.session.add(interpretation)
                db.session.commit()

                assert interpretation.id is not None
                assert interpretation.domain == domain
                assert interpretation.record_type == record_type

    def test_interpretation_confidence_score_precision(
        self, app, sample_calendar_event
    ):
        """Test confidence score maintains decimal precision."""
        with app.app_context():
            interpretation = CalendarEventInterpretation(
                calendar_event_id=sample_calendar_event.id,
                user_id=sample_calendar_event.user_id,
                domain=DOMAIN_HEALTH,
                record_type=RECORD_TYPE_WORKOUT,
                confidence_score=0.87,
                status=STATUS_INFERRED,
            )
            db.session.add(interpretation)
            db.session.commit()

            loaded = CalendarEventInterpretation.query.get(interpretation.id)
            assert float(loaded.confidence_score) == 0.87

    def test_interpretation_classification_data_json(self, app, sample_calendar_event):
        """Test classification_data stores complex JSON structures."""
        with app.app_context():
            complex_data = {
                "extracted_keywords": ["gym", "workout", "fitness"],
                "matched_patterns": ["exercise", "training"],
                "location_boost": True,
                "time_context": {
                    "morning": True,
                    "typical_workout_time": True,
                },
                "suggested_record": {
                    "workout_type": "strength",
                    "intensity": "medium",
                    "estimated_calories": 350,
                },
            }

            interpretation = CalendarEventInterpretation(
                calendar_event_id=sample_calendar_event.id,
                user_id=sample_calendar_event.user_id,
                domain=DOMAIN_HEALTH,
                record_type=RECORD_TYPE_WORKOUT,
                confidence_score=0.82,
                status=STATUS_INFERRED,
                classification_data=complex_data,
            )
            db.session.add(interpretation)
            db.session.commit()

            loaded = CalendarEventInterpretation.query.get(interpretation.id)
            assert loaded.classification_data == complex_data
            assert loaded.classification_data["time_context"]["morning"] is True

    def test_interpretation_calendar_event_relationship(
        self, app, event_with_interpretation
    ):
        """Test interpretation back-reference to calendar event."""
        event, interpretation = event_with_interpretation

        with app.app_context():
            loaded_interp = CalendarEventInterpretation.query.get(interpretation.id)
            assert loaded_interp.calendar_event is not None
            assert loaded_interp.calendar_event.id == event.id
            assert loaded_interp.calendar_event.title == "Gym Workout"


# ==================== Integration Tests: Database Operations ====================


class TestCalendarEventDatabaseIntegration:
    """Integration tests for CalendarEvent database operations."""

    def test_query_by_user_id(self, app, test_user, second_user):
        """Test querying events by user_id for isolation."""
        with app.app_context():
            # Create events for both users
            event1 = CalendarEvent(
                user_id=test_user.id,
                title="User 1 Event",
                start_time=datetime.now(),
            )
            event2 = CalendarEvent(
                user_id=second_user.id,
                title="User 2 Event",
                start_time=datetime.now(),
            )
            db.session.add_all([event1, event2])
            db.session.commit()

            # Query for test_user's events only
            user1_events = CalendarEvent.query.filter_by(user_id=test_user.id).all()
            assert len(user1_events) == 1
            assert user1_events[0].title == "User 1 Event"

    def test_query_by_date_range(self, app, multiple_events, test_user):
        """Test querying events within a date range."""
        with app.app_context():
            start = datetime(2025, 12, 7, 9, 0, 0)
            end = datetime(2025, 12, 7, 13, 0, 0)

            events = CalendarEvent.query.filter(
                CalendarEvent.user_id == test_user.id,
                CalendarEvent.start_time >= start,
                CalendarEvent.start_time <= end,
            ).all()

            # Should return events within the 9:00-13:00 window
            assert len(events) >= 2

    def test_query_by_source(self, app, multiple_events, test_user):
        """Test filtering events by source."""
        with app.app_context():
            manual_events = CalendarEvent.query.filter_by(
                user_id=test_user.id,
                source="manual",
            ).all()

            google_events = CalendarEvent.query.filter_by(
                user_id=test_user.id,
                source="sync_google",
            ).all()

            assert len(manual_events) > 0
            assert len(google_events) > 0
            assert all(e.source == "manual" for e in manual_events)
            assert all(e.source == "sync_google" for e in google_events)

    def test_unique_external_id_constraint(self, app, test_user):
        """Test unique constraint on user_id + external_id combination."""
        with app.app_context():
            event1 = CalendarEvent(
                user_id=test_user.id,
                title="First Synced Event",
                start_time=datetime.now(),
                source="sync_google",
                external_id="unique_google_id_123",
            )
            db.session.add(event1)
            db.session.commit()

            # Attempting to create another event with same external_id should fail
            event2 = CalendarEvent(
                user_id=test_user.id,
                title="Duplicate Synced Event",
                start_time=datetime.now(),
                source="sync_google",
                external_id="unique_google_id_123",
            )
            db.session.add(event2)

            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()

            db.session.rollback()

    def test_null_external_id_allows_duplicates(self, app, test_user):
        """Test that null external_id doesn't trigger unique constraint."""
        with app.app_context():
            event1 = CalendarEvent(
                user_id=test_user.id,
                title="Manual Event 1",
                start_time=datetime.now(),
                source="manual",
                external_id=None,
            )
            event2 = CalendarEvent(
                user_id=test_user.id,
                title="Manual Event 2",
                start_time=datetime.now(),
                source="manual",
                external_id=None,
            )
            db.session.add_all([event1, event2])
            db.session.commit()

            # Both should be created successfully
            assert event1.id is not None
            assert event2.id is not None
            assert event1.id != event2.id

    def test_ordering_by_start_time(self, app, multiple_events, test_user):
        """Test events can be ordered by start_time."""
        with app.app_context():
            ascending = (
                CalendarEvent.query.filter_by(user_id=test_user.id)
                .order_by(CalendarEvent.start_time.asc())
                .all()
            )

            descending = (
                CalendarEvent.query.filter_by(user_id=test_user.id)
                .order_by(CalendarEvent.start_time.desc())
                .all()
            )

            assert ascending[0].start_time <= ascending[-1].start_time
            assert descending[0].start_time >= descending[-1].start_time

    def test_interpretation_index_by_status(self, app, sample_calendar_event):
        """Test querying interpretations by user and status uses index."""
        with app.app_context():
            # Create interpretations with different statuses
            for status in [STATUS_INFERRED, STATUS_CONFIRMED, STATUS_REJECTED]:
                interpretation = CalendarEventInterpretation(
                    calendar_event_id=sample_calendar_event.id,
                    user_id=sample_calendar_event.user_id,
                    domain=DOMAIN_HEALTH,
                    record_type=RECORD_TYPE_WORKOUT,
                    confidence_score=0.70,
                    status=status,
                )
                db.session.add(interpretation)
            db.session.commit()

            # Query by status
            inferred = CalendarEventInterpretation.query.filter_by(
                user_id=sample_calendar_event.user_id,
                status=STATUS_INFERRED,
            ).all()

            assert len(inferred) == 1


# ==================== Integration Tests: Service Layer ====================


class TestCalendarServiceIntegration:
    """Integration tests for calendar service with the model layer."""

    def test_create_event_via_service(self, app, test_user):
        """Test creating an event through the service layer."""
        from lifeos.domains.calendar.services.calendar_service import (
            create_calendar_event,
        )

        with app.app_context():
            event = create_calendar_event(
                user_id=test_user.id,
                title="Service Created Event",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1),
                description="Created via service",
                location="Test Location",
                tags=["test", "service"],
            )

            assert event.id is not None
            assert event.title == "Service Created Event"
            assert event.tags == ["test", "service"]

            # Verify persisted in database
            loaded = CalendarEvent.query.get(event.id)
            assert loaded is not None
            assert loaded.description == "Created via service"

    def test_update_event_via_service(self, app, sample_calendar_event):
        """Test updating an event through the service layer."""
        from lifeos.domains.calendar.services.calendar_service import (
            update_calendar_event,
        )

        with app.app_context():
            event = update_calendar_event(
                user_id=sample_calendar_event.user_id,
                event_id=sample_calendar_event.id,
                title="Updated Title",
                location="New Location",
            )

            assert event.title == "Updated Title"
            assert event.location == "New Location"
            # Original fields preserved
            assert event.description == "Weekly sync with development team"

    def test_delete_event_via_service(self, app, sample_calendar_event):
        """Test deleting an event through the service layer."""
        from lifeos.domains.calendar.services.calendar_service import (
            delete_calendar_event,
        )

        with app.app_context():
            event_id = sample_calendar_event.id
            delete_calendar_event(
                user_id=sample_calendar_event.user_id,
                event_id=event_id,
            )

            assert CalendarEvent.query.get(event_id) is None

    def test_list_events_via_service(self, app, multiple_events, test_user):
        """Test listing events through the service layer."""
        from lifeos.domains.calendar.services.calendar_service import (
            list_calendar_events,
        )

        with app.app_context():
            events = list_calendar_events(
                user_id=test_user.id,
                limit=10,
            )

            assert len(events) == 5

    def test_service_validation_invalid_title(self, app, test_user):
        """Test service validation rejects empty title."""
        from lifeos.domains.calendar.services.calendar_service import (
            create_calendar_event,
        )

        with app.app_context():
            with pytest.raises(ValueError, match="invalid_title"):
                create_calendar_event(
                    user_id=test_user.id,
                    title="",
                    start_time=datetime.now(),
                )

    def test_service_validation_title_too_long(self, app, test_user):
        """Test service validation rejects overly long title."""
        from lifeos.domains.calendar.services.calendar_service import (
            create_calendar_event,
        )

        with app.app_context():
            long_title = "A" * 300  # Exceeds 255 char limit
            with pytest.raises(ValueError, match="title_too_long"):
                create_calendar_event(
                    user_id=test_user.id,
                    title=long_title,
                    start_time=datetime.now(),
                )

    def test_update_nonexistent_event(self, app, test_user):
        """Test updating a non-existent event raises error."""
        from lifeos.domains.calendar.services.calendar_service import (
            update_calendar_event,
        )

        with app.app_context():
            with pytest.raises(ValueError, match="not_found"):
                update_calendar_event(
                    user_id=test_user.id,
                    event_id=99999,
                    title="New Title",
                )

    def test_delete_nonexistent_event(self, app, test_user):
        """Test deleting a non-existent event raises error."""
        from lifeos.domains.calendar.services.calendar_service import (
            delete_calendar_event,
        )

        with app.app_context():
            with pytest.raises(ValueError, match="not_found"):
                delete_calendar_event(
                    user_id=test_user.id,
                    event_id=99999,
                )


# ==================== Integration Tests: Interpretation Workflow ====================


class TestInterpretationWorkflow:
    """Integration tests for the interpretation review workflow."""

    def test_get_pending_interpretations(
        self, app, event_with_interpretation, test_user
    ):
        """Test retrieving pending interpretations."""
        from lifeos.domains.calendar.services.calendar_service import (
            get_pending_interpretations,
        )

        with app.app_context():
            pending = get_pending_interpretations(user_id=test_user.id)
            assert len(pending) == 1
            assert pending[0].status == STATUS_INFERRED

    def test_confirm_interpretation(self, app, event_with_interpretation, test_user):
        """Test confirming an interpretation updates status and sets record_id."""
        from lifeos.domains.calendar.services.calendar_service import (
            update_interpretation_status,
        )

        event, interpretation = event_with_interpretation

        with app.app_context():
            updated = update_interpretation_status(
                user_id=test_user.id,
                interpretation_id=interpretation.id,
                status=STATUS_CONFIRMED,
                record_id=456,
            )

            assert updated.status == STATUS_CONFIRMED
            assert updated.record_id == 456

    def test_reject_interpretation(self, app, event_with_interpretation, test_user):
        """Test rejecting an interpretation updates status."""
        from lifeos.domains.calendar.services.calendar_service import (
            update_interpretation_status,
        )

        event, interpretation = event_with_interpretation

        with app.app_context():
            updated = update_interpretation_status(
                user_id=test_user.id,
                interpretation_id=interpretation.id,
                status=STATUS_REJECTED,
            )

            assert updated.status == STATUS_REJECTED
            assert updated.record_id is None

    def test_ignore_interpretation(self, app, event_with_interpretation, test_user):
        """Test ignoring an interpretation."""
        from lifeos.domains.calendar.services.calendar_service import (
            update_interpretation_status,
        )

        event, interpretation = event_with_interpretation

        with app.app_context():
            updated = update_interpretation_status(
                user_id=test_user.id,
                interpretation_id=interpretation.id,
                status=STATUS_IGNORED,
            )

            assert updated.status == STATUS_IGNORED

    def test_invalid_interpretation_status(
        self, app, event_with_interpretation, test_user
    ):
        """Test that invalid status values are rejected."""
        from lifeos.domains.calendar.services.calendar_service import (
            update_interpretation_status,
        )

        event, interpretation = event_with_interpretation

        with app.app_context():
            with pytest.raises(ValueError, match="invalid_status"):
                update_interpretation_status(
                    user_id=test_user.id,
                    interpretation_id=interpretation.id,
                    status="invalid_status",
                )

    def test_update_nonexistent_interpretation(self, app, test_user):
        """Test updating non-existent interpretation raises error."""
        from lifeos.domains.calendar.services.calendar_service import (
            update_interpretation_status,
        )

        with app.app_context():
            with pytest.raises(ValueError, match="not_found"):
                update_interpretation_status(
                    user_id=test_user.id,
                    interpretation_id=99999,
                    status=STATUS_CONFIRMED,
                )


# ==================== Mock Tests: Outbox Integration ====================


class TestCalendarEventOutboxMocks:
    """Tests with mocked outbox to verify event emission."""

    def test_create_event_emits_outbox_message(self, app, test_user):
        """Test that creating an event enqueues an outbox message."""
        from lifeos.domains.calendar.services.calendar_service import (
            create_calendar_event,
        )
        from lifeos.domains.calendar.events import CALENDAR_EVENT_CREATED

        with app.app_context():
            with patch(
                "lifeos.domains.calendar.services.calendar_service.enqueue_outbox"
            ) as mock_enqueue:
                event = create_calendar_event(
                    user_id=test_user.id,
                    title="Outbox Test Event",
                    start_time=datetime.now(),
                )

                mock_enqueue.assert_called_once()
                call_args = mock_enqueue.call_args
                assert call_args[0][0] == CALENDAR_EVENT_CREATED
                assert call_args[0][1]["event_id"] == event.id
                assert call_args[0][1]["title"] == "Outbox Test Event"

    def test_update_event_emits_outbox_message(self, app, sample_calendar_event):
        """Test that updating an event enqueues an outbox message."""
        from lifeos.domains.calendar.services.calendar_service import (
            update_calendar_event,
        )
        from lifeos.domains.calendar.events import CALENDAR_EVENT_UPDATED

        with app.app_context():
            with patch(
                "lifeos.domains.calendar.services.calendar_service.enqueue_outbox"
            ) as mock_enqueue:
                update_calendar_event(
                    user_id=sample_calendar_event.user_id,
                    event_id=sample_calendar_event.id,
                    title="Updated for Outbox Test",
                )

                mock_enqueue.assert_called_once()
                call_args = mock_enqueue.call_args
                assert call_args[0][0] == CALENDAR_EVENT_UPDATED
                assert "title" in call_args[0][1]["changed_fields"]

    def test_delete_event_emits_outbox_message(self, app, sample_calendar_event):
        """Test that deleting an event enqueues an outbox message."""
        from lifeos.domains.calendar.services.calendar_service import (
            delete_calendar_event,
        )
        from lifeos.domains.calendar.events import CALENDAR_EVENT_DELETED

        with app.app_context():
            event_id = sample_calendar_event.id
            with patch(
                "lifeos.domains.calendar.services.calendar_service.enqueue_outbox"
            ) as mock_enqueue:
                delete_calendar_event(
                    user_id=sample_calendar_event.user_id,
                    event_id=event_id,
                )

                mock_enqueue.assert_called_once()
                call_args = mock_enqueue.call_args
                assert call_args[0][0] == CALENDAR_EVENT_DELETED
                assert call_args[0][1]["event_id"] == event_id

    def test_confirm_interpretation_emits_event(
        self, app, event_with_interpretation, test_user
    ):
        """Test that confirming interpretation emits confirmation event."""
        from lifeos.domains.calendar.services.calendar_service import (
            update_interpretation_status,
        )
        from lifeos.domains.calendar.events import CALENDAR_INTERPRETATION_CONFIRMED

        event, interpretation = event_with_interpretation

        with app.app_context():
            with patch(
                "lifeos.domains.calendar.services.calendar_service.enqueue_outbox"
            ) as mock_enqueue:
                update_interpretation_status(
                    user_id=test_user.id,
                    interpretation_id=interpretation.id,
                    status=STATUS_CONFIRMED,
                    record_id=789,
                )

                mock_enqueue.assert_called_once()
                call_args = mock_enqueue.call_args
                assert call_args[0][0] == CALENDAR_INTERPRETATION_CONFIRMED
                assert call_args[0][1]["interpretation_id"] == interpretation.id
                assert call_args[0][1]["record_id"] == 789

    def test_reject_interpretation_emits_event(
        self, app, event_with_interpretation, test_user
    ):
        """Test that rejecting interpretation emits rejection event."""
        from lifeos.domains.calendar.services.calendar_service import (
            update_interpretation_status,
        )
        from lifeos.domains.calendar.events import CALENDAR_INTERPRETATION_REJECTED

        event, interpretation = event_with_interpretation

        with app.app_context():
            with patch(
                "lifeos.domains.calendar.services.calendar_service.enqueue_outbox"
            ) as mock_enqueue:
                update_interpretation_status(
                    user_id=test_user.id,
                    interpretation_id=interpretation.id,
                    status=STATUS_REJECTED,
                )

                mock_enqueue.assert_called_once()
                call_args = mock_enqueue.call_args
                assert call_args[0][0] == CALENDAR_INTERPRETATION_REJECTED

    def test_ignored_interpretation_no_event(
        self, app, event_with_interpretation, test_user
    ):
        """Test that ignoring interpretation does not emit an event."""
        from lifeos.domains.calendar.services.calendar_service import (
            update_interpretation_status,
        )

        event, interpretation = event_with_interpretation

        with app.app_context():
            with patch(
                "lifeos.domains.calendar.services.calendar_service.enqueue_outbox"
            ) as mock_enqueue:
                update_interpretation_status(
                    user_id=test_user.id,
                    interpretation_id=interpretation.id,
                    status=STATUS_IGNORED,
                )

                # Ignore status should not emit an event
                mock_enqueue.assert_not_called()


# ==================== Edge Case Tests ====================


class TestCalendarEventEdgeCases:
    """Edge case and boundary tests for calendar events."""

    def test_event_with_maximum_length_fields(self, app, test_user):
        """Test event creation with maximum allowed field lengths."""
        with app.app_context():
            event = CalendarEvent(
                user_id=test_user.id,
                title="A" * 255,  # Max title length
                description="B" * 10000,  # Long description
                location="C" * 512,  # Max location length
                color="#" + "F" * 15,  # Max color length
                start_time=datetime.now(),
            )
            db.session.add(event)
            db.session.commit()

            assert len(event.title) == 255
            assert len(event.location) == 512

    def test_event_with_unicode_characters(self, app, test_user):
        """Test event with Unicode characters in all text fields."""
        with app.app_context():
            event = CalendarEvent(
                user_id=test_user.id,
                title="Meeting with 田中さん 🗓️",
                description="Discuss プロジェクト details 📋",
                location="東京オフィス 🏢",
                start_time=datetime.now(),
                tags=["日本語", "meeting", "重要"],
            )
            db.session.add(event)
            db.session.commit()

            loaded = CalendarEvent.query.get(event.id)
            assert "田中" in loaded.title
            assert "🗓️" in loaded.title
            assert "日本語" in loaded.tags

    def test_event_spanning_multiple_days(self, app, test_user):
        """Test event that spans multiple days."""
        with app.app_context():
            event = CalendarEvent(
                user_id=test_user.id,
                title="Multi-day Conference",
                start_time=datetime(2025, 12, 7, 9, 0, 0),
                end_time=datetime(2025, 12, 10, 18, 0, 0),
                all_day=False,
            )
            db.session.add(event)
            db.session.commit()

            # Duration: Dec 7 9:00 to Dec 10 18:00 = 3 days + 9 hours = 81 hours = 4860 minutes
            assert event.duration_minutes == 4860

    def test_event_with_empty_tags_and_metadata(self, app, test_user):
        """Test event with explicitly empty tags and metadata."""
        with app.app_context():
            event = CalendarEvent(
                user_id=test_user.id,
                title="Empty Collections Event",
                start_time=datetime.now(),
                tags=[],
                metadata_={},
            )
            db.session.add(event)
            db.session.commit()

            loaded = CalendarEvent.query.get(event.id)
            assert loaded.tags == []
            assert loaded.metadata_ == {}

    def test_interpretation_with_zero_confidence(self, app, sample_calendar_event):
        """Test interpretation can have zero confidence score."""
        with app.app_context():
            interpretation = CalendarEventInterpretation(
                calendar_event_id=sample_calendar_event.id,
                user_id=sample_calendar_event.user_id,
                domain=DOMAIN_HEALTH,
                record_type=RECORD_TYPE_WORKOUT,
                confidence_score=0.0,
                status=STATUS_INFERRED,
            )
            db.session.add(interpretation)
            db.session.commit()

            loaded = CalendarEventInterpretation.query.get(interpretation.id)
            assert float(loaded.confidence_score) == 0.0

    def test_interpretation_with_max_confidence(self, app, sample_calendar_event):
        """Test interpretation with maximum confidence score."""
        with app.app_context():
            interpretation = CalendarEventInterpretation(
                calendar_event_id=sample_calendar_event.id,
                user_id=sample_calendar_event.user_id,
                domain=DOMAIN_HEALTH,
                record_type=RECORD_TYPE_WORKOUT,
                confidence_score=1.0,
                status=STATUS_INFERRED,
            )
            db.session.add(interpretation)
            db.session.commit()

            loaded = CalendarEventInterpretation.query.get(interpretation.id)
            assert float(loaded.confidence_score) == 1.0

    def test_multiple_interpretations_for_single_event(
        self, app, sample_calendar_event
    ):
        """Test that an event can have multiple interpretations."""
        with app.app_context():
            interpretation1 = CalendarEventInterpretation(
                calendar_event_id=sample_calendar_event.id,
                user_id=sample_calendar_event.user_id,
                domain=DOMAIN_PROJECTS,
                record_type=RECORD_TYPE_WORK_SESSION,
                confidence_score=0.75,
                status=STATUS_INFERRED,
            )
            interpretation2 = CalendarEventInterpretation(
                calendar_event_id=sample_calendar_event.id,
                user_id=sample_calendar_event.user_id,
                domain=DOMAIN_RELATIONSHIPS,
                record_type=RECORD_TYPE_INTERACTION,
                confidence_score=0.65,
                status=STATUS_INFERRED,
            )
            db.session.add_all([interpretation1, interpretation2])
            db.session.commit()

            loaded_event = CalendarEvent.query.get(sample_calendar_event.id)
            assert len(loaded_event.interpretations) == 2

            domains = {i.domain for i in loaded_event.interpretations}
            assert DOMAIN_PROJECTS in domains
            assert DOMAIN_RELATIONSHIPS in domains


# ==================== Concurrency & Isolation Tests ====================


class TestCalendarEventIsolation:
    """Tests for user isolation and concurrent access patterns."""

    def test_user_cannot_access_other_user_events(self, app, test_user, second_user):
        """Test that users can only access their own events."""
        with app.app_context():
            # Create event for test_user
            event = CalendarEvent(
                user_id=test_user.id,
                title="Private Event",
                start_time=datetime.now(),
            )
            db.session.add(event)
            db.session.commit()

            # Query as second_user should return nothing
            events = CalendarEvent.query.filter_by(user_id=second_user.id).all()

            assert len(events) == 0
            assert not any(e.id == event.id for e in events)

    def test_user_cannot_access_other_user_interpretations(
        self, app, test_user, second_user
    ):
        """Test interpretation isolation between users."""
        with app.app_context():
            event = CalendarEvent(
                user_id=test_user.id,
                title="Test Event",
                start_time=datetime.now(),
            )
            db.session.add(event)
            db.session.flush()

            interpretation = CalendarEventInterpretation(
                calendar_event_id=event.id,
                user_id=test_user.id,
                domain=DOMAIN_HEALTH,
                record_type=RECORD_TYPE_WORKOUT,
                confidence_score=0.8,
                status=STATUS_INFERRED,
            )
            db.session.add(interpretation)
            db.session.commit()

            # Query as second_user should return nothing
            interpretations = CalendarEventInterpretation.query.filter_by(
                user_id=second_user.id
            ).all()

            assert len(interpretations) == 0

    def test_service_enforces_user_ownership(self, app, test_user, second_user):
        """Test service layer enforces user ownership for updates."""
        from lifeos.domains.calendar.services.calendar_service import (
            update_calendar_event,
        )

        with app.app_context():
            # Create event for test_user
            event = CalendarEvent(
                user_id=test_user.id,
                title="Owned Event",
                start_time=datetime.now(),
            )
            db.session.add(event)
            db.session.commit()

            # Attempt to update as second_user should fail
            with pytest.raises(ValueError, match="not_found"):
                update_calendar_event(
                    user_id=second_user.id,  # Wrong user!
                    event_id=event.id,
                    title="Hacked Title",
                )


# ==================== Schema Validation Tests ====================


class TestCalendarSchemaValidation:
    """Tests for Pydantic schema validation."""

    def test_create_schema_valid_input(self):
        """Test CalendarEventCreate schema accepts valid input."""
        from lifeos.domains.calendar.schemas import CalendarEventCreate

        data = CalendarEventCreate(
            title="Valid Event",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            description="A valid description",
            location="Test Location",
            all_day=False,
            tags=["test"],
        )

        assert data.title == "Valid Event"
        assert data.all_day is False
        assert data.tags == ["test"]

    def test_create_schema_rejects_empty_title(self):
        """Test CalendarEventCreate schema rejects empty title."""
        from pydantic import ValidationError
        from lifeos.domains.calendar.schemas import CalendarEventCreate

        with pytest.raises(ValidationError):
            CalendarEventCreate(
                title="",
                start_time=datetime.now(),
            )

    def test_create_schema_rejects_long_title(self):
        """Test CalendarEventCreate schema rejects title > 255 chars."""
        from pydantic import ValidationError
        from lifeos.domains.calendar.schemas import CalendarEventCreate

        with pytest.raises(ValidationError):
            CalendarEventCreate(
                title="A" * 256,
                start_time=datetime.now(),
            )

    def test_interpretation_update_schema_valid_statuses(self):
        """Test InterpretationUpdate schema accepts valid statuses."""
        from lifeos.domains.calendar.schemas import InterpretationUpdate

        for status in ["confirmed", "rejected", "ignored"]:
            data = InterpretationUpdate(status=status)
            assert data.status == status

    def test_interpretation_update_schema_rejects_invalid_status(self):
        """Test InterpretationUpdate schema rejects invalid status."""
        from pydantic import ValidationError
        from lifeos.domains.calendar.schemas import InterpretationUpdate

        with pytest.raises(ValidationError):
            InterpretationUpdate(status="invalid")

    def test_list_params_schema_defaults(self):
        """Test CalendarEventListParams schema default values."""
        from lifeos.domains.calendar.schemas import CalendarEventListParams

        data = CalendarEventListParams()

        assert data.limit == 50
        assert data.offset == 0
        assert data.start_date is None
        assert data.end_date is None
        assert data.source is None

    def test_list_params_schema_bounds(self):
        """Test CalendarEventListParams schema bounds validation."""
        from pydantic import ValidationError
        from lifeos.domains.calendar.schemas import CalendarEventListParams

        # Valid max limit
        data = CalendarEventListParams(limit=500)
        assert data.limit == 500

        # Exceeds max limit
        with pytest.raises(ValidationError):
            CalendarEventListParams(limit=501)

        # Below min limit
        with pytest.raises(ValidationError):
            CalendarEventListParams(limit=0)

        # Negative offset
        with pytest.raises(ValidationError):
            CalendarEventListParams(offset=-1)


# ==================== API Edge Case Tests (Invalid IDs) ====================


class TestCalendarAPIInvalidIds:
    """
    Tests for API endpoints with invalid event IDs.

    These tests document the expected behavior when the frontend passes
    invalid IDs like 'null', empty strings, or non-numeric values.

    Bug context: Frontend was observed calling GET /api/calendar/events/null
    when editing an event, indicating the event ID was not properly captured.
    """

    def test_get_event_with_null_string_returns_404(self, client, auth_headers):
        """
        Test GET /api/calendar/events/null returns 404.

        This reproduces the bug where frontend passes 'null' as event_id.
        The API should gracefully handle this with a 404 response.
        """
        response = client.get(
            "/api/calendar/events/null",
            headers=auth_headers,
        )

        # Flask's int converter will reject 'null' and return 404
        assert response.status_code == 404

    def test_get_event_with_undefined_string_returns_404(self, client, auth_headers):
        """Test GET /api/calendar/events/undefined returns 404."""
        response = client.get(
            "/api/calendar/events/undefined",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_get_event_with_empty_string_returns_404(self, client, auth_headers):
        """Test GET /api/calendar/events/ (empty) returns 404 or method not allowed."""
        response = client.get(
            "/api/calendar/events/",
            headers=auth_headers,
        )

        # Empty string in URL typically routes to list endpoint or 404
        # Either 200 (list) or 404 is acceptable, but not 500
        assert response.status_code in (200, 404, 405)

    def test_update_event_with_null_string_returns_404(self, client, auth_headers):
        """
        Test PATCH /api/calendar/events/null returns 404.

        This ensures update endpoint also handles invalid IDs gracefully.
        """
        response = client.patch(
            "/api/calendar/events/null",
            json={"title": "Updated Title"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_delete_event_with_null_string_returns_404(self, client, auth_headers):
        """Test DELETE /api/calendar/events/null returns 404."""
        response = client.delete(
            "/api/calendar/events/null",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_get_event_with_negative_id_returns_404(self, client, auth_headers):
        """Test GET /api/calendar/events/-1 returns 404."""
        response = client.get(
            "/api/calendar/events/-1",
            headers=auth_headers,
        )

        # Negative IDs should return 404 (not found) rather than error
        assert response.status_code == 404

    def test_get_event_with_zero_id_returns_404(self, client, auth_headers):
        """Test GET /api/calendar/events/0 returns 404."""
        response = client.get(
            "/api/calendar/events/0",
            headers=auth_headers,
        )

        # ID 0 is invalid (auto-increment starts at 1)
        assert response.status_code == 404

    def test_get_event_with_very_large_id_returns_404(self, client, auth_headers):
        """Test GET /api/calendar/events/<large_id> returns 404."""
        response = client.get(
            "/api/calendar/events/999999999",
            headers=auth_headers,
        )

        assert response.status_code == 404
        data = response.get_json()
        assert data["ok"] is False
        assert data["error"] == "not_found"

    def test_update_interpretation_with_null_id_returns_404(self, client, auth_headers):
        """Test PATCH /api/calendar/interpretations/null returns 404."""
        response = client.patch(
            "/api/calendar/interpretations/null",
            json={"status": "confirmed"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_get_event_after_creation_returns_valid_id(self, client, auth_headers, app):
        """
        Test that event creation returns a valid numeric ID that can be used for GET.

        This tests the happy path to ensure the API returns usable event IDs.
        """
        # Create an event
        create_response = client.post(
            "/api/calendar/events",
            json={
                "title": "Test Event for ID Verification",
                "start_time": datetime.now().isoformat(),
            },
            headers=auth_headers,
        )

        assert create_response.status_code == 201
        create_data = create_response.get_json()
        assert create_data["ok"] is True

        event_id = create_data["event"]["id"]

        # Verify ID is a valid integer
        assert event_id is not None
        assert isinstance(event_id, int)
        assert event_id > 0

        # Verify we can fetch the event with this ID
        get_response = client.get(
            f"/api/calendar/events/{event_id}",
            headers=auth_headers,
        )

        assert get_response.status_code == 200
        get_data = get_response.get_json()
        assert get_data["ok"] is True
        assert get_data["event"]["id"] == event_id
        assert get_data["event"]["title"] == "Test Event for ID Verification"

    def test_update_event_returns_valid_id(self, client, auth_headers, app):
        """
        Test that event update response includes the same valid ID.

        Ensures ID consistency across create and update operations.
        """
        # Create an event
        create_response = client.post(
            "/api/calendar/events",
            json={
                "title": "Original Title",
                "start_time": datetime.now().isoformat(),
            },
            headers=auth_headers,
        )

        assert create_response.status_code == 201
        event_id = create_response.get_json()["event"]["id"]

        # Update the event
        update_response = client.patch(
            f"/api/calendar/events/{event_id}",
            json={"title": "Updated Title"},
            headers=auth_headers,
        )

        assert update_response.status_code == 200
        update_data = update_response.get_json()
        assert update_data["ok"] is True
        assert update_data["event"]["id"] == event_id  # Same ID preserved

    def test_list_events_returns_valid_ids(self, client, auth_headers, app, test_user):
        """
        Test that listing events returns valid numeric IDs for all events.

        Frontend should use these IDs for edit/delete operations.
        """
        # Create multiple events
        for i in range(3):
            client.post(
                "/api/calendar/events",
                json={
                    "title": f"List Test Event {i}",
                    "start_time": (datetime.now() + timedelta(hours=i)).isoformat(),
                },
                headers=auth_headers,
            )

        # List events
        list_response = client.get(
            "/api/calendar/events",
            headers=auth_headers,
        )

        assert list_response.status_code == 200
        list_data = list_response.get_json()
        assert list_data["ok"] is True

        # Verify all events have valid IDs
        for event in list_data["events"]:
            assert "id" in event
            assert event["id"] is not None
            assert isinstance(event["id"], int)
            assert event["id"] > 0

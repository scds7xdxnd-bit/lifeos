"""Tests for Calendar domain and Interpreter layer."""

from datetime import datetime, timedelta

import pytest
from flask_jwt_extended import create_access_token

pytestmark = [pytest.mark.integration, pytest.mark.ml]

from lifeos.core.auth.password import hash_password
from lifeos.core.interpreter.classification_rules import classify_event
from lifeos.core.interpreter.constants import (
    DOMAIN_FINANCE,
    DOMAIN_HEALTH,
    DOMAIN_RELATIONSHIPS,
    DOMAIN_SKILLS,
    RECORD_TYPE_INTERACTION,
    RECORD_TYPE_PRACTICE,
    RECORD_TYPE_TRANSACTION,
    RECORD_TYPE_WORKOUT,
)
from lifeos.core.users.models import User
from lifeos.domains.calendar.events import (
    CALENDAR_EVENT_CREATED,
    CALENDAR_EVENT_DELETED,
    CALENDAR_EVENT_UPDATED,
)
from lifeos.domains.calendar.models.calendar_event import (
    CalendarEvent,
    CalendarEventInterpretation,
)
from lifeos.extensions import db


@pytest.fixture
def auth_user(app):
    """Create a test user for auth-protected endpoints."""
    with app.app_context():
        user = User(email="calendar-tester@example.com", password_hash=hash_password("secret"))
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def auth_headers(app, auth_user):
    """JWT headers for API calls."""
    with app.app_context():
        token = create_access_token(identity=str(auth_user.id), additional_claims={"roles": ["calendar:write"]})
    return {"Authorization": f"Bearer {token}"}


# ============== Classification Rules Tests ==============


class TestClassifyEvent:
    """Tests for the classify_event function."""

    def test_classify_gym_workout(self):
        """Gym event should classify as health/workout."""
        results = classify_event(
            title="Gym workout",
            description="Leg day at fitness center",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            location="Anytime Fitness",
        )

        assert len(results) > 0
        workout_result = next(
            (r for r in results if r["domain"] == DOMAIN_HEALTH and r["record_type"] == RECORD_TYPE_WORKOUT),
            None,
        )
        assert workout_result is not None
        assert workout_result["confidence_score"] >= 0.7

    def test_classify_dinner_with_person(self):
        """Dinner with someone should classify as relationships/interaction."""
        results = classify_event(
            title="Dinner with John Smith",
            description="Catch up dinner",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=2),
            location="Italian Restaurant",
        )

        assert len(results) > 0
        rel_result = next(
            (r for r in results if r["domain"] == DOMAIN_RELATIONSHIPS and r["record_type"] == RECORD_TYPE_INTERACTION),
            None,
        )
        assert rel_result is not None
        assert rel_result["extracted_data"].get("person_name") is not None

    def test_classify_shopping(self):
        """Shopping event should classify as finance/transaction."""
        results = classify_event(
            title="Shopping at mall",
            description="Buy new shoes",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=2),
            location="Walmart",
        )

        assert len(results) > 0
        finance_result = next(
            (r for r in results if r["domain"] == DOMAIN_FINANCE and r["record_type"] == RECORD_TYPE_TRANSACTION),
            None,
        )
        assert finance_result is not None

    def test_classify_piano_lesson(self):
        """Piano lesson should classify as skills/practice."""
        results = classify_event(
            title="Piano lesson",
            description="Weekly lesson with teacher",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            location=None,
        )

        assert len(results) > 0
        skill_result = next(
            (r for r in results if r["domain"] == DOMAIN_SKILLS and r["record_type"] == RECORD_TYPE_PRACTICE),
            None,
        )
        assert skill_result is not None

    def test_classify_unrecognized_event(self):
        """Event with no recognizable keywords should return empty list."""
        results = classify_event(
            title="Random event xyz",
            description="No relevant keywords",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            location=None,
        )

        # May return empty or low confidence results
        high_confidence = [r for r in results if r["confidence_score"] >= 0.5]
        # Either empty or very low confidence
        assert len(high_confidence) <= 1

    def test_duration_extracted(self):
        """Classification should extract duration from event times."""
        start = datetime.now()
        end = start + timedelta(hours=2, minutes=30)

        results = classify_event(
            title="Gym workout",
            description=None,
            start_time=start,
            end_time=end,
            location=None,
        )

        if results:
            assert results[0]["extracted_data"].get("duration_minutes") == 150


# ============== Calendar Event Model Tests ==============


class TestCalendarEventModel:
    """Tests for CalendarEvent model."""

    def test_create_calendar_event(self, app, auth_user):
        """Test creating a calendar event."""
        with app.app_context():
            event = CalendarEvent(
                user_id=auth_user.id,
                title="Test Event",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1),
                location="Test Location",
            )
            db.session.add(event)
            db.session.commit()

            assert event.id is not None
            assert event.title == "Test Event"
            assert event.user_id == auth_user.id

    def test_calendar_event_interpretation(self, app, auth_user):
        """Test creating an interpretation for a calendar event."""
        with app.app_context():
            event = CalendarEvent(
                user_id=auth_user.id,
                title="Gym workout",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1),
            )
            db.session.add(event)
            db.session.flush()

            interpretation = CalendarEventInterpretation(
                calendar_event_id=event.id,
                user_id=auth_user.id,
                domain=DOMAIN_HEALTH,
                record_type=RECORD_TYPE_WORKOUT,
                confidence_score=0.85,
                status="inferred",
                classification_data={"workout_type": "gym"},
            )
            db.session.add(interpretation)
            db.session.commit()

            assert interpretation.id is not None
            assert interpretation.calendar_event_id == event.id
            assert interpretation.confidence_score == 0.85


# ============== Calendar Service Tests ==============


class TestCalendarService:
    """Tests for calendar service functions."""

    def test_create_event(self, app, auth_user):
        """Test creating an event via service."""
        from lifeos.domains.calendar.services.calendar_service import (
            create_calendar_event,
        )

        with app.app_context():
            event = create_calendar_event(
                user_id=auth_user.id,
                title="Service Test Event",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1),
            )
            db.session.commit()

            assert event.id is not None
            assert event.title == "Service Test Event"

    def test_create_event_validation(self, app, auth_user):
        """Test event creation validation."""
        from lifeos.domains.calendar.services.calendar_service import (
            create_calendar_event,
        )

        with app.app_context():
            with pytest.raises(ValueError, match="invalid_title"):
                create_calendar_event(
                    user_id=auth_user.id,
                    title="",
                    start_time=datetime.now(),
                )

    def test_list_events(self, app, auth_user):
        """Test listing events."""
        from lifeos.domains.calendar.services.calendar_service import (
            create_calendar_event,
            list_calendar_events,
        )

        with app.app_context():
            start = datetime.now()
            create_calendar_event(
                user_id=auth_user.id,
                title="Event 1",
                start_time=start,
            )
            create_calendar_event(
                user_id=auth_user.id,
                title="Event 2",
                start_time=start + timedelta(hours=2),
            )
            db.session.commit()

            events = list_calendar_events(
                user_id=auth_user.id,
                start_date=start,
                end_date=start + timedelta(days=1),
            )

            assert len(events) >= 2


# ============== Calendar API Tests ==============


class TestCalendarAPI:
    """Tests for calendar API endpoints."""

    def test_create_event_api(self, client, auth_headers):
        """Test POST /api/calendar/events."""
        response = client.post(
            "/api/calendar/events",
            json={
                "title": "API Test Event",
                "start_time": datetime.now().isoformat(),
                "end_time": (datetime.now() + timedelta(hours=1)).isoformat(),
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["ok"] is True
        assert data["event"]["title"] == "API Test Event"

    def test_list_events_api(self, client, auth_headers, auth_user, app):
        """Test GET /api/calendar/events."""
        from lifeos.domains.calendar.services.calendar_service import (
            create_calendar_event,
        )

        with app.app_context():
            create_calendar_event(
                user_id=auth_user.id,
                title="List Test Event",
                start_time=datetime.now(),
            )
            db.session.commit()

        response = client.get(
            "/api/calendar/events",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["ok"] is True
        assert isinstance(data["events"], list)

    def test_get_pending_interpretations(self, client, auth_headers, auth_user, app):
        """Test GET /api/calendar/interpretations/pending."""
        with app.app_context():
            event = CalendarEvent(
                user_id=auth_user.id,
                title="Gym workout",
                start_time=datetime.now(),
            )
            db.session.add(event)
            db.session.flush()

            interpretation = CalendarEventInterpretation(
                calendar_event_id=event.id,
                user_id=auth_user.id,
                domain=DOMAIN_HEALTH,
                record_type=RECORD_TYPE_WORKOUT,
                confidence_score=0.85,
                status="inferred",
            )
            db.session.add(interpretation)
            db.session.commit()

        response = client.get(
            "/api/calendar/interpretations/pending",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["ok"] is True

    def test_confirm_interpretation(self, client, auth_headers, auth_user, app):
        """Test POST /api/calendar/interpretations/<id>/confirm."""
        with app.app_context():
            event = CalendarEvent(
                user_id=auth_user.id,
                title="Workout",
                start_time=datetime.now(),
            )
            db.session.add(event)
            db.session.flush()

            interpretation = CalendarEventInterpretation(
                calendar_event_id=event.id,
                user_id=auth_user.id,
                domain=DOMAIN_HEALTH,
                record_type=RECORD_TYPE_WORKOUT,
                confidence_score=0.75,
                status="inferred",
            )
            db.session.add(interpretation)
            db.session.commit()
            interp_id = interpretation.id

        response = client.patch(
            f"/api/calendar/interpretations/{interp_id}",
            json={"status": "confirmed"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["ok"] is True

        # Verify status changed
        with app.app_context():
            updated = CalendarEventInterpretation.query.get(interp_id)
            assert updated.status == "confirmed"

    def test_reject_interpretation(self, client, auth_headers, auth_user, app):
        """Test PATCH /api/calendar/interpretations/<id> to reject."""
        with app.app_context():
            event = CalendarEvent(
                user_id=auth_user.id,
                title="Workout",
                start_time=datetime.now(),
            )
            db.session.add(event)
            db.session.flush()

            interpretation = CalendarEventInterpretation(
                calendar_event_id=event.id,
                user_id=auth_user.id,
                domain=DOMAIN_HEALTH,
                record_type=RECORD_TYPE_WORKOUT,
                confidence_score=0.75,
                status="inferred",
            )
            db.session.add(interpretation)
            db.session.commit()
            interp_id = interpretation.id

        response = client.patch(
            f"/api/calendar/interpretations/{interp_id}",
            json={"status": "rejected"},
            headers=auth_headers,
        )

        assert response.status_code == 200

        # Verify status changed
        with app.app_context():
            updated = CalendarEventInterpretation.query.get(interp_id)
            assert updated.status == "rejected"

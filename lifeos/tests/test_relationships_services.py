"""Tests for Relationships domain services: people and interactions."""

from datetime import date, datetime, timedelta
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.integration

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.domains.relationships.models.interaction_models import Interaction
from lifeos.domains.relationships.models.person_models import Person
from lifeos.domains.relationships.services import (
    compute_reconnect_candidates,
    create_person,
    delete_interaction,
    delete_person,
    edit_interaction,
    get_person,
    list_interactions,
    list_people,
    log_interaction,
    update_person,
)
from lifeos.extensions import db


@pytest.fixture
def test_user(app):
    """Create a test user for relationships tests."""
    with app.app_context():
        user = User(email="relationships-tester@example.com", password_hash=hash_password("secret"))
        db.session.add(user)
        db.session.commit()
        yield user


# ============== Person CRUD Tests ==============


class TestPersonService:
    """Tests for person creation, update, and deletion."""

    def test_create_person_success(self, app, test_user):
        """Create a valid person."""
        with app.app_context():
            person = create_person(
                test_user.id,
                name="John Smith",
                relationship_type="friend",
                importance_level=3,
                tags=["work", "mentor"],
                notes="Met at conference",
                birthday=date(1990, 5, 15),
                first_met_date=date(2020, 1, 1),
            )

            assert person.id is not None
            assert person.user_id == test_user.id
            assert person.name == "John Smith"
            assert person.relationship_type == "friend"
            assert person.importance_level == 3
            assert person.tags == ["work", "mentor"]
            assert person.notes == "Met at conference"
            assert person.birthday == date(1990, 5, 15)
            assert person.first_met_date == date(2020, 1, 1)

    def test_create_person_minimal(self, app, test_user):
        """Create person with minimal fields."""
        with app.app_context():
            person = create_person(test_user.id, name="Jane Doe")

            assert person.id is not None
            assert person.name == "Jane Doe"
            assert person.relationship_type is None
            assert person.importance_level is None
            assert person.tags == []

    def test_create_person_empty_name_fails(self, app, test_user):
        """Creating person with empty name fails."""
        with app.app_context():
            with pytest.raises(ValueError, match="validation_error"):
                create_person(test_user.id, name="")

    def test_create_person_whitespace_name_fails(self, app, test_user):
        """Creating person with whitespace-only name fails."""
        with app.app_context():
            with pytest.raises(ValueError, match="validation_error"):
                create_person(test_user.id, name="   ")

    def test_create_person_duplicate_name_fails(self, app, test_user):
        """Creating person with duplicate name fails."""
        with app.app_context():
            create_person(test_user.id, name="Unique Person")

            with pytest.raises(ValueError, match="duplicate"):
                create_person(test_user.id, name="Unique Person")

    def test_update_person_success(self, app, test_user):
        """Update an existing person."""
        with app.app_context():
            person = create_person(test_user.id, name="Update Person")

            updated = update_person(
                test_user.id,
                person.id,
                relationship_type="family",
                importance_level=5,
                notes="Updated notes",
            )

            assert updated is not None
            assert updated.relationship_type == "family"
            assert updated.importance_level == 5
            assert updated.notes == "Updated notes"

    def test_update_person_not_found(self, app, test_user):
        """Update non-existent person returns None."""
        with app.app_context():
            result = update_person(test_user.id, 99999, name="New Name")
            assert result is None

    def test_update_person_tags(self, app, test_user):
        """Update person's tags."""
        with app.app_context():
            person = create_person(test_user.id, name="Tag Person", tags=["friend"])

            updated = update_person(test_user.id, person.id, tags=["friend", "colleague"])

            assert updated.tags == ["friend", "colleague"]

    def test_delete_person_success(self, app, test_user):
        """Delete an existing person."""
        with app.app_context():
            person = create_person(test_user.id, name="To Delete")
            person_id = person.id

            deleted = delete_person(test_user.id, person_id)
            assert deleted is True

            # Verify it's gone
            assert Person.query.get(person_id) is None

    def test_delete_person_not_found(self, app, test_user):
        """Delete non-existent person returns False."""
        with app.app_context():
            deleted = delete_person(test_user.id, 99999)
            assert deleted is False

    def test_get_person(self, app, test_user):
        """Get a specific person."""
        with app.app_context():
            person = create_person(test_user.id, name="Get Person")

            fetched = get_person(test_user.id, person.id)

            assert fetched is not None
            assert fetched.name == "Get Person"

    def test_get_person_not_found(self, app, test_user):
        """Get non-existent person returns None."""
        with app.app_context():
            fetched = get_person(test_user.id, 99999)
            assert fetched is None


# ============== Person List/Filter Tests ==============


class TestPersonListService:
    """Tests for person listing and filtering."""

    def test_list_people_basic(self, app, test_user):
        """List all people."""
        with app.app_context():
            create_person(test_user.id, name="Person A")
            create_person(test_user.id, name="Person B")
            create_person(test_user.id, name="Person C")

            people = list_people(test_user.id)

            assert len(people) == 3

    @pytest.mark.xfail(reason="SQLite JSON contains() filter does not work correctly with array fields")
    def test_list_people_by_tag(self, app, test_user):
        """Filter people by tag."""
        with app.app_context():
            create_person(test_user.id, name="Work Friend", tags=["work", "friend"])
            create_person(test_user.id, name="School Friend", tags=["school", "friend"])
            create_person(test_user.id, name="Work Colleague", tags=["work"])

            work_people = list_people(test_user.id, tag="work")

            assert len(work_people) == 2

    def test_list_people_by_relationship_type(self, app, test_user):
        """Filter people by relationship type."""
        with app.app_context():
            create_person(test_user.id, name="Friend 1", relationship_type="friend")
            create_person(test_user.id, name="Friend 2", relationship_type="friend")
            create_person(test_user.id, name="Family 1", relationship_type="family")

            friends = list_people(test_user.id, relationship_type="friend")

            assert len(friends) == 2

    def test_list_people_by_importance(self, app, test_user):
        """Filter people by importance level."""
        with app.app_context():
            create_person(test_user.id, name="Important 1", importance_level=5)
            create_person(test_user.id, name="Important 2", importance_level=5)
            create_person(test_user.id, name="Normal", importance_level=3)

            important = list_people(test_user.id, importance_level=5)

            assert len(important) == 2

    def test_list_people_search(self, app, test_user):
        """Search people by name."""
        with app.app_context():
            create_person(test_user.id, name="John Smith")
            create_person(test_user.id, name="Jane Doe")
            create_person(test_user.id, name="Johnny Appleseed")

            results = list_people(test_user.id, search="John")

            assert len(results) == 2


# ============== Interaction Tests ==============


class TestInteractionService:
    """Tests for interaction logging and retrieval."""

    def test_log_interaction_success(self, app, test_user):
        """Log an interaction with a person."""
        with app.app_context():
            person = create_person(test_user.id, name="Interaction Person")

            interaction = log_interaction(
                test_user.id,
                person.id,
                date_value=date.today(),
                method="call",
                notes="Caught up on phone",
                sentiment="positive",
            )

            assert interaction.id is not None
            assert interaction.person_id == person.id
            assert interaction.user_id == test_user.id
            assert interaction.method == "call"
            assert interaction.notes == "Caught up on phone"
            assert interaction.sentiment == "positive"
            assert interaction.source == "manual"

    def test_log_interaction_minimal(self, app, test_user):
        """Log interaction with minimal fields."""
        with app.app_context():
            person = create_person(test_user.id, name="Minimal Interaction Person")

            interaction = log_interaction(test_user.id, person.id, date_value=date.today())

            assert interaction.id is not None
            assert interaction.method is None
            assert interaction.notes is None

    def test_log_interaction_person_not_found(self, app, test_user):
        """Logging interaction for non-existent person fails."""
        with app.app_context():
            with pytest.raises(ValueError, match="not_found"):
                log_interaction(test_user.id, 99999, date_value=date.today())

    def test_list_interactions(self, app, test_user):
        """List interactions for a person."""
        with app.app_context():
            person = create_person(test_user.id, name="List Interactions Person")
            log_interaction(test_user.id, person.id, date_value=date.today(), method="call")
            log_interaction(
                test_user.id, person.id, date_value=date.today() - timedelta(days=1), method="message"
            )
            log_interaction(
                test_user.id, person.id, date_value=date.today() - timedelta(days=2), method="meeting"
            )

            interactions = list_interactions(test_user.id, person.id)

            assert len(interactions) == 3

    def test_list_interactions_person_not_found(self, app, test_user):
        """Listing interactions for non-existent person fails."""
        with app.app_context():
            with pytest.raises(ValueError, match="not_found"):
                list_interactions(test_user.id, 99999)

    def test_edit_interaction(self, app, test_user):
        """Edit an existing interaction."""
        with app.app_context():
            person = create_person(test_user.id, name="Edit Interaction Person")
            interaction = log_interaction(
                test_user.id, person.id, date_value=date.today(), method="call"
            )

            updated = edit_interaction(
                test_user.id,
                interaction.id,
                notes="Updated notes",
                sentiment="neutral",
            )

            assert updated is not None
            assert updated.notes == "Updated notes"
            assert updated.sentiment == "neutral"

    def test_edit_interaction_not_found(self, app, test_user):
        """Edit non-existent interaction returns None."""
        with app.app_context():
            result = edit_interaction(test_user.id, 99999, notes="Updated")
            assert result is None

    def test_delete_interaction(self, app, test_user):
        """Delete an interaction."""
        with app.app_context():
            person = create_person(test_user.id, name="Delete Interaction Person")
            interaction = log_interaction(test_user.id, person.id, date_value=date.today())
            interaction_id = interaction.id

            deleted = delete_interaction(test_user.id, interaction_id)
            assert deleted is True
            assert Interaction.query.get(interaction_id) is None

    def test_delete_interaction_not_found(self, app, test_user):
        """Delete non-existent interaction returns False."""
        with app.app_context():
            deleted = delete_interaction(test_user.id, 99999)
            assert deleted is False


# ============== Reconnect Candidates Tests ==============


class TestReconnectCandidates:
    """Tests for reconnect candidate computation."""

    def test_compute_reconnect_candidates_no_interaction(self, app, test_user):
        """People with no interactions should be candidates."""
        with app.app_context():
            create_person(test_user.id, name="Never Contacted")

            candidates = compute_reconnect_candidates(test_user.id, cutoff_days=30)

            assert len(candidates) == 1
            assert candidates[0]["person"].name == "Never Contacted"
            assert candidates[0]["last_interaction_date"] is None

    def test_compute_reconnect_candidates_old_interaction(self, app, test_user):
        """People with old interactions should be candidates."""
        with app.app_context():
            person = create_person(test_user.id, name="Old Contact")
            log_interaction(
                test_user.id,
                person.id,
                date_value=date.today() - timedelta(days=60),
            )

            candidates = compute_reconnect_candidates(test_user.id, cutoff_days=30)

            assert len(candidates) == 1
            assert candidates[0]["person"].name == "Old Contact"

    def test_compute_reconnect_candidates_recent_interaction_excluded(self, app, test_user):
        """People with recent interactions should not be candidates."""
        with app.app_context():
            person = create_person(test_user.id, name="Recent Contact")
            log_interaction(
                test_user.id,
                person.id,
                date_value=date.today() - timedelta(days=5),
            )

            candidates = compute_reconnect_candidates(test_user.id, cutoff_days=30)

            assert len(candidates) == 0

    def test_compute_reconnect_candidates_limit(self, app, test_user):
        """Reconnect candidates should respect limit."""
        with app.app_context():
            for i in range(10):
                create_person(test_user.id, name=f"Contact {i}")

            candidates = compute_reconnect_candidates(test_user.id, limit=5, cutoff_days=30)

            assert len(candidates) == 5

    def test_compute_reconnect_candidates_ordered_by_last_contact(self, app, test_user):
        """Candidates should be ordered by oldest contact first."""
        with app.app_context():
            p1 = create_person(test_user.id, name="Very Old")
            p2 = create_person(test_user.id, name="Old")
            p3 = create_person(test_user.id, name="Medium Old")

            log_interaction(test_user.id, p1.id, date_value=date.today() - timedelta(days=90))
            log_interaction(test_user.id, p2.id, date_value=date.today() - timedelta(days=60))
            log_interaction(test_user.id, p3.id, date_value=date.today() - timedelta(days=45))

            candidates = compute_reconnect_candidates(test_user.id, cutoff_days=30)

            assert len(candidates) == 3
            # Oldest contact should be first
            assert candidates[0]["person"].name == "Very Old"


# ============== Event Emission Tests ==============


class TestRelationshipEventEmission:
    """Tests for relationship event emission to outbox."""

    def test_person_created_event_emitted(self, app, test_user):
        """Person creation should emit event to outbox."""
        with app.app_context():
            from lifeos.platform.outbox.models import OutboxMessage

            initial_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="relationships.person.created"
            ).count()

            create_person(test_user.id, name="Event Person")

            final_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="relationships.person.created"
            ).count()

            assert final_count == initial_count + 1

    def test_person_updated_event_emitted(self, app, test_user):
        """Person update should emit event to outbox."""
        with app.app_context():
            from lifeos.platform.outbox.models import OutboxMessage

            person = create_person(test_user.id, name="Update Event Person")

            initial_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="relationships.person.updated"
            ).count()

            update_person(test_user.id, person.id, notes="Updated")

            final_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="relationships.person.updated"
            ).count()

            assert final_count == initial_count + 1

    def test_person_deleted_event_emitted(self, app, test_user):
        """Person deletion should emit event to outbox."""
        with app.app_context():
            from lifeos.platform.outbox.models import OutboxMessage

            person = create_person(test_user.id, name="Delete Event Person")

            initial_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="relationships.person.deleted"
            ).count()

            delete_person(test_user.id, person.id)

            final_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="relationships.person.deleted"
            ).count()

            assert final_count == initial_count + 1

    def test_interaction_logged_event_emitted(self, app, test_user):
        """Interaction logging should emit event to outbox."""
        with app.app_context():
            from lifeos.platform.outbox.models import OutboxMessage

            person = create_person(test_user.id, name="Interaction Event Person")

            initial_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="relationships.interaction.logged"
            ).count()

            log_interaction(test_user.id, person.id, date_value=date.today())

            final_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="relationships.interaction.logged"
            ).count()

            assert final_count == initial_count + 1


# ============== User Isolation Tests ==============


class TestRelationshipUserIsolation:
    """Tests ensuring relationships are properly isolated per user."""

    def test_people_isolated_by_user(self, app, test_user):
        """Users can only see their own people."""
        with app.app_context():
            # Create person for test user
            create_person(test_user.id, name="User A Person")

            # Create another user with person
            other_user = User(email="other-rel@example.com", password_hash=hash_password("secret"))
            db.session.add(other_user)
            db.session.commit()
            create_person(other_user.id, name="User B Person")

            # List people for test user
            people = list_people(test_user.id)

            assert len(people) == 1
            assert people[0].name == "User A Person"

    def test_interactions_isolated_by_user(self, app, test_user):
        """Users can only log interactions for their own people."""
        with app.app_context():
            # Create another user's person
            other_user = User(email="other-int@example.com", password_hash=hash_password("secret"))
            db.session.add(other_user)
            db.session.commit()
            other_person = create_person(other_user.id, name="Other User's Person")

            # Test user cannot log interaction with other's person
            with pytest.raises(ValueError, match="not_found"):
                log_interaction(test_user.id, other_person.id, date_value=date.today())

    def test_get_person_isolated(self, app, test_user):
        """Cannot get another user's person."""
        with app.app_context():
            other_user = User(email="other-get@example.com", password_hash=hash_password("secret"))
            db.session.add(other_user)
            db.session.commit()
            other_person = create_person(other_user.id, name="Private Person")

            result = get_person(test_user.id, other_person.id)
            assert result is None

    def test_delete_person_isolated(self, app, test_user):
        """Cannot delete another user's person."""
        with app.app_context():
            other_user = User(email="other-del@example.com", password_hash=hash_password("secret"))
            db.session.add(other_user)
            db.session.commit()
            other_person = create_person(other_user.id, name="Protected Person")

            deleted = delete_person(test_user.id, other_person.id)
            assert deleted is False

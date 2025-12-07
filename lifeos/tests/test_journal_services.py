"""Comprehensive Journal Services tests.

Tests all service functions for the journal domain:
- create_entry
- update_entry
- delete_entry
- get_entry
- list_entries (with filters)
- mood validation
- outbox event emission
"""

from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.integration

from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.domains.journal.events import (
    JOURNAL_ENTRY_CREATED,
    JOURNAL_ENTRY_UPDATED,
    JOURNAL_ENTRY_DELETED,
)
from lifeos.domains.journal.models import JournalEntry
from lifeos.domains.journal.services import journal_service
from lifeos.extensions import db


# ==================== Fixtures ====================


@pytest.fixture
def test_user(app):
    """Create a test user and return user object."""
    with app.app_context():
        user = create_user(
            UserCreateRequest(
                email="journal-service-test@example.com",
                password="secret123",
                full_name="Journal Tester",
                timezone="UTC",
            )
        )
        db.session.commit()
        return user


@pytest.fixture
def other_user(app):
    """Create another test user for isolation tests."""
    with app.app_context():
        user = create_user(
            UserCreateRequest(
                email="other-journal-user@example.com",
                password="secret123",
                full_name="Other User",
                timezone="UTC",
            )
        )
        db.session.commit()
        return user


# ==================== Create Entry Tests ====================


def test_create_entry_success(app, test_user):
    """Should create journal entry with all fields."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox") as mock_enqueue:
            entry = journal_service.create_entry(
                user_id=test_user.id,
                title="My First Entry",
                body="This is the content of my journal entry.",
                entry_date=date.today(),
                mood=3,
                tags=["gratitude", "reflection"],
                is_private=True,
                sentiment_score=0.75,
                emotion_label="happy",
            )

            assert entry is not None
            assert entry.id is not None
            assert entry.title == "My First Entry"
            assert entry.body == "This is the content of my journal entry."
            assert entry.mood == 3
            assert entry.tags == ["gratitude", "reflection"]
            assert entry.is_private is True
            assert entry.sentiment_score == 0.75
            assert entry.emotion_label == "happy"

            # Verify outbox event
            mock_enqueue.assert_called_once()
            call_args = mock_enqueue.call_args
            assert call_args[0][0] == JOURNAL_ENTRY_CREATED
            assert call_args[0][1]["entry_id"] == entry.id
            assert call_args[0][1]["user_id"] == test_user.id


def test_create_entry_minimal_fields(app, test_user):
    """Should create entry with only required fields."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox"):
            entry = journal_service.create_entry(
                user_id=test_user.id,
                title=None,
                body="Just the body",
                entry_date=date.today(),
            )

            assert entry is not None
            assert entry.title is None
            assert entry.body == "Just the body"
            assert entry.mood is None
            assert entry.tags == []


def test_create_entry_empty_body_fails(app, test_user):
    """Should reject entry with empty body."""
    with app.app_context():
        with pytest.raises(ValueError, match="validation_error"):
            journal_service.create_entry(
                user_id=test_user.id,
                title="Title Only",
                body="",
                entry_date=date.today(),
            )


def test_create_entry_whitespace_body_fails(app, test_user):
    """Should reject entry with whitespace-only body."""
    with app.app_context():
        with pytest.raises(ValueError, match="validation_error"):
            journal_service.create_entry(
                user_id=test_user.id,
                title="Title Only",
                body="   \n\t  ",
                entry_date=date.today(),
            )


def test_create_entry_strips_whitespace(app, test_user):
    """Should trim whitespace from title and body."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox"):
            entry = journal_service.create_entry(
                user_id=test_user.id,
                title="  Padded Title  ",
                body="  Padded body  ",
                entry_date=date.today(),
            )

            assert entry.title == "Padded Title"
            assert entry.body == "Padded body"


# ==================== Mood Validation Tests ====================


def test_create_entry_mood_valid_range(app, test_user):
    """Should accept mood within valid range (-5 to 5)."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox"):
            for mood in [-5, -3, 0, 3, 5]:
                entry = journal_service.create_entry(
                    user_id=test_user.id,
                    title=f"Mood {mood}",
                    body=f"Entry with mood {mood}",
                    entry_date=date.today(),
                    mood=mood,
                )
                assert entry.mood == mood


def test_create_entry_mood_invalid_below_min(app, test_user):
    """Should reject mood below minimum (-5)."""
    with app.app_context():
        with pytest.raises(ValueError, match="validation_error"):
            journal_service.create_entry(
                user_id=test_user.id,
                title="Bad Mood",
                body="Content",
                entry_date=date.today(),
                mood=-6,
            )


def test_create_entry_mood_invalid_above_max(app, test_user):
    """Should reject mood above maximum (5)."""
    with app.app_context():
        with pytest.raises(ValueError, match="validation_error"):
            journal_service.create_entry(
                user_id=test_user.id,
                title="Too Good",
                body="Content",
                entry_date=date.today(),
                mood=6,
            )


def test_create_entry_mood_none_allowed(app, test_user):
    """Should allow null mood."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox"):
            entry = journal_service.create_entry(
                user_id=test_user.id,
                title="No Mood",
                body="Content",
                entry_date=date.today(),
                mood=None,
            )
            assert entry.mood is None


# ==================== Update Entry Tests ====================


def test_update_entry_success(app, test_user):
    """Should update entry fields."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox") as mock_enqueue:
            # Create entry
            entry = journal_service.create_entry(
                user_id=test_user.id,
                title="Original",
                body="Original body",
                entry_date=date.today(),
                mood=2,
            )
            entry_id = entry.id
            mock_enqueue.reset_mock()

            # Update entry
            updated = journal_service.update_entry(
                test_user.id,
                entry_id,
                title="Updated Title",
                body="Updated body",
                mood=4,
            )

            assert updated is not None
            assert updated.title == "Updated Title"
            assert updated.body == "Updated body"
            assert updated.mood == 4

            # Verify outbox event
            mock_enqueue.assert_called_once()
            call_args = mock_enqueue.call_args
            assert call_args[0][0] == JOURNAL_ENTRY_UPDATED
            assert call_args[0][1]["entry_id"] == entry_id


def test_update_entry_partial(app, test_user):
    """Should update only provided fields."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox"):
            entry = journal_service.create_entry(
                user_id=test_user.id,
                title="Keep This",
                body="Keep body",
                entry_date=date.today(),
                mood=2,
                tags=["original"],
            )
            entry_id = entry.id

            updated = journal_service.update_entry(
                test_user.id,
                entry_id,
                mood=5,
            )

            assert updated.title == "Keep This"  # Unchanged
            assert updated.body == "Keep body"  # Unchanged
            assert updated.mood == 5  # Updated
            assert updated.tags == ["original"]  # Unchanged


def test_update_entry_not_found(app, test_user):
    """Should return None for non-existent entry."""
    with app.app_context():
        result = journal_service.update_entry(
            test_user.id,
            99999,
            title="New Title",
        )
        assert result is None


def test_update_entry_other_user(app, test_user, other_user):
    """Should not update other user's entry."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox"):
            entry = journal_service.create_entry(
                user_id=test_user.id,
                title="My Entry",
                body="My content",
                entry_date=date.today(),
            )
            entry_id = entry.id

        result = journal_service.update_entry(
            other_user.id,
            entry_id,
            title="Hacked",
        )
        assert result is None


# ==================== Delete Entry Tests ====================


def test_delete_entry_success(app, test_user):
    """Should delete entry."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox") as mock_enqueue:
            entry = journal_service.create_entry(
                user_id=test_user.id,
                title="Delete Me",
                body="Content",
                entry_date=date.today(),
            )
            entry_id = entry.id
            mock_enqueue.reset_mock()

            result = journal_service.delete_entry(test_user.id, entry_id)

            assert result is True
            # Verify gone
            assert JournalEntry.query.get(entry_id) is None

            # Verify outbox event
            mock_enqueue.assert_called_once()
            call_args = mock_enqueue.call_args
            assert call_args[0][0] == JOURNAL_ENTRY_DELETED


def test_delete_entry_not_found(app, test_user):
    """Should return False for non-existent entry."""
    with app.app_context():
        result = journal_service.delete_entry(test_user.id, 99999)
        assert result is False


def test_delete_entry_other_user(app, test_user, other_user):
    """Should not delete other user's entry."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox"):
            entry = journal_service.create_entry(
                user_id=test_user.id,
                title="Protected",
                body="Content",
                entry_date=date.today(),
            )
            entry_id = entry.id

        result = journal_service.delete_entry(other_user.id, entry_id)
        assert result is False

        # Verify still exists
        assert JournalEntry.query.get(entry_id) is not None


# ==================== Get Entry Tests ====================


def test_get_entry_success(app, test_user):
    """Should retrieve entry by ID."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox"):
            entry = journal_service.create_entry(
                user_id=test_user.id,
                title="Get Me",
                body="Content",
                entry_date=date.today(),
            )
            entry_id = entry.id

        result = journal_service.get_entry(test_user.id, entry_id)
        assert result is not None
        assert result.id == entry_id
        assert result.title == "Get Me"


def test_get_entry_not_found(app, test_user):
    """Should return None for non-existent entry."""
    with app.app_context():
        result = journal_service.get_entry(test_user.id, 99999)
        assert result is None


def test_get_entry_other_user(app, test_user, other_user):
    """Should not retrieve other user's entry."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox"):
            entry = journal_service.create_entry(
                user_id=test_user.id,
                title="Private Entry",
                body="Content",
                entry_date=date.today(),
            )
            entry_id = entry.id

        result = journal_service.get_entry(other_user.id, entry_id)
        assert result is None


# ==================== List Entries Tests ====================


def test_list_entries_empty(app, test_user):
    """Should return empty list when no entries."""
    with app.app_context():
        entries, total = journal_service.list_entries(test_user.id)
        assert entries == []
        assert total == 0


def test_list_entries_basic(app, test_user):
    """Should list entries for user."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox"):
            for i in range(3):
                journal_service.create_entry(
                    user_id=test_user.id,
                    title=f"Entry {i}",
                    body=f"Content {i}",
                    entry_date=date.today() - timedelta(days=i),
                )

        entries, total = journal_service.list_entries(test_user.id)
        assert len(entries) == 3
        assert total == 3


def test_list_entries_ordered_by_date_desc(app, test_user):
    """Should order entries by date descending."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox"):
            journal_service.create_entry(
                user_id=test_user.id,
                title="Old",
                body="Content",
                entry_date=date.today() - timedelta(days=10),
            )
            journal_service.create_entry(
                user_id=test_user.id,
                title="New",
                body="Content",
                entry_date=date.today(),
            )

        entries, _ = journal_service.list_entries(test_user.id)
        assert entries[0].title == "New"
        assert entries[1].title == "Old"


def test_list_entries_filter_by_date_range(app, test_user):
    """Should filter by date range."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox"):
            today = date.today()
            for i in range(5):
                journal_service.create_entry(
                    user_id=test_user.id,
                    title=f"Entry {i}",
                    body=f"Content {i}",
                    entry_date=today - timedelta(days=i),
                )

        entries, total = journal_service.list_entries(
            test_user.id,
            date_from=today - timedelta(days=2),
            date_to=today,
        )
        assert total == 3  # Today, yesterday, day before


def test_list_entries_filter_by_mood(app, test_user):
    """Should filter by mood."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox"):
            journal_service.create_entry(
                user_id=test_user.id,
                title="Happy",
                body="Content",
                entry_date=date.today(),
                mood=5,
            )
            journal_service.create_entry(
                user_id=test_user.id,
                title="Sad",
                body="Content",
                entry_date=date.today(),
                mood=-3,
            )

        entries, total = journal_service.list_entries(test_user.id, mood=5)
        assert total == 1
        assert entries[0].title == "Happy"


@pytest.mark.xfail(reason="SQLite JSON contains() filter does not work correctly with array fields")
def test_list_entries_filter_by_tag(app, test_user):
    """Should filter by tag."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox"):
            journal_service.create_entry(
                user_id=test_user.id,
                title="Tagged",
                body="Content",
                entry_date=date.today(),
                tags=["gratitude", "morning"],
            )
            journal_service.create_entry(
                user_id=test_user.id,
                title="Untagged",
                body="Content",
                entry_date=date.today(),
                tags=[],
            )

        entries, total = journal_service.list_entries(test_user.id, tag="gratitude")
        assert total == 1
        assert entries[0].title == "Tagged"


def test_list_entries_search_text(app, test_user):
    """Should search in title and body."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox"):
            journal_service.create_entry(
                user_id=test_user.id,
                title="Python Learning",
                body="Learned about decorators",
                entry_date=date.today(),
            )
            journal_service.create_entry(
                user_id=test_user.id,
                title="Random",
                body="Nothing special",
                entry_date=date.today(),
            )

        # Search in title
        entries, total = journal_service.list_entries(test_user.id, search_text="Python")
        assert total == 1
        assert entries[0].title == "Python Learning"

        # Search in body
        entries, total = journal_service.list_entries(test_user.id, search_text="decorators")
        assert total == 1


def test_list_entries_pagination(app, test_user):
    """Should paginate results."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox"):
            for i in range(15):
                journal_service.create_entry(
                    user_id=test_user.id,
                    title=f"Entry {i}",
                    body=f"Content {i}",
                    entry_date=date.today() - timedelta(days=i),
                )

        # First page
        entries, total = journal_service.list_entries(test_user.id, page=1, per_page=5)
        assert len(entries) == 5
        assert total == 15

        # Second page
        entries, total = journal_service.list_entries(test_user.id, page=2, per_page=5)
        assert len(entries) == 5

        # Last page
        entries, total = journal_service.list_entries(test_user.id, page=3, per_page=5)
        assert len(entries) == 5


def test_list_entries_isolation(app, test_user, other_user):
    """Should not list other user's entries."""
    with app.app_context():
        with patch("lifeos.domains.journal.services.journal_service.enqueue_outbox"):
            journal_service.create_entry(
                user_id=test_user.id,
                title="My Entry",
                body="Content",
                entry_date=date.today(),
            )

        entries, total = journal_service.list_entries(other_user.id)
        assert entries == []
        assert total == 0

"""Tests for Skills domain services: skills, practice sessions, metrics."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.integration

from lifeos.core.auth.password import hash_password
from lifeos.core.users.models import User
from lifeos.domains.skills.models.skill_models import PracticeSession, Skill
from lifeos.domains.skills.services.skill_service import (
    create_skill,
    delete_practice_session,
    delete_skill,
    get_skill_summary,
    list_skills_with_aggregates,
    log_practice_session,
    update_practice_session,
    update_skill,
)
from lifeos.extensions import db


@pytest.fixture
def test_user(app):
    """Create a test user for skills tests."""
    with app.app_context():
        user = User(
            email="skills-tester@example.com", password_hash=hash_password("secret")
        )
        db.session.add(user)
        db.session.commit()
        yield user


# ============== Skill CRUD Tests ==============


class TestSkillService:
    """Tests for skill creation, update, and deletion."""

    def test_create_skill_success(self, app, test_user):
        """Create a valid skill."""
        with app.app_context():
            skill = create_skill(
                test_user.id,
                name="Piano",
                category="Music",
                difficulty="intermediate",
                target_level=5,
                current_level=2,
                description="Learning classical piano",
                tags=["music", "instrument"],
            )

            assert skill.id is not None
            assert skill.user_id == test_user.id
            assert skill.name == "Piano"
            assert skill.category == "Music"
            assert skill.difficulty == "intermediate"
            assert skill.target_level == 5
            assert skill.current_level == 2
            assert skill.description == "Learning classical piano"
            assert skill.tags == ["music", "instrument"]

    def test_create_skill_minimal(self, app, test_user):
        """Create skill with minimal fields."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Guitar")

            assert skill.id is not None
            assert skill.name == "Guitar"
            assert skill.category is None
            assert skill.difficulty is None

    def test_create_skill_empty_name_fails(self, app, test_user):
        """Creating skill with empty name fails."""
        with app.app_context():
            with pytest.raises(ValueError, match="validation_error"):
                create_skill(test_user.id, name="")

    def test_create_skill_whitespace_name_fails(self, app, test_user):
        """Creating skill with whitespace-only name fails."""
        with app.app_context():
            with pytest.raises(ValueError, match="validation_error"):
                create_skill(test_user.id, name="   ")

    def test_create_skill_duplicate_name_fails(self, app, test_user):
        """Creating skill with duplicate name fails."""
        with app.app_context():
            create_skill(test_user.id, name="Python")

            with pytest.raises(ValueError, match="duplicate"):
                create_skill(test_user.id, name="Python")

    def test_update_skill_success(self, app, test_user):
        """Update an existing skill."""
        with app.app_context():
            skill = create_skill(
                test_user.id, name="JavaScript", category="Programming"
            )

            updated = update_skill(
                test_user.id,
                skill.id,
                description="Full-stack JavaScript development",
                current_level=3,
            )

            assert updated is not None
            assert updated.description == "Full-stack JavaScript development"
            assert updated.current_level == 3

    def test_update_skill_not_found(self, app, test_user):
        """Update non-existent skill returns None."""
        with app.app_context():
            result = update_skill(test_user.id, 99999, name="New Name")
            assert result is None

    def test_update_skill_wrong_user(self, app, test_user):
        """Cannot update another user's skill."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Rust")

            # Create another user
            other_user = User(
                email="other-skills@example.com", password_hash=hash_password("secret")
            )
            db.session.add(other_user)
            db.session.commit()

            result = update_skill(other_user.id, skill.id, name="New Name")
            assert result is None

    def test_delete_skill_success(self, app, test_user):
        """Delete an existing skill."""
        with app.app_context():
            skill = create_skill(test_user.id, name="To Delete")
            skill_id = skill.id

            deleted = delete_skill(test_user.id, skill_id)
            assert deleted is True

            # Verify it's gone
            assert Skill.query.get(skill_id) is None

    def test_delete_skill_not_found(self, app, test_user):
        """Delete non-existent skill returns False."""
        with app.app_context():
            deleted = delete_skill(test_user.id, 99999)
            assert deleted is False


# ============== Practice Session Tests ==============


class TestPracticeSessionService:
    """Tests for practice session logging."""

    def test_log_practice_session_success(self, app, test_user):
        """Log a valid practice session."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Drawing")

            session = log_practice_session(
                test_user.id,
                skill.id,
                duration_minutes=60,
                intensity=4,
                notes="Practiced portrait sketching",
            )

            assert session.id is not None
            assert session.skill_id == skill.id
            assert session.user_id == test_user.id
            assert session.duration_minutes == 60
            assert session.intensity == 4
            assert session.notes == "Practiced portrait sketching"
            assert session.source == "manual"

    def test_log_practice_session_with_timestamp(self, app, test_user):
        """Log practice session with custom timestamp."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Photography")
            past_time = datetime.utcnow() - timedelta(days=1)

            session = log_practice_session(
                test_user.id,
                skill.id,
                duration_minutes=45,
                practiced_at=past_time,
            )

            assert session.practiced_at.date() == past_time.date()

    def test_log_practice_session_skill_not_found(self, app, test_user):
        """Logging practice for non-existent skill fails."""
        with app.app_context():
            with pytest.raises(ValueError, match="not_found"):
                log_practice_session(test_user.id, 99999, duration_minutes=30)

    def test_log_practice_session_zero_duration_fails(self, app, test_user):
        """Duration must be positive."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Cooking")

            with pytest.raises(ValueError, match="validation_error"):
                log_practice_session(test_user.id, skill.id, duration_minutes=0)

    def test_log_practice_session_negative_duration_fails(self, app, test_user):
        """Duration cannot be negative."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Gardening")

            with pytest.raises(ValueError, match="validation_error"):
                log_practice_session(test_user.id, skill.id, duration_minutes=-10)

    def test_update_practice_session(self, app, test_user):
        """Update an existing practice session."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Woodworking")
            session = log_practice_session(test_user.id, skill.id, duration_minutes=30)

            updated = update_practice_session(
                test_user.id,
                session.id,
                duration_minutes=45,
                notes="Updated notes",
            )

            assert updated is not None
            assert updated.duration_minutes == 45
            assert updated.notes == "Updated notes"

    def test_delete_practice_session(self, app, test_user):
        """Delete a practice session."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Welding")
            session = log_practice_session(test_user.id, skill.id, duration_minutes=30)
            session_id = session.id

            deleted = delete_practice_session(test_user.id, session_id)
            assert deleted is True
            assert PracticeSession.query.get(session_id) is None


# ============== Skill Aggregation Tests ==============


class TestSkillAggregation:
    """Tests for skill listing with aggregates and progress."""

    def test_list_skills_with_aggregates(self, app, test_user):
        """List skills with practice aggregates."""
        with app.app_context():
            skill1 = create_skill(test_user.id, name="Python Programming")
            skill2 = create_skill(test_user.id, name="Spanish")

            # Add practice sessions
            log_practice_session(test_user.id, skill1.id, duration_minutes=60)
            log_practice_session(test_user.id, skill1.id, duration_minutes=90)
            log_practice_session(test_user.id, skill2.id, duration_minutes=30)

            records = list_skills_with_aggregates(user_id=test_user.id)

            assert len(records) == 2

            # Find Python skill record
            python_rec = next(
                r for r in records if r["skill"].name == "Python Programming"
            )
            assert python_rec["totals"]["total_minutes"] == 150
            assert python_rec["totals"]["session_count"] == 2

    def test_get_skill_summary(self, app, test_user):
        """Get detailed skill summary with stats."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Chess")

            # Log sessions over multiple days
            now = datetime.utcnow()
            log_practice_session(
                test_user.id, skill.id, duration_minutes=30, practiced_at=now
            )
            log_practice_session(
                test_user.id,
                skill.id,
                duration_minutes=45,
                practiced_at=now - timedelta(days=1),
            )
            log_practice_session(
                test_user.id,
                skill.id,
                duration_minutes=60,
                practiced_at=now - timedelta(days=2),
            )

            summary = get_skill_summary(test_user.id, skill.id)

            assert summary is not None
            assert summary["skill"].name == "Chess"
            assert summary["totals"]["total_minutes"] == 135
            assert summary["totals"]["session_count"] == 3

    def test_get_skill_summary_not_found(self, app, test_user):
        """Get summary for non-existent skill returns None."""
        with app.app_context():
            summary = get_skill_summary(test_user.id, 99999)
            assert summary is None


# ============== Skill Progress Tests ==============


class TestSkillProgress:
    """Tests for skill progress computation using get_skill_summary."""

    def test_skill_summary_with_sessions(self, app, test_user):
        """Get summary for skill with practice history."""
        with app.app_context():
            skill = create_skill(
                test_user.id, name="TypeScript", target_level=5, current_level=2
            )

            now = datetime.utcnow()
            # Log sessions over the past week
            for i in range(5):
                log_practice_session(
                    test_user.id,
                    skill.id,
                    duration_minutes=30,
                    practiced_at=now - timedelta(days=i),
                )

            summary = get_skill_summary(test_user.id, skill.id)

            assert summary is not None
            assert summary["totals"]["total_minutes"] >= 150  # 5 * 30min = 150min
            assert summary["totals"]["session_count"] == 5

    def test_skill_summary_empty(self, app, test_user):
        """Get summary for skill with no practice."""
        with app.app_context():
            skill = create_skill(test_user.id, name="Go Language")

            summary = get_skill_summary(test_user.id, skill.id)

            assert summary is not None
            assert summary["totals"].get("total_minutes", 0) == 0
            assert summary["totals"].get("session_count", 0) == 0


# ============== Event Emission Tests ==============


class TestSkillEventEmission:
    """Tests for skill event emission to outbox."""

    def test_skill_created_event_emitted(self, app, test_user):
        """Skill creation should emit event to outbox."""
        with app.app_context():
            from lifeos.lifeos_platform.outbox.models import OutboxMessage

            initial_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="skills.skill.created"
            ).count()

            create_skill(test_user.id, name="Event Test Skill")

            final_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="skills.skill.created"
            ).count()

            assert final_count == initial_count + 1

    def test_skill_updated_event_emitted(self, app, test_user):
        """Skill update should emit event to outbox."""
        with app.app_context():
            from lifeos.lifeos_platform.outbox.models import OutboxMessage

            skill = create_skill(test_user.id, name="Update Event Skill")

            initial_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="skills.skill.updated"
            ).count()

            update_skill(test_user.id, skill.id, description="Updated")

            final_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="skills.skill.updated"
            ).count()

            assert final_count == initial_count + 1

    def test_skill_deleted_event_emitted(self, app, test_user):
        """Skill deletion should emit event to outbox."""
        with app.app_context():
            from lifeos.lifeos_platform.outbox.models import OutboxMessage

            skill = create_skill(test_user.id, name="Delete Event Skill")

            initial_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="skills.skill.deleted"
            ).count()

            delete_skill(test_user.id, skill.id)

            final_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="skills.skill.deleted"
            ).count()

            assert final_count == initial_count + 1

    def test_practice_logged_event_emitted(self, app, test_user):
        """Practice session logging should emit event to outbox."""
        with app.app_context():
            from lifeos.lifeos_platform.outbox.models import OutboxMessage

            skill = create_skill(test_user.id, name="Practice Event Skill")

            initial_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="skills.practice.logged"
            ).count()

            log_practice_session(test_user.id, skill.id, duration_minutes=30)

            final_count = OutboxMessage.query.filter_by(
                user_id=test_user.id, event_type="skills.practice.logged"
            ).count()

            assert final_count == initial_count + 1


# ============== User Isolation Tests ==============


class TestSkillUserIsolation:
    """Tests ensuring skills are properly isolated per user."""

    def test_skills_isolated_by_user(self, app, test_user):
        """Users can only see their own skills."""
        with app.app_context():
            # Create skill for test user
            create_skill(test_user.id, name="User A Skill")

            # Create another user with skill
            other_user = User(
                email="other-skills2@example.com", password_hash=hash_password("secret")
            )
            db.session.add(other_user)
            db.session.commit()
            create_skill(other_user.id, name="User B Skill")

            # List skills for test user
            records = list_skills_with_aggregates(user_id=test_user.id)

            assert len(records) == 1
            assert records[0]["skill"].name == "User A Skill"

    def test_practice_sessions_isolated_by_user(self, app, test_user):
        """Users can only log practice for their own skills."""
        with app.app_context():
            # Create skill for test user
            skill = create_skill(test_user.id, name="Isolated Skill")

            # Create another user
            other_user = User(
                email="other-practice@example.com",
                password_hash=hash_password("secret"),
            )
            db.session.add(other_user)
            db.session.commit()

            # Other user cannot log practice for test user's skill
            with pytest.raises(ValueError, match="not_found"):
                log_practice_session(other_user.id, skill.id, duration_minutes=30)

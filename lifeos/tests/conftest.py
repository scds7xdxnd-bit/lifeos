import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lifeos import create_app
from lifeos.extensions import db
from lifeos.core.auth import models as auth_models
from lifeos.core.users import models as user_models
from lifeos.core.events import event_models
from lifeos.domains.finance.models import (
    accounting_models,
    schedule_models,
    receivable_models,
)
from lifeos.domains.habits.models import habit
from lifeos.domains.skills.models.skill_models import (
    Skill as skill,
    PracticeSession as practice_session,
)
from lifeos.domains.skills.models import skill_metric
from lifeos.domains.health.models import biometrics, workout, nutrition
from lifeos.domains.journal.models import journal_entry
from lifeos.domains.relationships.models import contact, interaction
from lifeos.domains.projects.models import project, task, task_log
from lifeos.core.insights import models as insight_models
from lifeos.domains.finance.models import schedule_models
from lifeos.core.auth.models import Role
from lifeos.core.users.models import User
from lifeos.platform.outbox import models as outbox_models
from lifeos.domains.calendar.models import calendar_event as calendar_models


# ==================== Pytest Markers ====================
def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests (no external dependencies)")
    config.addinivalue_line("markers", "integration: Integration tests (database, API)")
    config.addinivalue_line("markers", "ml: Machine learning tests (model inference)")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "smoke: Quick smoke tests for CI")


@pytest.fixture()
def app():
    app = create_app("testing")
    with app.app_context():
        # ensure all models are imported so metadata is populated before create_all
        _ = (
            auth_models,
            user_models,
            event_models,
            accounting_models,
            schedule_models,
            receivable_models,
            habit,
            skill,
            practice_session,
            skill_metric,
            biometrics,
            workout,
            nutrition,
            journal_entry,
            contact,
            interaction,
            project,
            task,
            task_log,
            outbox_models,
            calendar_models,
        )
        db.create_all()
        # Seed a default user for FK-dependent tests
        if not User.query.filter_by(email="test@example.com").first():
            db.session.add(User(email="test@example.com", password_hash="test"))
            db.session.commit()
        # seed a default admin role so require_roles can find it
        if not Role.query.filter_by(name="admin").first():
            db.session.add(Role(name="admin", description="admin role for tests"))
            db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()

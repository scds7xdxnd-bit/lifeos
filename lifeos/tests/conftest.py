import sys
from pathlib import Path

import os

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config as AlembicConfig

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
from lifeos.lifeos_platform.outbox import models as outbox_models
from lifeos.domains.calendar.models import calendar_event as calendar_models


# ==================== Pytest Markers ====================
def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests (no external dependencies)")
    config.addinivalue_line("markers", "integration: Integration tests (database, API)")
    config.addinivalue_line("markers", "ml: Machine learning tests (model inference)")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "smoke: Quick smoke tests for CI")


def _alembic_config() -> AlembicConfig:
    cfg = AlembicConfig(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", "lifeos/migrations")
    cfg.set_main_option("lifeos_env", "testing")
    db_url = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not db_url:
        db_url = "sqlite:///instance/test.db"
    if db_url:
        cfg.set_main_option("sqlalchemy.url", db_url)
    return cfg


@pytest.fixture(scope="session", autouse=True)
def migrated_db():
    """Apply migrations once per session to mirror production schema."""
    cfg = _alembic_config()
    command.upgrade(cfg, "head")
    yield
    try:
        command.downgrade(cfg, "base")
    except Exception:
        # Downgrade is optional for local/CI runs; ignore failures to avoid hiding test results.
        pass


@pytest.fixture()
def app(migrated_db):
    app = create_app("testing")
    with app.app_context():
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


@pytest.fixture()
def client(app):
    return app.test_client()

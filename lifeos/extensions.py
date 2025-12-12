"""Shared extensions for the LifeOS application."""

from pathlib import Path

from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Core persistence and auth/security primitives
db = SQLAlchemy(session_options={"expire_on_commit": False})
migrate = Migrate()
jwt = JWTManager()
login_manager = LoginManager()
bcrypt = Bcrypt()
limiter = Limiter(
    key_func=get_remote_address, enabled=True, default_limits=["200 per hour"]
)


def init_extensions(app) -> None:
    """Initialize all extensions with the Flask app."""
    db.init_app(app)
    migrations_dir = Path(__file__).resolve().parent / "migrations"
    migrate.init_app(app, db, directory=str(migrations_dir))
    jwt.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    limiter.enabled = app.config.get("RATELIMIT_ENABLED", True)
    limiter.default_limits = [app.config.get("RATELIMIT_DEFAULT", "200 per hour")]
    limiter.storage_uri = app.config.get("RATELIMIT_STORAGE_URI", "memory://")
    limiter.init_app(app)

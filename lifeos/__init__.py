"""LifeOS application factory and bootstrap."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from flask import Flask, redirect, url_for
from sqlalchemy.engine import processors

from lifeos.config import config_by_name
from lifeos.core.auth.csrf import generate_csrf_token
from lifeos.core.events.event_bus import event_bus
from lifeos.core.insights.engine import insights_engine
from lifeos.extensions import init_extensions, login_manager


def _patch_str_to_datetime_processor() -> None:
    """Make SQLAlchemy tolerant of sqlite returning datetime objects.

    sqlite3 with detect_types enabled can emit datetime objects; SQLAlchemy's
    default str_to_datetime expects strings and will raise TypeError. This
    shim returns datetime values as-is while delegating normal parsing to the
    original processor for strings.
    """
    original = processors.str_to_datetime

    def _safe(value):
        if value is None or isinstance(value, datetime):
            return value
        try:
            return original(value)
        except TypeError:
            return value

    processors.str_to_datetime = _safe


_patch_str_to_datetime_processor()


def create_app(config_name: Optional[str] = None) -> Flask:
    """Create and configure the LifeOS Flask application."""
    env_name = (config_name or os.environ.get("APP_ENV") or "development").lower()
    project_root = Path(__file__).resolve().parent.parent
    instance_root = project_root / "instance"

    app = Flask(
        __name__,
        instance_path=str(instance_root),
        instance_relative_config=True,
        static_folder=str(Path(__file__).parent / "static"),
        template_folder=str(Path(__file__).parent / "templates"),
    )
    config_cls = config_by_name.get(env_name, config_by_name["development"])
    app.config.from_object(config_cls)

    # Ensure instance folders exist (uploads, migrations)
    instance_root.mkdir(parents=True, exist_ok=True)
    uploads_config = app.config.get("UPLOAD_FOLDER", "instance/uploads")
    uploads_path = Path(uploads_config)
    if not uploads_path.is_absolute():
        uploads_path = project_root / uploads_config
    uploads_path.mkdir(parents=True, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = str(uploads_path)

    # Normalize sqlite path to absolute to avoid "unable to open database file"
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI")
    is_sqlite = db_uri and db_uri.startswith("sqlite:")
    if is_sqlite and db_uri.startswith("sqlite:///"):
        db_path = db_uri.replace("sqlite:///", "", 1)
        abs_path = project_root / db_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{abs_path}"

    if is_sqlite:
        # Guard against sqlite3 returning datetime objects that SQLAlchemy also tries to parse.
        engine_opts = app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {})
        connect_args = engine_opts.setdefault("connect_args", {})
        # Force-disable sqlite datetime parsing so values stay as strings for SQLAlchemy's processors.
        connect_args["detect_types"] = 0
        # Increase busy timeout to reduce "database is locked" errors when multiple writes happen.
        connect_args.setdefault("timeout", 30)
        try:
            import sqlite3

            sqlite3.register_converter(
                "DATETIME",
                lambda val: (val.decode() if isinstance(val, (bytes, bytearray)) else str(val)),
            )
            sqlite3.register_converter(
                "TIMESTAMP",
                lambda val: (val.decode() if isinstance(val, (bytes, bytearray)) else str(val)),
            )
        except Exception:
            # If sqlite3 is unavailable or converters cannot be registered, continue with detect_types disabled.
            pass
    else:
        # Remove sqlite-specific connect_args that break Postgres/MySQL drivers in CI
        engine_opts = app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {})
        connect_args = engine_opts.get("connect_args") or {}
        connect_args.pop("detect_types", None)
        # Convert sqlite busy timeout to Postgres connect_timeout, otherwise drop it
        if "timeout" in connect_args:
            timeout_val = connect_args.pop("timeout")
            is_postgres = db_uri.startswith("postgresql")
            if is_postgres:
                connect_args.setdefault("connect_timeout", timeout_val)
        # If nothing remains, drop connect_args entirely
        if not connect_args and "connect_args" in engine_opts:
            engine_opts.pop("connect_args")
        else:
            engine_opts["connect_args"] = connect_args

    init_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_auth_handlers(app)

    # Attach shared engines
    app.extensions["event_bus"] = event_bus
    app.extensions["insights_engine"] = insights_engine

    # Register calendar interpreter subscriptions
    from lifeos.core.interpreter import calendar_interpreter

    calendar_interpreter.register_subscriptions()
    app.extensions["calendar_interpreter"] = calendar_interpreter

    @app.get("/")
    def index():
        # Send users to the finance dashboard by default.
        return redirect(url_for("finance_pages.dashboard"))

    @app.get("/health")
    def health():
        return {"ok": True}, 200

    @app.get("/api/v1/ping")
    def ping():
        """Lightweight endpoint for load-balancer health checks."""
        return {"pong": True}, 200

    # Register CLI commands
    from lifeos.scripts.sync_calendars import register_commands

    register_commands(app)

    return app


def _register_blueprints(app: Flask) -> None:
    """Lazy import and register all controllers."""
    from lifeos.core.admin.controllers import admin_debug_bp
    from lifeos.core.auth.controllers import auth_bp  # local import to avoid circulars
    from lifeos.core.insights.controllers import insights_api_bp
    from lifeos.core.insights.pages import insights_pages_bp
    from lifeos.core.users.controllers import user_api_bp, user_pages_bp
    from lifeos.domains.calendar.controllers.calendar_api import calendar_api_bp
    from lifeos.domains.calendar.controllers.calendar_pages import calendar_pages_bp

    # Domain controllers (API + pages). Each module exposes *_bp variables.
    from lifeos.domains.finance.controllers.accounting_api import finance_api_bp
    from lifeos.domains.finance.controllers.dashboard_api import dashboard_api_bp
    from lifeos.domains.finance.controllers.forecast_api import forecast_api_bp
    from lifeos.domains.finance.controllers.import_api import import_api_bp
    from lifeos.domains.finance.controllers.journal_api import (
        journal_api_bp as finance_journal_api_bp,
    )
    from lifeos.domains.finance.controllers.pages import finance_pages_bp
    from lifeos.domains.finance.controllers.receivable_api import receivable_api_bp
    from lifeos.domains.finance.controllers.schedule_api import schedule_api_bp
    from lifeos.domains.finance.controllers.trial_balance_api import (
        trial_balance_api_bp,
    )
    from lifeos.domains.habits.controllers.habit_api import habit_api_bp
    from lifeos.domains.habits.controllers.habit_pages import habit_pages_bp
    from lifeos.domains.health.controllers.health_api import health_api_bp
    from lifeos.domains.health.controllers.health_pages import health_pages_bp
    from lifeos.domains.journal.controllers.journal_api import journal_api_bp
    from lifeos.domains.journal.controllers.journal_pages import journal_pages_bp
    from lifeos.domains.projects.controllers.project_api import project_api_bp
    from lifeos.domains.projects.controllers.project_pages import project_pages_bp
    from lifeos.domains.relationships.controllers.rel_api import rel_api_bp
    from lifeos.domains.relationships.controllers.rel_pages import rel_pages_bp
    from lifeos.domains.skills.controllers.skill_api import skill_api_bp
    from lifeos.domains.skills.controllers.skill_pages import skill_pages_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_api_bp, url_prefix="/api/users")
    app.register_blueprint(user_pages_bp, url_prefix="/users")

    app.register_blueprint(finance_api_bp, url_prefix="/api/finance")
    app.register_blueprint(trial_balance_api_bp, url_prefix="/api/finance")
    app.register_blueprint(schedule_api_bp, url_prefix="/api/finance")
    app.register_blueprint(finance_journal_api_bp, url_prefix="/api/finance")
    app.register_blueprint(receivable_api_bp, url_prefix="/api/finance")
    app.register_blueprint(forecast_api_bp, url_prefix="/api/finance")
    app.register_blueprint(dashboard_api_bp, url_prefix="/api/finance")
    app.register_blueprint(finance_pages_bp, url_prefix="/finance")
    app.register_blueprint(import_api_bp, url_prefix="/api/finance")
    app.register_blueprint(habit_api_bp, url_prefix="/api/habits")
    app.register_blueprint(habit_pages_bp, url_prefix="/habits")
    app.register_blueprint(skill_api_bp, url_prefix="/api/skills")
    app.register_blueprint(skill_pages_bp, url_prefix="/skills")
    app.register_blueprint(health_api_bp, url_prefix="/api/health")
    app.register_blueprint(health_pages_bp, url_prefix="/health")
    app.register_blueprint(journal_api_bp, url_prefix="/api/journal")
    app.register_blueprint(journal_pages_bp, url_prefix="/journal")
    app.register_blueprint(rel_api_bp, url_prefix="/api/relationships")
    app.register_blueprint(rel_pages_bp, url_prefix="/relationships")
    app.register_blueprint(project_api_bp, url_prefix="/api/projects")
    app.register_blueprint(project_pages_bp, url_prefix="/projects")
    app.register_blueprint(insights_api_bp, url_prefix="/api/insights")
    app.register_blueprint(insights_pages_bp, url_prefix="/insights")
    app.register_blueprint(calendar_api_bp, url_prefix="/api/calendar")
    app.register_blueprint(calendar_pages_bp, url_prefix="/calendar")

    # Admin/debug endpoints: register only in non-production or when debugging.
    env = (app.config.get("ENV") or "").lower()
    if env != "production" or app.debug:
        app.register_blueprint(admin_debug_bp)


def _register_error_handlers(app: Flask) -> None:
    """Basic JSON error responses."""
    from werkzeug.exceptions import HTTPException

    @app.errorhandler(HTTPException)
    def _http_error(exc: HTTPException):
        return {"ok": False, "error": exc.description}, exc.code

    @app.errorhandler(Exception)
    def _generic_error(exc: Exception):
        try:
            app.logger.exception("Unhandled error: %s", exc)
        except Exception:
            pass
        # In debug/testing, surface the exception message to speed up diagnosis
        if app.debug or app.testing:
            return {"ok": False, "error": str(exc)}, 500
        return {"ok": False, "error": "unexpected_error"}, 500


def _register_auth_handlers(app: Flask) -> None:
    """Login manager and template helpers."""
    login_manager.login_view = "auth_api.login"

    @login_manager.user_loader
    def _load_user(user_id: str):
        from lifeos.core.users.models import User

        return User.query.get(int(user_id)) if user_id else None

    @app.context_processor
    def inject_csrf_token():
        return {"csrf_token": generate_csrf_token}


# WSGI entrypoint compatibility
app = create_app()

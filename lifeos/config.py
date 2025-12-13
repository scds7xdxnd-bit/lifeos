"""Application configuration for LifeOS."""

from __future__ import annotations

import os
from datetime import timedelta
from typing import Dict, Type

from dotenv import load_dotenv
from sqlalchemy.engine.url import make_url

load_dotenv()


def _engine_options_from_uri(uri: str) -> dict:
    url = make_url(uri)
    # Always keep pool_pre_ping, vary connect_args by dialect.
    if url.get_backend_name() == "sqlite":
        return {
            "pool_pre_ping": True,
            "connect_args": {"detect_types": 0, "timeout": 30},
        }
    if url.get_backend_name() in {"postgresql", "postgres"}:
        timeout = int(os.environ.get("DB_CONNECT_TIMEOUT_SECONDS", "10"))
        return {"pool_pre_ping": True, "connect_args": {"connect_timeout": timeout}}
    return {"pool_pre_ping": True}


class BaseConfig:
    """Base configuration loaded for all environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///instance/lifeos.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = _engine_options_from_uri(SQLALCHEMY_DATABASE_URI)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() in ("1", "true", "yes")
    PERMANENT_SESSION_LIFETIME = int(os.environ.get("SESSION_TTL_SECONDS", "86400"))
    WTF_CSRF_ENABLED = True

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_SECURE = SESSION_COOKIE_SECURE
    JWT_COOKIE_SAMESITE = SESSION_COOKIE_SAMESITE
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.environ.get("JWT_ACCESS_MINUTES", "30")))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get("JWT_REFRESH_DAYS", "14")))

    RATELIMIT_DEFAULT = "200/hour"
    RATELIMIT_STORAGE_URI = os.environ.get("REDIS_URL", "memory://")
    RATELIMIT_ENABLED = os.environ.get("RATELIMIT_ENABLED", "true").lower() in (
        "1",
        "true",
        "yes",
    )

    STATIC_CACHE_MAX_AGE = int(os.environ.get("STATIC_CACHE_MAX_AGE", "3600"))
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH", str(10 * 1024 * 1024)))
    UPLOAD_ALLOWED_EXTENSIONS = set(
        (os.environ.get("UPLOAD_ALLOWED_EXTENSIONS") or "csv,png,jpg,jpeg,gif,pdf").split(",")
    )
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "instance/uploads")

    ENABLE_INSIGHTS = os.environ.get("ENABLE_INSIGHTS", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    ENABLE_ASSISTANT = os.environ.get("ENABLE_ASSISTANT", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    ENABLE_ML = os.environ.get("ENABLE_ML", "true").lower() in ("1", "true", "yes")
    MLSUGGESTER_MODEL_DIR = os.environ.get("MLSUGGESTER_MODEL_DIR", "flask_app")

    # Google Calendar OAuth
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.environ.get(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:5000/api/v1/calendar/oauth/google/callback",
    )
    GOOGLE_CALENDAR_SCOPES = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events.readonly",
    ]


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV = "development"


class TestingConfig(BaseConfig):
    TESTING = True
    # Use file-backed SQLite so Alembic migrations and app share the same DB.
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite:///instance/test.db")
    SQLALCHEMY_ENGINE_OPTIONS = _engine_options_from_uri(SQLALCHEMY_DATABASE_URI)
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_COOKIE_CSRF_PROTECT = False


class ProductionConfig(BaseConfig):
    ENV = "production"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"


config_by_name: Dict[str, Type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    # CI pipelines set APP_ENV=ci; map to testing defaults.
    "ci": TestingConfig,
}

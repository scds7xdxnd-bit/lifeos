"""Application configuration for LifeOS."""

from __future__ import annotations

import os
import socket
from datetime import timedelta
from typing import Dict, Type

from dotenv import load_dotenv
from sqlalchemy.engine.url import make_url

load_dotenv()


def _detect_lan_ip() -> str | None:
    """Best-effort LAN IP detection for local-device testing (e.g., phone on Wi-Fi)."""
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Does not send packets; used only to determine outbound interface.
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        if ip and ip != "127.0.0.1":
            return ip
    except OSError:
        return None
    finally:
        if sock is not None:
            sock.close()
    return None


def _build_dev_cors_origins() -> list[str]:
    """Build CORS origins for local frontend usage, including LAN testing on devices."""
    origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

    lan_ip = _detect_lan_ip()
    if lan_ip:
        origins.extend(
            [
                f"http://{lan_ip}:3000",
                f"http://{lan_ip}:3001",
            ]
        )

    extra = os.environ.get("CORS_ORIGINS", "")
    if extra.strip():
        origins.extend([item.strip() for item in extra.split(",") if item.strip()])

    # Preserve order while deduplicating.
    return list(dict.fromkeys(origins))


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
    BUILD_ID = (
        os.environ.get("LIFEOS_BUILD_ID")
        or os.environ.get("BUILD_ID")
        or os.environ.get("GIT_SHA")
        or os.environ.get("COMMIT_SHA")
        or "unknown"
    )
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///instance/lifeos.db").replace(
        "postgres://", "postgresql://", 1
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = _engine_options_from_uri(SQLALCHEMY_DATABASE_URI)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Session-cookie primary auth: cookie transport security is environment-scoped
    # via concrete config classes (dev/testing HTTP vs production HTTPS).
    SESSION_COOKIE_SECURE = False
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

    READ_CACHE_ENABLED = os.environ.get("READ_CACHE_ENABLED", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    READ_CACHE_DEFAULT_TTL_SECONDS = int(os.environ.get("READ_CACHE_DEFAULT_TTL_SECONDS", "30"))
    READ_CACHE_VERSION_TTL_SECONDS = int(os.environ.get("READ_CACHE_VERSION_TTL_SECONDS", "86400"))
    READ_CACHE_REDIS_URL = os.environ.get("READ_CACHE_REDIS_URL", os.environ.get("REDIS_URL", ""))

    STATIC_CACHE_MAX_AGE = int(os.environ.get("STATIC_CACHE_MAX_AGE", "3600"))
    SEND_FILE_MAX_AGE_DEFAULT = STATIC_CACHE_MAX_AGE
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

    ENABLE_PHASE5B_INSIGHTS = os.environ.get("ENABLE_PHASE5B_INSIGHTS", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    _phase5b_insight_types = [
        item.strip() for item in os.environ.get("PHASE5B_INSIGHT_TYPES", "").split(",") if item.strip()
    ]
    PHASE5B_INSIGHT_TYPES = _phase5b_insight_types or None
    ENABLE_PHASE6_FOCUSED_INQUIRY = os.environ.get("ENABLE_PHASE6_FOCUSED_INQUIRY", "false").lower() in (
        "1",
        "true",
        "yes",
    )
    ENABLE_PHASE8_CROSS_DOMAIN_PAIR_PROFILES = os.environ.get(
        "ENABLE_PHASE8_CROSS_DOMAIN_PAIR_PROFILES",
        "false",
    ).lower() in (
        "1",
        "true",
        "yes",
    )
    PHASE8_ENABLED_PAIR_PROFILES = (
        tuple(item.strip() for item in os.environ.get("PHASE8_ENABLED_PAIR_PROFILES", "").split(",") if item.strip())
        or None
    )
    ENABLE_PHASE9_TIMELINE_INTELLIGENCE = os.environ.get(
        "ENABLE_PHASE9_TIMELINE_INTELLIGENCE",
        "false",
    ).lower() in (
        "1",
        "true",
        "yes",
    )
    PHASE9_ENABLED_TIMELINE_PROFILES = (
        tuple(
            item.strip() for item in os.environ.get("PHASE9_ENABLED_TIMELINE_PROFILES", "").split(",") if item.strip()
        )
        or None
    )
    ENABLE_PHASE10_INQUIRY_HUMANIZATION = os.environ.get(
        "ENABLE_PHASE10_INQUIRY_HUMANIZATION",
        "false",
    ).lower() in (
        "1",
        "true",
        "yes",
    )
    PHASE6_INQUIRY_MIGRATION_HEAD = os.environ.get(
        "PHASE6_INQUIRY_MIGRATION_HEAD",
        "20260314_private_alpha_feedback_linkage",
    )
    ENABLE_PRIVATE_ALPHA = os.environ.get("ENABLE_PRIVATE_ALPHA", "false").lower() in (
        "1",
        "true",
        "yes",
    )
    ALPHA_INVITE_ONLY = os.environ.get("ALPHA_INVITE_ONLY", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    ALPHA_MAX_USERS = int(os.environ.get("ALPHA_MAX_USERS", "30"))
    ALPHA_VISIBLE_DOMAINS = tuple(
        item.strip().lower() for item in os.environ.get("ALPHA_VISIBLE_DOMAINS", "").split(",") if item.strip()
    )
    ALPHA_ENABLED_CROSS_DOMAIN_PAIR_PROFILES = tuple(
        item.strip()
        for item in os.environ.get("ALPHA_ENABLED_CROSS_DOMAIN_PAIR_PROFILES", "").split(",")
        if item.strip()
    )
    ALPHA_ENABLE_TECHNICAL_BRIEF = os.environ.get("ALPHA_ENABLE_TECHNICAL_BRIEF", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    ALPHA_ENABLE_HISTORY = os.environ.get("ALPHA_ENABLE_HISTORY", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    ALPHA_ENABLE_INQUIRY_FEEDBACK = os.environ.get("ALPHA_ENABLE_INQUIRY_FEEDBACK", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    ALPHA_HIDE_DOMAIN_CRUD = os.environ.get("ALPHA_HIDE_DOMAIN_CRUD", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    ALPHA_REQUIRE_DATA_READINESS = os.environ.get("ALPHA_REQUIRE_DATA_READINESS", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    ALPHA_ENABLE_CALENDAR_SYNC = os.environ.get("ALPHA_ENABLE_CALENDAR_SYNC", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    ALPHA_SUPPORT_CONTACT = os.environ.get("ALPHA_SUPPORT_CONTACT", "").strip()

    ENABLE_TIMELINE_INGESTION = os.environ.get("ENABLE_TIMELINE_INGESTION", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    PERSONALIZATION_ENABLED = os.environ.get("PERSONALIZATION_ENABLED", "false").lower() in (
        "1",
        "true",
        "yes",
    )
    ENABLE_INTERPRETATION_RELATIONSHIP = os.environ.get("ENABLE_INTERPRETATION_RELATIONSHIP", "true").lower() in (
        "1",
        "true",
        "yes",
    )
    ENABLE_INTERPRETATION_OBLIGATION = os.environ.get("ENABLE_INTERPRETATION_OBLIGATION", "false").lower() in (
        "1",
        "true",
        "yes",
    )

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
    TEMPLATES_AUTO_RELOAD = True
    SESSION_COOKIE_SECURE = False
    JWT_COOKIE_SECURE = False
    ENABLE_PHASE6_FOCUSED_INQUIRY = True
    ENABLE_PHASE8_CROSS_DOMAIN_PAIR_PROFILES = True
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]


class TestingConfig(BaseConfig):
    TESTING = True
    # Use file-backed SQLite so Alembic migrations and app share the same DB.
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", "sqlite:///instance/test.db")
    SQLALCHEMY_ENGINE_OPTIONS = _engine_options_from_uri(SQLALCHEMY_DATABASE_URI)
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    READ_CACHE_ENABLED = False
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_COOKIE_CSRF_PROTECT = False
    SESSION_COOKIE_SECURE = False
    JWT_COOKIE_SECURE = False
    ENABLE_PHASE6_FOCUSED_INQUIRY = True
    ENABLE_PHASE8_CROSS_DOMAIN_PAIR_PROFILES = True


class ProductionConfig(BaseConfig):
    ENV = "production"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"
    JWT_COOKIE_SECURE = True
    # Parse CORS origins from environment, default to allowing same-domain + localhost for dev
    _cors_env = os.environ.get(
        "CORS_ORIGINS", "https://lifeos-black-pond-2352.fly.dev,http://localhost:3000,http://localhost:3001"
    )
    CORS_ORIGINS = [o.strip() for o in _cors_env.split(",") if o.strip()]


class StagingConfig(ProductionConfig):
    ENV = "staging"


config_by_name: Dict[str, Type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "local-dev": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "staging": StagingConfig,
    # CI pipelines set APP_ENV=ci; map to testing defaults.
    "ci": TestingConfig,
}

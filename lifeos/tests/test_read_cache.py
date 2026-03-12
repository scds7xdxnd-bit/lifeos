from __future__ import annotations

import time

import pytest

from lifeos.core import read_cache as read_cache_module
from lifeos.core.read_cache import ReadCache, read_cache


pytestmark = pytest.mark.unit


def test_read_cache_get_set_and_bump(app):
    app.config["READ_CACHE_ENABLED"] = True
    app.config["READ_CACHE_DEFAULT_TTL_SECONDS"] = 60
    app.config["READ_CACHE_REDIS_URL"] = "memory://"
    read_cache.clear()

    scope = "calendar.views"
    user_id = 42
    key = {"view": "day", "date": "2030-01-01"}
    payload = {"ok": True, "events": []}

    assert read_cache.get(scope, user_id, key) is None
    read_cache.set(scope, user_id, key, payload)
    assert read_cache.get(scope, user_id, key) == payload

    read_cache.bump(scope, user_id)
    assert read_cache.get(scope, user_id, key) is None


def test_read_cache_expired_entry_is_evicted(app, monkeypatch):
    app.config["READ_CACHE_ENABLED"] = True
    app.config["READ_CACHE_DEFAULT_TTL_SECONDS"] = 1
    app.config["READ_CACHE_REDIS_URL"] = "memory://"
    read_cache.clear()

    base = time.time()
    monkeypatch.setattr(read_cache_module.time, "time", lambda: base)

    scope = "finance.reads"
    user_id = 7
    key = {"view": "dashboard"}
    read_cache.set(scope, user_id, key, {"ok": True}, ttl=1)

    monkeypatch.setattr(read_cache_module.time, "time", lambda: base + 2)
    assert read_cache.get(scope, user_id, key) is None


def test_read_cache_defaults_without_app_context(monkeypatch):
    class _DummyRedisModule:
        class Redis:
            @staticmethod
            def from_url(url, decode_responses=True):  # pragma: no cover - should not be called
                raise AssertionError("from_url should not be called for empty URL")

    cache = ReadCache()
    monkeypatch.setattr(read_cache_module, "redis", _DummyRedisModule)
    monkeypatch.delenv("REDIS_URL", raising=False)

    assert cache._enabled() is False
    assert cache._default_ttl() == 30
    assert cache._version_ttl() == 86400
    assert cache._redis_client() is None


def test_read_cache_redis_paths_with_fake_client(app, monkeypatch):
    class _FakeRedisClient:
        def __init__(self):
            self.store: dict[str, str] = {}

        def get(self, key):
            return self.store.get(key)

        def set(self, key, value, ex=None):
            self.store[key] = str(value)
            return True

        def setex(self, key, ttl, value):
            self.store[key] = str(value)
            return True

    class _FakeRedisModule:
        class Redis:
            calls = 0
            client = _FakeRedisClient()

            @classmethod
            def from_url(cls, url, decode_responses=True):
                cls.calls += 1
                return cls.client

    app.config["READ_CACHE_ENABLED"] = True
    app.config["READ_CACHE_REDIS_URL"] = "redis://cache.example:6379/0"

    monkeypatch.setattr(read_cache_module, "redis", _FakeRedisModule)

    cache = ReadCache()

    client1 = cache._redis_client()
    client2 = cache._redis_client()
    assert client1 is not None
    assert client1 is client2
    assert _FakeRedisModule.Redis.calls == 1

    scope = "calendar.views"
    user_id = 21
    key = {"view": "week", "date": "2032-01-01"}
    value = {"ok": True, "items": [1]}

    assert cache.get(scope, user_id, key) is None
    cache.set(scope, user_id, key, value, ttl=30)
    assert cache.get(scope, user_id, key) == value

    version1 = cache._current_version(scope, user_id)
    version2 = cache._current_version(scope, user_id)
    assert version1 == version2

    cache.bump(scope, user_id)
    version3 = cache._current_version(scope, user_id)
    assert version3 != version1


def test_read_cache_returns_none_when_redis_not_available(app, monkeypatch):
    app.config["READ_CACHE_ENABLED"] = True
    app.config["READ_CACHE_REDIS_URL"] = "redis://cache.example:6379/0"

    monkeypatch.setattr(read_cache_module, "redis", None)

    cache = ReadCache()
    assert cache._redis_client() is None

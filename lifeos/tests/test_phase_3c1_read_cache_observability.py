"""Phase 3c-1 read cache observability checks."""

from __future__ import annotations

import uuid

import pytest

from lifeos.core.observability.metrics import READ_CACHE_HITS_TOTAL, READ_CACHE_MISSES_TOTAL
from lifeos.core.read_cache import read_cache

pytestmark = pytest.mark.unit


def _counter_value(counter, scope: str) -> float:
    return counter.labels(scope=scope)._value.get()


def test_read_cache_records_hit_and_miss(app):
    app.config["READ_CACHE_ENABLED"] = True
    app.config["READ_CACHE_DEFAULT_TTL_SECONDS"] = 60
    app.config["READ_CACHE_REDIS_URL"] = "memory://"
    read_cache.clear()

    scope = f"calendar.views.{uuid.uuid4().hex}"
    user_id = 9
    key = {"view": "day", "date": "2031-01-01"}
    payload = {"ok": True, "events": []}

    miss_before = _counter_value(READ_CACHE_MISSES_TOTAL, scope)
    hit_before = _counter_value(READ_CACHE_HITS_TOTAL, scope)

    assert read_cache.get(scope, user_id, key) is None
    assert _counter_value(READ_CACHE_MISSES_TOTAL, scope) == miss_before + 1
    assert _counter_value(READ_CACHE_HITS_TOTAL, scope) == hit_before

    read_cache.set(scope, user_id, key, payload)
    assert read_cache.get(scope, user_id, key) == payload
    assert _counter_value(READ_CACHE_HITS_TOTAL, scope) == hit_before + 1

    read_cache.bump(scope, user_id)
    assert read_cache.get(scope, user_id, key) is None
    assert _counter_value(READ_CACHE_MISSES_TOTAL, scope) == miss_before + 2


def test_read_cache_disabled_no_metrics(app):
    app.config["READ_CACHE_ENABLED"] = False
    read_cache.clear()

    scope = f"finance.reads.{uuid.uuid4().hex}"
    user_id = 11
    key = {"view": "dashboard", "day": "2031-01-01"}
    payload = {"ok": True}

    miss_before = _counter_value(READ_CACHE_MISSES_TOTAL, scope)
    hit_before = _counter_value(READ_CACHE_HITS_TOTAL, scope)

    assert read_cache.get(scope, user_id, key) is None
    read_cache.set(scope, user_id, key, payload)
    read_cache.bump(scope, user_id)

    assert _counter_value(READ_CACHE_MISSES_TOTAL, scope) == miss_before
    assert _counter_value(READ_CACHE_HITS_TOTAL, scope) == hit_before

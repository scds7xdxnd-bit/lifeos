"""Phase 3c-1 read cache observability checks."""

from __future__ import annotations

import uuid

import pytest

from lifeos.core.observability.metrics import (
    CONTRACT_VIOLATIONS_TOTAL,
    EVENT_DISPATCH_LATENCY_SECONDS,
    HTTP_REQUEST_LATENCY_SECONDS,
    PROJECTION_CORRECTNESS_ERRORS_TOTAL,
    PROJECTION_CORRECTNESS_TOTAL,
    READ_CACHE_HITS_TOTAL,
    READ_CACHE_MISSES_TOTAL,
    REPLAY_DETERMINISM_FAILURES_TOTAL,
    record_contract_violation,
    record_event_dispatch_latency_seconds,
    record_http_request_latency_seconds,
    record_insight_latency_ms,
    record_projection_check,
    record_projection_error,
    record_replay_determinism_failure,
)
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


def test_observability_metric_recorders_cover_guard_paths():
    projection_before = PROJECTION_CORRECTNESS_TOTAL._value.get()
    projection_error_before = PROJECTION_CORRECTNESS_ERRORS_TOTAL._value.get()
    replay_before = REPLAY_DETERMINISM_FAILURES_TOTAL._value.get()
    contract_before = CONTRACT_VIOLATIONS_TOTAL._value.get()

    record_projection_check()
    record_projection_error()
    record_replay_determinism_failure()
    record_contract_violation()

    assert PROJECTION_CORRECTNESS_TOTAL._value.get() == projection_before + 1
    assert PROJECTION_CORRECTNESS_ERRORS_TOTAL._value.get() == projection_error_before + 1
    assert REPLAY_DETERMINISM_FAILURES_TOTAL._value.get() == replay_before + 1
    assert CONTRACT_VIOLATIONS_TOTAL._value.get() == contract_before + 1

    record_insight_latency_ms(None)
    record_insight_latency_ms(250.0)

    http_before = HTTP_REQUEST_LATENCY_SECONDS.labels(
        method="unknown",
        route="unknown",
        status_code="0",
    )._sum.get()
    record_http_request_latency_seconds(None, method="GET", route="/ping", status_code="200")
    record_http_request_latency_seconds(0.3, method="", route="", status_code="")
    assert (
        HTTP_REQUEST_LATENCY_SECONDS.labels(
            method="unknown",
            route="unknown",
            status_code="0",
        )._sum.get()
        >= http_before + 0.3
    )

    event_before = EVENT_DISPATCH_LATENCY_SECONDS._sum.get()
    record_event_dispatch_latency_seconds(None)
    record_event_dispatch_latency_seconds(0.02)
    assert EVENT_DISPATCH_LATENCY_SECONDS._sum.get() >= event_before + 0.02

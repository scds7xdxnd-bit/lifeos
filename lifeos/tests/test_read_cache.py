import pytest

from lifeos.core.read_cache import read_cache


pytestmark = pytest.mark.integration


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

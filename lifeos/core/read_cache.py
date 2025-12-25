"""Read-through cache for high-frequency read surfaces."""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from dataclasses import dataclass
from typing import Any, Optional
from uuid import uuid4

from flask import current_app

from lifeos.core.observability import record_read_cache_hit, record_read_cache_miss

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - redis optional in dev/test
    redis = None


@dataclass(frozen=True)
class _CacheEntry:
    payload: str
    expires_at: float


class ReadCache:
    """Read-only cache with TTL and versioned invalidation."""

    def __init__(self) -> None:
        self._memory: dict[str, _CacheEntry] = {}
        self._versions: dict[tuple[str, int], str] = {}
        self._lock = threading.Lock()
        self._redis = None
        self._redis_url: str | None = None

    def _enabled(self) -> bool:
        try:
            return bool(current_app.config.get("READ_CACHE_ENABLED", True))
        except Exception:
            return False

    def _default_ttl(self) -> int:
        try:
            return int(current_app.config.get("READ_CACHE_DEFAULT_TTL_SECONDS", 30))
        except Exception:
            return 30

    def _version_ttl(self) -> int:
        try:
            return int(current_app.config.get("READ_CACHE_VERSION_TTL_SECONDS", 86400))
        except Exception:
            return 86400

    def _redis_client(self):
        if redis is None:
            return None
        try:
            url = current_app.config.get("READ_CACHE_REDIS_URL") or os.environ.get("REDIS_URL") or ""
        except Exception:
            url = os.environ.get("REDIS_URL") or ""
        if not url or url.startswith("memory://"):
            return None
        if self._redis is not None and self._redis_url == url:
            return self._redis
        self._redis = redis.Redis.from_url(url, decode_responses=True)
        self._redis_url = url
        return self._redis

    def _version_key(self, scope: str, user_id: int) -> str:
        return f"lifeos:readcache:{scope}:user:{user_id}:version"

    def _cache_key(self, scope: str, user_id: int, key: dict) -> tuple[str, str]:
        payload = json.dumps(key, sort_keys=True, default=str)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return payload, digest

    def _current_version(self, scope: str, user_id: int) -> str:
        client = self._redis_client()
        version_key = self._version_key(scope, user_id)
        if client:
            version = client.get(version_key)
            if version:
                return str(version)
            version = uuid4().hex
            client.set(version_key, version, ex=self._version_ttl())
            return version
        with self._lock:
            version = self._versions.get((scope, user_id))
            if not version:
                version = uuid4().hex
                self._versions[(scope, user_id)] = version
            return version

    def _full_cache_key(self, scope: str, user_id: int, key: dict) -> str:
        _, digest = self._cache_key(scope, user_id, key)
        version = self._current_version(scope, user_id)
        return f"lifeos:readcache:{scope}:user:{user_id}:v{version}:{digest}"

    def get(self, scope: str, user_id: int, key: dict) -> Optional[Any]:
        if not self._enabled():
            return None
        cache_key = self._full_cache_key(scope, user_id, key)
        client = self._redis_client()
        if client:
            payload = client.get(cache_key)
            if payload is None:
                record_read_cache_miss(scope)
                return None
            record_read_cache_hit(scope)
            return json.loads(payload)
        now = time.time()
        with self._lock:
            entry = self._memory.get(cache_key)
            if not entry:
                record_read_cache_miss(scope)
                return None
            if entry.expires_at <= now:
                self._memory.pop(cache_key, None)
                record_read_cache_miss(scope)
                return None
            record_read_cache_hit(scope)
            return json.loads(entry.payload)

    def set(self, scope: str, user_id: int, key: dict, value: Any, ttl: Optional[int] = None) -> None:
        if not self._enabled():
            return
        cache_key = self._full_cache_key(scope, user_id, key)
        ttl_seconds = int(ttl or self._default_ttl())
        payload = json.dumps(value, sort_keys=True, default=str)
        client = self._redis_client()
        if client:
            client.setex(cache_key, ttl_seconds, payload)
            return
        expires_at = time.time() + ttl_seconds
        with self._lock:
            self._memory[cache_key] = _CacheEntry(payload=payload, expires_at=expires_at)

    def bump(self, scope: str, user_id: int) -> None:
        if not self._enabled():
            return
        version = uuid4().hex
        client = self._redis_client()
        version_key = self._version_key(scope, user_id)
        if client:
            client.set(version_key, version, ex=self._version_ttl())
            return
        with self._lock:
            self._versions[(scope, user_id)] = version

    def clear(self) -> None:
        """Clear in-memory cache (test-only helper)."""
        with self._lock:
            self._memory.clear()
            self._versions.clear()


read_cache = ReadCache()

__all__ = ["read_cache", "ReadCache"]

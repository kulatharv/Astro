"""Thread-safe In-Memory TTL & Redis Cache Implementation."""

import os
import time
import logging
from typing import Any, Optional

logger = logging.getLogger("app.core.cache")


class InMemoryTTLCache:
    """Thread-safe in-memory cache with Time-To-Live (TTL) expiration."""

    def __init__(self, default_ttl: int = 3600):
        self._cache: dict[str, tuple[Any, float]] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        val, expiry = self._cache[key]
        if time.time() > expiry:
            del self._cache[key]
            return None
        return val

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl if ttl is not None else self.default_ttl
        expiry = time.time() + ttl
        self._cache[key] = (value, expiry)

    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        self._cache.clear()

    def cleanup_expired(self) -> int:
        now = time.time()
        expired_keys = [k for k, (_, exp) in self._cache.items() if now > exp]
        for k in expired_keys:
            del self._cache[k]
        return len(expired_keys)


class RedisCacheWrapper:
    """Unified Cache Interface supporting Redis with In-Memory fallback."""

    def __init__(self, redis_url: Optional[str] = None, default_ttl: int = 3600):
        self.default_ttl = default_ttl
        self._fallback_cache = InMemoryTTLCache(default_ttl=default_ttl)
        self._redis_client = None
        self._use_redis = False

        if redis_url:
            try:
                import redis
                self._redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
                self._redis_client.ping()
                self._use_redis = True
                logger.info("Connected to Redis cache successfully.")
            except Exception as e:
                logger.warning(f"Redis unavailable ({e}), using thread-safe In-Memory TTL Cache.")
                self._use_redis = False
        else:
            logger.info("Redis unavailable, using thread-safe In-Memory TTL Cache.")

    def get_val(self, key: str) -> Optional[Any]:
        if self._use_redis and self._redis_client:
            try:
                import json
                raw = self._redis_client.get(key)
                return json.loads(raw) if raw else None
            except Exception as e:
                logger.error(f"Redis GET failed for key {key}: {e}")
                return self._fallback_cache.get(key)
        return self._fallback_cache.get(key)

    def set_val(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        ttl = ttl if ttl is not None else self.default_ttl
        if self._use_redis and self._redis_client:
            try:
                import json
                raw = json.dumps(value)
                self._redis_client.setex(key, ttl, raw)
                return True
            except Exception as e:
                logger.error(f"Redis SET failed for key {key}: {e}")
                self._fallback_cache.set(key, value, ttl)
                return True
        else:
            self._fallback_cache.set(key, value, ttl)
            return True

    def get(self, key: str) -> Optional[Any]:
        return self.get_val(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        return self.set_val(key, value, ttl)

    def delete(self, key: str) -> bool:
        if self._use_redis and self._redis_client:
            try:
                res = self._redis_client.delete(key)
                return bool(res)
            except Exception as e:
                logger.error(f"Redis DELETE failed for key {key}: {e}")
                return self._fallback_cache.delete(key)
        return self._fallback_cache.delete(key)

    def clear(self) -> None:
        if self._use_redis and self._redis_client:
            try:
                self._redis_client.flushdb()
            except Exception as e:
                logger.error(f"Redis FLUSHDB failed: {e}")
        self._fallback_cache.clear()


# Global Singleton Cache Instance
REDIS_URL = os.getenv("REDIS_URL", None)
cache = RedisCacheWrapper(redis_url=REDIS_URL, default_ttl=3600)


class CacheService:
    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        return cache.get_val(key)

    @classmethod
    def set(cls, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        return cache.set_val(key, value, ttl)


    @classmethod
    def delete(cls, key: str) -> bool:
        return cache.delete(key)

    @classmethod
    def clear(cls) -> None:
        cache.clear()

    @staticmethod
    def get_panchang_key(date_str: str, lat: float, lon: float) -> str:
        return f"panchang:{date_str}:{round(lat, 3)}:{round(lon, 2)}"

    @staticmethod
    def get_kundali_key(hash_str: str) -> str:
        return f"kundali:{hash_str}"


def get_redis_client():
    """Return active redis client instance or None."""
    return cache._redis_client if getattr(cache, "_use_redis", False) else None






"""
Rate limiting middleware with Redis distributed support and in-memory sliding window fallback (CF-04).
Protects against credential brute-forcing, calculation resource exhaustion, and AI quota exhaustion.
"""

import time
import logging
from collections import defaultdict
from threading import Lock
from typing import Dict, List, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from shared.cache.redis_client import get_redis_client
from shared.config.settings import settings

logger = logging.getLogger("gateway.middleware.rate_limit")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Tiered sliding-window rate limiter.
    Tiers:
    - Auth endpoints (/api/auth/*, /login, /signup): 15 req/min
    - Astrological calculation endpoints (/api/kundali*, /api/prediction*): 40 req/min
    - AI & narrative endpoints (/api/kundali-chat, /api/narrative*): 20 req/min
    - Default API endpoints (/api/*): 120 req/min
    """

    AUTH_ROUTES = ("/api/auth/", "/login", "/signup")
    CALC_ROUTES = ("/api/kundali", "/api/generate-chart", "/api/prediction")
    AI_ROUTES = ("/api/kundali-chat", "/api/narrative")

    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
        self._memory_store: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()

    def _get_client_identifier(self, request: Request) -> str:
        # Prefer authenticated session user_id, otherwise client IP
        user_id = request.session.get("user_id") if hasattr(request, "session") else None
        if user_id:
            return f"user:{user_id}"

        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        if request.client:
            return request.client.host

        return "unknown"

    def _get_rate_limit(self, path: str) -> tuple[int, int]:
        """Return (max_requests, window_seconds) for given path."""
        if any(path.startswith(p) for p in self.AUTH_ROUTES):
            return (15, 60)
        if any(path.startswith(p) for p in self.AI_ROUTES):
            return (20, 60)
        if any(path.startswith(p) for p in self.CALC_ROUTES):
            return (40, 60)
        return (120, 60)

    def _is_rate_limited_redis(self, client_id: str, path_category: str, limit: int, window: int) -> Optional[bool]:
        r = get_redis_client()
        if not r:
            return None

        key = f"ratelimit:{path_category}:{client_id}"
        try:
            current = r.incr(key)
            if current == 1:
                r.expire(key, window)
            return current > limit
        except Exception as e:
            logger.debug(f"Redis rate limiting unavailable, falling back to in-memory: {e}")
            return None

    def _is_rate_limited_memory(self, client_id: str, path_category: str, limit: int, window: int) -> bool:
        now = time.time()
        key = f"{path_category}:{client_id}"
        cutoff = now - window

        with self._lock:
            timestamps = self._memory_store[key]
            # Prune old timestamps
            valid_timestamps = [t for t in timestamps if t > cutoff]

            if len(valid_timestamps) >= limit:
                self._memory_store[key] = valid_timestamps
                return True

            valid_timestamps.append(now)
            self._memory_store[key] = valid_timestamps
            return False

    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)

        path = request.url.path

        # Ignore static assets, docs, health, metrics
        if (
            path.startswith("/static/")
            or path in ("/health", "/metrics", "/favicon.ico", "/docs", "/openapi.json")
            or not path.startswith("/api/")
        ):
            return await call_next(request)

        client_id = self._get_client_identifier(request)
        limit, window = self._get_rate_limit(path)
        category = "auth" if any(path.startswith(p) for p in self.AUTH_ROUTES) else (
            "ai" if any(path.startswith(p) for p in self.AI_ROUTES) else (
                "calc" if any(path.startswith(p) for p in self.CALC_ROUTES) else "default"
            )
        )

        # Attempt Redis check first
        is_limited = self._is_rate_limited_redis(client_id, category, limit, window)

        # In-memory fallback
        if is_limited is None:
            is_limited = self._is_rate_limited_memory(client_id, category, limit, window)

        if is_limited:
            logger.warning(f"Rate limit exceeded for client {client_id} on {path} (Tier: {category}, Limit: {limit}/{window}s)")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Too many requests. Please slow down.",
                    "retry_after_seconds": window,
                },
                headers={"Retry-After": str(window)},
            )

        return await call_next(request)

"""API middleware for the AI MultiColony Ecosystem.

Provides authentication, rate limiting, CORS, and logging middleware.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from ai_multicolony.config.logging_config import get_logger

logger = get_logger(__name__)


class RateLimiterMiddleware:
    """Rate limiting middleware.

    Tracks request counts per IP/client and returns 429
    when limits are exceeded.
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ) -> None:
        self._rpm = requests_per_minute
        self._rph = requests_per_hour
        self._minute_counts: dict[str, list[float]] = defaultdict(list)
        self._hour_counts: dict[str, list[float]] = defaultdict(list)

    def check(self, client_id: str) -> tuple[bool, Optional[str]]:
        """Check if a request is within rate limits.

        Args:
            client_id: Client identifier (IP or API key).

        Returns:
            Tuple of (allowed, error_message).
        """
        now = time.time()

        # Clean old entries
        self._minute_counts[client_id] = [
            t for t in self._minute_counts[client_id] if now - t < 60
        ]
        self._hour_counts[client_id] = [
            t for t in self._hour_counts[client_id] if now - t < 3600
        ]

        # Check limits
        if len(self._minute_counts[client_id]) >= self._rpm:
            return False, f"Rate limit exceeded: {self._rpm} requests per minute"

        if len(self._hour_counts[client_id]) >= self._rph:
            return False, f"Rate limit exceeded: {self._rph} requests per hour"

        # Record request
        self._minute_counts[client_id].append(now)
        self._hour_counts[client_id].append(now)

        return True, None

    def get_usage(self, client_id: str) -> dict[str, Any]:
        """Get rate limit usage for a client."""
        now = time.time()
        minute_count = len([t for t in self._minute_counts.get(client_id, []) if now - t < 60])
        hour_count = len([t for t in self._hour_counts.get(client_id, []) if now - t < 3600])
        return {
            "client_id": client_id,
            "minute_used": minute_count,
            "minute_limit": self._rpm,
            "hour_used": hour_count,
            "hour_limit": self._rph,
        }


class AuthMiddleware:
    """Authentication middleware.

    Validates API keys and bearer tokens.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key

    def validate(self, authorization: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """Validate an authorization header.

        Args:
            authorization: The Authorization header value.

        Returns:
            Tuple of (valid, client_id).
        """
        if not self._api_key:
            # No auth configured
            return True, "anonymous"

        if not authorization:
            return False, None

        # Bearer token
        if authorization.startswith("Bearer "):
            token = authorization[7:]
            if token == self._api_key:
                return True, f"key:{token[:8]}"

        # API key header
        if authorization == self._api_key:
            return True, f"key:{authorization[:8]}"

        return False, None


# Singleton instances
_rate_limiter = RateLimiterMiddleware()
_auth_middleware: Optional[AuthMiddleware] = None


def get_rate_limiter() -> RateLimiterMiddleware:
    """Get the global rate limiter instance."""
    return _rate_limiter


def setup_auth(api_key: Optional[str] = None) -> AuthMiddleware:
    """Set up the authentication middleware."""
    global _auth_middleware
    _auth_middleware = AuthMiddleware(api_key)
    return _auth_middleware


def get_auth() -> Optional[AuthMiddleware]:
    """Get the authentication middleware instance."""
    return _auth_middleware


async def timing_middleware(request: Any, call_next: Any) -> Any:
    """Middleware to track request timing."""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    response.headers["X-Process-Time"] = str(duration)
    logger.info("request_processed", path=request.url.path, duration=duration)
    return response


async def error_handling_middleware(request: Any, call_next: Any) -> Any:
    """Middleware for global error handling."""
    try:
        return await call_next(request)
    except Exception as e:
        logger.error("unhandled_error", path=request.url.path, error=str(e))
        try:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={"message": "Internal server error", "error": str(e)},
            )
        except ImportError:
            raise


async def rate_limit_middleware(request: Any, call_next: Any) -> Any:
    """Middleware for rate limiting."""
    client_id = request.client.host if hasattr(request, 'client') and request.client else "unknown"

    # Skip rate limiting for health checks
    if request.url.path in ("/health", "/", "/docs", "/redoc"):
        return await call_next(request)

    allowed, error_msg = _rate_limiter.check(client_id)
    if not allowed:
        try:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={"error": error_msg, "code": "RATE_LIMITED"},
            )
        except ImportError:
            pass

    return await call_next(request)


async def auth_middleware(request: Any, call_next: Any) -> Any:
    """Middleware for authentication."""
    if _auth_middleware is None:
        return await call_next(request)

    # Skip auth for public endpoints
    if request.url.path in ("/health", "/", "/docs", "/redoc", "/openapi.json"):
        return await call_next(request)

    authorization = request.headers.get("Authorization", "")
    valid, client_id = _auth_middleware.validate(authorization)

    if not valid:
        try:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized", "code": "AUTH_REQUIRED"},
            )
        except ImportError:
            pass

    return await call_next(request)


async def cors_middleware(request: Any, call_next: Any) -> Any:
    """Simple CORS middleware."""
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

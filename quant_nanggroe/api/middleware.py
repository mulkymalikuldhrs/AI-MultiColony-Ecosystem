"""API Middleware — Auth, CORS, rate limiting
=========================================="""

from __future__ import annotations

import logging
import os
import time
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Auth configuration — read dynamically from env so test overrides work
API_KEY_HEADER = "X-API-Key"


def _is_auth_required() -> bool:
    """Check if auth is required by reading env at runtime."""
    return os.environ.get("REQUIRE_AUTH", "true").lower() in ("true", "1", "yes")


def _get_valid_api_keys() -> set[str]:
    """Load valid API keys from environment variable."""
    keys_str = os.environ.get("QUANT_API_KEYS", "")
    if keys_str:
        return {k.strip() for k in keys_str.split(",") if k.strip()}
    return set()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware.

    Tracks requests per client IP address and enforces a maximum
    number of requests per minute. Uses an in-memory sliding window.
    """

    def __init__(self, app: Any, requests_per_minute: int = 60) -> None:
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Process request with rate limiting check.

        Args:
            request: Incoming HTTP request.
            call_next: Next middleware/handler in the chain.

        Returns:
            HTTP response or 429 if rate limit exceeded.
        """
        client_id = request.client.host if request.client else "unknown"
        now = time.time()

        if client_id not in self.requests:
            self.requests[client_id] = []

        # Clean old requests
        self.requests[client_id] = [t for t in self.requests[client_id] if now - t < 60]

        if len(self.requests[client_id]) >= self.requests_per_minute:
            return Response(content="Rate limit exceeded", status_code=429)

        self.requests[client_id].append(now)
        response = await call_next(request)
        return response


class AuthMiddleware(BaseHTTPMiddleware):
    """API key authentication middleware.

    When REQUIRE_AUTH=true (default), all requests must include a valid
    X-API-Key header matching one of the keys in QUANT_API_KEYS env var.

    Health check endpoints (/health, /) are always accessible.
    When REQUIRE_AUTH=false, auth is skipped (development only).
    """

    # Paths that never require authentication
    PUBLIC_PATHS = {"/health", "/", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Enforce API key authentication if enabled."""
        # Skip auth for public paths
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)

        if not _is_auth_required():
            return await call_next(request)

        api_key = request.headers.get(API_KEY_HEADER, "")
        valid_keys = _get_valid_api_keys()

        if not valid_keys:
            logger.warning(
                "SEC-001: REQUIRE_AUTH=true but no QUANT_API_KEYS set — "
                "denying requests. Set QUANT_API_KEYS or REQUIRE_AUTH=false"
            )
            # In development/testing without keys configured, allow through with warning
            # In production, this MUST be configured properly
            dev_mode = os.environ.get("QUANT_DEV_MODE", "false").lower() in ("true", "1", "yes")
            if dev_mode:
                logger.warning("SEC-003: Dev mode bypass — auth skipped (NEVER use in production!)")
                return await call_next(request)
            return Response(
                content="Authentication required but no API keys configured",
                status_code=503,
            )

        if api_key not in valid_keys:
            logger.warning(
                "SEC-002: Invalid API key from %s for %s",
                request.client.host if request.client else "?",
                request.url.path,
            )
            return Response(content="Unauthorized", status_code=401)

        return await call_next(request)

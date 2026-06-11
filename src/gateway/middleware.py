"""
Middleware Pipeline - Request/response processing pipeline.
Includes rate limiting, authentication, and logging middleware.
Port of Crucix API patterns to Python with Pydantic v2.
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.gateway.middleware")


class RequestContext(BaseModel):
    """Context for a request passing through the middleware pipeline."""
    method: str
    path: str
    headers: dict[str, str] = Field(default_factory=dict)
    params: dict[str, str] = Field(default_factory=dict)
    client_ip: str = "unknown"
    user_id: str | None = None
    extra: dict = Field(default_factory=dict)


class MiddlewareResult(BaseModel):
    """Result of middleware processing."""
    allowed: bool
    reason: str = ""
    status_code: int = 200
    headers: dict[str, str] = Field(default_factory=dict)


class Middleware(ABC):
    """Base class for middleware."""

    @abstractmethod
    def process(self, context: RequestContext) -> MiddlewareResult:
        """Process a request. Return MiddlewareResult with allowed=True to continue."""
        ...


class RateLimitMiddleware(Middleware):
    """Rate limiting middleware using sliding window algorithm."""

    def __init__(self, default_limit: int = 60, window_seconds: int = 60) -> None:
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def process(self, context: RequestContext) -> MiddlewareResult:
        """Check rate limit for the client."""
        key = context.client_ip
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests
        self._requests[key] = [t for t in self._requests[key] if t > window_start]

        if len(self._requests[key]) >= self.default_limit:
            return MiddlewareResult(
                allowed=False,
                reason="Rate limit exceeded",
                status_code=429,
                headers={"Retry-After": str(self.window_seconds)},
            )

        self._requests[key].append(now)
        remaining = self.default_limit - len(self._requests[key])

        return MiddlewareResult(
            allowed=True,
            headers={
                "X-RateLimit-Limit": str(self.default_limit),
                "X-RateLimit-Remaining": str(remaining),
            },
        )


class AuthMiddleware(Middleware):
    """Authentication middleware.

    Validates Bearer tokens and sets user_id in context.
    """

    def __init__(self, valid_tokens: dict[str, str] | None = None) -> None:
        """Initialize with token -> user_id mapping.

        Args:
            valid_tokens: Dict mapping token strings to user IDs.
        """
        self.valid_tokens = valid_tokens or {}

    def add_token(self, token: str, user_id: str) -> None:
        """Add a valid token."""
        self.valid_tokens[token] = user_id

    def process(self, context: RequestContext) -> MiddlewareResult:
        """Validate authentication."""
        auth_header = context.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return MiddlewareResult(
                allowed=False,
                reason="Missing or invalid Authorization header",
                status_code=401,
            )

        token = auth_header[7:]  # Strip "Bearer "
        user_id = self.valid_tokens.get(token)
        if not user_id:
            return MiddlewareResult(
                allowed=False,
                reason="Invalid token",
                status_code=401,
            )

        # Mutate context (Pydantic models are mutable by default)
        context.user_id = user_id
        return MiddlewareResult(allowed=True)


class LoggingMiddleware(Middleware):
    """Request logging middleware."""

    def __init__(self) -> None:
        self.request_log: list[dict] = []

    def process(self, context: RequestContext) -> MiddlewareResult:
        """Log the request."""
        entry = {
            "method": context.method,
            "path": context.path,
            "client_ip": context.client_ip,
            "user_id": context.user_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        self.request_log.append(entry)
        if len(self.request_log) > 1000:
            self.request_log = self.request_log[-500:]

        logger.info("%s %s from %s", context.method, context.path, context.client_ip)
        return MiddlewareResult(allowed=True)


class MiddlewarePipeline:
    """Pipeline for processing requests through multiple middleware."""

    def __init__(self) -> None:
        self.middlewares: list[Middleware] = []

    def add(self, middleware: Middleware) -> None:
        """Add middleware to the pipeline."""
        self.middlewares.append(middleware)

    def process(self, context: RequestContext) -> MiddlewareResult:
        """Process a request through all middleware.

        Returns the first denial or the final success.
        """
        combined_headers: dict[str, str] = {}

        for middleware in self.middlewares:
            result = middleware.process(context)
            combined_headers.update(result.headers)

            if not result.allowed:
                result.headers = combined_headers
                return result

        return MiddlewareResult(allowed=True, headers=combined_headers)

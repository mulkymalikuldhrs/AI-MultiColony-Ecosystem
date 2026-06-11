"""
API Router - Request routing with path matching and parameter extraction.
Port of Crucix API gateway patterns to Python with Pydantic v2.
"""

from __future__ import annotations

import re
import logging
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.gateway.router")


class HTTPMethod(str, Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"


class Route(BaseModel):
    """API route definition."""
    path: str
    method: HTTPMethod = HTTPMethod.GET
    handler_name: str
    description: str = ""
    auth_required: bool = False
    rate_limit: int | None = None  # requests per minute


class RouteMatch(BaseModel):
    """Result of a route match."""
    route: Route
    params: dict[str, str] = Field(default_factory=dict)


class APIRouter:
    """API request router with path parameter extraction.

    Supports:
    - Exact path matching
    - Path parameters (e.g., /users/{id})
    - Method-based routing
    - Route metadata (auth, rate limiting)
    """

    def __init__(self) -> None:
        self.routes: list[Route] = []

    def add_route(self, route: Route) -> None:
        """Add a route to the router."""
        self.routes.append(route)
        logger.debug("Added route: %s %s -> %s", route.method.value, route.path, route.handler_name)

    def add_routes(self, routes: list[Route]) -> None:
        """Add multiple routes."""
        for route in routes:
            self.add_route(route)

    def _path_to_regex(self, path: str) -> re.Pattern:
        """Convert a route path with {param} to a regex pattern."""
        # Replace {param} with named capture groups
        pattern = re.sub(r"\{(\w+)\}", r"(?P<\1>[^/]+)", path)
        return re.compile(f"^{pattern}$")

    def match(self, method: str, path: str) -> Optional[RouteMatch]:
        """Match a request to a route.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path

        Returns:
            RouteMatch if found, None otherwise.
        """
        for route in self.routes:
            if route.method.value != method.upper():
                continue

            regex = self._path_to_regex(route.path)
            match = regex.match(path)
            if match:
                return RouteMatch(
                    route=route,
                    params=match.groupdict(),
                )

        return None

    def list_routes(self) -> list[dict]:
        """List all registered routes."""
        return [
            {
                "path": r.path,
                "method": r.method.value,
                "handler": r.handler_name,
                "auth_required": r.auth_required,
                "rate_limit": r.rate_limit,
                "description": r.description,
            }
            for r in self.routes
        ]

    def get_routes_for_handler(self, handler_name: str) -> list[Route]:
        """Get all routes for a specific handler."""
        return [r for r in self.routes if r.handler_name == handler_name]

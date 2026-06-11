"""
API Gateway Module - Enhanced API patterns from Crucix.
Provides request routing, middleware pipeline, rate limiting, and localization support.
"""

from src.gateway.router import APIRouter, Route, RouteMatch
from src.gateway.middleware import MiddlewarePipeline, RateLimitMiddleware, AuthMiddleware, LoggingMiddleware
from src.gateway.localization import LocalizationManager

__all__ = [
    "APIRouter",
    "Route",
    "RouteMatch",
    "MiddlewarePipeline",
    "RateLimitMiddleware",
    "AuthMiddleware",
    "LoggingMiddleware",
    "LocalizationManager",
]

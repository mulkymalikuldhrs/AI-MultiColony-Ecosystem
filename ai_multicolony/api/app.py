"""FastAPI application factory for the AI MultiColony Ecosystem.

Creates and configures a FastAPI application with all routers,
middleware, and startup/shutdown lifecycle hooks.
"""

from __future__ import annotations

from typing import Any

from ai_multicolony.config.logging_config import get_logger
from ai_multicolony.config.settings import get_settings

logger = get_logger(__name__)


def create_app() -> Any:
    """Create and configure the FastAPI application.

    This is a factory function compatible with uvicorn's --factory flag:
        uvicorn ai_multicolony.api.app:create_app --factory

    Returns:
        Configured FastAPI application.
    """
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
    except ImportError:
        raise ImportError("FastAPI not installed. Install with: pip install fastapi uvicorn")

    settings = get_settings()
    settings.apply_to_env()

    app = FastAPI(
        title=settings.app_name,
        description="AI MultiColony Ecosystem - Colony-based Agent Operating System",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware
    from ai_multicolony.api.middleware import (
        timing_middleware,
        error_handling_middleware,
        rate_limit_middleware,
        auth_middleware,
    )
    from ai_multicolony.api.middleware import setup_auth

    app.middleware("http")(timing_middleware)
    app.middleware("http")(error_handling_middleware)
    app.middleware("http")(rate_limit_middleware)
    app.middleware("http")(auth_middleware)

    # Setup auth
    setup_auth(settings.api.api_key)

    # Import and include routers
    from ai_multicolony.api.routes.agents import create_router as agents_router
    from ai_multicolony.api.routes.colony import create_router as colony_router
    from ai_multicolony.api.routes.tools import create_router as tools_router
    from ai_multicolony.api.routes.memory import create_router as memory_router
    from ai_multicolony.api.routes.ws import create_router as ws_router

    app.include_router(agents_router(), prefix="/api/agents", tags=["agents"])
    app.include_router(colony_router(), prefix="/api/colony", tags=["colony"])
    app.include_router(tools_router(), prefix="/api/tools", tags=["tools"])
    app.include_router(memory_router(), prefix="/api/memory", tags=["memory"])
    app.include_router(ws_router(), prefix="/api/ws", tags=["websocket"])

    @app.on_event("startup")
    async def startup() -> None:
        """Initialize services on startup."""
        from ai_multicolony.core.event_bus import EventBus

        bus = EventBus.get_instance()
        await bus.start()
        logger.info("api_startup", env=settings.app_env)

    @app.on_event("shutdown")
    async def shutdown() -> None:
        """Clean up services on shutdown."""
        from ai_multicolony.core.event_bus import EventBus

        bus = EventBus.get_instance()
        await bus.stop()
        logger.info("api_shutdown")

    @app.get("/health")
    async def health() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "ok", "version": "0.1.0"}

    @app.get("/")
    async def root() -> dict[str, str]:
        """Root endpoint with API info."""
        return {
            "name": settings.app_name,
            "version": "0.1.0",
            "environment": settings.app_env,
            "docs": "/docs",
        }

    return app

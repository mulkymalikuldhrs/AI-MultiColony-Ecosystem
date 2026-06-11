"""FastAPI Application — Main API server
=======================================
Lifespan events, router inclusion, CORS, auth middleware, health check endpoint.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from quant_nanggroe.config import get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan — startup and shutdown events."""
    settings = get_settings()

    # ── Startup ─────────────────────────────────────────────────────
    # Initialize shared engine singletons eagerly so import errors
    # surface immediately rather than on the first request.
    try:
        from quant_nanggroe.services import init_all_services
        init_all_services(app)
        logger.info("startup_services_initialized")
    except Exception as exc:
        logger.warning(
            "startup_services_unavailable",
            extra={"error": str(exc), "msg": "Services not available — running without persistence"},
        )

    logger.info("startup_complete", extra={"app": settings.app_name, "env": "development"})

    yield

    # ── Shutdown ────────────────────────────────────────────────────
    logger.info("shutdown_complete")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI instance
    """
    import os

    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="Agentic Trading Intelligence OS",
        version="1.0.0",
        lifespan=lifespan,
    )

    # ── CORS Middleware (SEC-016) ────────────────────────────────────
    cors_env = os.environ.get("CORS_ORIGINS", "")
    if cors_env:
        allowed_origins = [o.strip() for o in cors_env.split(",") if o.strip()]
        if allowed_origins == ["*"]:
            logger.warning(
                "CORS_ORIGINS=['*'] with credentials is insecure — "
                "use specific origins in production"
            )
    else:
        allowed_origins = ["http://localhost:3000", "http://localhost:8000"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Include Routers ─────────────────────────────────────────────
    from quant_nanggroe.api.routes import market, trading, agents, backtest, portfolio, ws

    app.include_router(market.router, prefix="/api/market", tags=["Market"])
    app.include_router(trading.router, prefix="/api/trading", tags=["Trading"])
    app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
    app.include_router(backtest.router, prefix="/api/backtest", tags=["Backtest"])
    app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
    app.include_router(ws.router, prefix="/api/ws", tags=["WebSocket"])

    # ── Health Check ────────────────────────────────────────────────
    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "healthy", "service": "quant-nanggroe-ai"}

    # ── Global Exception Handler ────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "unhandled_exception",
            extra={
                "method": request.method,
                "path": str(request.url),
                "error_type": type(exc).__name__,
                "error": str(exc),
            },
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "type": type(exc).__name__},
        )

    return app

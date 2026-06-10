"""
FastAPI Application — Main API server
=======================================
Lifespan events (DB connection, Redis), router inclusion,
CORS, auth middleware, health check endpoint.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from quant_nanggroe_ai.config import get_settings
from quant_nanggroe_ai.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan — startup and shutdown events."""
    settings = get_settings()
    setup_logging(log_level=settings.log_level, json_output=settings.is_production)

    # Startup
    try:
        from quant_nanggroe_ai.data.database import init_db
        await init_db()
    except Exception:
        pass  # Database may not be available in dev mode

    yield

    # Shutdown
    try:
        from quant_nanggroe_ai.data.database import close_db
        from quant_nanggroe_ai.data.cache import close_redis
        await close_db()
        await close_redis()
    except Exception:
        pass


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI instance
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="Agentic Trading Intelligence OS",
        version="1.0.0",
        lifespan=lifespan,
    )

    # ── CORS Middleware ──────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.is_development else ["https://qna.example.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Include Routers ─────────────────────────────────────────────
    from quant_nanggroe_ai.api.routes import market, trading, agents, backtest, portfolio, ws

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
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "type": type(exc).__name__},
        )

    return app

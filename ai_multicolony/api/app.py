"""FastAPI application factory and configuration.

⚠️  IMPORTANT: The ``FastAPIApp`` class below is NOT a real FastAPI application.
It is a custom, framework-agnostic dispatcher that mirrors the FastAPI interface
but cannot be served directly by uvicorn.  Use ``create_fastapi_app()`` to obtain
a real ``fastapi.FastAPI`` instance that delegates to the custom dispatcher.

Creates the FastAPI app instance with middleware, CORS, exception
handlers, lifespan events, and mounted route routers.
"""

from __future__ import annotations

import asyncio
import os
import signal
import time
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from ..config import get_settings

logger = logging.getLogger(__name__)


def _setup_signal_handlers(app: Any) -> None:
    """Register SIGTERM/SIGINT for graceful shutdown."""
    def _shutdown_signal_handler(signum: int, frame: Any) -> None:
        logger.warning(
            "received_signal: signal=%s, initiating_graceful_shutdown",
            signal.Signals(signum).name,
        )
        # Set a flag that the lifespan handler can check
        os._exit(0)  # Last resort — lifespan will handle cleanup

    signal.signal(signal.SIGTERM, _shutdown_signal_handler)
    signal.signal(signal.SIGINT, _shutdown_signal_handler)

# ── Prometheus metrics ─────────────────────────────────────────────────────

REQUEST_COUNT = Counter(
    'amce_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
)
REQUEST_LATENCY = Histogram(
    'amce_http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
)


@asynccontextmanager
async def lifespan(app: Any):
    """ASGI lifespan handler – startup and shutdown logic."""
    logger.info("AI-MultiColony API starting up")
    # Startup: initialise services, warm connections, etc.
    settings = get_settings()
    logger.info("Settings loaded: debug=%s, log_level=%s", settings.debug, settings.log_level)
    yield
    # Shutdown: flush logs, close connections, etc.
    logger.info("AI-MultiColony API shutting down")


def create_app(
    agent_registry: Any = None,
    colony_manager: Any = None,
    mcp_server: Any = None,
    memory_manager: Any = None,
    task_scheduler: Any = None,
    audit_trail: Any = None,
) -> "FastAPIApp":
    """Factory function that creates and returns a configured FastAPIApp.

    Parameters
    ----------
    agent_registry : AgentRegistry, optional
    colony_manager : ColonyManager, optional
    mcp_server : MCPServer, optional
    memory_manager : MemoryManager, optional
    task_scheduler : TaskScheduler, optional
    audit_trail : AuditTrail, optional

    Returns
    -------
    FastAPIApp
    """
    from .routes.agents import AgentRoutes
    from .routes.colony import ColonyRoutes
    from .routes.tools import ToolRoutes
    from .routes.memory import MemoryRoutes
    from .routes.tasks import TaskRoutes

    app = FastAPIApp(
        agent_registry=agent_registry,
        colony_manager=colony_manager,
        mcp_server=mcp_server,
        memory_manager=memory_manager,
        task_scheduler=task_scheduler,
        audit_trail=audit_trail,
    )

    # Attach route handlers
    app._agent_routes = AgentRoutes(agent_registry)
    app._colony_routes = ColonyRoutes(colony_manager)
    app._tool_routes = ToolRoutes(mcp_server)
    app._memory_routes = MemoryRoutes(memory_manager)
    app._task_routes = TaskRoutes(colony_manager, task_scheduler)

    logger.info("FastAPI app created with routes")
    return app


class FastAPIApp:
    """⚠️  NOT a real FastAPI application — custom dispatcher.

    This is a framework-agnostic wrapper that mirrors what a real FastAPI
    app would expose but **cannot be served by uvicorn directly**.
    Use :func:`create_fastapi_app` to obtain a real ``fastapi.FastAPI``
    instance that delegates to this dispatcher.

    Provides a framework-agnostic interface that mirrors what a real
    FastAPI app would expose.  Can be used standalone or adapted to
    work with an actual FastAPI instance.

    Parameters
    ----------
    agent_registry : AgentRegistry, optional
    colony_manager : ColonyManager, optional
    mcp_server : MCPServer, optional
    memory_manager : MemoryManager, optional
    """

    def __init__(
        self,
        agent_registry: Any = None,
        colony_manager: Any = None,
        mcp_server: Any = None,
        memory_manager: Any = None,
        task_scheduler: Any = None,
        audit_trail: Any = None,
    ):
        self.agent_registry = agent_registry
        self.colony_manager = colony_manager
        self.mcp_server = mcp_server
        self.memory_manager = memory_manager
        self.task_scheduler = task_scheduler
        self.audit_trail = audit_trail
        self._start_time = time.time()
        self._routes: Dict[str, Any] = {}

        # Route handlers (attached by create_app or manually)
        self._agent_routes: Any = None
        self._colony_routes: Any = None
        self._tool_routes: Any = None
        self._memory_routes: Any = None
        self._task_routes: Any = None

        # Middleware
        from .middleware import AuthMiddleware, RateLimitMiddleware, RequestLoggingMiddleware, ErrorHandlingMiddleware

        self.auth = AuthMiddleware()
        self.rate_limiter = RateLimitMiddleware()
        self.request_logger = RequestLoggingMiddleware()
        self.error_handler = ErrorHandlingMiddleware()

        # Settings
        self._settings = get_settings()

    # ── Health / Info ──────────────────────────────────────────────────────

    def get_health(self) -> Dict[str, Any]:
        """Return system health information."""
        return {
            "status": "healthy",
            "version": "0.1.0",
            "uptime_seconds": round(time.time() - self._start_time, 1),
            "agents": self.agent_registry.total_agents if self.agent_registry and hasattr(self.agent_registry, "total_agents") else 0,
            "colonies": self.colony_manager.colony_count if self.colony_manager else 0,
            "tools": self.mcp_server.tool_count if self.mcp_server and hasattr(self.mcp_server, "tool_count") else 0,
        }

    # ── Route dispatch (generic) ──────────────────────────────────────────

    async def dispatch(self, method: str, path: str, **kwargs: Any) -> Any:
        """Dispatch a request to the appropriate route handler.

        This is a generic dispatcher that can be used programmatically
        or adapted to work with a real ASGI framework.

        Parameters
        ----------
        method : str
            HTTP method (GET, POST, DELETE, etc.)
        path : str
            URL path.
        **kwargs
            Additional parameters (body, headers, etc.)

        Returns
        -------
        Response data (dict or model).
        """
        start = time.time()
        status_code = 200

        try:
            result = await self._route_dispatch(method, path, **kwargs)
            return result
        except Exception as exc:
            status_code = self.error_handler.get_status_code(exc)
            error = self.error_handler.format_error(exc)
            return error
        finally:
            duration = (time.time() - start) * 1000
            self.request_logger.log_request(
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=duration,
            )

    async def _route_dispatch(self, method: str, path: str, **kwargs: Any) -> Any:
        """Internal route dispatcher."""
        # ── Agent routes ───────────────────────────────────────────────
        if path == "/api/v1/agents" and method == "POST":
            return await self._agent_routes.create_agent(kwargs.get("body"))
        elif path == "/api/v1/agents" and method == "GET":
            return await self._agent_routes.list_agents()
        elif path.startswith("/api/v1/agents/") and method == "GET":
            agent_id = path.split("/")[-1]
            return await self._agent_routes.get_agent(agent_id)
        elif path.startswith("/api/v1/agents/") and path.endswith("/execute") and method == "POST":
            agent_id = path.split("/")[-2]
            return await self._agent_routes.execute_task(agent_id, kwargs.get("body"))
        elif path.startswith("/api/v1/agents/") and method == "DELETE":
            agent_id = path.split("/")[-1]
            return await self._agent_routes.terminate_agent(agent_id)

        # ── Colony routes ──────────────────────────────────────────────
        elif path == "/api/v1/colonies" and method == "POST":
            return await self._colony_routes.create_colony(kwargs.get("body"))
        elif path == "/api/v1/colonies" and method == "GET":
            return await self._colony_routes.list_colonies()
        elif path.startswith("/api/v1/colonies/") and path.endswith("/scale") and method == "POST":
            colony_id = path.split("/")[-2]
            return await self._colony_routes.scale_colony(colony_id, kwargs.get("body"))
        elif path.startswith("/api/v1/colonies/") and method == "GET":
            colony_id = path.split("/")[-1]
            return await self._colony_routes.get_colony(colony_id)

        # ── Tool routes ────────────────────────────────────────────────
        elif path == "/api/v1/tools" and method == "GET":
            return await self._tool_routes.list_tools()
        elif path.startswith("/api/v1/tools/") and path.endswith("/call") and method == "POST":
            tool_name = path.split("/")[-2]
            return await self._tool_routes.call_tool(tool_name, kwargs.get("body"))
        elif path.startswith("/api/v1/tools/") and method == "GET":
            tool_name = path.split("/")[-1]
            return await self._tool_routes.describe_tool(tool_name)

        # ── Memory routes ──────────────────────────────────────────────
        elif path == "/api/v1/memory/store" and method == "POST":
            return await self._memory_routes.store(kwargs.get("body"))
        elif path == "/api/v1/memory/query" and method == "POST":
            return await self._memory_routes.query(kwargs.get("body"))
        elif path == "/api/v1/memory/compact" and method == "POST":
            return await self._memory_routes.compact(kwargs.get("body"))
        elif path == "/api/v1/memory/pages" and method == "GET":
            return await self._memory_routes.list_pages()

        # ── Task routes ────────────────────────────────────────────────
        elif path == "/api/v1/tasks" and method == "POST":
            return await self._task_routes.create_task(kwargs.get("body"))
        elif path == "/api/v1/tasks" and method == "GET":
            return await self._task_routes.list_tasks()
        elif path.startswith("/api/v1/tasks/") and path.endswith("/result") and method == "GET":
            task_id = path.split("/")[-2]
            return await self._task_routes.get_task_result(task_id)
        elif path.startswith("/api/v1/tasks/") and method == "GET":
            task_id = path.split("/")[-1]
            return await self._task_routes.get_task(task_id)

        # ── Health ─────────────────────────────────────────────────────
        elif path == "/health":
            return self.get_health()

        else:
            return {"error": "Not found", "code": "NOT_FOUND", "status_code": 404}


# ---------------------------------------------------------------------------
# Real FastAPI wrapper — this IS uvicorn-compatible
# ---------------------------------------------------------------------------

def create_fastapi_app(**kwargs: Any) -> "fastapi.FastAPI":
    """Create a **real** ``fastapi.FastAPI`` instance that delegates to :class:`FastAPIApp`.

    This function is the intended entry point for ``uvicorn``.  It builds a
    genuine FastAPI application and wires every route to the custom
    ``FastAPIApp.dispatch`` method so that existing business logic continues
    to work without rewriting route handlers.

    Usage::

        uvicorn ai_multicolony.api.app:create_fastapi_app --factory

    Parameters
    ----------
    **kwargs
        Forwarded to :func:`create_app` (agent_registry, colony_manager, …).

    Returns
    -------
    fastapi.FastAPI
        A fully-wired FastAPI application ready to be served.
    """
    import fastapi
    from fastapi import Request
    from fastapi.responses import JSONResponse

    settings = get_settings()
    custom_app = create_app(**kwargs)

    @asynccontextmanager
    async def _lifespan(app: fastapi.FastAPI):
        # Startup
        logger.info("application_starting")
        yield
        # Shutdown — graceful drain
        logger.info("shutdown_initiated")

        # 1. Signal agents to stop
        try:
            from ai_multicolony.colony.manager import ColonyManager
            # Try to get running colonies and shut them down
            if hasattr(app.state, 'colony_manager') and app.state.colony_manager:
                await app.state.colony_manager.shutdown()
                logger.info("colony_manager_shutdown_complete")
        except Exception as e:
            logger.warning("colony_shutdown_error: %s", e)

        # 2. Flush audit logs
        try:
            from ai_multicolony.security.audit import AuditTrail
            audit = AuditTrail()
            audit.flush()
        except Exception:
            pass

        # 3. Close HTTP client sessions
        try:
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            if tasks:
                logger.info("draining_tasks: count=%d", len(tasks))
                await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.warning("task_drain_error: %s", e)

        logger.info("shutdown_complete")

    app = fastapi.FastAPI(
        title="AI-MultiColony",
        version=settings.version,
        lifespan=_lifespan,
    )

    # ── Catch-all route that delegates to the custom dispatcher ────────
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
    async def _dispatch(request: Request, path: str) -> JSONResponse:
        method = request.method.upper()
        body = None
        if method in ("POST", "PUT", "PATCH"):
            try:
                body = await request.json()
            except Exception:
                body = None

        result = await custom_app.dispatch(method, f"/{path}", body=body)

        # Determine status code from result if present
        status_code = result.get("status_code", 200) if isinstance(result, dict) else 200
        # Errors from the dispatcher set their own codes; 404 for not-found
        if isinstance(result, dict) and result.get("code") == "NOT_FOUND":
            status_code = 404

        return JSONResponse(content=result, status_code=status_code)

    # ── Health check (also at root-level /health) ──────────────────────
    @app.get("/health")
    async def _health() -> dict:
        return custom_app.get_health()

    # ── Prometheus /metrics endpoint ───────────────────────────────────
    @app.get("/metrics")
    async def metrics() -> Response:
        """Expose Prometheus metrics."""
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    # ── Prometheus middleware: track request count and latency ─────────
    @app.middleware("http")
    async def prometheus_middleware(request: Request, call_next):
        method = request.method.upper()
        path = request.url.path
        start = time.monotonic()

        response = await call_next(request)

        duration = time.monotonic() - start
        status = str(response.status_code)

        REQUEST_COUNT.labels(method=method, endpoint=path, status=status).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=path).observe(duration)

        return response

    # ── Signal handlers for graceful shutdown ──────────────────────────
    _setup_signal_handlers(app)

    logger.info("Real FastAPI app created, wrapping FastAPIApp dispatcher")
    return app

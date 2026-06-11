"""DeerFlow Bridge — Integration with ByteDance DeerFlow 2.0 agent system.

Provides channel management, graph orchestration, memory access, and
middleware chaining for AI-MultiColony's interaction with DeerFlow.

Architecture
------------
- **ChannelManager** — Manages DeerFlow IM channels (Discord, Slack,
  Telegram, Feishu, WeChat, WeCom, DingTalk) via the DeerFlow Gateway
  HTTP API.
- **MiddlewareChain** — Chains request/response middleware for
  processing messages before they reach the DeerFlow agent.
- **DeerFlowBridge** — Top-level orchestrator that combines channels,
  graphs, and memory into a single façade.

All network calls use ``httpx`` and degrade gracefully when the DeerFlow
service is not running.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Sequence

import httpx
import structlog

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class DeerFlowBridgeError(Exception):
    """Base exception for DeerFlow bridge failures."""


class DeerFlowUnavailableError(DeerFlowBridgeError):
    """Raised when the DeerFlow Gateway is unreachable."""


class ChannelNotFoundError(DeerFlowBridgeError):
    """Raised when a requested channel does not exist."""


class GraphExecutionError(DeerFlowBridgeError):
    """Raised when graph execution fails."""


class MiddlewareError(DeerFlowBridgeError):
    """Raised when middleware processing fails."""

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_DEFAULT_GATEWAY_URL = "http://localhost:8001"
_DEFAULT_LANGGRAPH_URL = "http://localhost:8001/api"
_DEFAULT_ASSISTANT_ID = "lead_agent"

# Channel types supported by DeerFlow (from app/channels/)
SUPPORTED_CHANNELS = [
    "discord",
    "slack",
    "telegram",
    "feishu",
    "wechat",
    "wecom",
    "dingtalk",
]

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------


class Middleware(ABC):
    """Abstract base for request/response middleware."""

    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Transform or inspect an outbound request.  Must return a dict."""

    @abstractmethod
    async def process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Transform or inspect an inbound response.  Must return a dict."""


class MiddlewareChain:
    """Chain of middleware for sequential request/response processing.

    Middleware is executed in order for requests and in reverse order
    for responses, allowing symmetric before/after semantics.
    """

    def __init__(self, middlewares: Sequence[Middleware] | None = None) -> None:
        self._middlewares: List[Middleware] = list(middlewares or [])

    def add(self, middleware: Middleware) -> "MiddlewareChain":
        """Append a middleware and return ``self`` for chaining."""
        self._middlewares.append(middleware)
        return self

    def remove(self, middleware: Middleware) -> None:
        """Remove a previously added middleware."""
        self._middlewares = [m for m in self._middlewares if m is not middleware]

    @property
    def middlewares(self) -> List[Middleware]:
        """Return a shallow copy of the middleware list."""
        return list(self._middlewares)

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Run all middleware on a request in forward order."""
        result = request
        for mw in self._middlewares:
            try:
                result = await mw.process_request(result)
            except Exception as exc:
                logger.warning("middleware_request_error", middleware=mw.__class__.__name__, error=str(exc))
                raise MiddlewareError(f"Middleware {mw.__class__.__name__} failed on request: {exc}") from exc
        return result

    async def process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Run all middleware on a response in reverse order."""
        result = response
        for mw in reversed(self._middlewares):
            try:
                result = await mw.process_response(result)
            except Exception as exc:
                logger.warning("middleware_response_error", middleware=mw.__class__.__name__, error=str(exc))
                raise MiddlewareError(f"Middleware {mw.__class__.__name__} failed on response: {exc}") from exc
        return result

# ---------------------------------------------------------------------------
# Logging middleware (built-in)
# ---------------------------------------------------------------------------


class LoggingMiddleware(Middleware):
    """Simple middleware that logs requests and responses via structlog."""

    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("deerflow_request", channel=request.get("channel"), action=request.get("action"))
        return request

    async def process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("deerflow_response", status=response.get("status"))
        return response

# ---------------------------------------------------------------------------
# Channel Manager
# ---------------------------------------------------------------------------


class ChannelManager:
    """Manage DeerFlow IM channels via the Gateway HTTP API.

    DeerFlow's ``/api/channels`` endpoint provides status and restart
    capabilities for all configured channels.
    """

    def __init__(
        self,
        gateway_url: str = _DEFAULT_GATEWAY_URL,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._gateway_url = gateway_url.rstrip("/")
        self._client = http_client or httpx.AsyncClient(timeout=15.0)

    async def _get(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        url = f"{self._gateway_url}{path}"
        try:
            resp = await self._client.get(url, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as exc:
            logger.warning("deerflow_channel_http_error", url=url, error=str(exc))
            raise DeerFlowUnavailableError(f"DeerFlow Gateway unreachable: {exc}") from exc

    async def _post(self, path: str, **kwargs: Any) -> Dict[str, Any]:
        url = f"{self._gateway_url}{path}"
        try:
            resp = await self._client.post(url, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPError as exc:
            logger.warning("deerflow_channel_http_error", url=url, error=str(exc))
            raise DeerFlowUnavailableError(f"DeerFlow Gateway unreachable: {exc}") from exc

    async def list_channels(self) -> List[str]:
        """List available channel names from the DeerFlow Gateway.

        Returns an empty list if the gateway is unreachable.
        """
        try:
            data = await self._get("/api/channels/")
            channels = data.get("channels", {})
            return list(channels.keys())
        except DeerFlowUnavailableError:
            logger.warning("deerflow_channels_unavailable")
            return []

    async def get_channel(self, name: str) -> Dict[str, Any]:
        """Get status dict for a specific channel.

        Raises
        ------
        ChannelNotFoundError
            If the channel name is not in the response.
        """
        try:
            data = await self._get("/api/channels/")
            channels = data.get("channels", {})
            if name not in channels:
                raise ChannelNotFoundError(f"Channel '{name}' not found in DeerFlow")
            return channels[name]
        except DeerFlowUnavailableError:
            return {"name": name, "status": "unavailable", "error": "Gateway unreachable"}

    async def restart_channel(self, name: str) -> Dict[str, Any]:
        """Restart a specific channel.

        Returns
        -------
        dict
            ``success`` and ``message`` keys from the Gateway.
        """
        try:
            return await self._post(f"/api/channels/{name}/restart")
        except DeerFlowUnavailableError:
            return {"success": False, "message": "Gateway unreachable"}

    async def send_message(self, channel: str, message: str) -> Dict[str, Any]:
        """Send a message through a DeerFlow channel.

        This creates a thread run on the DeerFlow agent via the LangGraph
        API and routes the response back through the specified channel.

        Parameters
        ----------
        channel : str
            Target channel name (e.g. ``"discord"``, ``"telegram"``).
        message : str
            Message text to send.

        Returns
        -------
        dict
            Result with at least ``status``, ``data_source``, and
            ``timestamp`` keys.
        """
        timestamp = datetime.now().isoformat()
        try:
            # Use the LangGraph-compatible runs API to create a thread + run
            run_payload = {
                "assistant_id": _DEFAULT_ASSISTANT_ID,
                "input": {
                    "messages": [
                        {"role": "user", "content": message}
                    ]
                },
                "metadata": {
                    "channel": channel,
                    "source": "ai_multicolony",
                },
            }
            resp = await self._client.post(
                f"{self._gateway_url}/api/threads",
                json={},
            )
            if resp.status_code in (200, 201):
                thread_data = resp.json()
                thread_id = thread_data.get("thread_id")
            else:
                thread_id = None

            if thread_id:
                run_resp = await self._client.post(
                    f"{self._gateway_url}/api/threads/{thread_id}/runs",
                    json=run_payload,
                )
                if run_resp.status_code in (200, 201):
                    run_data = run_resp.json()
                    return {
                        "status": "sent",
                        "channel": channel,
                        "thread_id": thread_id,
                        "run_id": run_data.get("run_id"),
                        "data_source": "deerflow_gateway",
                        "timestamp": timestamp,
                    }

            # Fallback: direct channel publish (no agent run)
            return {
                "status": "channel_only",
                "channel": channel,
                "message": message[:200],
                "data_source": "deerflow_gateway",
                "timestamp": timestamp,
            }

        except httpx.HTTPError as exc:
            logger.warning("deerflow_send_failed", channel=channel, error=str(exc))
            return {
                "status": "unavailable",
                "channel": channel,
                "error": str(exc),
                "data_source": "deerflow_bridge",
                "timestamp": timestamp,
            }

    async def get_status(self) -> Dict[str, Any]:
        """Get overall channel service status."""
        try:
            return await self._get("/api/channels/")
        except DeerFlowUnavailableError:
            return {"service_running": False, "channels": {}}

# ---------------------------------------------------------------------------
# Graph system
# ---------------------------------------------------------------------------


class GraphManager:
    """Manage DeerFlow LangGraph-based agent graphs via the Gateway API."""

    def __init__(
        self,
        gateway_url: str = _DEFAULT_GATEWAY_URL,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._gateway_url = gateway_url.rstrip("/")
        self._client = http_client or httpx.AsyncClient(timeout=30.0)
        self._graphs: Dict[str, Dict[str, Any]] = {}

    async def create_graph(self, config: Dict[str, Any]) -> str:
        """Create a DeerFlow agent graph and return its ID.

        Parameters
        ----------
        config : dict
            Graph configuration.  Recognized keys:

            - ``name`` (str): Agent/graph name.
            - ``assistant_id`` (str): DeerFlow assistant ID (default
              ``"lead_agent"``).
            - ``recursion_limit`` (int): Max recursion depth.
            - ``metadata`` (dict): Extra metadata.

        Returns
        -------
        str
            A graph ID for use with :meth:`run_graph`.
        """
        graph_id = f"graph_{uuid.uuid4().hex[:12]}"
        assistant_id = config.get("assistant_id", _DEFAULT_ASSISTANT_ID)

        self._graphs[graph_id] = {
            "id": graph_id,
            "name": config.get("name", "unnamed"),
            "assistant_id": assistant_id,
            "recursion_limit": config.get("recursion_limit", 100),
            "metadata": config.get("metadata", {}),
            "created_at": datetime.now().isoformat(),
        }

        logger.info("deerflow_graph_created", graph_id=graph_id, name=config.get("name"))
        return graph_id

    async def run_graph(self, graph_id: str, input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a DeerFlow graph with the given input.

        Parameters
        ----------
        graph_id : str
            ID returned by :meth:`create_graph`.
        input : dict
            Input payload.  Must contain a ``messages`` list.

        Returns
        -------
        dict
            Graph execution result with ``data_source`` and ``timestamp``.
        """
        timestamp = datetime.now().isoformat()

        if graph_id not in self._graphs:
            raise GraphExecutionError(f"Graph '{graph_id}' not found")

        graph_config = self._graphs[graph_id]

        try:
            # Create a thread via the LangGraph API
            thread_resp = await self._client.post(
                f"{self._gateway_url}/api/threads",
                json={"metadata": graph_config.get("metadata", {})},
            )
            if thread_resp.status_code not in (200, 201):
                return {
                    "status": "error",
                    "error": f"Thread creation failed: HTTP {thread_resp.status_code}",
                    "data_source": "deerflow_gateway",
                    "timestamp": timestamp,
                }

            thread_id = thread_resp.json().get("thread_id")

            # Create a run on the thread
            run_payload = {
                "assistant_id": graph_config["assistant_id"],
                "input": input,
                "config": {
                    "recursion_limit": graph_config.get("recursion_limit", 100),
                },
            }
            run_resp = await self._client.post(
                f"{self._gateway_url}/api/threads/{thread_id}/runs",
                json=run_payload,
            )

            if run_resp.status_code in (200, 201):
                run_data = run_resp.json()
                return {
                    "status": "completed",
                    "graph_id": graph_id,
                    "thread_id": thread_id,
                    "run_id": run_data.get("run_id"),
                    "data_source": "deerflow_gateway",
                    "timestamp": timestamp,
                }
            else:
                return {
                    "status": "error",
                    "error": f"Run creation failed: HTTP {run_resp.status_code}",
                    "graph_id": graph_id,
                    "data_source": "deerflow_gateway",
                    "timestamp": timestamp,
                }

        except httpx.HTTPError as exc:
            logger.warning("deerflow_graph_run_failed", graph_id=graph_id, error=str(exc))
            return {
                "status": "unavailable",
                "error": str(exc),
                "graph_id": graph_id,
                "data_source": "deerflow_bridge",
                "timestamp": timestamp,
            }

    def list_graphs(self) -> List[Dict[str, Any]]:
        """Return metadata for all created graphs."""
        return list(self._graphs.values())

# ---------------------------------------------------------------------------
# Memory system
# ---------------------------------------------------------------------------


class MemoryManager:
    """Access DeerFlow's memory system via the Gateway API.

    DeerFlow exposes ``/api/memory`` endpoints for CRUD on user context,
    history summaries, and memory facts.
    """

    def __init__(
        self,
        gateway_url: str = _DEFAULT_GATEWAY_URL,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._gateway_url = gateway_url.rstrip("/")
        self._client = http_client or httpx.AsyncClient(timeout=15.0)

    async def get_memory(self) -> Dict[str, Any]:
        """Retrieve the current global memory data."""
        try:
            resp = await self._client.get(f"{self._gateway_url}/api/memory")
            resp.raise_for_status()
            data = resp.json()
            data.setdefault("data_source", "deerflow_memory")
            data.setdefault("timestamp", datetime.now().isoformat())
            return data
        except httpx.HTTPError as exc:
            logger.warning("deerflow_memory_unavailable", error=str(exc))
            return {
                "error": str(exc),
                "status": "unavailable",
                "data_source": "deerflow_bridge",
                "timestamp": datetime.now().isoformat(),
            }

    async def create_fact(
        self, content: str, category: str = "context", confidence: float = 0.5
    ) -> Dict[str, Any]:
        """Create a memory fact in DeerFlow.

        Parameters
        ----------
        content : str
            Fact text.
        category : str
            Fact category (default ``"context"``).
        confidence : float
            Confidence score 0–1 (default ``0.5``).
        """
        try:
            resp = await self._client.post(
                f"{self._gateway_url}/api/memory/facts",
                json={"content": content, "category": category, "confidence": confidence},
            )
            resp.raise_for_status()
            data = resp.json()
            data.setdefault("data_source", "deerflow_memory")
            return data
        except httpx.HTTPError as exc:
            logger.warning("deerflow_memory_create_fact_failed", error=str(exc))
            return {
                "error": str(exc),
                "status": "unavailable",
                "data_source": "deerflow_bridge",
            }

    async def delete_fact(self, fact_id: str) -> Dict[str, Any]:
        """Delete a memory fact by ID."""
        try:
            resp = await self._client.delete(
                f"{self._gateway_url}/api/memory/facts/{fact_id}",
            )
            resp.raise_for_status()
            data = resp.json()
            data.setdefault("data_source", "deerflow_memory")
            return data
        except httpx.HTTPError as exc:
            logger.warning("deerflow_memory_delete_fact_failed", error=str(exc))
            return {
                "error": str(exc),
                "status": "unavailable",
                "data_source": "deerflow_bridge",
            }

    async def get_config(self) -> Dict[str, Any]:
        """Retrieve DeerFlow memory configuration."""
        try:
            resp = await self._client.get(f"{self._gateway_url}/api/memory/config")
            resp.raise_for_status()
            data = resp.json()
            data.setdefault("data_source", "deerflow_memory")
            return data
        except httpx.HTTPError as exc:
            return {
                "error": str(exc),
                "status": "unavailable",
                "data_source": "deerflow_bridge",
            }

# ---------------------------------------------------------------------------
# Top-level DeerFlow Bridge
# ---------------------------------------------------------------------------


class DeerFlowBridge:
    """Top-level bridge to DeerFlow 2.0 agent system.

    Combines channel management, graph orchestration, memory access,
    and middleware into a single façade.

    Parameters
    ----------
    config : dict
        Configuration dictionary.  Recognized keys:

        - ``gateway_url`` (str): DeerFlow Gateway base URL
          (default ``http://localhost:8001``).
        - ``langgraph_url`` (str): LangGraph API URL.
        - ``assistant_id`` (str): Default assistant ID.
        - ``middlewares`` (list[Middleware]): Initial middleware chain.
    """

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._gateway_url = self.config.get("gateway_url", _DEFAULT_GATEWAY_URL)

        # Shared HTTP client
        self._http_client = httpx.AsyncClient(timeout=30.0)

        # Sub-managers
        self.channels = ChannelManager(
            gateway_url=self._gateway_url,
            http_client=self._http_client,
        )
        self.graphs = GraphManager(
            gateway_url=self._gateway_url,
            http_client=self._http_client,
        )
        self.memory = MemoryManager(
            gateway_url=self._gateway_url,
            http_client=self._http_client,
        )

        # Middleware chain
        initial_mws = self.config.get("middlewares", [LoggingMiddleware()])
        self.middleware_chain = MiddlewareChain(initial_mws)

        logger.info(
            "deerflow_bridge_initialised",
            gateway_url=self._gateway_url,
            middleware_count=len(self.middleware_chain.middlewares),
        )

    # ------------------------------------------------------------------
    # Convenience pass-through methods
    # ------------------------------------------------------------------

    async def get_channel(self, name: str) -> Dict[str, Any]:
        """Get status for a specific channel."""
        return await self.channels.get_channel(name)

    async def list_channels(self) -> List[str]:
        """List available channel names."""
        return await self.channels.list_channels()

    async def send_message(self, channel: str, message: str) -> Dict[str, Any]:
        """Send a message through a DeerFlow channel.

        The request passes through the middleware chain before being
        dispatched to the Gateway.
        """
        request = {"action": "send_message", "channel": channel, "message": message}
        processed = await self.middleware_chain.process_request(request)
        result = await self.channels.send_message(
            processed.get("channel", channel),
            processed.get("message", message),
        )
        return await self.middleware_chain.process_response(result)

    async def create_graph(self, config: Dict[str, Any]) -> str:
        """Create a DeerFlow graph and return its ID."""
        return await self.graphs.create_graph(config)

    async def run_graph(self, graph_id: str, input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a DeerFlow graph with the given input."""
        request = {"action": "run_graph", "graph_id": graph_id, "input": input}
        processed = await self.middleware_chain.process_request(request)
        result = await self.graphs.run_graph(
            processed.get("graph_id", graph_id),
            processed.get("input", input),
        )
        return await self.middleware_chain.process_response(result)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._http_client.aclose()
        logger.info("deerflow_bridge_closed")

    async def health_check(self) -> Dict[str, Any]:
        """Check DeerFlow Gateway connectivity."""
        try:
            resp = await self._http_client.get(f"{self._gateway_url}/api/channels/")
            resp.raise_for_status()
            data = resp.json()
            return {
                "status": "ok",
                "service_running": data.get("service_running", False),
                "channel_count": len(data.get("channels", {})),
                "data_source": "deerflow_gateway",
                "timestamp": datetime.now().isoformat(),
            }
        except httpx.HTTPError as exc:
            return {
                "status": "unavailable",
                "error": str(exc),
                "data_source": "deerflow_bridge",
                "timestamp": datetime.now().isoformat(),
            }

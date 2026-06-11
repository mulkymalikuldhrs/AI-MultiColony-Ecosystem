"""MCP JSON-RPC server implementation.

Provides a full MCP server with stdio + SSE transport, tool registration,
permission engine, rate limiting, circuit breaker, and audit logging.
"""

from __future__ import annotations

import asyncio
import json
import time
from collections import defaultdict
from typing import Any, Callable, Optional

from ai_multicolony.config.logging_config import get_logger
from ai_multicolony.mcp.protocol import (
    CircuitState,
    MCPErrorCode,
    MCPMethod,
    MCPNotification,
    MCPRequest,
    MCPResponse,
    MCPServerInfo,
    PermissionLevel,
    PromptDefinition,
    RateLimitEntry,
    ResourceDefinition,
    ToolDefinition,
)

logger = get_logger(__name__)


class CircuitBreaker:
    """Circuit breaker for tool execution.

    Prevents cascading failures by opening the circuit after
    consecutive failures and allowing periodic retry attempts.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 1,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._half_open_max_calls = half_open_max_calls
        self._circuits: dict[str, dict[str, Any]] = {}

    def _get_circuit(self, tool_name: str) -> dict[str, Any]:
        """Get or create circuit state for a tool."""
        if tool_name not in self._circuits:
            self._circuits[tool_name] = {
                "state": CircuitState.CLOSED,
                "failure_count": 0,
                "last_failure_time": 0.0,
                "half_open_calls": 0,
            }
        return self._circuits[tool_name]

    def can_execute(self, tool_name: str) -> bool:
        """Check if the circuit allows execution."""
        circuit = self._get_circuit(tool_name)
        state = circuit["state"]

        if state == CircuitState.CLOSED:
            return True
        elif state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if time.time() - circuit["last_failure_time"] >= self._recovery_timeout:
                circuit["state"] = CircuitState.HALF_OPEN
                circuit["half_open_calls"] = 1
                return True
            return False
        elif state == CircuitState.HALF_OPEN:
            if circuit["half_open_calls"] < self._half_open_max_calls:
                circuit["half_open_calls"] += 1
                return True
            return False
        return True

    def record_success(self, tool_name: str) -> None:
        """Record a successful execution."""
        circuit = self._get_circuit(tool_name)
        circuit["failure_count"] = 0
        circuit["state"] = CircuitState.CLOSED
        circuit["half_open_calls"] = 0

    def record_failure(self, tool_name: str) -> None:
        """Record a failed execution."""
        circuit = self._get_circuit(tool_name)
        circuit["failure_count"] += 1
        circuit["last_failure_time"] = time.time()

        if circuit["state"] == CircuitState.HALF_OPEN:
            circuit["state"] = CircuitState.OPEN
        elif circuit["failure_count"] >= self._failure_threshold:
            circuit["state"] = CircuitState.OPEN
            logger.warning("circuit_breaker_opened", tool_name=tool_name)

    def get_state(self, tool_name: str) -> CircuitState:
        """Get the current circuit state."""
        return self._get_circuit(tool_name)["state"]

    def reset(self, tool_name: Optional[str] = None) -> None:
        """Reset circuit breaker state."""
        if tool_name:
            self._circuits.pop(tool_name, None)
        else:
            self._circuits.clear()


class RateLimiter:
    """Sliding window rate limiter for MCP tool calls.

    Tracks request counts per agent/tool combination using
    a fixed-window algorithm with configurable limits.
    """

    def __init__(self, default_rpm: int = 60) -> None:
        self._default_rpm = default_rpm
        self._limits: dict[str, int] = {}  # tool_name -> rpm
        self._windows: dict[str, RateLimitEntry] = {}

    def set_limit(self, tool_name: str, rpm: int) -> None:
        """Set a custom rate limit for a tool."""
        self._limits[tool_name] = rpm

    def check(self, agent_id: str, tool_name: str) -> bool:
        """Check if a request is within rate limits.

        Returns:
            True if the request is allowed, False if rate limited.
        """
        key = f"{agent_id}:{tool_name}"
        rpm = self._limits.get(tool_name, self._default_rpm)
        now = time.time()

        if key not in self._windows:
            self._windows[key] = RateLimitEntry(
                agent_id=agent_id,
                tool_name=tool_name,
                request_count=1,
                window_start=now,
            )
            return True

        entry = self._windows[key]

        # Reset window if expired
        if now - entry.window_start >= entry.window_seconds:
            entry.request_count = 1
            entry.window_start = now
            return True

        # Check limit
        if entry.request_count >= rpm:
            return False

        entry.request_count += 1
        return True

    def get_usage(self, agent_id: str, tool_name: str) -> dict[str, Any]:
        """Get rate limit usage for an agent/tool combination."""
        key = f"{agent_id}:{tool_name}"
        rpm = self._limits.get(tool_name, self._default_rpm)
        entry = self._windows.get(key)

        if not entry:
            return {"used": 0, "limit": rpm, "remaining": rpm}

        return {
            "used": entry.request_count,
            "limit": rpm,
            "remaining": max(0, rpm - entry.request_count),
            "window_reset": entry.window_start + entry.window_seconds,
        }


class AuditLogger:
    """Audit logger for MCP operations.

    Records all tool calls, permission checks, and system events
    for compliance and debugging purposes.
    """

    def __init__(self, max_entries: int = 10000) -> None:
        self._entries: list[dict[str, Any]] = []
        self._max_entries = max_entries

    def log(
        self,
        action: str,
        agent_id: str = "",
        tool_name: str = "",
        resource_uri: str = "",
        result: str = "",
        error: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Record an audit entry."""
        entry = {
            "timestamp": time.time(),
            "action": action,
            "agent_id": agent_id,
            "tool_name": tool_name,
            "resource_uri": resource_uri,
            "result": result,
            "error": error,
            "metadata": metadata or {},
        }
        self._entries.append(entry)
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]

    def query(
        self,
        agent_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        action: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query audit entries with optional filters."""
        results = self._entries
        if agent_id:
            results = [e for e in results if e["agent_id"] == agent_id]
        if tool_name:
            results = [e for e in results if e["tool_name"] == tool_name]
        if action:
            results = [e for e in results if e["action"] == action]
        if start_time:
            results = [e for e in results if e["timestamp"] >= start_time]
        if end_time:
            results = [e for e in results if e["timestamp"] <= end_time]
        return results[-limit:]


class MCPServer:
    """MCP JSON-RPC Server with full transport and safety features.

    Features:
    - Register tools, resources, and prompts with rich definitions
    - Permission-based access control per tool/resource
    - Rate limiting per agent/tool
    - Circuit breaker for fault tolerance
    - Audit logging for compliance
    - stdio and SSE transport support
    - FastAPI integration
    """

    def __init__(
        self,
        name: str = "ai-multicolony-mcp",
        version: str = "0.1.0",
        default_rate_limit: int = 60,
        circuit_failure_threshold: int = 5,
        circuit_recovery_timeout: float = 60.0,
    ) -> None:
        self._name = name
        self._version = version
        self._tools: dict[str, ToolDefinition] = {}
        self._tool_handlers: dict[str, Callable] = {}
        self._resources: dict[str, ResourceDefinition] = {}
        self._resource_handlers: dict[str, Callable] = {}
        self._prompts: dict[str, PromptDefinition] = {}
        self._prompt_handlers: dict[str, Callable] = {}
        self._subscriptions: dict[str, set[str]] = defaultdict(set)  # uri -> set of agent_ids
        self._initialized = False

        # Safety features
        self._rate_limiter = RateLimiter(default_rpm=default_rate_limit)
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_failure_threshold,
            recovery_timeout=circuit_recovery_timeout,
        )
        self._audit = AuditLogger()
        self._permissions: dict[str, PermissionLevel] = {}  # agent_id -> max permission

    # === Registration ===

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: Callable,
        required_permission: PermissionLevel = PermissionLevel.EXECUTE,
        rate_limit: Optional[int] = None,
        timeout: int = 30,
        category: str = "general",
    ) -> None:
        """Register a tool with the MCP server.

        Args:
            name: Tool name.
            description: Tool description.
            input_schema: JSON Schema for input parameters.
            handler: Async callable to handle tool calls.
            required_permission: Minimum permission level to use this tool.
            rate_limit: Optional requests per minute limit.
            timeout: Execution timeout in seconds.
            category: Tool category for organization.
        """
        self._tools[name] = ToolDefinition(
            name=name,
            description=description,
            input_schema=input_schema,
            required_permission=required_permission,
            rate_limit=rate_limit,
            timeout=timeout,
            category=category,
        )
        self._tool_handlers[name] = handler
        if rate_limit:
            self._rate_limiter.set_limit(name, rate_limit)

    def register_resource(
        self,
        uri: str,
        name: str,
        description: str = "",
        mime_type: str = "text/plain",
        handler: Optional[Callable] = None,
        required_permission: PermissionLevel = PermissionLevel.READ,
        subscribable: bool = False,
    ) -> None:
        """Register a resource with the MCP server.

        Args:
            uri: Resource URI.
            name: Resource name.
            description: Resource description.
            mime_type: MIME type.
            handler: Optional async callable to read the resource.
            required_permission: Minimum permission level.
            subscribable: Whether clients can subscribe to updates.
        """
        self._resources[uri] = ResourceDefinition(
            uri=uri,
            name=name,
            description=description,
            mime_type=mime_type,
            required_permission=required_permission,
            subscribable=subscribable,
        )
        if handler:
            self._resource_handlers[uri] = handler

    def register_prompt(
        self,
        name: str,
        description: str = "",
        arguments: Optional[list[dict[str, Any]]] = None,
        handler: Optional[Callable] = None,
        required_permission: PermissionLevel = PermissionLevel.READ,
        category: str = "general",
    ) -> None:
        """Register a prompt template with the MCP server.

        Args:
            name: Prompt name.
            description: Prompt description.
            arguments: List of argument definitions.
            handler: Optional async callable to render the prompt.
            required_permission: Minimum permission level.
            category: Prompt category.
        """
        self._prompts[name] = PromptDefinition(
            name=name,
            description=description,
            arguments=arguments or [],
            required_permission=required_permission,
            category=category,
        )
        if handler:
            self._prompt_handlers[name] = handler

    # === Permission Management ===

    def set_agent_permission(self, agent_id: str, level: PermissionLevel) -> None:
        """Set the permission level for an agent."""
        self._permissions[agent_id] = level

    def _check_permission(self, agent_id: str, required: PermissionLevel) -> bool:
        """Check if an agent has sufficient permissions."""
        agent_level = self._permissions.get(agent_id, PermissionLevel.NONE)
        return agent_level.gte(required)

    # === Request Handling ===

    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle an incoming MCP JSON-RPC request.

        Args:
            request: The MCP request.

        Returns:
            MCP response.
        """
        self._audit.log(
            action="request_received",
            agent_id=request.params.get("_agent_id", ""),
            metadata={"method": request.method, "id": str(request.id)},
        )

        try:
            method = request.method

            if method == MCPMethod.INITIALIZE:
                return self._handle_initialize(request)
            elif method == MCPMethod.LIST_TOOLS:
                return self._handle_list_tools(request)
            elif method == MCPMethod.CALL_TOOL:
                return await self._handle_call_tool(request)
            elif method == MCPMethod.LIST_RESOURCES:
                return self._handle_list_resources(request)
            elif method == MCPMethod.READ_RESOURCE:
                return await self._handle_read_resource(request)
            elif method == MCPMethod.SUBSCRIBE_RESOURCE:
                return self._handle_subscribe(request)
            elif method == MCPMethod.UNSUBSCRIBE_RESOURCE:
                return self._handle_unsubscribe(request)
            elif method == MCPMethod.LIST_PROMPTS:
                return self._handle_list_prompts(request)
            elif method == MCPMethod.GET_PROMPT:
                return await self._handle_get_prompt(request)
            else:
                return MCPResponse.from_error(
                    request.id, MCPErrorCode.METHOD_NOT_FOUND,
                    f"Method not found: {method}",
                )
        except Exception as e:
            logger.error("mcp_request_error", method=request.method, error=str(e))
            self._audit.log(
                action="request_error",
                metadata={"method": request.method, "error": str(e)},
            )
            return MCPResponse.from_error(
                request.id, MCPErrorCode.INTERNAL_ERROR,
                f"Internal error: {e}",
            )

    def _handle_initialize(self, request: MCPRequest) -> MCPResponse:
        """Handle initialize request."""
        self._initialized = True
        info = MCPServerInfo(name=self._name, version=self._version)
        self._audit.log(action="initialized")
        return MCPResponse(id=request.id, result=info.model_dump())

    def _handle_list_tools(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/list request."""
        agent_id = request.params.get("_agent_id", "")
        tools = []
        for t in self._tools.values():
            if self._check_permission(agent_id, t.required_permission):
                tools.append(t.model_dump())
        return MCPResponse(id=request.id, result={"tools": tools})

    async def _handle_call_tool(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/call request with rate limiting, circuit breaker, and permissions."""
        tool_name = request.params.get("name", "")
        arguments = request.params.get("arguments", {})
        agent_id = request.params.get("_agent_id", "")

        # Check tool exists
        if tool_name not in self._tools:
            return MCPResponse.from_error(
                request.id, MCPErrorCode.UNKNOWN_TOOL,
                f"Tool not found: {tool_name}",
            )

        tool = self._tools[tool_name]

        # Permission check
        if not self._check_permission(agent_id, tool.required_permission):
            self._audit.log(
                action="permission_denied", agent_id=agent_id, tool_name=tool_name,
                error=f"Required: {tool.required_permission.value}",
            )
            return MCPResponse.from_error(
                request.id, MCPErrorCode.PERMISSION_DENIED,
                f"Agent '{agent_id}' lacks permission for tool '{tool_name}'",
            )

        # Rate limit check
        if not self._rate_limiter.check(agent_id, tool_name):
            self._audit.log(action="rate_limited", agent_id=agent_id, tool_name=tool_name)
            return MCPResponse.from_error(
                request.id, MCPErrorCode.RATE_LIMITED,
                f"Rate limit exceeded for tool '{tool_name}'",
            )

        # Circuit breaker check
        if not self._circuit_breaker.can_execute(tool_name):
            self._audit.log(action="circuit_open", tool_name=tool_name)
            return MCPResponse.from_error(
                request.id, MCPErrorCode.CIRCUIT_OPEN,
                f"Circuit breaker is open for tool '{tool_name}'",
            )

        # Execute
        handler = self._tool_handlers.get(tool_name)
        if not handler:
            return MCPResponse.from_error(
                request.id, MCPErrorCode.INTERNAL_ERROR,
                f"No handler for tool: {tool_name}",
            )

        try:
            if asyncio.iscoroutinefunction(handler):
                result = await asyncio.wait_for(
                    handler(arguments),
                    timeout=tool.timeout,
                )
            else:
                result = handler(arguments)

            self._circuit_breaker.record_success(tool_name)
            self._audit.log(
                action="tool_executed", agent_id=agent_id, tool_name=tool_name,
                result="success",
            )

            return MCPResponse(
                id=request.id,
                result={"content": [{"type": "text", "text": str(result)}]},
            )
        except asyncio.TimeoutError:
            self._circuit_breaker.record_failure(tool_name)
            self._audit.log(
                action="tool_timeout", agent_id=agent_id, tool_name=tool_name,
                error=f"Timeout after {tool.timeout}s",
            )
            return MCPResponse.from_error(
                request.id, MCPErrorCode.INTERNAL_ERROR,
                f"Tool '{tool_name}' timed out after {tool.timeout}s",
            )
        except Exception as e:
            self._circuit_breaker.record_failure(tool_name)
            self._audit.log(
                action="tool_error", agent_id=agent_id, tool_name=tool_name,
                error=str(e),
            )
            return MCPResponse.from_error(
                request.id, MCPErrorCode.INTERNAL_ERROR,
                f"Tool execution error: {e}",
            )

    def _handle_list_resources(self, request: MCPRequest) -> MCPResponse:
        """Handle resources/list request."""
        resources = [r.model_dump() for r in self._resources.values()]
        return MCPResponse(id=request.id, result={"resources": resources})

    async def _handle_read_resource(self, request: MCPRequest) -> MCPResponse:
        """Handle resources/read request."""
        uri = request.params.get("uri", "")
        agent_id = request.params.get("_agent_id", "")

        if uri not in self._resources:
            return MCPResponse.from_error(
                request.id, MCPErrorCode.UNKNOWN_RESOURCE,
                f"Resource not found: {uri}",
            )

        resource = self._resources[uri]

        # Permission check
        if not self._check_permission(agent_id, resource.required_permission):
            return MCPResponse.from_error(
                request.id, MCPErrorCode.PERMISSION_DENIED,
                f"Agent '{agent_id}' lacks permission for resource '{uri}'",
            )

        handler = self._resource_handlers.get(uri)
        if handler:
            try:
                if asyncio.iscoroutinefunction(handler):
                    content = await handler(uri)
                else:
                    content = handler(uri)
            except Exception as e:
                return MCPResponse.from_error(
                    request.id, MCPErrorCode.INTERNAL_ERROR,
                    f"Resource read error: {e}",
                )
        else:
            content = f"Resource: {uri}"

        self._audit.log(action="resource_read", agent_id=agent_id, resource_uri=uri)
        return MCPResponse(
            id=request.id,
            result={
                "contents": [{
                    "uri": uri,
                    "mimeType": resource.mime_type,
                    "text": str(content),
                }],
            },
        )

    def _handle_subscribe(self, request: MCPRequest) -> MCPResponse:
        """Handle resources/subscribe request."""
        uri = request.params.get("uri", "")
        agent_id = request.params.get("_agent_id", "")

        if uri not in self._resources:
            return MCPResponse.from_error(
                request.id, MCPErrorCode.UNKNOWN_RESOURCE,
                f"Resource not found: {uri}",
            )

        if not self._resources[uri].subscribable:
            return MCPResponse.from_error(
                request.id, MCPErrorCode.INVALID_PARAMS,
                f"Resource '{uri}' is not subscribable",
            )

        self._subscriptions[uri].add(agent_id)
        return MCPResponse(id=request.id, result={"subscribed": True})

    def _handle_unsubscribe(self, request: MCPRequest) -> MCPResponse:
        """Handle resources/unsubscribe request."""
        uri = request.params.get("uri", "")
        agent_id = request.params.get("_agent_id", "")
        self._subscriptions[uri].discard(agent_id)
        return MCPResponse(id=request.id, result={"unsubscribed": True})

    def _handle_list_prompts(self, request: MCPRequest) -> MCPResponse:
        """Handle prompts/list request."""
        prompts = [p.model_dump() for p in self._prompts.values()]
        return MCPResponse(id=request.id, result={"prompts": prompts})

    async def _handle_get_prompt(self, request: MCPRequest) -> MCPResponse:
        """Handle prompts/get request."""
        name = request.params.get("name", "")
        arguments = request.params.get("arguments", {})
        agent_id = request.params.get("_agent_id", "")

        if name not in self._prompts:
            return MCPResponse.from_error(
                request.id, MCPErrorCode.UNKNOWN_PROMPT,
                f"Prompt not found: {name}",
            )

        prompt = self._prompts[name]

        # Permission check
        if not self._check_permission(agent_id, prompt.required_permission):
            return MCPResponse.from_error(
                request.id, MCPErrorCode.PERMISSION_DENIED,
                f"Agent '{agent_id}' lacks permission for prompt '{name}'",
            )

        handler = self._prompt_handlers.get(name)
        if handler:
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(arguments)
                else:
                    result = handler(arguments)
            except Exception as e:
                return MCPResponse.from_error(
                    request.id, MCPErrorCode.INTERNAL_ERROR,
                    f"Prompt render error: {e}",
                )
        else:
            result = {"messages": [{"role": "user", "content": {"type": "text", "text": prompt.description}}]}

        self._audit.log(action="prompt_rendered", agent_id=agent_id, tool_name=name)
        return MCPResponse(id=request.id, result=result)

    # === Transport ===

    def create_fastapi_app(self) -> Any:
        """Create a FastAPI application for the MCP server (SSE transport).

        Returns:
            FastAPI application instance.
        """
        try:
            from fastapi import FastAPI, Request
            from fastapi.responses import JSONResponse
        except ImportError:
            raise ImportError("FastAPI not installed. Install with: pip install fastapi")

        app = FastAPI(title=self._name, version=self._version)
        server = self

        @app.post("/mcp")
        async def mcp_endpoint(request: Request) -> JSONResponse:
            """HTTP-based MCP endpoint."""
            body = await request.json()
            mcp_request = MCPRequest(**body)
            response = await server.handle_request(mcp_request)
            return JSONResponse(content=response.model_dump(exclude_none=True))

        @app.get("/mcp/sse")
        async def sse_endpoint(request: Request) -> Any:
            """SSE endpoint for streaming notifications."""
            try:
                from sse_starlette.sse import EventSourceResponse
            except ImportError:
                return JSONResponse(
                    status_code=501,
                    content={"error": "SSE not available. Install sse-starlette."},
                )

            async def event_generator() -> Any:
                """Generate SSE events."""
                while True:
                    await asyncio.sleep(1)
                    yield {"event": "ping", "data": json.dumps({"type": "ping"})}

            return EventSourceResponse(event_generator())

        @app.get("/health")
        async def health() -> dict[str, str]:
            """Health check endpoint."""
            return {"status": "ok", "name": server._name, "version": server._version}

        return app

    async def handle_stdio(self, input_stream: Any = None, output_stream: Any = None) -> None:
        """Handle MCP requests over stdio transport.

        Reads JSON-RPC messages from stdin and writes responses to stdout.
        Falls back to sys.stdin/sys.stdout if streams not provided.

        Args:
            input_stream: Optional input stream (defaults to sys.stdin).
            output_stream: Optional output stream (defaults to sys.stdout).
        """
        import sys

        in_stream = input_stream or sys.stdin
        out_stream = output_stream or sys.stdout

        logger.info("mcp_stdio_transport_started")

        try:
            for line in in_stream:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    request = MCPRequest(**data)
                    response = await self.handle_request(request)
                    out_stream.write(json.dumps(response.model_dump(exclude_none=True)) + "\n")
                    out_stream.flush()
                except json.JSONDecodeError as e:
                    error_resp = MCPResponse.from_error(
                        "0", MCPErrorCode.PARSE_ERROR, f"Invalid JSON: {e}"
                    )
                    out_stream.write(json.dumps(error_resp.model_dump(exclude_none=True)) + "\n")
                    out_stream.flush()
                except Exception as e:
                    error_resp = MCPResponse.from_error(
                        "0", MCPErrorCode.INTERNAL_ERROR, f"Error: {e}"
                    )
                    out_stream.write(json.dumps(error_resp.model_dump(exclude_none=True)) + "\n")
                    out_stream.flush()
        except (KeyboardInterrupt, EOFError):
            pass
        finally:
            logger.info("mcp_stdio_transport_stopped")

    # === Status ===

    def get_stats(self) -> dict[str, Any]:
        """Get server statistics."""
        return {
            "name": self._name,
            "version": self._version,
            "initialized": self._initialized,
            "tools": len(self._tools),
            "resources": len(self._resources),
            "prompts": len(self._prompts),
            "subscriptions": {uri: len(agents) for uri, agents in self._subscriptions.items()},
            "circuit_breakers": {
                name: circuit["state"].value for name, circuit in self._circuit_breaker._circuits.items()
            },
        }

    @property
    def audit(self) -> AuditLogger:
        """Access the audit logger."""
        return self._audit

    @property
    def rate_limiter(self) -> RateLimiter:
        """Access the rate limiter."""
        return self._rate_limiter

    @property
    def circuit_breaker(self) -> CircuitBreaker:
        """Access the circuit breaker."""
        return self._circuit_breaker

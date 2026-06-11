"""Comprehensive tests for MCP module (server, client, protocol).

Covers JSON-RPC message handling, tool registration and discovery,
permission levels, rate limiting, circuit breaker, and client operations.
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_multicolony.mcp.protocol import (
    CircuitState,
    MCPErrorCode,
    MCPMethod,
    MCPNotification,
    MCPRequest,
    MCPResponse,
    MCPServerInfo,
    MCPToolDef,
    PermissionLevel,
    PromptDefinition,
    RateLimitEntry,
    ResourceDefinition,
    ToolDefinition,
)
from ai_multicolony.mcp.server import AuditLogger, CircuitBreaker, MCPServer, RateLimiter
from ai_multicolony.mcp.client import MCPClient, MCPConnectionError


# ============================================================
# Protocol Types Tests
# ============================================================


class TestMCPRequest:
    """Test MCPRequest model."""

    def test_default_jsonrpc_version(self):
        req = MCPRequest(method="initialize")
        assert req.jsonrpc == "2.0"

    def test_auto_generated_id(self):
        req = MCPRequest(method="initialize")
        assert req.id is not None
        assert isinstance(req.id, str)

    def test_custom_id(self):
        req = MCPRequest(id=42, method="initialize")
        assert req.id == 42

    def test_method_stored(self):
        req = MCPRequest(method="tools/list")
        assert req.method == "tools/list"

    def test_default_empty_params(self):
        req = MCPRequest(method="initialize")
        assert req.params == {}

    def test_custom_params(self):
        req = MCPRequest(method="tools/call", params={"name": "echo"})
        assert req.params["name"] == "echo"

    def test_serialization(self):
        req = MCPRequest(id="1", method="initialize", params={"key": "val"})
        data = req.model_dump()
        assert data["jsonrpc"] == "2.0"
        assert data["method"] == "initialize"


class TestMCPResponse:
    """Test MCPResponse model."""

    def test_success_response(self):
        resp = MCPResponse(id=1, result={"status": "ok"})
        assert not resp.is_error
        assert resp.result == {"status": "ok"}

    def test_error_response(self):
        resp = MCPResponse(id=1, error={"code": -32601, "message": "Not found"})
        assert resp.is_error
        assert resp.error["code"] == -32601

    def test_from_error_factory(self):
        resp = MCPResponse.from_error(1, MCPErrorCode.METHOD_NOT_FOUND, "Method not found")
        assert resp.is_error
        assert resp.error["code"] == MCPErrorCode.METHOD_NOT_FOUND.value
        assert "Method not found" in resp.error["message"]

    def test_from_error_with_data(self):
        resp = MCPResponse.from_error(1, MCPErrorCode.INVALID_PARAMS, "Bad params", data={"detail": "x"})
        assert resp.error["data"] == {"detail": "x"}

    def test_from_error_without_data(self):
        resp = MCPResponse.from_error(1, MCPErrorCode.INTERNAL_ERROR, "Oops")
        assert "data" not in resp.error


class TestPermissionLevel:
    """Test PermissionLevel enum."""

    def test_levels_exist(self):
        assert PermissionLevel.NONE.value == "none"
        assert PermissionLevel.READ.value == "read"
        assert PermissionLevel.WRITE.value == "write"
        assert PermissionLevel.EXECUTE.value == "execute"
        assert PermissionLevel.ADMIN.value == "admin"

    def test_level_ordering(self):
        assert PermissionLevel.NONE.level == 0
        assert PermissionLevel.READ.level == 1
        assert PermissionLevel.WRITE.level == 2
        assert PermissionLevel.EXECUTE.level == 3
        assert PermissionLevel.ADMIN.level == 4

    def test_gte_self(self):
        assert PermissionLevel.READ.gte(PermissionLevel.READ)

    def test_gte_higher(self):
        assert PermissionLevel.ADMIN.gte(PermissionLevel.NONE)

    def test_gte_lower_fails(self):
        assert not PermissionLevel.NONE.gte(PermissionLevel.READ)

    def test_gte_cross_levels(self):
        assert PermissionLevel.EXECUTE.gte(PermissionLevel.WRITE)
        assert not PermissionLevel.WRITE.gte(PermissionLevel.EXECUTE)


class TestMCPErrorCode:
    """Test MCPErrorCode enum."""

    def test_standard_codes(self):
        assert MCPErrorCode.PARSE_ERROR == -32700
        assert MCPErrorCode.INVALID_REQUEST == -32600
        assert MCPErrorCode.METHOD_NOT_FOUND == -32601
        assert MCPErrorCode.INVALID_PARAMS == -32602
        assert MCPErrorCode.INTERNAL_ERROR == -32603

    def test_mcp_specific_codes(self):
        assert MCPErrorCode.SERVER_NOT_INITIALIZED == -32002
        assert MCPErrorCode.UNKNOWN_TOOL == -32001
        assert MCPErrorCode.UNKNOWN_RESOURCE == -32003
        assert MCPErrorCode.UNKNOWN_PROMPT == -32004
        assert MCPErrorCode.PERMISSION_DENIED == -32010
        assert MCPErrorCode.RATE_LIMITED == -32011
        assert MCPErrorCode.CIRCUIT_OPEN == -32012


class TestMCPMethod:
    """Test MCPMethod enum."""

    def test_all_methods_defined(self):
        assert MCPMethod.INITIALIZE == "initialize"
        assert MCPMethod.LIST_TOOLS == "tools/list"
        assert MCPMethod.CALL_TOOL == "tools/call"
        assert MCPMethod.LIST_RESOURCES == "resources/list"
        assert MCPMethod.READ_RESOURCE == "resources/read"
        assert MCPMethod.SUBSCRIBE_RESOURCE == "resources/subscribe"
        assert MCPMethod.UNSUBSCRIBE_RESOURCE == "resources/unsubscribe"
        assert MCPMethod.LIST_PROMPTS == "prompts/list"
        assert MCPMethod.GET_PROMPT == "prompts/get"


class TestToolDefinition:
    """Test ToolDefinition model."""

    def test_minimal(self):
        td = ToolDefinition(name="test")
        assert td.name == "test"
        assert td.required_permission == PermissionLevel.EXECUTE

    def test_full(self):
        td = ToolDefinition(
            name="scan", description="Security scan",
            input_schema={"type": "object"},
            required_permission=PermissionLevel.ADMIN,
            rate_limit=10, timeout=60, category="security",
        )
        assert td.rate_limit == 10
        assert td.category == "security"

    def test_backward_compat_alias(self):
        td = MCPToolDef(name="test")
        assert isinstance(td, ToolDefinition)


class TestResourceDefinition:
    """Test ResourceDefinition model."""

    def test_minimal(self):
        rd = ResourceDefinition(uri="test://r", name="R")
        assert rd.uri == "test://r"
        assert rd.mime_type == "text/plain"

    def test_subscribable(self):
        rd = ResourceDefinition(uri="test://r", name="R", subscribable=True)
        assert rd.subscribable is True


class TestPromptDefinition:
    """Test PromptDefinition model."""

    def test_minimal(self):
        pd = PromptDefinition(name="greet")
        assert pd.name == "greet"
        assert pd.arguments == []

    def test_with_arguments(self):
        pd = PromptDefinition(name="greet", arguments=[{"name": "user"}])
        assert len(pd.arguments) == 1


class TestMCPServerInfo:
    """Test MCPServerInfo model."""

    def test_defaults(self):
        info = MCPServerInfo()
        assert info.protocol_version == "2024-11-05"
        assert "tools" in info.capabilities

    def test_custom(self):
        info = MCPServerInfo(name="custom-server", version="1.0")
        assert info.name == "custom-server"


class TestCircuitState:
    """Test CircuitState enum."""

    def test_states(self):
        assert CircuitState.CLOSED == "closed"
        assert CircuitState.OPEN == "open"
        assert CircuitState.HALF_OPEN == "half_open"


class TestRateLimitEntry:
    """Test RateLimitEntry model."""

    def test_defaults(self):
        entry = RateLimitEntry(agent_id="a", tool_name="t")
        assert entry.request_count == 0
        assert entry.window_seconds == 60


class TestMCPNotification:
    """Test MCPNotification model."""

    def test_creation(self):
        n = MCPNotification(method="notifications/progress")
        assert n.jsonrpc == "2.0"
        assert n.method == "notifications/progress"


# ============================================================
# CircuitBreaker Tests
# ============================================================


class TestCircuitBreaker:
    """Test CircuitBreaker."""

    def test_initial_state_closed(self):
        cb = CircuitBreaker()
        assert cb.get_state("tool_a") == CircuitState.CLOSED

    def test_can_execute_when_closed(self):
        cb = CircuitBreaker()
        assert cb.can_execute("tool_a") is True

    def test_record_success_resets(self):
        cb = CircuitBreaker()
        cb.record_failure("tool_a")
        cb.record_failure("tool_a")
        cb.record_success("tool_a")
        assert cb.get_state("tool_a") == CircuitState.CLOSED

    def test_opens_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=3)
        for _ in range(3):
            cb.record_failure("tool_a")
        assert cb.get_state("tool_a") == CircuitState.OPEN

    def test_cannot_execute_when_open(self):
        cb = CircuitBreaker(failure_threshold=2)
        cb.record_failure("tool_a")
        cb.record_failure("tool_a")
        assert cb.can_execute("tool_a") is False

    def test_half_open_after_recovery_timeout(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.0)
        cb.record_failure("tool_a")
        cb.record_failure("tool_a")
        assert cb.get_state("tool_a") == CircuitState.OPEN
        # With 0 recovery timeout, should transition to half-open
        assert cb.can_execute("tool_a") is True
        assert cb.get_state("tool_a") == CircuitState.HALF_OPEN

    def test_half_open_success_closes(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.0)
        cb.record_failure("tool_a")
        cb.record_failure("tool_a")
        cb.can_execute("tool_a")  # triggers half-open
        cb.record_success("tool_a")
        assert cb.get_state("tool_a") == CircuitState.CLOSED

    def test_half_open_failure_reopens(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.0)
        cb.record_failure("tool_a")
        cb.record_failure("tool_a")
        cb.can_execute("tool_a")  # triggers half-open
        cb.record_failure("tool_a")
        assert cb.get_state("tool_a") == CircuitState.OPEN

    def test_half_open_max_calls(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.0, half_open_max_calls=1)
        cb.record_failure("tool_a")
        cb.record_failure("tool_a")
        cb.can_execute("tool_a")  # first call allowed
        assert cb.can_execute("tool_a") is False  # second call blocked

    def test_reset_specific_tool(self):
        cb = CircuitBreaker(failure_threshold=2)
        cb.record_failure("tool_a")
        cb.record_failure("tool_a")
        cb.reset("tool_a")
        assert cb.get_state("tool_a") == CircuitState.CLOSED

    def test_reset_all(self):
        cb = CircuitBreaker(failure_threshold=2)
        cb.record_failure("tool_a")
        cb.record_failure("tool_a")
        cb.record_failure("tool_b")
        cb.record_failure("tool_b")
        cb.reset()
        assert cb.get_state("tool_a") == CircuitState.CLOSED
        assert cb.get_state("tool_b") == CircuitState.CLOSED

    def test_separate_circuits_per_tool(self):
        cb = CircuitBreaker(failure_threshold=2)
        cb.record_failure("tool_a")
        cb.record_failure("tool_a")
        assert cb.get_state("tool_a") == CircuitState.OPEN
        assert cb.get_state("tool_b") == CircuitState.CLOSED


# ============================================================
# RateLimiter Tests
# ============================================================


class TestRateLimiter:
    """Test RateLimiter."""

    def test_default_rpm(self):
        rl = RateLimiter(default_rpm=60)
        result = rl.check("agent1", "tool1")
        assert result is True

    def test_custom_rpm_per_tool(self):
        rl = RateLimiter(default_rpm=60)
        rl.set_limit("limited_tool", 2)
        assert rl.check("agent1", "limited_tool") is True
        assert rl.check("agent1", "limited_tool") is True
        assert rl.check("agent1", "limited_tool") is False

    def test_rate_limit_per_agent(self):
        rl = RateLimiter(default_rpm=2)
        assert rl.check("agent1", "tool1") is True
        assert rl.check("agent1", "tool1") is True
        assert rl.check("agent1", "tool1") is False
        # Different agent is not affected
        assert rl.check("agent2", "tool1") is True

    def test_get_usage_empty(self):
        rl = RateLimiter(default_rpm=60)
        usage = rl.get_usage("agent1", "tool1")
        assert usage["used"] == 0
        assert usage["limit"] == 60

    def test_get_usage_after_requests(self):
        rl = RateLimiter(default_rpm=60)
        rl.check("agent1", "tool1")
        rl.check("agent1", "tool1")
        usage = rl.get_usage("agent1", "tool1")
        assert usage["used"] == 2
        assert usage["remaining"] == 58

    def test_window_reset(self):
        rl = RateLimiter(default_rpm=1)
        rl.check("agent1", "tool1")
        assert rl.check("agent1", "tool1") is False
        # Force window expiry
        key = "agent1:tool1"
        rl._windows[key].window_start = time.time() - 61
        assert rl.check("agent1", "tool1") is True


# ============================================================
# AuditLogger Tests
# ============================================================


class TestAuditLogger:
    """Test AuditLogger."""

    def test_log_and_query(self):
        al = AuditLogger()
        al.log(action="test", agent_id="a1")
        results = al.query(agent_id="a1")
        assert len(results) == 1
        assert results[0]["action"] == "test"

    def test_query_by_action(self):
        al = AuditLogger()
        al.log(action="read")
        al.log(action="write")
        results = al.query(action="read")
        assert len(results) == 1

    def test_query_by_tool(self):
        al = AuditLogger()
        al.log(action="call", tool_name="echo")
        al.log(action="call", tool_name="scan")
        results = al.query(tool_name="echo")
        assert len(results) == 1

    def test_query_by_time_range(self):
        al = AuditLogger()
        t1 = time.time() - 100
        t2 = time.time() + 100
        al.log(action="old")
        results = al.query(start_time=t1, end_time=t2)
        assert len(results) == 1

    def test_max_entries_trimming(self):
        al = AuditLogger(max_entries=3)
        for i in range(5):
            al.log(action=f"action_{i}")
        results = al.query()
        assert len(results) == 3

    def test_query_limit(self):
        al = AuditLogger()
        for i in range(10):
            al.log(action=f"action_{i}")
        results = al.query(limit=3)
        assert len(results) == 3

    def test_metadata_stored(self):
        al = AuditLogger()
        al.log(action="test", metadata={"key": "val"})
        results = al.query(action="test")
        assert results[0]["metadata"]["key"] == "val"


# ============================================================
# MCPServer Tests
# ============================================================


class TestMCPServerInit:
    """Test MCPServer initialization."""

    def test_default_name(self):
        server = MCPServer()
        assert server._name == "ai-multicolony-mcp"

    def test_custom_name(self):
        server = MCPServer(name="custom")
        assert server._name == "custom"

    def test_default_not_initialized(self):
        server = MCPServer()
        assert server._initialized is False

    def test_internal_components(self):
        server = MCPServer()
        assert isinstance(server._rate_limiter, RateLimiter)
        assert isinstance(server._circuit_breaker, CircuitBreaker)
        assert isinstance(server._audit, AuditLogger)


class TestMCPServerRegistration:
    """Test tool/resource/prompt registration."""

    def test_register_tool(self):
        server = MCPServer()
        server.register_tool("echo", "Echo tool", {"type": "object"}, lambda a: "ok")
        assert "echo" in server._tools
        assert "echo" in server._tool_handlers

    def test_register_tool_with_rate_limit(self):
        server = MCPServer()
        server.register_tool("limited", "Limited", {}, lambda a: "ok", rate_limit=10)
        assert server._tools["limited"].rate_limit == 10

    def test_register_tool_with_permission(self):
        server = MCPServer()
        server.register_tool("admin_tool", "Admin", {}, lambda a: "ok",
                             required_permission=PermissionLevel.ADMIN)
        assert server._tools["admin_tool"].required_permission == PermissionLevel.ADMIN

    def test_register_resource(self):
        server = MCPServer()
        server.register_resource("test://data", "Data")
        assert "test://data" in server._resources

    def test_register_resource_subscribable(self):
        server = MCPServer()
        server.register_resource("test://live", "Live", subscribable=True)
        assert server._resources["test://live"].subscribable is True

    def test_register_resource_with_handler(self):
        server = MCPServer()
        handler = AsyncMock(return_value="content")
        server.register_resource("test://data", "Data", handler=handler)
        assert "test://data" in server._resource_handlers

    def test_register_prompt(self):
        server = MCPServer()
        server.register_prompt("greet", "Greeting prompt")
        assert "greet" in server._prompts

    def test_register_prompt_with_arguments(self):
        server = MCPServer()
        server.register_prompt("greet", "Greeting",
                               arguments=[{"name": "user", "required": True}])
        assert len(server._prompts["greet"].arguments) == 1

    def test_register_prompt_with_handler(self):
        server = MCPServer()
        handler = AsyncMock(return_value={"messages": []})
        server.register_prompt("greet", "Greeting", handler=handler)
        assert "greet" in server._prompt_handlers


class TestMCPServerPermissions:
    """Test MCPServer permission management."""

    def test_set_agent_permission(self):
        server = MCPServer()
        server.set_agent_permission("agent1", PermissionLevel.ADMIN)
        assert server._permissions["agent1"] == PermissionLevel.ADMIN

    def test_check_permission_sufficient(self):
        server = MCPServer()
        server.set_agent_permission("agent1", PermissionLevel.ADMIN)
        assert server._check_permission("agent1", PermissionLevel.EXECUTE) is True

    def test_check_permission_insufficient(self):
        server = MCPServer()
        server.set_agent_permission("agent1", PermissionLevel.READ)
        assert server._check_permission("agent1", PermissionLevel.EXECUTE) is False

    def test_check_permission_no_agent_default_none(self):
        server = MCPServer()
        assert server._check_permission("unknown", PermissionLevel.READ) is False


class TestMCPServerRequestHandling:
    """Test MCPServer request handling."""

    async def test_handle_initialize(self):
        server = MCPServer()
        request = MCPRequest(method=MCPMethod.INITIALIZE)
        response = await server.handle_request(request)
        assert response.result is not None
        assert "name" in response.result
        assert server._initialized is True

    async def test_handle_list_tools_empty(self):
        server = MCPServer()
        request = MCPRequest(method=MCPMethod.LIST_TOOLS)
        response = await server.handle_request(request)
        assert response.result["tools"] == []

    async def test_handle_list_tools_with_tools(self):
        server = MCPServer()
        server.register_tool("echo", "Echo", {}, lambda a: "ok")
        server.set_agent_permission("agent1", PermissionLevel.EXECUTE)
        request = MCPRequest(method=MCPMethod.LIST_TOOLS, params={"_agent_id": "agent1"})
        response = await server.handle_request(request)
        assert len(response.result["tools"]) == 1

    async def test_handle_list_tools_permission_filter(self):
        server = MCPServer()
        server.register_tool("admin_tool", "Admin", {}, lambda a: "ok",
                             required_permission=PermissionLevel.ADMIN)
        server.register_tool("basic_tool", "Basic", {}, lambda a: "ok",
                             required_permission=PermissionLevel.READ)
        server.set_agent_permission("reader", PermissionLevel.READ)
        request = MCPRequest(method=MCPMethod.LIST_TOOLS, params={"_agent_id": "reader"})
        response = await server.handle_request(request)
        tool_names = [t["name"] for t in response.result["tools"]]
        assert "basic_tool" in tool_names
        assert "admin_tool" not in tool_names

    async def test_handle_call_tool_success(self):
        server = MCPServer()
        async def handler(args):
            return f"Result: {args.get('text', '')}"
        server.register_tool("echo", "Echo", {"type": "object"}, handler)
        server.set_agent_permission("agent1", PermissionLevel.EXECUTE)
        request = MCPRequest(method=MCPMethod.CALL_TOOL,
                             params={"name": "echo", "arguments": {"text": "hi"}, "_agent_id": "agent1"})
        response = await server.handle_request(request)
        assert response.result is not None
        assert "content" in response.result

    async def test_handle_call_tool_sync_handler(self):
        server = MCPServer()
        def handler(args):
            return "sync result"
        server.register_tool("sync_tool", "Sync", {}, handler)
        server.set_agent_permission("agent1", PermissionLevel.EXECUTE)
        request = MCPRequest(method=MCPMethod.CALL_TOOL,
                             params={"name": "sync_tool", "arguments": {}, "_agent_id": "agent1"})
        response = await server.handle_request(request)
        assert response.result is not None

    async def test_handle_call_tool_unknown(self):
        server = MCPServer()
        request = MCPRequest(method=MCPMethod.CALL_TOOL,
                             params={"name": "nonexistent", "arguments": {}})
        response = await server.handle_request(request)
        assert response.is_error
        assert response.error["code"] == MCPErrorCode.UNKNOWN_TOOL.value

    async def test_handle_call_tool_permission_denied(self):
        server = MCPServer()
        server.register_tool("admin_tool", "Admin", {}, lambda a: "ok",
                             required_permission=PermissionLevel.ADMIN)
        server.set_agent_permission("reader", PermissionLevel.READ)
        request = MCPRequest(method=MCPMethod.CALL_TOOL,
                             params={"name": "admin_tool", "arguments": {}, "_agent_id": "reader"})
        response = await server.handle_request(request)
        assert response.is_error
        assert response.error["code"] == MCPErrorCode.PERMISSION_DENIED.value

    async def test_handle_call_tool_rate_limited(self):
        server = MCPServer(default_rate_limit=1)
        server.register_tool("limited", "Limited", {}, lambda a: "ok")
        server.set_agent_permission("agent1", PermissionLevel.EXECUTE)
        request = MCPRequest(method=MCPMethod.CALL_TOOL,
                             params={"name": "limited", "arguments": {}, "_agent_id": "agent1"})
        await server.handle_request(request)
        response = await server.handle_request(request)
        assert response.is_error
        assert response.error["code"] == MCPErrorCode.RATE_LIMITED.value

    async def test_handle_call_tool_circuit_open(self):
        server = MCPServer(circuit_failure_threshold=2)
        server.register_tool("flaky", "Flaky", {}, handler=lambda a: (_ for _ in ()).throw(RuntimeError("fail")))
        server.set_agent_permission("agent1", PermissionLevel.EXECUTE)
        # Manually open circuit
        server._circuit_breaker.record_failure("flaky")
        server._circuit_breaker.record_failure("flaky")
        request = MCPRequest(method=MCPMethod.CALL_TOOL,
                             params={"name": "flaky", "arguments": {}, "_agent_id": "agent1"})
        response = await server.handle_request(request)
        assert response.is_error
        assert response.error["code"] == MCPErrorCode.CIRCUIT_OPEN.value

    async def test_handle_call_tool_exception(self):
        server = MCPServer()
        async def bad_handler(args):
            raise ValueError("Something broke")
        server.register_tool("bad", "Bad", {}, bad_handler)
        server.set_agent_permission("agent1", PermissionLevel.EXECUTE)
        request = MCPRequest(method=MCPMethod.CALL_TOOL,
                             params={"name": "bad", "arguments": {}, "_agent_id": "agent1"})
        response = await server.handle_request(request)
        assert response.is_error

    async def test_handle_list_resources(self):
        server = MCPServer()
        server.register_resource("test://data", "Data")
        request = MCPRequest(method=MCPMethod.LIST_RESOURCES)
        response = await server.handle_request(request)
        assert len(response.result["resources"]) == 1

    async def test_handle_read_resource(self):
        server = MCPServer()
        server.register_resource("test://data", "Data")
        server.set_agent_permission("agent1", PermissionLevel.READ)
        request = MCPRequest(method=MCPMethod.READ_RESOURCE,
                             params={"uri": "test://data", "_agent_id": "agent1"})
        response = await server.handle_request(request)
        assert response.result is not None
        assert "contents" in response.result

    async def test_handle_read_resource_unknown(self):
        server = MCPServer()
        request = MCPRequest(method=MCPMethod.READ_RESOURCE,
                             params={"uri": "missing://resource"})
        response = await server.handle_request(request)
        assert response.is_error

    async def test_handle_subscribe(self):
        server = MCPServer()
        server.register_resource("test://live", "Live", subscribable=True)
        request = MCPRequest(method=MCPMethod.SUBSCRIBE_RESOURCE,
                             params={"uri": "test://live", "_agent_id": "agent1"})
        response = await server.handle_request(request)
        assert response.result["subscribed"] is True

    async def test_handle_subscribe_not_subscribable(self):
        server = MCPServer()
        server.register_resource("test://static", "Static", subscribable=False)
        request = MCPRequest(method=MCPMethod.SUBSCRIBE_RESOURCE,
                             params={"uri": "test://static", "_agent_id": "agent1"})
        response = await server.handle_request(request)
        assert response.is_error

    async def test_handle_subscribe_unknown_resource(self):
        server = MCPServer()
        request = MCPRequest(method=MCPMethod.SUBSCRIBE_RESOURCE,
                             params={"uri": "missing://resource"})
        response = await server.handle_request(request)
        assert response.is_error

    async def test_handle_unsubscribe(self):
        server = MCPServer()
        request = MCPRequest(method=MCPMethod.UNSUBSCRIBE_RESOURCE,
                             params={"uri": "test://data", "_agent_id": "agent1"})
        response = await server.handle_request(request)
        assert response.result["unsubscribed"] is True

    async def test_handle_list_prompts(self):
        server = MCPServer()
        server.register_prompt("greet", "Greeting")
        request = MCPRequest(method=MCPMethod.LIST_PROMPTS)
        response = await server.handle_request(request)
        assert len(response.result["prompts"]) == 1

    async def test_handle_get_prompt(self):
        server = MCPServer()
        server.register_prompt("greet", "Say hello")
        server.set_agent_permission("agent1", PermissionLevel.READ)
        request = MCPRequest(method=MCPMethod.GET_PROMPT,
                             params={"name": "greet", "_agent_id": "agent1"})
        response = await server.handle_request(request)
        assert response.result is not None

    async def test_handle_get_prompt_unknown(self):
        server = MCPServer()
        request = MCPRequest(method=MCPMethod.GET_PROMPT,
                             params={"name": "nonexistent"})
        response = await server.handle_request(request)
        assert response.is_error

    async def test_handle_unknown_method(self):
        server = MCPServer()
        request = MCPRequest(method="unknown/method")
        response = await server.handle_request(request)
        assert response.is_error
        assert response.error["code"] == MCPErrorCode.METHOD_NOT_FOUND.value


class TestMCPServerStats:
    """Test MCPServer stats and properties."""

    def test_get_stats(self):
        server = MCPServer()
        server.register_tool("t1", "T1", {}, lambda a: "ok")
        server.register_resource("test://r", "R")
        server.register_prompt("p1", "P1")
        stats = server.get_stats()
        assert stats["tools"] == 1
        assert stats["resources"] == 1
        assert stats["prompts"] == 1
        assert stats["initialized"] is False

    def test_audit_property(self):
        server = MCPServer()
        assert isinstance(server.audit, AuditLogger)

    def test_rate_limiter_property(self):
        server = MCPServer()
        assert isinstance(server.rate_limiter, RateLimiter)

    def test_circuit_breaker_property(self):
        server = MCPServer()
        assert isinstance(server.circuit_breaker, CircuitBreaker)


class TestMCPServerStdio:
    """Test MCPServer stdio transport."""

    async def test_handle_stdio_json(self):
        server = MCPServer()
        output_lines = []

        class MockInputStream:
            def __iter__(self):
                return iter(['{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}', ''])

        class MockOutputStream:
            def write(self, s):
                output_lines.append(s)
            def flush(self):
                pass

        await server.handle_stdio(input_stream=MockInputStream(), output_stream=MockOutputStream())
        assert len(output_lines) >= 1

    async def test_handle_stdio_invalid_json(self):
        server = MCPServer()
        output_lines = []

        class MockInputStream:
            def __iter__(self):
                return iter(['not json at all', ''])

        class MockOutputStream:
            def write(self, s):
                output_lines.append(s)
            def flush(self):
                pass

        await server.handle_stdio(input_stream=MockInputStream(), output_stream=MockOutputStream())
        assert len(output_lines) >= 1
        assert "PARSE_ERROR" in output_lines[0] or "-32700" in output_lines[0]


# ============================================================
# MCPClient Tests
# ============================================================


class TestMCPClientInit:
    """Test MCPClient initialization."""

    def test_default_init(self):
        client = MCPClient("http://localhost:5000")
        assert client._server_url == "http://localhost:5000"
        assert client._timeout == 30.0
        assert client._max_retries == 3

    def test_url_trailing_slash_stripped(self):
        client = MCPClient("http://localhost:5000/")
        assert client._server_url == "http://localhost:5000"

    def test_custom_params(self):
        client = MCPClient("http://localhost:5000", timeout=10, max_retries=5, agent_id="a1")
        assert client._timeout == 10
        assert client._max_retries == 5
        assert client._agent_id == "a1"

    def test_not_connected_initially(self):
        client = MCPClient("http://localhost:5000")
        assert client.is_connected is False

    def test_server_info_none_initially(self):
        client = MCPClient("http://localhost:5000")
        assert client.server_info is None

    def test_available_tools_empty_initially(self):
        client = MCPClient("http://localhost:5000")
        assert client.available_tools == []

    def test_available_resources_empty_initially(self):
        client = MCPClient("http://localhost:5000")
        assert client.available_resources == []

    def test_available_prompts_empty_initially(self):
        client = MCPClient("http://localhost:5000")
        assert client.available_prompts == []


class TestMCPClientProperties:
    """Test MCPClient properties and get methods."""

    def test_get_tool(self):
        client = MCPClient("http://localhost:5000")
        assert client.get_tool("nonexistent") is None

    def test_get_stats(self):
        client = MCPClient("http://localhost:5000")
        stats = client.get_stats()
        assert stats["connected"] is False
        assert stats["request_count"] == 0
        assert stats["error_count"] == 0


class TestMCPClientConnect:
    """Test MCPClient connect/disconnect."""

    async def test_disconnect_clears_state(self):
        client = MCPClient("http://localhost:5000")
        client._connected = True
        client._tools["test"] = ToolDefinition(name="test")
        client._server_info = {"name": "test"}
        await client.disconnect()
        assert client.is_connected is False
        assert len(client.available_tools) == 0
        assert client.server_info is None


class TestMCPClientSendRequest:
    """Test MCPClient _send_request with mocked httpx."""

    async def test_send_request_connection_error(self):
        client = MCPClient("http://localhost:5000")
        # Without httpx or with unreachable server, should return error response
        with patch("ai_multicolony.mcp.client.httpx", create=True):
            response = await client._send_request(MCPRequest(method="initialize"))
            # Will get a connection error response since httpx import will fail or connection fails
            assert response is not None

    async def test_send_request_increments_count(self):
        client = MCPClient("http://localhost:5000")
        initial_count = client._request_count
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = {"jsonrpc": "2.0", "id": "1", "result": {}}
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_client_cls.return_value = mock_instance
            await client._send_request(MCPRequest(method="initialize"))
            assert client._request_count == initial_count + 1


class TestMCPClientCallTool:
    """Test MCPClient call_tool with retries."""

    async def test_call_tool_permission_denied_no_retry(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(
                id="1",
                error={"code": MCPErrorCode.PERMISSION_DENIED.value, "message": "Denied"},
            )
            with pytest.raises(RuntimeError, match="Tool call failed"):
                await client.call_tool("admin_tool", {})

    async def test_call_tool_unknown_tool_no_retry(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(
                id="1",
                error={"code": MCPErrorCode.UNKNOWN_TOOL.value, "message": "Unknown"},
            )
            with pytest.raises(RuntimeError, match="Tool call failed"):
                await client.call_tool("missing_tool", {})

    async def test_call_tool_rate_limited_no_retry(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(
                id="1",
                error={"code": MCPErrorCode.RATE_LIMITED.value, "message": "Limited"},
            )
            with pytest.raises(RuntimeError, match="Tool call failed"):
                await client.call_tool("limited", {})

    async def test_call_tool_success(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(
                id="1",
                result={"content": [{"type": "text", "text": "Hello!"}]},
            )
            result = await client.call_tool("echo", {"text": "hi"})
            assert result == "Hello!"

    async def test_call_tool_retries_on_other_errors(self):
        client = MCPClient("http://localhost:5000", max_retries=2, retry_delay=0.0)
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(
                id="1",
                error={"code": MCPErrorCode.INTERNAL_ERROR.value, "message": "Temp fail"},
            )
            with pytest.raises(RuntimeError, match="failed after 2 retries"):
                await client.call_tool("flaky", {})


class TestMCPClientResourceAccess:
    """Test MCPClient resource operations."""

    async def test_discover_tools_error_returns_empty(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(id="1", error={"code": -1, "message": "err"})
            tools = await client.discover_tools()
            assert tools == []

    async def test_discover_tools_success(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(
                id="1",
                result={"tools": [{"name": "echo", "description": "Echo tool"}]},
            )
            tools = await client.discover_tools()
            assert len(tools) == 1
            assert tools[0].name == "echo"

    async def test_list_tools_uses_cache(self):
        client = MCPClient("http://localhost:5000")
        client._tools["echo"] = ToolDefinition(name="echo")
        tools = await client.list_tools()
        assert len(tools) == 1

    async def test_discover_resources_error_returns_empty(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(id="1", error={"code": -1, "message": "err"})
            resources = await client.discover_resources()
            assert resources == []

    async def test_discover_resources_success(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(
                id="1",
                result={"resources": [{"uri": "test://r", "name": "R"}]},
            )
            resources = await client.discover_resources()
            assert len(resources) == 1

    async def test_read_resource_error(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(id="1", error={"code": -1, "message": "err"})
            with pytest.raises(RuntimeError, match="Failed to read resource"):
                await client.read_resource("test://r")

    async def test_read_resource_success(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(
                id="1",
                result={"contents": [{"text": "hello"}]},
            )
            content = await client.read_resource("test://r")
            assert content == "hello"

    async def test_subscribe_resource(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(id="1", result={"subscribed": True})
            result = await client.subscribe_resource("test://r")
            assert result is True

    async def test_unsubscribe_resource(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(id="1", result={"unsubscribed": True})
            result = await client.unsubscribe_resource("test://r")
            assert result is True

    async def test_list_resources_discover_on_empty(self):
        client = MCPClient("http://localhost:5000")
        resource = ResourceDefinition(uri="test://r", name="R")

        async def fake_discover():
            client._resources["test://r"] = resource
            return [resource]

        with patch.object(client, "discover_resources", side_effect=fake_discover):
            result = await client.list_resources()
            assert len(result) == 1


class TestMCPClientPromptAccess:
    """Test MCPClient prompt operations."""

    async def test_discover_prompts_success(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(
                id="1",
                result={"prompts": [{"name": "greet", "description": "Greeting"}]},
            )
            prompts = await client.discover_prompts()
            assert len(prompts) == 1

    async def test_discover_prompts_error(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(id="1", error={"code": -1, "message": "err"})
            prompts = await client.discover_prompts()
            assert prompts == []

    async def test_get_prompt_error(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(id="1", error={"code": -1, "message": "err"})
            with pytest.raises(RuntimeError, match="Failed to get prompt"):
                await client.get_prompt("missing")

    async def test_get_prompt_success(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(
                id="1",
                result={"messages": [{"role": "user", "content": "Hello"}]},
            )
            result = await client.get_prompt("greet")
            assert "messages" in result

    async def test_get_prompt_with_arguments(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(id="1", result={"messages": []})
            await client.get_prompt("greet", arguments={"user": "Alice"})
            call_args = mock_send.call_args[0][0]
            assert call_args.params["arguments"] == {"user": "Alice"}


class TestMCPClientPing:
    """Test MCPClient ping."""

    async def test_ping_success(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(id="1", result={"name": "server"})
            result = await client.ping()
            assert result is True

    async def test_ping_failure(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(id="1", error={"code": -1, "message": "err"})
            result = await client.ping()
            assert result is False

    async def test_ping_exception(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = Exception("Connection refused")
            result = await client.ping()
            assert result is False


class TestMCPClientConnectFlow:
    """Test full connect flow."""

    async def test_connect_success(self):
        client = MCPClient("http://localhost:5000", agent_id="test-agent")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = [
                MCPResponse(id="1", result={"name": "server", "version": "1.0"}),
                MCPResponse(id="2", result={"tools": [{"name": "echo", "description": "Echo"}]}),
                MCPResponse(id="3", result={"resources": []}),
                MCPResponse(id="4", result={"prompts": []}),
            ]
            info = await client.connect()
            assert client.is_connected is True
            assert info["name"] == "server"

    async def test_connect_failure(self):
        client = MCPClient("http://localhost:5000")
        with patch.object(client, "_send_request", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = MCPResponse(id="1", error={"code": -1, "message": "Failed"})
            with pytest.raises(MCPConnectionError):
                await client.connect()

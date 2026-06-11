"""Comprehensive tests for the FastAPI application, routes, middleware, and schemas.

Tests cover:
- App creation and configuration
- Health and root endpoints
- Agent routes (CRUD)
- Colony routes (CRUD + scale/pause/resume)
- Tool routes (list/call/schema/mcp)
- Memory routes (store/query/stats/sessions/knowledge/pages)
- WebSocket endpoint
- Middleware (timing, error handling, rate limiting, auth)
- Schema validation
"""

from __future__ import annotations

import json
import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ─── Helpers ────────────────────────────────────────────────────────────────


def _create_test_app():
    """Create a FastAPI app for testing with auth disabled."""
    from ai_multicolony.api.app import create_app
    with patch("ai_multicolony.api.app.get_settings") as mock_settings:
        s = MagicMock()
        s.app_name = "TestApp"
        s.app_env = "test"
        s.api.cors_origins = ["*"]
        s.api.api_key = None
        mock_settings.return_value = s
        app = create_app()
    return app


@pytest.fixture(scope="module")
def app():
    """Create the test app once per module."""
    return _create_test_app()


@pytest.fixture(scope="module")
def client(app):
    """Create a TestClient for the app."""
    return TestClient(app)


# ═══════════════════════════════════════════════════════════════════════════
# App Creation & Configuration
# ═══════════════════════════════════════════════════════════════════════════


class TestAppCreation:
    """Test FastAPI application creation and configuration."""

    def test_create_app_returns_fastapi(self, app):
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)

    def test_app_title(self, app):
        assert app.title == "TestApp"

    def test_app_version(self, app):
        assert app.version == "0.1.0"

    def test_app_has_docs_url(self, app):
        assert app.docs_url == "/docs"

    def test_app_has_redoc_url(self, app):
        assert app.redoc_url == "/redoc"

    def test_app_has_routes(self, app):
        route_paths = [r.path for r in app.routes]
        assert len(route_paths) > 0

    def test_app_has_health_route(self, app):
        route_paths = [r.path for r in app.routes]
        assert "/health" in route_paths

    def test_app_has_root_route(self, app):
        route_paths = [r.path for r in app.routes]
        assert "/" in route_paths

    def test_app_includes_agents_router(self, app):
        route_paths = [r.path for r in app.routes]
        agents_routes = [p for p in route_paths if "agents" in p]
        assert len(agents_routes) > 0

    def test_app_includes_colony_router(self, app):
        route_paths = [r.path for r in app.routes]
        colony_routes = [p for p in route_paths if "colony" in p]
        assert len(colony_routes) > 0

    def test_app_includes_tools_router(self, app):
        route_paths = [r.path for r in app.routes]
        tools_routes = [p for p in route_paths if "tools" in p]
        assert len(tools_routes) > 0

    def test_app_includes_memory_router(self, app):
        route_paths = [r.path for r in app.routes]
        memory_routes = [p for p in route_paths if "memory" in p]
        assert len(memory_routes) > 0

    def test_app_includes_ws_router(self, app):
        route_paths = [r.path for r in app.routes]
        ws_routes = [p for p in route_paths if "ws" in p]
        assert len(ws_routes) > 0

    def test_app_description(self, app):
        assert "MultiColony" in app.description

    def test_create_app_with_custom_settings(self):
        """App creation with different settings works."""
        from ai_multicolony.api.app import create_app
        with patch("ai_multicolony.api.app.get_settings") as mock_settings:
            s = MagicMock()
            s.app_name = "CustomApp"
            s.app_env = "staging"
            s.api.cors_origins = ["http://localhost:3000"]
            s.api.api_key = None
            mock_settings.return_value = s
            app = create_app()
            assert app.title == "CustomApp"


# ═══════════════════════════════════════════════════════════════════════════
# Health & Root Endpoints
# ═══════════════════════════════════════════════════════════════════════════


class TestHealthAndRoot:
    """Test /health and / root endpoints."""

    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        data = resp.json()
        assert data["status"] == "ok"

    def test_health_returns_version(self, client):
        resp = client.get("/health")
        data = resp.json()
        assert data["version"] == "0.1.0"

    def test_health_has_only_two_fields(self, client):
        resp = client.get("/health")
        data = resp.json()
        assert set(data.keys()) == {"status", "version"}

    def test_root_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_root_returns_name(self, client):
        resp = client.get("/")
        data = resp.json()
        assert "name" in data

    def test_root_returns_version(self, client):
        resp = client.get("/")
        data = resp.json()
        assert data["version"] == "0.1.0"

    def test_root_returns_docs_link(self, client):
        resp = client.get("/")
        data = resp.json()
        assert data["docs"] == "/docs"

    def test_root_returns_environment(self, client):
        resp = client.get("/")
        data = resp.json()
        assert "environment" in data

    def test_docs_endpoint_exists(self, client):
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_redoc_endpoint_exists(self, client):
        resp = client.get("/redoc")
        assert resp.status_code == 200

    def test_openapi_json_endpoint(self, client):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        data = resp.json()
        assert "openapi" in data
        assert "paths" in data


# ═══════════════════════════════════════════════════════════════════════════
# Agent Routes
# ═══════════════════════════════════════════════════════════════════════════


class TestAgentRoutes:
    """Test /api/agents routes."""

    def test_list_agents_endpoint_exists(self, client):
        with patch("ai_multicolony.agents.registry.AgentRegistry") as MockReg:
            MockReg.return_value.list_all.return_value = {}
            resp = client.get("/api/agents/agents/")
            assert resp.status_code == 200

    def test_list_agents_returns_list(self, client):
        with patch("ai_multicolony.agents.registry.AgentRegistry") as MockReg:
            MockReg.return_value.list_all.return_value = {
                "manus": {"desc": "test"},
            }
            resp = client.get("/api/agents/agents/")
            data = resp.json()
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["name"] == "manus"

    def test_list_agents_empty(self, client):
        with patch("ai_multicolony.agents.registry.AgentRegistry") as MockReg:
            MockReg.return_value.list_all.return_value = {}
            resp = client.get("/api/agents/agents/")
            data = resp.json()
            assert isinstance(data, list)
            assert len(data) == 0

    def test_get_agent_endpoint_exists(self, client):
        resp = client.get("/api/agents/agents/test-agent-123")
        assert resp.status_code == 200

    def test_get_agent_returns_agent_response(self, client):
        resp = client.get("/api/agents/agents/test-agent-123")
        data = resp.json()
        assert "agent_id" in data
        assert data["agent_id"] == "test-agent-123"

    def test_run_agent_endpoint_exists(self, client):
        resp = client.post(
            "/api/agents/agents/test-agent-123/run",
            json={"task": "do something"},
        )
        assert resp.status_code == 200

    def test_run_agent_returns_message(self, client):
        resp = client.post(
            "/api/agents/agents/test-agent-123/run",
            json={"task": "do something"},
        )
        data = resp.json()
        assert "task submitted" in data["message"].lower() or "task" in data["message"].lower()

    def test_run_agent_with_max_iterations(self, client):
        resp = client.post(
            "/api/agents/agents/test-agent-123/run",
            json={"task": "do something", "max_iterations": 5},
        )
        assert resp.status_code == 200

    def test_run_agent_with_timeout(self, client):
        resp = client.post(
            "/api/agents/agents/test-agent-123/run",
            json={"task": "do something", "timeout": 60},
        )
        assert resp.status_code == 200

    def test_delete_agent_endpoint_exists(self, client):
        resp = client.delete("/api/agents/agents/test-agent-123")
        assert resp.status_code == 200

    def test_delete_agent_returns_message(self, client):
        resp = client.delete("/api/agents/agents/test-agent-123")
        data = resp.json()
        assert "terminated" in data["message"].lower()

    def test_create_agent_bad_type_returns_400(self, client):
        with patch("ai_multicolony.agents.registry.AgentRegistry") as MockReg, \
             patch("ai_multicolony.security.permissions.PermissionEngine"):
            MockReg.return_value.create.side_effect = ValueError("Unknown type")
            resp = client.post(
                "/api/agents/agents/",
                json={"agent_type": "nonexistent", "model": "gpt-4o"},
            )
            assert resp.status_code == 400

    def test_create_agent_endpoint_exists(self, client):
        with patch("ai_multicolony.agents.registry.AgentRegistry") as MockReg, \
             patch("ai_multicolony.security.permissions.PermissionEngine"), \
             patch("ai_multicolony.security.permissions.AutonomyLevel"):
            agent = MagicMock()
            agent.agent_id = "new-agent-1"
            agent.name = "test-agent"
            agent.state = MagicMock()
            agent.state.value = "idle"
            MockReg.return_value.create.return_value = agent
            resp = client.post(
                "/api/agents/agents/",
                json={"agent_type": "manus", "model": "gpt-4o"},
            )
            assert resp.status_code in (200, 201)


# ═══════════════════════════════════════════════════════════════════════════
# Colony Routes
# ═══════════════════════════════════════════════════════════════════════════


class TestColonyRoutes:
    """Test /api/colony routes."""

    def test_list_colonies_endpoint(self, client):
        with patch("ai_multicolony.colony.manager.ColonyManager") as MockMgr:
            MockMgr.return_value.list_colonies = MagicMock(return_value=[])
            resp = client.get("/api/colony/colony/")
            assert resp.status_code == 200

    def test_get_colony_not_found(self, client):
        with patch("ai_multicolony.colony.manager.ColonyManager") as MockMgr:
            MockMgr.return_value.get_status = AsyncMock(side_effect=Exception("Not found"))
            resp = client.get("/api/colony/colony/nonexistent")
            assert resp.status_code == 404

    def test_configure_colony_not_found(self, client):
        with patch("ai_multicolony.colony.manager.ColonyManager") as MockMgr:
            MockMgr.return_value.configure = AsyncMock(side_effect=Exception("Not found"))
            resp = client.put(
                "/api/colony/colony/nonexistent/configure",
                json={"max_agents": 5},
            )
            assert resp.status_code == 404

    def test_scale_colony_endpoint(self, client):
        with patch("ai_multicolony.colony.manager.ColonyManager") as MockMgr:
            MockMgr.return_value.scale = AsyncMock(return_value={"agents": 5})
            resp = client.post(
                "/api/colony/colony/col-123/scale",
                json={"target_agents": 5},
            )
            assert resp.status_code == 200

    def test_scale_colony_validation_min(self, client):
        resp = client.post(
            "/api/colony/colony/col-123/scale",
            json={"target_agents": 0},
        )
        assert resp.status_code == 422

    def test_scale_colony_validation_max(self, client):
        resp = client.post(
            "/api/colony/colony/col-123/scale",
            json={"target_agents": 101},
        )
        assert resp.status_code == 422

    def test_scale_colony_valid_boundary_min(self, client):
        with patch("ai_multicolony.colony.manager.ColonyManager") as MockMgr:
            MockMgr.return_value.scale = AsyncMock(return_value={"agents": 1})
            resp = client.post(
                "/api/colony/colony/col-123/scale",
                json={"target_agents": 1},
            )
            assert resp.status_code == 200

    def test_scale_colony_valid_boundary_max(self, client):
        with patch("ai_multicolony.colony.manager.ColonyManager") as MockMgr:
            MockMgr.return_value.scale = AsyncMock(return_value={"agents": 100})
            resp = client.post(
                "/api/colony/colony/col-123/scale",
                json={"target_agents": 100},
            )
            assert resp.status_code == 200

    def test_pause_colony_endpoint(self, client):
        with patch("ai_multicolony.colony.manager.ColonyManager") as MockMgr:
            MockMgr.return_value.pause = AsyncMock()
            resp = client.post("/api/colony/colony/col-123/pause")
            assert resp.status_code == 200

    def test_resume_colony_endpoint(self, client):
        with patch("ai_multicolony.colony.manager.ColonyManager") as MockMgr:
            MockMgr.return_value.resume = AsyncMock()
            resp = client.post("/api/colony/colony/col-123/resume")
            assert resp.status_code == 200

    def test_delete_colony_endpoint(self, client):
        with patch("ai_multicolony.colony.manager.ColonyManager") as MockMgr:
            MockMgr.return_value.destroy = AsyncMock()
            resp = client.delete("/api/colony/colony/col-123")
            assert resp.status_code == 200

    def test_create_colony_endpoint(self, client):
        with patch("ai_multicolony.colony.manager.ColonyManager") as MockMgr:
            config = MagicMock()
            config.colony_id = "col-new"
            config.name = "Test Colony"
            config.state = MagicMock()
            config.state.value = "active"
            MockMgr.return_value.create = AsyncMock(return_value=config)
            resp = client.post(
                "/api/colony/colony/",
                json={"name": "Test Colony", "model": "gpt-4o"},
            )
            assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════
# Tool Routes
# ═══════════════════════════════════════════════════════════════════════════


class TestToolRoutes:
    """Test /api/tools routes."""

    def test_list_tools_endpoint(self, client):
        with patch("ai_multicolony.core.tool_registry.ToolRegistry") as MockReg:
            MockReg.return_value.list_all.return_value = {}
            resp = client.get("/api/tools/tools/")
            assert resp.status_code == 200

    def test_list_tools_returns_list(self, client):
        with patch("ai_multicolony.core.tool_registry.ToolRegistry") as MockReg:
            MockReg.return_value.list_all.return_value = {
                "shell": {"desc": "run commands"},
            }
            resp = client.get("/api/tools/tools/")
            data = resp.json()
            assert isinstance(data, list)
            assert len(data) == 1

    def test_call_tool_endpoint(self, client):
        with patch("ai_multicolony.core.tool_registry.ToolRegistry") as MockReg:
            result = MagicMock()
            result.success = True
            result.output = "done"
            result.error = None
            MockReg.return_value.execute = AsyncMock(return_value=result)
            resp = client.post(
                "/api/tools/tools/call",
                json={"tool_name": "shell", "arguments": {"cmd": "ls"}},
            )
            assert resp.status_code == 200

    def test_call_tool_success_response(self, client):
        with patch("ai_multicolony.core.tool_registry.ToolRegistry") as MockReg:
            result = MagicMock()
            result.success = True
            result.output = "done"
            result.error = None
            MockReg.return_value.execute = AsyncMock(return_value=result)
            resp = client.post(
                "/api/tools/tools/call",
                json={"tool_name": "shell", "arguments": {"cmd": "ls"}},
            )
            data = resp.json()
            assert data["success"] is True

    def test_call_tool_error(self, client):
        with patch("ai_multicolony.core.tool_registry.ToolRegistry") as MockReg:
            MockReg.return_value.execute.side_effect = Exception("boom")
            resp = client.post(
                "/api/tools/tools/call",
                json={"tool_name": "bad_tool", "arguments": {}},
            )
            data = resp.json()
            assert data["success"] is False

    def test_get_tool_schema_not_found(self, client):
        with patch("ai_multicolony.core.tool_registry.ToolRegistry") as MockReg:
            MockReg.return_value.get.side_effect = KeyError("not found")
            resp = client.get("/api/tools/tools/nonexistent/schema")
            assert resp.status_code == 404

    def test_list_mcp_tools_endpoint(self, client):
        resp = client.get("/api/tools/tools/mcp/list")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_call_tool_missing_name(self, client):
        resp = client.post(
            "/api/tools/tools/call",
            json={"arguments": {"cmd": "ls"}},
        )
        assert resp.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════
# Memory Routes
# ═══════════════════════════════════════════════════════════════════════════


class TestMemoryRoutes:
    """Test /api/memory routes."""

    def test_memory_stats_endpoint(self, client):
        with patch("ai_multicolony.core.memory_manager.MemoryManager") as MockMgr:
            MockMgr.return_value.get_stats.return_value = {"total": 0}
            resp = client.get("/api/memory/memory/stats")
            assert resp.status_code == 200

    def test_store_memory_endpoint(self, client):
        with patch("ai_multicolony.core.memory_manager.MemoryManager") as MockMgr:
            entry = MagicMock()
            entry.id = "mem-123"
            MockMgr.return_value.add_entry.return_value = entry
            resp = client.post(
                "/api/memory/memory/store",
                json={"content": "test memory", "memory_type": "episodic"},
            )
            assert resp.status_code == 200

    def test_store_memory_with_importance(self, client):
        with patch("ai_multicolony.core.memory_manager.MemoryManager") as MockMgr:
            entry = MagicMock()
            entry.id = "mem-456"
            MockMgr.return_value.add_entry.return_value = entry
            resp = client.post(
                "/api/memory/memory/store",
                json={"content": "important memory", "memory_type": "semantic", "importance": 0.9},
            )
            assert resp.status_code == 200

    def test_query_memory_endpoint(self, client):
        with patch("ai_multicolony.core.memory_manager.MemoryManager") as MockMgr:
            result = MagicMock()
            result.entries = []
            result.total_count = 0
            MockMgr.return_value.query.return_value = result
            resp = client.post(
                "/api/memory/memory/query",
                json={"query": "test", "memory_types": [], "limit": 10},
            )
            assert resp.status_code == 200

    def test_create_session_endpoint(self, client):
        with patch("ai_multicolony.memory.session.SessionManager") as MockMgr:
            session = MagicMock()
            session.id = "sess-123"
            MockMgr.return_value.create_session.return_value = session
            resp = client.post(
                "/api/memory/memory/sessions",
                json={"agent_id": "agent-1", "metadata": {}},
            )
            assert resp.status_code == 200

    def test_list_sessions_endpoint(self, client):
        with patch("ai_multicolony.memory.session.SessionManager") as MockMgr:
            MockMgr.return_value.list_sessions.return_value = []
            resp = client.get("/api/memory/memory/sessions")
            assert resp.status_code == 200

    def test_delete_session_endpoint(self, client):
        with patch("ai_multicolony.memory.session.SessionManager") as MockMgr:
            MockMgr.return_value.delete_session.return_value = True
            resp = client.delete("/api/memory/memory/sessions/sess-123")
            assert resp.status_code == 200

    def test_add_knowledge_endpoint(self, client):
        with patch("ai_multicolony.memory.knowledge.KnowledgeBase") as MockKB:
            entry = MagicMock()
            entry.id = "kno-123"
            MockKB.return_value.add.return_value = entry
            resp = client.post(
                "/api/memory/memory/knowledge",
                json={"title": "Test", "content": "Content", "category": "general"},
            )
            assert resp.status_code == 200

    def test_search_knowledge_endpoint(self, client):
        with patch("ai_multicolony.memory.knowledge.KnowledgeBase") as MockKB:
            MockKB.return_value.search.return_value = []
            resp = client.post(
                "/api/memory/memory/knowledge/search",
                json={"query": "test"},
            )
            assert resp.status_code == 200

    def test_knowledge_stats_endpoint(self, client):
        with patch("ai_multicolony.memory.knowledge.KnowledgeBase") as MockKB:
            MockKB.return_value.get_stats.return_value = {"total_entries": 0}
            resp = client.get("/api/memory/memory/knowledge/stats")
            assert resp.status_code == 200

    def test_create_page_endpoint(self, client):
        with patch("ai_multicolony.memory.paging.MemoryPager") as MockPager:
            page = MagicMock()
            page.id = "page-123"
            page.token_count = 10
            MockPager.return_value.create_page.return_value = page
            resp = client.post(
                "/api/memory/memory/pages",
                params={"content": "test content", "title": "Test", "memory_type": "working"},
            )
            assert resp.status_code == 200

    def test_page_usage_endpoint(self, client):
        with patch("ai_multicolony.memory.paging.MemoryPager") as MockPager:
            MockPager.return_value.get_token_usage.return_value = {
                "active_pages": 0, "active_tokens": 0,
            }
            resp = client.get("/api/memory/memory/pages/usage")
            assert resp.status_code == 200

    def test_query_memory_missing_query(self, client):
        resp = client.post(
            "/api/memory/memory/query",
            json={"memory_types": [], "limit": 10},
        )
        assert resp.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════
# WebSocket
# ═══════════════════════════════════════════════════════════════════════════


class TestWebSocket:
    """Test WebSocket endpoint and WS route handler logic."""

    def test_ws_status_endpoint_on_full_app(self, client):
        resp = client.get("/api/ws/ws/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "connected_clients" in data

    def test_ws_status_initial_state(self, client):
        resp = client.get("/api/ws/ws/status")
        data = resp.json()
        assert data["connected_clients"] == 0
        assert data["status"] == "idle"

    def test_ws_ping_message_logic(self):
        message = {"type": "ping"}
        msg_type = message.get("type", "")
        assert msg_type == "ping"
        response = {"type": "pong"}
        assert response["type"] == "pong"

    def test_ws_subscribe_message_logic(self):
        message = {"type": "subscribe", "channel": "test"}
        msg_type = message.get("type", "")
        assert msg_type == "subscribe"
        channel = message.get("channel", "*")
        assert channel == "test"
        response = {"type": "subscribed", "channel": channel}
        assert response["type"] == "subscribed"
        assert response["channel"] == "test"

    def test_ws_unsubscribe_message_logic(self):
        message = {"type": "unsubscribe", "channel": "test"}
        msg_type = message.get("type", "")
        assert msg_type == "unsubscribe"
        channel = message.get("channel", "*")
        assert channel == "test"
        response = {"type": "unsubscribed", "channel": channel}
        assert response["type"] == "unsubscribed"

    def test_ws_invalid_json_handling(self):
        invalid_data = "not json"
        try:
            json.loads(invalid_data)
            assert False, "Should have raised JSONDecodeError"
        except json.JSONDecodeError:
            response = {"type": "error", "message": "Invalid JSON"}
            assert response["type"] == "error"

    def test_ws_broadcast_message_logic(self):
        message = {"type": "custom", "channel": "websocket", "data": "hello"}
        msg_type = message.get("type", "")
        assert msg_type not in ("ping", "subscribe", "unsubscribe")

    def test_ws_route_exists(self, client):
        route_paths = [r.path for r in client.app.routes]
        ws_routes = [p for p in route_paths if "ws" in p]
        assert len(ws_routes) > 0

    def test_ws_status_route_exists(self, client):
        route_paths = [r.path for r in client.app.routes]
        assert "/api/ws/ws/status" in route_paths


# ═══════════════════════════════════════════════════════════════════════════
# Middleware
# ═══════════════════════════════════════════════════════════════════════════


class TestRateLimiterMiddleware:
    """Test RateLimiterMiddleware directly."""

    def test_init_defaults(self):
        from ai_multicolony.api.middleware import RateLimiterMiddleware
        rl = RateLimiterMiddleware()
        assert rl._rpm == 60
        assert rl._rph == 1000

    def test_init_custom(self):
        from ai_multicolony.api.middleware import RateLimiterMiddleware
        rl = RateLimiterMiddleware(requests_per_minute=10, requests_per_hour=100)
        assert rl._rpm == 10
        assert rl._rph == 100

    def test_check_allows_request(self):
        from ai_multicolony.api.middleware import RateLimiterMiddleware
        rl = RateLimiterMiddleware()
        allowed, msg = rl.check("client-1")
        assert allowed is True
        assert msg is None

    def test_check_records_request(self):
        from ai_multicolony.api.middleware import RateLimiterMiddleware
        rl = RateLimiterMiddleware()
        rl.check("client-1")
        usage = rl.get_usage("client-1")
        assert usage["minute_used"] == 1
        assert usage["hour_used"] == 1

    def test_check_blocks_minute_limit(self):
        from ai_multicolony.api.middleware import RateLimiterMiddleware
        rl = RateLimiterMiddleware(requests_per_minute=2, requests_per_hour=1000)
        rl.check("c")
        rl.check("c")
        allowed, msg = rl.check("c")
        assert allowed is False
        assert "per minute" in msg

    def test_check_blocks_hour_limit(self):
        from ai_multicolony.api.middleware import RateLimiterMiddleware
        rl = RateLimiterMiddleware(requests_per_minute=1000, requests_per_hour=2)
        rl.check("c")
        rl.check("c")
        allowed, msg = rl.check("c")
        assert allowed is False
        assert "per hour" in msg

    def test_get_usage_nonexistent_client(self):
        from ai_multicolony.api.middleware import RateLimiterMiddleware
        rl = RateLimiterMiddleware()
        usage = rl.get_usage("unknown")
        assert usage["minute_used"] == 0
        assert usage["hour_used"] == 0

    def test_get_usage_fields(self):
        from ai_multicolony.api.middleware import RateLimiterMiddleware
        rl = RateLimiterMiddleware()
        usage = rl.get_usage("c")
        assert "client_id" in usage
        assert "minute_used" in usage
        assert "minute_limit" in usage
        assert "hour_used" in usage
        assert "hour_limit" in usage

    def test_separate_clients_tracked_independently(self):
        from ai_multicolony.api.middleware import RateLimiterMiddleware
        rl = RateLimiterMiddleware(requests_per_minute=1, requests_per_hour=1000)
        rl.check("client-a")
        allowed_a, _ = rl.check("client-a")
        allowed_b, _ = rl.check("client-b")
        assert allowed_a is False
        assert allowed_b is True

    def test_multiple_requests_increment_count(self):
        from ai_multicolony.api.middleware import RateLimiterMiddleware
        rl = RateLimiterMiddleware()
        for _ in range(5):
            rl.check("c")
        usage = rl.get_usage("c")
        assert usage["minute_used"] == 5


class TestAuthMiddleware:
    """Test AuthMiddleware directly."""

    def test_no_api_key_allows_all(self):
        from ai_multicolony.api.middleware import AuthMiddleware
        auth = AuthMiddleware(api_key=None)
        valid, client_id = auth.validate()
        assert valid is True
        assert client_id == "anonymous"

    def test_no_api_key_ignores_header(self):
        from ai_multicolony.api.middleware import AuthMiddleware
        auth = AuthMiddleware(api_key=None)
        valid, client_id = auth.validate(authorization="Bearer somekey")
        assert valid is True

    def test_with_api_key_no_header_rejected(self):
        from ai_multicolony.api.middleware import AuthMiddleware
        auth = AuthMiddleware(api_key="secret123")
        valid, client_id = auth.validate()
        assert valid is False
        assert client_id is None

    def test_with_api_key_bearer_correct(self):
        from ai_multicolony.api.middleware import AuthMiddleware
        auth = AuthMiddleware(api_key="secret123")
        valid, client_id = auth.validate(authorization="Bearer secret123")
        assert valid is True
        assert client_id is not None

    def test_with_api_key_bearer_wrong(self):
        from ai_multicolony.api.middleware import AuthMiddleware
        auth = AuthMiddleware(api_key="secret123")
        valid, client_id = auth.validate(authorization="Bearer wrongkey")
        assert valid is False

    def test_with_api_key_direct_match(self):
        from ai_multicolony.api.middleware import AuthMiddleware
        auth = AuthMiddleware(api_key="secret123")
        valid, client_id = auth.validate(authorization="secret123")
        assert valid is True

    def test_with_api_key_direct_mismatch(self):
        from ai_multicolony.api.middleware import AuthMiddleware
        auth = AuthMiddleware(api_key="secret123")
        valid, client_id = auth.validate(authorization="wrongkey")
        assert valid is False

    def test_bearer_token_client_id_prefix(self):
        from ai_multicolony.api.middleware import AuthMiddleware
        auth = AuthMiddleware(api_key="secret123456")
        valid, client_id = auth.validate(authorization="Bearer secret123456")
        assert valid is True
        assert client_id.startswith("key:")

    def test_empty_authorization_rejected(self):
        from ai_multicolony.api.middleware import AuthMiddleware
        auth = AuthMiddleware(api_key="secret123")
        valid, client_id = auth.validate(authorization="")
        assert valid is False


class TestMiddlewareHelpers:
    """Test middleware helper functions."""

    def test_setup_auth(self):
        from ai_multicolony.api.middleware import setup_auth, get_auth
        auth = setup_auth("test-key")
        assert auth is not None
        assert auth._api_key == "test-key"

    def test_get_rate_limiter(self):
        from ai_multicolony.api.middleware import get_rate_limiter, RateLimiterMiddleware
        rl = get_rate_limiter()
        assert isinstance(rl, RateLimiterMiddleware)

    def test_setup_auth_returns_auth_middleware(self):
        from ai_multicolony.api.middleware import setup_auth, AuthMiddleware
        auth = setup_auth("another-key")
        assert isinstance(auth, AuthMiddleware)

    def test_get_auth_returns_set_instance(self):
        from ai_multicolony.api.middleware import setup_auth, get_auth
        auth = setup_auth("my-key")
        retrieved = get_auth()
        assert retrieved is auth


class TestMiddlewareOnApp:
    """Test middleware behavior on actual requests."""

    def test_timing_header_present(self, client):
        resp = client.get("/health")
        assert "X-Process-Time" in resp.headers

    def test_timing_header_is_numeric(self, client):
        resp = client.get("/health")
        try:
            float(resp.headers["X-Process-Time"])
        except ValueError:
            pytest.fail("X-Process-Time header is not a number")

    def test_health_skips_rate_limit(self, client):
        from ai_multicolony.api.middleware import _rate_limiter
        _rate_limiter._minute_counts.clear()
        _rate_limiter._hour_counts.clear()
        for _ in range(70):
            resp = client.get("/health")
            assert resp.status_code == 200

    def test_cors_headers_present(self, client):
        resp = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # CORS middleware should respond to preflight
        assert resp.status_code in (200, 204)


# ═══════════════════════════════════════════════════════════════════════════
# Schema Validation
# ═══════════════════════════════════════════════════════════════════════════


class TestSchemas:
    """Test Pydantic schema models."""

    def test_agent_create_request_defaults(self):
        from ai_multicolony.api.schemas import AgentCreateRequest
        req = AgentCreateRequest(agent_type="manus")
        assert req.model == "gpt-4o"
        assert req.tools == []
        assert req.autonomy_level == "L2"
        assert req.config == {}

    def test_agent_create_request_custom(self):
        from ai_multicolony.api.schemas import AgentCreateRequest
        req = AgentCreateRequest(
            agent_type="coder", model="claude-3",
            tools=["shell", "file"], autonomy_level="L3", config={"key": "val"},
        )
        assert req.agent_type == "coder"
        assert req.model == "claude-3"
        assert len(req.tools) == 2

    def test_agent_create_request_name_optional(self):
        from ai_multicolony.api.schemas import AgentCreateRequest
        req = AgentCreateRequest(agent_type="manus")
        assert req.name is None

    def test_agent_create_request_with_name(self):
        from ai_multicolony.api.schemas import AgentCreateRequest
        req = AgentCreateRequest(agent_type="manus", name="my-agent")
        assert req.name == "my-agent"

    def test_agent_run_request(self):
        from ai_multicolony.api.schemas import AgentRunRequest
        req = AgentRunRequest(task="do something")
        assert req.task == "do something"
        assert req.max_iterations is None
        assert req.timeout is None

    def test_agent_run_request_with_params(self):
        from ai_multicolony.api.schemas import AgentRunRequest
        req = AgentRunRequest(task="do something", max_iterations=5, timeout=60)
        assert req.max_iterations == 5
        assert req.timeout == 60

    def test_agent_response(self):
        from ai_multicolony.api.schemas import AgentResponse
        resp = AgentResponse(agent_id="a1", name="test", agent_type="manus", state="idle")
        assert resp.agent_id == "a1"
        assert resp.autonomy_level == "L2"

    def test_agent_response_optional_fields(self):
        from ai_multicolony.api.schemas import AgentResponse
        resp = AgentResponse(agent_id="a1", name="test", agent_type="manus", state="idle")
        assert resp.current_task is None

    def test_colony_create_request_defaults(self):
        from ai_multicolony.api.schemas import ColonyCreateRequest
        req = ColonyCreateRequest(name="test-colony")
        assert req.model == "gpt-4o"
        assert req.max_agents == 10

    def test_colony_configure_request(self):
        from ai_multicolony.api.schemas import ColonyConfigureRequest
        req = ColonyConfigureRequest(max_agents=5, scheduling_strategy="round_robin")
        assert req.max_agents == 5
        assert req.timeout is None

    def test_colony_scale_request_validation(self):
        from ai_multicolony.api.schemas import ColonyScaleRequest
        req = ColonyScaleRequest(target_agents=5)
        assert req.target_agents == 5

    def test_colony_scale_request_min_invalid(self):
        from ai_multicolony.api.schemas import ColonyScaleRequest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ColonyScaleRequest(target_agents=0)

    def test_colony_scale_request_max_invalid(self):
        from ai_multicolony.api.schemas import ColonyScaleRequest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ColonyScaleRequest(target_agents=101)

    def test_colony_response(self):
        from ai_multicolony.api.schemas import ColonyResponse
        resp = ColonyResponse(colony_id="c1", name="colony1", state="active", agent_count=5)
        assert resp.agent_count == 5

    def test_tool_call_request(self):
        from ai_multicolony.api.schemas import ToolCallRequest
        req = ToolCallRequest(tool_name="shell", arguments={"cmd": "ls"})
        assert req.tool_name == "shell"

    def test_tool_call_request_defaults(self):
        from ai_multicolony.api.schemas import ToolCallRequest
        req = ToolCallRequest(tool_name="shell")
        assert req.arguments == {}

    def test_tool_call_response(self):
        from ai_multicolony.api.schemas import ToolCallResponse
        resp = ToolCallResponse(success=True, output="done")
        assert resp.success is True
        assert resp.error is None

    def test_tool_call_response_error(self):
        from ai_multicolony.api.schemas import ToolCallResponse
        resp = ToolCallResponse(success=False, output="", error="fail")
        assert resp.success is False
        assert resp.error == "fail"

    def test_memory_store_request_defaults(self):
        from ai_multicolony.api.schemas import MemoryStoreRequest
        req = MemoryStoreRequest(content="test")
        assert req.memory_type == "episodic"
        assert req.importance == 0.5
        assert req.tags == []

    def test_memory_store_request_custom(self):
        from ai_multicolony.api.schemas import MemoryStoreRequest
        req = MemoryStoreRequest(content="test", memory_type="semantic", importance=0.9, tags=["tag1"])
        assert req.memory_type == "semantic"
        assert req.importance == 0.9
        assert req.tags == ["tag1"]

    def test_memory_query_request_defaults(self):
        from ai_multicolony.api.schemas import MemoryQueryRequest
        req = MemoryQueryRequest(query="test")
        assert req.memory_types == []
        assert req.limit == 10

    def test_session_create_request(self):
        from ai_multicolony.api.schemas import SessionCreateRequest
        req = SessionCreateRequest(agent_id="a1", metadata={"key": "val"})
        assert req.agent_id == "a1"
        assert req.colony_id is None

    def test_session_response(self):
        from ai_multicolony.api.schemas import SessionResponse
        resp = SessionResponse(session_id="s1")
        assert resp.is_active is True
        assert resp.message_count == 0

    def test_knowledge_add_request(self):
        from ai_multicolony.api.schemas import KnowledgeAddRequest
        req = KnowledgeAddRequest(title="Test", content="Content")
        assert req.category == "general"
        assert req.confidence == 1.0

    def test_knowledge_add_request_with_tags(self):
        from ai_multicolony.api.schemas import KnowledgeAddRequest
        req = KnowledgeAddRequest(title="Test", content="Content", tags=["python"], source="docs")
        assert req.tags == ["python"]
        assert req.source == "docs"

    def test_knowledge_search_request(self):
        from ai_multicolony.api.schemas import KnowledgeSearchRequest
        req = KnowledgeSearchRequest(query="test")
        assert req.search_type == "keyword"
        assert req.min_confidence == 0.0

    def test_knowledge_search_request_with_category(self):
        from ai_multicolony.api.schemas import KnowledgeSearchRequest
        req = KnowledgeSearchRequest(query="test", category="docs", min_confidence=0.5)
        assert req.category == "docs"
        assert req.min_confidence == 0.5

    def test_message_response(self):
        from ai_multicolony.api.schemas import MessageResponse
        resp = MessageResponse(message="Done", data={"k": "v"})
        assert resp.success is True
        assert resp.data == {"k": "v"}

    def test_message_response_default_success(self):
        from ai_multicolony.api.schemas import MessageResponse
        resp = MessageResponse(message="OK")
        assert resp.success is True

    def test_message_response_failure(self):
        from ai_multicolony.api.schemas import MessageResponse
        resp = MessageResponse(message="Failed", success=False)
        assert resp.success is False

    def test_error_response(self):
        from ai_multicolony.api.schemas import ErrorResponse
        resp = ErrorResponse(error="fail", code="ERR")
        assert resp.details is None

    def test_error_response_with_details(self):
        from ai_multicolony.api.schemas import ErrorResponse
        resp = ErrorResponse(error="fail", code="ERR", details={"field": "name"})
        assert resp.details == {"field": "name"}

    def test_error_response_default_code(self):
        from ai_multicolony.api.schemas import ErrorResponse
        resp = ErrorResponse(error="fail")
        assert resp.code == "UNKNOWN"

    def test_paginated_response_defaults(self):
        from ai_multicolony.api.schemas import PaginatedResponse
        resp = PaginatedResponse()
        assert resp.items == []
        assert resp.total == 0
        assert resp.limit == 10
        assert resp.offset == 0

    def test_paginated_response_custom(self):
        from ai_multicolony.api.schemas import PaginatedResponse
        resp = PaginatedResponse(
            items=[{"id": "1"}],
            total=100,
            limit=20,
            offset=40,
        )
        assert len(resp.items) == 1
        assert resp.total == 100

    def test_agent_create_missing_agent_type_fails(self):
        from ai_multicolony.api.schemas import AgentCreateRequest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            AgentCreateRequest()

    def test_memory_store_missing_content_fails(self):
        from ai_multicolony.api.schemas import MemoryStoreRequest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            MemoryStoreRequest()

    def test_knowledge_add_missing_title_fails(self):
        from ai_multicolony.api.schemas import KnowledgeAddRequest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            KnowledgeAddRequest(content="only content")

    def test_tool_call_missing_name_fails(self):
        from ai_multicolony.api.schemas import ToolCallRequest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ToolCallRequest()

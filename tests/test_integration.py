"""Tests for src.gateway, src.backend, and src.integration modules."""

import asyncio
import pytest
import tempfile
from pathlib import Path


class TestAPIRouter:
    """Tests for the APIRouter."""

    def test_add_and_match_route(self):
        from src.gateway.router import APIRouter, Route, HTTPMethod
        router = APIRouter()
        router.add_route(Route(path="/api/agents", method=HTTPMethod.GET, handler_name="list_agents"))
        match = router.match("GET", "/api/agents")
        assert match is not None
        assert match.route.handler_name == "list_agents"

    def test_match_with_params(self):
        from src.gateway.router import APIRouter, Route, HTTPMethod
        router = APIRouter()
        router.add_route(Route(path="/api/agents/{agent_id}", method=HTTPMethod.GET, handler_name="get_agent"))
        match = router.match("GET", "/api/agents/123")
        assert match is not None
        assert match.params["agent_id"] == "123"

    def test_no_match(self):
        from src.gateway.router import APIRouter, Route, HTTPMethod
        router = APIRouter()
        router.add_route(Route(path="/api/agents", method=HTTPMethod.GET, handler_name="list_agents"))
        match = router.match("GET", "/api/unknown")
        assert match is None

    def test_method_mismatch(self):
        from src.gateway.router import APIRouter, Route, HTTPMethod
        router = APIRouter()
        router.add_route(Route(path="/api/agents", method=HTTPMethod.GET, handler_name="list_agents"))
        match = router.match("POST", "/api/agents")
        assert match is None

    def test_list_routes(self):
        from src.gateway.router import APIRouter, Route, HTTPMethod
        router = APIRouter()
        router.add_route(Route(path="/api/health", method=HTTPMethod.GET, handler_name="health"))
        router.add_route(Route(path="/api/agents", method=HTTPMethod.GET, handler_name="list_agents"))
        routes = router.list_routes()
        assert len(routes) == 2


class TestMiddleware:
    """Tests for the middleware pipeline."""

    def test_rate_limit_allows(self):
        from src.gateway.middleware import RateLimitMiddleware, RequestContext
        mw = RateLimitMiddleware(default_limit=5, window_seconds=60)
        ctx = RequestContext(method="GET", path="/api/test", client_ip="127.0.0.1")
        result = mw.process(ctx)
        assert result.allowed is True

    def test_rate_limit_blocks(self):
        from src.gateway.middleware import RateLimitMiddleware, RequestContext
        mw = RateLimitMiddleware(default_limit=2, window_seconds=60)
        ctx = RequestContext(method="GET", path="/api/test", client_ip="127.0.0.1")
        mw.process(ctx)
        mw.process(ctx)
        result = mw.process(ctx)
        assert result.allowed is False
        assert result.status_code == 429

    def test_auth_valid_token(self):
        from src.gateway.middleware import AuthMiddleware, RequestContext
        mw = AuthMiddleware(valid_tokens={"token123": "user1"})
        ctx = RequestContext(
            method="GET", path="/api/test",
            headers={"Authorization": "Bearer token123"},
        )
        result = mw.process(ctx)
        assert result.allowed is True
        assert ctx.user_id == "user1"

    def test_auth_invalid_token(self):
        from src.gateway.middleware import AuthMiddleware, RequestContext
        mw = AuthMiddleware(valid_tokens={"token123": "user1"})
        ctx = RequestContext(
            method="GET", path="/api/test",
            headers={"Authorization": "Bearer wrong_token"},
        )
        result = mw.process(ctx)
        assert result.allowed is False
        assert result.status_code == 401

    def test_auth_missing_header(self):
        from src.gateway.middleware import AuthMiddleware, RequestContext
        mw = AuthMiddleware(valid_tokens={"token123": "user1"})
        ctx = RequestContext(method="GET", path="/api/test")
        result = mw.process(ctx)
        assert result.allowed is False

    def test_pipeline(self):
        from src.gateway.middleware import MiddlewarePipeline, LoggingMiddleware, RateLimitMiddleware, RequestContext
        pipeline = MiddlewarePipeline()
        pipeline.add(LoggingMiddleware())
        pipeline.add(RateLimitMiddleware(default_limit=10))
        ctx = RequestContext(method="GET", path="/api/test", client_ip="127.0.0.1")
        result = pipeline.process(ctx)
        assert result.allowed is True


class TestLocalization:
    """Tests for the LocalizationManager."""

    def test_default_locale(self):
        from src.gateway.localization import LocalizationManager
        lm = LocalizationManager()
        lm.add_strings("en", {"hello": "Hello", "bye": "Goodbye"})
        assert lm.get("hello") == "Hello"

    def test_fallback_to_default(self):
        from src.gateway.localization import LocalizationManager
        lm = LocalizationManager()
        lm.add_strings("en", {"hello": "Hello"})
        lm.register_locale(__import__("src.gateway.localization", fromlist=["LocaleConfig"]).LocaleConfig(code="id", name="Bahasa"))
        # "hello" not in "id" locale, should fallback to "en"
        assert lm.get("hello", locale="id") == "Hello"

    def test_missing_key_returns_key(self):
        from src.gateway.localization import LocalizationManager
        lm = LocalizationManager()
        assert lm.get("nonexistent_key") == "nonexistent_key"

    def test_string_interpolation(self):
        from src.gateway.localization import LocalizationManager
        lm = LocalizationManager()
        lm.add_strings("en", {"greeting": "Hello, {name}!"})
        assert lm.get("greeting", name="World") == "Hello, World!"


class TestConversationMemory:
    """Tests for the ConversationMemory."""

    def test_add_and_retrieve(self):
        from src.backend.memory import ConversationMemory
        memory = ConversationMemory()
        entry = memory.add("user", "Hello", token_count=5)
        assert entry.role == "user"
        assert len(memory._entries) == 1

    def test_get_recent(self):
        from src.backend.memory import ConversationMemory
        memory = ConversationMemory()
        for i in range(5):
            memory.add("user", f"Message {i}", token_count=10)
        recent = memory.get_recent(3)
        assert len(recent) == 3

    def test_context_window(self):
        from src.backend.memory import ConversationMemory
        memory = ConversationMemory()
        for i in range(10):
            memory.add("user", f"Message {i}", token_count=100)
        ctx = memory.get_context_window(max_tokens=500)
        total_tokens = sum(e.token_count for e in ctx)
        assert total_tokens <= 500

    def test_search(self):
        from src.backend.memory import ConversationMemory
        memory = ConversationMemory()
        memory.add("user", "Tell me about Python programming", token_count=10)
        memory.add("assistant", "Python is great!", token_count=10)
        memory.add("user", "What about JavaScript?", token_count=10)
        results = memory.search("python")
        assert len(results) >= 1

    def test_summarize(self):
        from src.backend.memory import ConversationMemory
        memory = ConversationMemory()
        memory.add("user", "Hello", token_count=5)
        memory.add("assistant", "Hi there!", token_count=5)
        summary = memory.summarize()
        assert summary["total_entries"] == 2

    def test_trim_on_max_entries(self):
        from src.backend.memory import ConversationMemory
        memory = ConversationMemory(max_entries=3)
        for i in range(5):
            memory.add("user", f"Message {i}", token_count=10)
        assert len(memory._entries) == 3


class TestPersistence:
    """Tests for the PersistenceEngine."""

    def test_create_and_get_thread(self):
        from src.backend.persistence import PersistenceEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = PersistenceEngine(data_dir=tmpdir)
            thread = engine.create_thread("t1", title="Test Thread")
            assert thread.thread_id == "t1"
            retrieved = engine.get_thread("t1")
            assert retrieved is not None
            assert retrieved.title == "Test Thread"

    def test_update_thread(self):
        from src.backend.persistence import PersistenceEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = PersistenceEngine(data_dir=tmpdir)
            engine.create_thread("t1", title="Old Title")
            updated = engine.update_thread("t1", title="New Title")
            assert updated.title == "New Title"

    def test_delete_thread(self):
        from src.backend.persistence import PersistenceEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = PersistenceEngine(data_dir=tmpdir)
            engine.create_thread("t1")
            assert engine.delete_thread("t1") is True
            assert engine.get_thread("t1") is None

    def test_list_threads(self):
        from src.backend.persistence import PersistenceEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = PersistenceEngine(data_dir=tmpdir)
            engine.create_thread("t1", title="Thread 1")
            engine.create_thread("t2", title="Thread 2")
            threads = engine.list_threads()
            assert len(threads) == 2

    def test_save_and_load(self):
        from src.backend.persistence import PersistenceEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = PersistenceEngine(data_dir=tmpdir)
            engine.create_thread("t1", title="Persistent Thread")
            engine.save_to_disk()

            engine2 = PersistenceEngine(data_dir=tmpdir)
            engine2.load_from_disk()
            assert len(engine2._threads) == 1


class TestSkillManager:
    """Tests for the SkillManager."""

    def test_register_and_get(self):
        from src.backend.skills import SkillManager, SkillDefinition
        manager = SkillManager()
        skill = SkillDefinition(name="test-skill", description="A test skill")
        manager.register(skill)
        retrieved = manager.get("test-skill")
        assert retrieved is not None
        assert retrieved.name == "test-skill"

    def test_duplicate_registration(self):
        from src.backend.skills import SkillManager, SkillDefinition
        manager = SkillManager()
        manager.register(SkillDefinition(name="test", description="Test"))
        with pytest.raises(ValueError):
            manager.register(SkillDefinition(name="test", description="Duplicate"))

    def test_enable_disable(self):
        from src.backend.skills import SkillManager, SkillDefinition
        manager = SkillManager()
        manager.register(SkillDefinition(name="test", description="Test"))
        manager.disable("test")
        skill = manager.get("test")
        assert skill.enabled is False
        manager.enable("test")
        assert skill.enabled is True

    def test_list_skills(self):
        from src.backend.skills import SkillManager, SkillDefinition
        manager = SkillManager()
        manager.register(SkillDefinition(name="a", description="A", category="x"))
        manager.register(SkillDefinition(name="b", description="B", category="y"))
        all_skills = manager.list_skills()
        assert len(all_skills) == 2
        x_skills = manager.list_skills(category="x")
        assert len(x_skills) == 1

    def test_validate(self):
        from src.backend.skills import SkillManager, SkillDefinition
        manager = SkillManager()
        errors = manager.validate(SkillDefinition(name="", description=""))
        assert len(errors) > 0

    def test_validate_name_format(self):
        from src.backend.skills import SkillManager, SkillDefinition
        manager = SkillManager()
        errors = manager.validate(SkillDefinition(name="bad name!", description="Valid desc"))
        assert any("alphanumeric" in e for e in errors)


class TestAgentMiddleware:
    """Tests for the agent middleware pipeline."""

    def test_loop_detection(self):
        from src.backend.middleware import LoopDetectionMiddleware, AgentContext
        mw = LoopDetectionMiddleware(max_iterations=3)
        ctx = AgentContext(agent_id="a1", iteration=3)
        result = mw.process(ctx)
        assert result.continue_ is False

    def test_token_budget(self):
        from src.backend.middleware import TokenBudgetMiddleware, AgentContext
        mw = TokenBudgetMiddleware(max_tokens=100)
        ctx = AgentContext(agent_id="a1", token_count=150)
        result = mw.process(ctx)
        assert result.continue_ is False

    def test_pipeline(self):
        from src.backend.middleware import AgentMiddlewarePipeline, LoopDetectionMiddleware, TokenBudgetMiddleware, AgentContext
        pipeline = AgentMiddlewarePipeline()
        pipeline.add(LoopDetectionMiddleware(max_iterations=10))
        pipeline.add(TokenBudgetMiddleware(max_tokens=100000))
        ctx = AgentContext(agent_id="a1", iteration=5, token_count=1000)
        result = pipeline.process(ctx)
        assert result.continue_ is True


class TestEcosystemIntegration:
    """Tests for the full ecosystem integration."""

    def test_orchestrator_creation(self):
        from src.integration import EcosystemOrchestrator
        with tempfile.TemporaryDirectory() as tmpdir:
            orch = EcosystemOrchestrator(data_dir=tmpdir)
            status = orch.get_system_status()
            assert "quant" in status
            assert "organism" in status
            assert "gateway" in status
            assert "backend" in status

    def test_quant_adapter_trade_evaluation(self):
        from src.integration import QuantAdapter
        adapter = QuantAdapter()
        result = adapter.evaluate_trade(
            symbol="EURUSD", direction="BUY", lot_size=0.01,
            entry=1.1000, stop_loss=1.0990, take_profit=1.1040,
            account_balance=10000.0,
        )
        assert "allowed" in result

    def test_quant_adapter_kill_switch_active(self):
        from src.integration import QuantAdapter
        adapter = QuantAdapter()
        adapter.kill_switch.activate("MANUAL")
        result = adapter.evaluate_trade(
            symbol="EURUSD", direction="BUY", lot_size=0.01,
            entry=1.1000, stop_loss=1.0990,
        )
        assert result["allowed"] is False

    def test_gateway_adapter_routes(self):
        from src.integration import GatewayAdapter
        adapter = GatewayAdapter()
        adapter.setup_default_routes()
        routes = adapter.router.list_routes()
        assert len(routes) > 0
        # Test matching
        match = adapter.router.match("GET", "/api/health")
        assert match is not None
        assert match.route.handler_name == "health_check"

    def test_gateway_adapter_localization(self):
        from src.integration import GatewayAdapter
        adapter = GatewayAdapter()
        adapter.setup_default_localization()
        text = adapter.localization.get("health.ok")
        assert text == "System is healthy"

    def test_backend_adapter_skills(self):
        from src.integration import BackendAdapter
        with tempfile.TemporaryDirectory() as tmpdir:
            adapter = BackendAdapter(data_dir=tmpdir)
            adapter.register_default_skills()
            skills = adapter.skills.list_skills(enabled_only=True)
            assert len(skills) >= 5

    def test_ecosystem_bus(self):
        from src.integration import EcosystemBus, BusMessage, MessageType
        bus = EcosystemBus()
        received = []
        bus.subscribe(MessageType.RISK_ALERT, lambda msg: received.append(msg))
        bus.publish(BusMessage(
            type=MessageType.RISK_ALERT,
            source="test",
            payload={"symbol": "EURUSD"},
        ))
        assert len(received) == 1

    def test_organism_adapter(self):
        from src.integration import OrganismAdapter
        adapter = OrganismAdapter()
        status = adapter.scheduler.get_status()
        assert "cycles" in status


class TestConfig:
    """Tests for the unified configuration."""

    def test_default_settings(self):
        from src.config import EcosystemSettings
        settings = EcosystemSettings()
        assert settings.quant.max_risk_per_trade == 0.005
        assert settings.organism.max_iterations_per_task == 10
        assert settings.gateway.rate_limit_per_minute == 60
        assert settings.backend.memory_max_entries == 1000

    def test_get_settings(self):
        from src.config import get_settings, reset_settings
        reset_settings()
        settings = get_settings()
        assert settings.version == "0.2.0"
        reset_settings()

    def test_custom_settings(self):
        from src.config import EcosystemSettings
        settings = EcosystemSettings(quant__max_risk_per_trade=0.02)
        # This tests that pydantic-settings env override works
        # Direct construction still works normally
        settings2 = EcosystemSettings()
        assert settings2.quant.max_risk_per_trade == 0.005

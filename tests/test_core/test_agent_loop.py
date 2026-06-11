"""Tests for AgentLoop — loop execution, hooks, state management."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from ai_multicolony.core.agent_loop import AgentLoop, LoopConfig, LoopResult, LoopState
from ai_multicolony.core.event_bus import EventBus
from ai_multicolony.core.llm_provider import LLMProvider, LLMResponse, LLMUsage
from ai_multicolony.core.tool_registry import ToolRegistry
from ai_multicolony.exceptions import AgentError, AgentTimeoutError
from ai_multicolony.types.messages import Message, MessageRole


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_singletons():
    EventBus.reset()
    ToolRegistry.reset()
    yield
    EventBus.reset()
    ToolRegistry.reset()


@pytest.fixture
def mock_llm_provider():
    provider = MagicMock(spec=LLMProvider)
    provider.chat = AsyncMock(return_value=LLMResponse(
        content="Done",
        tool_calls=[],
        usage=LLMUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        model="gpt-4o",
        cost=0.001,
    ))
    return provider


@pytest.fixture
def loop(mock_llm_provider):
    bus = EventBus()
    return AgentLoop(
        agent_id="test-agent",
        config=LoopConfig(max_iterations=5, pause_between_iterations=0.0),
        event_bus=bus,
        llm_provider=mock_llm_provider,
    )


# ── LoopConfig ────────────────────────────────────────────────────────────

class TestLoopConfig:
    """Test LoopConfig defaults."""

    def test_defaults(self):
        config = LoopConfig()
        assert config.max_iterations == 10
        assert config.timeout == 300.0
        assert config.retry_on_error is True
        assert config.max_retries == 3


# ── LoopState ─────────────────────────────────────────────────────────────

class TestLoopState:
    """Test LoopState enum."""

    def test_states(self):
        assert LoopState.IDLE.value == "idle"
        assert LoopState.PROCESSING.value == "processing"
        assert LoopState.COMPLETED.value == "completed"
        assert LoopState.ERROR.value == "error"


# ── LoopResult ────────────────────────────────────────────────────────────

class TestLoopResult:
    """Test LoopResult dataclass."""

    def test_defaults(self):
        result = LoopResult()
        assert result.success is True
        assert result.final_response == ""
        assert result.iterations == 0
        assert result.errors == []


# ── AgentLoop Core ────────────────────────────────────────────────────────

class TestAgentLoopCore:
    """Test basic loop operations."""

    @pytest.mark.asyncio
    async def test_run_completes(self, loop, mock_llm_provider):
        result = await loop.run("Do something")
        assert isinstance(result, LoopResult)
        assert result.success is True
        assert result.final_response == "Done"

    @pytest.mark.asyncio
    async def test_run_sets_state_to_completed(self, loop, mock_llm_provider):
        await loop.run("Do something")
        assert loop.state == LoopState.COMPLETED

    @pytest.mark.asyncio
    async def test_run_tracks_iterations(self, loop, mock_llm_provider):
        await loop.run("Do something")
        assert loop.iteration >= 1

    @pytest.mark.asyncio
    async def test_run_tracks_tokens(self, loop, mock_llm_provider):
        result = await loop.run("Do something")
        assert result.total_tokens > 0

    @pytest.mark.asyncio
    async def test_run_tracks_cost(self, loop, mock_llm_provider):
        result = await loop.run("Do something")
        assert result.total_cost > 0

    @pytest.mark.asyncio
    async def test_run_with_system_prompt(self, loop, mock_llm_provider):
        result = await loop.run("Do something", system_prompt="You are a test assistant.")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_run_without_llm_provider_raises(self):
        """Running without LLM provider should raise an error."""
        loop_no_llm = AgentLoop(agent_id="test-agent")
        with pytest.raises(Exception):
            # Either AgentError or AttributeError depending on setup
            await loop_no_llm.run("Do something")


# ── Hooks ─────────────────────────────────────────────────────────────────

class TestAgentLoopHooks:
    """Test lifecycle hooks."""

    @pytest.mark.asyncio
    async def test_pre_iteration_hook(self, loop, mock_llm_provider):
        calls = []
        loop.add_hook("pre_iteration", lambda **kw: calls.append(kw))
        await loop.run("Do something")
        assert len(calls) >= 1

    @pytest.mark.asyncio
    async def test_post_iteration_hook(self, loop, mock_llm_provider):
        calls = []
        loop.add_hook("post_iteration", lambda **kw: calls.append(kw))
        await loop.run("Do something")
        assert len(calls) >= 1

    @pytest.mark.asyncio
    async def test_async_hook(self, loop, mock_llm_provider):
        calls = []
        async def async_hook(**kw):
            calls.append(kw)

        loop.add_hook("pre_iteration", async_hook)
        await loop.run("Do something")
        assert len(calls) >= 1

    @pytest.mark.asyncio
    async def test_hook_error_does_not_break_loop(self, loop, mock_llm_provider):
        def bad_hook(**kw):
            raise RuntimeError("Hook error")

        loop.add_hook("pre_iteration", bad_hook)
        result = await loop.run("Do something")
        assert result.success is True


# ── Control Methods ───────────────────────────────────────────────────────

class TestAgentLoopControl:
    """Test pause, resume, reset."""

    def test_pause(self, loop):
        loop.pause()
        assert loop.state == LoopState.PAUSED

    def test_resume(self, loop):
        loop.pause()
        loop.resume()
        assert loop.state == LoopState.PROCESSING

    def test_reset(self, loop):
        loop._iteration = 5
        loop._total_tokens = 100
        loop.reset()
        assert loop.state == LoopState.IDLE
        assert loop.iteration == 0
        assert loop._total_tokens == 0


# ── Stats ─────────────────────────────────────────────────────────────────

class TestAgentLoopStats:
    """Test stats reporting."""

    @pytest.mark.asyncio
    async def test_stats_after_run(self, loop, mock_llm_provider):
        await loop.run("Do something")
        stats = loop.get_stats()
        assert stats["state"] == "completed"
        assert stats["iteration"] >= 1
        assert stats["total_tokens"] > 0
        assert stats["message_count"] > 0

    def test_stats_initial(self, loop):
        stats = loop.get_stats()
        assert stats["state"] == "idle"
        assert stats["iteration"] == 0

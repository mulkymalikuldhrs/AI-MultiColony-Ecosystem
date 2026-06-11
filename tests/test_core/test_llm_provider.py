"""Tests for LLMProvider — chat, cost tracking, retry logic."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_multicolony.core.llm_provider import CostTracker, LLMProvider, LLMResponse, LLMUsage
from ai_multicolony.exceptions import LLMError, LLMRateLimitError, LLMTokensExceededError


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def provider():
    """Create an LLMProvider with low cost limit for testing."""
    return LLMProvider(default_model="gpt-4o", cost_limit_daily=10.0)


# ── LLMUsage ───────────────────────────────────────────────────────────────

class TestLLMUsage:
    """Test LLMUsage dataclass."""

    def test_default_values(self):
        usage = LLMUsage()
        assert usage.prompt_tokens == 0
        assert usage.completion_tokens == 0
        assert usage.total_tokens == 0

    def test_addition(self):
        u1 = LLMUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        u2 = LLMUsage(prompt_tokens=5, completion_tokens=10, total_tokens=15)
        result = u1 + u2
        assert result.prompt_tokens == 15
        assert result.completion_tokens == 30
        assert result.total_tokens == 45


# ── LLMResponse ────────────────────────────────────────────────────────────

class TestLLMResponse:
    """Test LLMResponse dataclass."""

    def test_default_values(self):
        resp = LLMResponse()
        assert resp.content == ""
        assert resp.tool_calls == []
        assert resp.cost == 0.0

    def test_custom_values(self):
        resp = LLMResponse(content="Hello", model="gpt-4o", cost=0.002)
        assert resp.content == "Hello"
        assert resp.model == "gpt-4o"


# ── CostTracker ────────────────────────────────────────────────────────────

class TestCostTracker:
    """Test cost tracking."""

    def test_calculate_cost_known_model(self):
        tracker = CostTracker()
        usage = LLMUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
        cost = tracker.calculate_cost("gpt-4o", usage)
        assert cost > 0
        # gpt-4o: input $0.0025/1K, output $0.01/1K
        expected = (1000 / 1000) * 0.0025 + (500 / 1000) * 0.01
        assert abs(cost - expected) < 0.0001

    def test_calculate_cost_unknown_model(self):
        tracker = CostTracker()
        usage = LLMUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
        cost = tracker.calculate_cost("unknown-model", usage)
        assert cost > 0  # Uses default rates

    def test_record_cost(self):
        tracker = CostTracker()
        usage = LLMUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
        cost = tracker.calculate_cost("gpt-4o", usage)
        tracker.record("gpt-4o", usage, cost)
        assert tracker.total_cost == cost
        assert tracker.get_daily_cost() == cost

    def test_per_model_costs(self):
        tracker = CostTracker()
        tracker.record("gpt-4o", LLMUsage(total_tokens=100), 0.01)
        tracker.record("gpt-4o", LLMUsage(total_tokens=200), 0.02)
        assert tracker.per_model_costs["gpt-4o"] == pytest.approx(0.03)


# ── LLMProvider Init ──────────────────────────────────────────────────────

class TestLLMProviderInit:
    """Test provider initialization."""

    def test_default_config(self):
        p = LLMProvider()
        assert p.default_model == "gpt-4o"
        assert p.temperature == 0.1
        assert p.max_tokens == 4096
        assert p.max_retries == 3
        assert p.cost_limit_daily == 100.0

    def test_custom_config(self):
        p = LLMProvider(default_model="claude-3-opus", max_retries=5, cost_limit_daily=50.0)
        assert p.default_model == "claude-3-opus"
        assert p.max_retries == 5
        assert p.cost_limit_daily == 50.0


# ── Chat ───────────────────────────────────────────────────────────────────

class TestChat:
    """Test chat method."""

    @pytest.mark.asyncio
    async def test_chat_uses_mock_when_no_litellm(self, provider):
        """When litellm is not installed, should use mock completion."""
        result = await provider.chat(
            messages=[{"role": "user", "content": "Hello"}],
            model="gpt-4o",
        )
        assert isinstance(result, LLMResponse)
        assert "Mock response" in result.content

    @pytest.mark.asyncio
    async def test_chat_tracks_cost(self, provider):
        initial_cost = provider.cost_tracker.total_cost
        await provider.chat(messages=[{"role": "user", "content": "Hello"}])
        assert provider.cost_tracker.total_cost > initial_cost

    @pytest.mark.asyncio
    async def test_chat_increments_call_count(self, provider):
        assert provider._call_count == 0
        await provider.chat(messages=[{"role": "user", "content": "Hello"}])
        assert provider._call_count == 1

    @pytest.mark.asyncio
    async def test_cost_limit_exceeded(self):
        p = LLMProvider(cost_limit_daily=0.0001)  # Very small limit
        # Record a cost that exceeds the limit
        p.cost_tracker.record("gpt-4o", LLMUsage(total_tokens=1), 0.01)
        with pytest.raises(LLMTokensExceededError):
            await p.chat(messages=[{"role": "user", "content": "Hello"}])

    @pytest.mark.asyncio
    async def test_chat_model_override(self, provider):
        result = await provider.chat(
            messages=[{"role": "user", "content": "Hello"}],
            model="gpt-3.5-turbo",
        )
        assert result.model == "gpt-3.5-turbo"

    @pytest.mark.asyncio
    async def test_chat_with_tools(self, provider):
        tools = [{"type": "function", "function": {"name": "test", "parameters": {}}}]
        result = await provider.chat(
            messages=[{"role": "user", "content": "Hello"}],
            tools=tools,
        )
        assert isinstance(result, LLMResponse)


# ── Token Counting ─────────────────────────────────────────────────────────

class TestTokenCounting:
    """Test token estimation."""

    def test_count_tokens(self, provider):
        messages = [
            {"role": "user", "content": "Hello, world!"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        count = provider._count_tokens(messages)
        assert count > 0

    def test_count_tokens_empty(self, provider):
        count = provider._count_tokens([])
        assert count >= 0


# ── Stats ──────────────────────────────────────────────────────────────────

class TestStats:
    """Test statistics."""

    @pytest.mark.asyncio
    async def test_get_stats(self, provider):
        await provider.chat(messages=[{"role": "user", "content": "Hello"}])
        stats = provider.get_stats()
        assert stats["total_calls"] == 1
        assert stats["total_cost"] > 0
        assert stats["default_model"] == "gpt-4o"

    def test_reset_stats(self, provider):
        provider._call_count = 5
        provider.reset_stats()
        assert provider._call_count == 0
        assert provider.cost_tracker.total_cost == 0.0


# ── Mock Completion ────────────────────────────────────────────────────────

class TestMockCompletion:
    """Test the mock completion fallback."""

    @pytest.mark.asyncio
    async def test_mock_returns_last_user_content(self, provider):
        result = await provider.chat(
            messages=[
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "Test query"},
            ],
        )
        assert "Test query" in result.content

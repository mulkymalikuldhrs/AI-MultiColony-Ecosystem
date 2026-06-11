"""Comprehensive tests for LLMProvider.

Tests cover:
- LLMUsage dataclass and addition
- LLMResponse dataclass
- CostTracker calculation and recording
- LLMProvider initialization
- Chat completion (mocked)
- Token counting
- Retry logic
- Cost tracking and limits
- Streaming (mocked)
- Statistics and reset
- Model-specific cost rates
"""

from __future__ import annotations

import asyncio
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_multicolony.core.llm_provider import CostTracker, LLMProvider, LLMResponse, LLMUsage
from ai_multicolony.exceptions import LLMError, LLMRateLimitError, LLMTokensExceededError


# ══════════════════════════════════════════════════════════════════════
# 1. LLMUsage
# ══════════════════════════════════════════════════════════════════════


class TestLLMUsage:
    """Test LLMUsage dataclass."""

    def test_default_values(self):
        usage = LLMUsage()
        assert usage.prompt_tokens == 0
        assert usage.completion_tokens == 0
        assert usage.total_tokens == 0

    def test_custom_values(self):
        usage = LLMUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150

    def test_add_two_usages(self):
        u1 = LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        u2 = LLMUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30)
        result = u1 + u2
        assert result.prompt_tokens == 30
        assert result.completion_tokens == 15
        assert result.total_tokens == 45

    def test_add_zero_usage(self):
        u1 = LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        u2 = LLMUsage()
        result = u1 + u2
        assert result.prompt_tokens == 10
        assert result.completion_tokens == 5
        assert result.total_tokens == 15

    def test_add_does_not_mutate_original(self):
        u1 = LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        u2 = LLMUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30)
        _ = u1 + u2
        assert u1.prompt_tokens == 10
        assert u2.prompt_tokens == 20


# ══════════════════════════════════════════════════════════════════════
# 2. LLMResponse
# ══════════════════════════════════════════════════════════════════════


class TestLLMResponse:
    """Test LLMResponse dataclass."""

    def test_default_values(self):
        resp = LLMResponse()
        assert resp.content == ""
        assert resp.tool_calls == []
        assert resp.model == ""
        assert resp.cost == 0.0
        assert resp.latency == 0.0
        assert resp.finish_reason is None
        assert resp.raw_response is None

    def test_custom_values(self):
        resp = LLMResponse(
            content="Hello!",
            model="gpt-4o",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            cost=0.001,
            latency=0.5,
            finish_reason="stop",
        )
        assert resp.content == "Hello!"
        assert resp.model == "gpt-4o"
        assert resp.usage.total_tokens == 15
        assert resp.cost == 0.001
        assert resp.finish_reason == "stop"

    def test_response_with_tool_calls(self):
        resp = LLMResponse(
            content="",
            tool_calls=[{"id": "call-1", "type": "function", "function": {"name": "test", "arguments": "{}"}}],
        )
        assert len(resp.tool_calls) == 1
        assert resp.tool_calls[0]["function"]["name"] == "test"


# ══════════════════════════════════════════════════════════════════════
# 3. CostTracker
# ══════════════════════════════════════════════════════════════════════


class TestCostTracker:
    """Test CostTracker calculation and recording."""

    def test_calculate_cost_gpt4o(self):
        tracker = CostTracker()
        usage = LLMUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
        cost = tracker.calculate_cost("gpt-4o", usage)
        # gpt-4o: input $0.0025/1K, output $0.01/1K
        expected = (1000 / 1000) * 0.0025 + (500 / 1000) * 0.01
        assert abs(cost - expected) < 0.0001

    def test_calculate_cost_gpt4_turbo(self):
        tracker = CostTracker()
        usage = LLMUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
        cost = tracker.calculate_cost("gpt-4-turbo", usage)
        expected = (1000 / 1000) * 0.01 + (500 / 1000) * 0.03
        assert abs(cost - expected) < 0.0001

    def test_calculate_cost_claude3_sonnet(self):
        tracker = CostTracker()
        usage = LLMUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
        cost = tracker.calculate_cost("claude-3-sonnet", usage)
        expected = (1000 / 1000) * 0.003 + (500 / 1000) * 0.015
        assert abs(cost - expected) < 0.0001

    def test_calculate_cost_unknown_model(self):
        tracker = CostTracker()
        usage = LLMUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
        cost = tracker.calculate_cost("unknown-model-xyz", usage)
        # Default rates: input $0.001/1K, output $0.002/1K
        expected = (1000 / 1000) * 0.001 + (500 / 1000) * 0.002
        assert abs(cost - expected) < 0.0001

    def test_calculate_cost_partial_model_match(self):
        tracker = CostTracker()
        usage = LLMUsage(prompt_tokens=1000, completion_tokens=0, total_tokens=1000)
        # "openai/claude-3-haiku" should match "claude-3-haiku"
        cost = tracker.calculate_cost("openai/claude-3-haiku", usage)
        expected = (1000 / 1000) * 0.00025
        assert abs(cost - expected) < 0.0001

    def test_record_cost(self):
        tracker = CostTracker()
        usage = LLMUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        cost = 0.005
        tracker.record("gpt-4o", usage, cost)
        assert tracker.total_cost == 0.005
        assert "gpt-4o" in tracker.per_model_costs
        assert tracker.per_model_costs["gpt-4o"] == 0.005

    def test_record_multiple_costs(self):
        tracker = CostTracker()
        usage = LLMUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        tracker.record("gpt-4o", usage, 0.005)
        tracker.record("gpt-4o", usage, 0.003)
        assert tracker.total_cost == 0.008
        assert tracker.per_model_costs["gpt-4o"] == 0.008

    def test_daily_cost(self):
        tracker = CostTracker()
        usage = LLMUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        tracker.record("gpt-4o", usage, 0.005)
        assert tracker.get_daily_cost() == 0.005

    def test_daily_cost_no_records(self):
        tracker = CostTracker()
        assert tracker.get_daily_cost() == 0.0

    def test_per_model_tokens_tracking(self):
        tracker = CostTracker()
        usage1 = LLMUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        usage2 = LLMUsage(prompt_tokens=200, completion_tokens=100, total_tokens=300)
        tracker.record("gpt-4o", usage1, 0.005)
        tracker.record("gpt-4o", usage2, 0.008)
        assert "gpt-4o" in tracker.per_model_tokens

    def test_record_multiple_models(self):
        tracker = CostTracker()
        usage = LLMUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        tracker.record("gpt-4o", usage, 0.005)
        tracker.record("claude-3-opus", usage, 0.010)
        assert "gpt-4o" in tracker.per_model_costs
        assert "claude-3-opus" in tracker.per_model_costs
        assert tracker.total_cost == 0.015


# ══════════════════════════════════════════════════════════════════════
# 4. LLMProvider Initialization
# ══════════════════════════════════════════════════════════════════════


class TestLLMProviderInit:
    """Test LLMProvider initialization."""

    def test_default_model(self):
        provider = LLMProvider()
        assert provider.default_model == "gpt-4o"

    def test_default_temperature(self):
        provider = LLMProvider()
        assert provider.temperature == 0.1

    def test_default_max_tokens(self):
        provider = LLMProvider()
        assert provider.max_tokens == 4096

    def test_default_max_retries(self):
        provider = LLMProvider()
        assert provider.max_retries == 3

    def test_default_timeout(self):
        provider = LLMProvider()
        assert provider.timeout == 120

    def test_default_cost_limit(self):
        provider = LLMProvider()
        assert provider.cost_limit_daily == 100.0

    def test_custom_model(self):
        provider = LLMProvider(default_model="claude-3-opus")
        assert provider.default_model == "claude-3-opus"

    def test_custom_temperature(self):
        provider = LLMProvider(temperature=0.7)
        assert provider.temperature == 0.7

    def test_custom_max_tokens(self):
        provider = LLMProvider(max_tokens=8192)
        assert provider.max_tokens == 8192

    def test_custom_cost_limit(self):
        provider = LLMProvider(cost_limit_daily=50.0)
        assert provider.cost_limit_daily == 50.0

    def test_custom_max_retries(self):
        provider = LLMProvider(max_retries=5)
        assert provider.max_retries == 5


# ══════════════════════════════════════════════════════════════════════
# 5. Chat Completion (Mocked)
# ══════════════════════════════════════════════════════════════════════


class TestLLMProviderChat:
    """Test chat completion with mock backend."""

    @pytest.mark.asyncio
    async def test_chat_returns_response(self, llm_provider):
        response = await llm_provider.chat(
            messages=[{"role": "user", "content": "Hello"}],
        )
        assert isinstance(response, LLMResponse)
        assert response.content

    @pytest.mark.asyncio
    async def test_chat_default_model(self, llm_provider):
        response = await llm_provider.chat(
            messages=[{"role": "user", "content": "Hello"}],
        )
        assert response.model == "gpt-4o"

    @pytest.mark.asyncio
    async def test_chat_override_model(self, llm_provider):
        response = await llm_provider.chat(
            messages=[{"role": "user", "content": "Hello"}],
            model="gpt-3.5-turbo",
        )
        assert response.model == "gpt-3.5-turbo"

    @pytest.mark.asyncio
    async def test_chat_tracks_usage(self, llm_provider):
        response = await llm_provider.chat(
            messages=[{"role": "user", "content": "Hello"}],
        )
        assert response.usage.total_tokens > 0
        assert response.usage.prompt_tokens >= 0
        assert response.usage.completion_tokens > 0

    @pytest.mark.asyncio
    async def test_chat_tracks_cost(self, llm_provider):
        await llm_provider.chat(
            messages=[{"role": "user", "content": "Hello"}],
        )
        assert llm_provider.cost_tracker.total_cost > 0

    @pytest.mark.asyncio
    async def test_chat_increments_call_count(self, llm_provider):
        await llm_provider.chat(messages=[{"role": "user", "content": "Hi"}])
        assert llm_provider._call_count == 1
        await llm_provider.chat(messages=[{"role": "user", "content": "Hi again"}])
        assert llm_provider._call_count == 2

    @pytest.mark.asyncio
    async def test_chat_has_latency(self, llm_provider):
        response = await llm_provider.chat(
            messages=[{"role": "user", "content": "Hello"}],
        )
        assert response.latency >= 0

    @pytest.mark.asyncio
    async def test_chat_with_tools(self, llm_provider):
        tools = [{"type": "function", "function": {"name": "test", "description": "Test", "parameters": {}}}]
        response = await llm_provider.chat(
            messages=[{"role": "user", "content": "Hello"}],
            tools=tools,
        )
        assert isinstance(response, LLMResponse)

    @pytest.mark.asyncio
    async def test_chat_with_tool_choice(self, llm_provider):
        response = await llm_provider.chat(
            messages=[{"role": "user", "content": "Hello"}],
            tool_choice={"type": "auto"},
        )
        assert isinstance(response, LLMResponse)

    @pytest.mark.asyncio
    async def test_chat_with_custom_temperature(self, llm_provider):
        response = await llm_provider.chat(
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.9,
        )
        assert isinstance(response, LLMResponse)

    @pytest.mark.asyncio
    async def test_chat_with_custom_max_tokens(self, llm_provider):
        response = await llm_provider.chat(
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=100,
        )
        assert isinstance(response, LLMResponse)

    @pytest.mark.asyncio
    async def test_mock_response_content(self, llm_provider):
        response = await llm_provider.chat(
            messages=[{"role": "user", "content": "What is 2+2?"}],
        )
        # Mock response includes the user content
        assert "Mock response" in response.content or "2+2" in response.content


# ══════════════════════════════════════════════════════════════════════
# 6. Token Counting
# ══════════════════════════════════════════════════════════════════════


class TestTokenCounting:
    """Test token counting heuristic."""

    def test_count_tokens_basic(self, llm_provider):
        count = llm_provider._count_tokens([{"role": "user", "content": "Hello world"}])
        assert count > 0

    def test_count_tokens_empty_messages(self, llm_provider):
        count = llm_provider._count_tokens([])
        assert count == 0

    def test_count_tokens_multiple_messages(self, llm_provider):
        messages = [
            {"role": "system", "content": "You are a helper."},
            {"role": "user", "content": "Hello"},
        ]
        count = llm_provider._count_tokens(messages)
        assert count > 0

    def test_count_tokens_increases_with_content(self, llm_provider):
        short = llm_provider._count_tokens([{"role": "user", "content": "Hi"}])
        long = llm_provider._count_tokens([{"role": "user", "content": "This is a much longer message with more tokens"}])
        assert long >= short


# ══════════════════════════════════════════════════════════════════════
# 7. Retry Logic
# ══════════════════════════════════════════════════════════════════════


class TestLLMProviderRetry:
    """Test retry logic with mocked failures."""

    @pytest.mark.asyncio
    async def test_retry_on_rate_limit(self, llm_provider):
        call_count = 0

        async def mock_call(kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("rate_limit exceeded")
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content="Success", tool_calls=None),
                        finish_reason="stop",
                    )
                ],
                usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            )

        with patch.object(llm_provider, '_call_litellm', side_effect=mock_call):
            response = await llm_provider.chat(
                messages=[{"role": "user", "content": "Hello"}],
            )
            assert response.content == "Success"
            assert call_count == 2

    @pytest.mark.asyncio
    async def test_retry_on_generic_error(self, llm_provider):
        call_count = 0

        async def mock_call(kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Connection error")
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content="Success", tool_calls=None),
                        finish_reason="stop",
                    )
                ],
                usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            )

        with patch.object(llm_provider, '_call_litellm', side_effect=mock_call):
            response = await llm_provider.chat(
                messages=[{"role": "user", "content": "Hello"}],
            )
            assert response.content == "Success"
            assert call_count == 3

    @pytest.mark.asyncio
    async def test_raises_after_max_retries(self, llm_provider):
        async def mock_call(kwargs):
            raise Exception("Persistent error")

        with patch.object(llm_provider, '_call_litellm', side_effect=mock_call):
            with pytest.raises(LLMError, match="failed after"):
                await llm_provider.chat(
                    messages=[{"role": "user", "content": "Hello"}],
                )

    @pytest.mark.asyncio
    async def test_context_length_error_raises_immediately(self, llm_provider):
        async def mock_call(kwargs):
            raise Exception("context_length exceeded")

        with patch.object(llm_provider, '_call_litellm', side_effect=mock_call):
            with pytest.raises(LLMTokensExceededError):
                await llm_provider.chat(
                    messages=[{"role": "user", "content": "Hello"}],
                )

    @pytest.mark.asyncio
    async def test_token_exceeded_error_in_chat(self, llm_provider):
        async def mock_call(kwargs):
            raise Exception("token limit exceeded")

        with patch.object(llm_provider, '_call_litellm', side_effect=mock_call):
            with pytest.raises(LLMTokensExceededError):
                await llm_provider.chat(
                    messages=[{"role": "user", "content": "Hello"}],
                )


# ══════════════════════════════════════════════════════════════════════
# 8. Cost Limit
# ══════════════════════════════════════════════════════════════════════


class TestCostLimit:
    """Test daily cost limit enforcement."""

    def test_check_cost_limit_below(self, llm_provider):
        llm_provider.cost_limit_daily = 100.0
        llm_provider._check_cost_limit()  # Should not raise

    def test_check_cost_limit_exceeded(self):
        provider = LLMProvider(cost_limit_daily=0.001)
        usage = LLMUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        provider.cost_tracker.record("gpt-4o", usage, 1.0)
        with pytest.raises(LLMTokensExceededError):
            provider._check_cost_limit()

    @pytest.mark.asyncio
    async def test_chat_refuses_when_cost_exceeded(self):
        provider = LLMProvider(cost_limit_daily=0.001)
        usage = LLMUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        provider.cost_tracker.record("gpt-4o", usage, 1.0)
        with pytest.raises(LLMTokensExceededError):
            await provider.chat(messages=[{"role": "user", "content": "Hello"}])


# ══════════════════════════════════════════════════════════════════════
# 9. Streaming (Mocked)
# ══════════════════════════════════════════════════════════════════════


class TestLLMProviderStreaming:
    """Test streaming chat completion."""

    @pytest.mark.asyncio
    async def test_stream_yields_content(self, llm_provider):
        chunks = []
        async for chunk in llm_provider.chat_stream(
            messages=[{"role": "user", "content": "Hello"}],
        ):
            chunks.append(chunk)
        assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_stream_default_model(self, llm_provider):
        chunks = []
        async for chunk in llm_provider.chat_stream(
            messages=[{"role": "user", "content": "Hello"}],
        ):
            chunks.append(chunk)
        # Mock streaming returns a single chunk
        assert any("Mock" in c for c in chunks)

    @pytest.mark.asyncio
    async def test_stream_custom_model(self, llm_provider):
        chunks = []
        async for chunk in llm_provider.chat_stream(
            messages=[{"role": "user", "content": "Hello"}],
            model="gpt-3.5-turbo",
        ):
            chunks.append(chunk)
        assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_stream_custom_temperature(self, llm_provider):
        chunks = []
        async for chunk in llm_provider.chat_stream(
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.9,
        ):
            chunks.append(chunk)
        assert len(chunks) > 0


# ══════════════════════════════════════════════════════════════════════
# 10. Statistics and Reset
# ══════════════════════════════════════════════════════════════════════


class TestLLMProviderStats:
    """Test get_stats and reset_stats."""

    def test_initial_stats(self, llm_provider):
        stats = llm_provider.get_stats()
        assert stats["total_calls"] == 0
        assert stats["total_cost"] == 0.0
        assert stats["daily_cost"] == 0.0
        assert stats["default_model"] == "gpt-4o"

    @pytest.mark.asyncio
    async def test_stats_after_chat(self, llm_provider):
        await llm_provider.chat(messages=[{"role": "user", "content": "Hello"}])
        stats = llm_provider.get_stats()
        assert stats["total_calls"] == 1
        assert stats["total_cost"] > 0

    @pytest.mark.asyncio
    async def test_stats_per_model_costs(self, llm_provider):
        await llm_provider.chat(messages=[{"role": "user", "content": "Hello"}])
        stats = llm_provider.get_stats()
        assert "gpt-4o" in stats["per_model_costs"]

    def test_reset_stats(self, llm_provider):
        llm_provider._call_count = 5
        llm_provider.cost_tracker.total_cost = 1.0
        llm_provider.reset_stats()
        assert llm_provider._call_count == 0
        assert llm_provider.cost_tracker.total_cost == 0.0

    @pytest.mark.asyncio
    async def test_reset_clears_model_costs(self, llm_provider):
        await llm_provider.chat(messages=[{"role": "user", "content": "Hello"}])
        llm_provider.reset_stats()
        stats = llm_provider.get_stats()
        assert stats["per_model_costs"] == {}


# ══════════════════════════════════════════════════════════════════════
# 11. Mock Completion
# ══════════════════════════════════════════════════════════════════════


class TestMockCompletion:
    """Test the mock completion fallback."""

    @pytest.mark.asyncio
    async def test_mock_returns_response(self, llm_provider):
        result = await llm_provider._mock_completion({
            "messages": [{"role": "user", "content": "Hello"}],
        })
        assert result.choices[0].message.content is not None

    @pytest.mark.asyncio
    async def test_mock_includes_user_content(self, llm_provider):
        result = await llm_provider._mock_completion({
            "messages": [{"role": "user", "content": "Test query"}],
        })
        assert "Test query" in result.choices[0].message.content

    @pytest.mark.asyncio
    async def test_mock_usage_tracking(self, llm_provider):
        result = await llm_provider._mock_completion({
            "messages": [{"role": "user", "content": "Hello"}],
        })
        assert result.usage.total_tokens > 0

    @pytest.mark.asyncio
    async def test_mock_no_tool_calls(self, llm_provider):
        result = await llm_provider._mock_completion({
            "messages": [{"role": "user", "content": "Hello"}],
        })
        assert result.choices[0].message.tool_calls is None

    @pytest.mark.asyncio
    async def test_mock_finish_reason(self, llm_provider):
        result = await llm_provider._mock_completion({
            "messages": [{"role": "user", "content": "Hello"}],
        })
        assert result.choices[0].finish_reason == "stop"

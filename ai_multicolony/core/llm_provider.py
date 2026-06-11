"""LLM provider with LiteLLM integration for the AI MultiColony Ecosystem.

Standardizes on LiteLLM for multi-provider support with token counting,
retry logic, and cost tracking. Patterns from OpenHands, Suna, and Nanobot.

NOTE: This is the canonical LLM client. Other LLM clients in this repo
(connectors/llm_gateway.py, ai_multicolony/core/legacy/llm_client.py,
quant_nanggroe/engine/llm_router.py) are deprecated in favour of this module.
"""

from __future__ import annotations

import asyncio
import time
import warnings
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Optional

from ai_multicolony.config.logging_config import get_logger
from ai_multicolony.exceptions import LLMError, LLMRateLimitError, LLMTokensExceededError

logger = get_logger(__name__)

# ── Emit deprecation warnings for other LLM clients ──────────────────────
try:
    from connectors.llm_gateway import LLMGateway as _LegacyLLMGateway  # noqa: F401
    warnings.warn(
        "connectors.llm_gateway.LLMGateway is deprecated — use "
        "ai_multicolony.core.llm_provider.LLMProvider instead.",
        DeprecationWarning,
        stacklevel=2,
    )
except ImportError:
    pass

try:
    from ai_multicolony.core.legacy.llm_client import LLMClient as _LegacyLLMClient  # noqa: F401
    warnings.warn(
        "ai_multicolony.core.legacy.llm_client.LLMClient is deprecated — use "
        "ai_multicolony.core.llm_provider.LLMProvider instead.",
        DeprecationWarning,
        stacklevel=2,
    )
except ImportError:
    pass

try:
    from quant_nanggroe.engine.llm_router import LLMRouter as _LegacyLLMRouter  # noqa: F401
    warnings.warn(
        "quant_nanggroe.engine.llm_router.LLMRouter is deprecated — use "
        "ai_multicolony.core.llm_provider.LLMProvider instead.",
        DeprecationWarning,
        stacklevel=2,
    )
except ImportError:
    pass


@dataclass
class LLMUsage:
    """Token usage tracking for an LLM call."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def __add__(self, other: LLMUsage) -> LLMUsage:
        return LLMUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
        )


@dataclass
class LLMResponse:
    """Response from an LLM call."""

    content: str = ""
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    usage: LLMUsage = field(default_factory=LLMUsage)
    model: str = ""
    finish_reason: Optional[str] = None
    cost: float = 0.0
    latency: float = 0.0
    raw_response: Optional[dict[str, Any]] = None


@dataclass
class CostTracker:
    """Track LLM API costs."""

    daily_costs: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    per_model_costs: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    per_model_tokens: dict[str, LLMUsage] = field(default_factory=lambda: defaultdict(LLMUsage))
    total_cost: float = 0.0

    # Approximate cost per 1K tokens (input/output) - updated 2024 rates
    COST_PER_1K: dict[str, dict[str, float]] = field(default_factory=lambda: {
        "gpt-4o": {"input": 0.0025, "output": 0.01},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "claude-3.5-sonnet": {"input": 0.003, "output": 0.015},
    })

    def calculate_cost(self, model: str, usage: LLMUsage) -> float:
        """Calculate the cost of an LLM call.

        Args:
            model: The model name.
            usage: Token usage information.

        Returns:
            Estimated cost in USD.
        """
        # Find cost rates (match partial model names)
        rates = None
        for key, val in self.COST_PER_1K.items():
            if key in model:
                rates = val
                break
        if rates is None:
            rates = {"input": 0.001, "output": 0.002}

        cost = (
            (usage.prompt_tokens / 1000.0) * rates["input"]
            + (usage.completion_tokens / 1000.0) * rates["output"]
        )
        return cost

    def record(self, model: str, usage: LLMUsage, cost: float) -> None:
        """Record a cost entry.

        Args:
            model: The model name.
            usage: Token usage.
            cost: The calculated cost.
        """
        today = time.strftime("%Y-%m-%d")
        self.daily_costs[today] += cost
        self.per_model_costs[model] += cost
        self.per_model_tokens[model] = self.per_model_tokens.get(model, LLMUsage()) + usage
        self.total_cost += cost

    def get_daily_cost(self) -> float:
        """Get today's total cost."""
        today = time.strftime("%Y-%m-%d")
        return self.daily_costs.get(today, 0.0)


class LLMProvider:
    """LLM provider with LiteLLM integration.

    Features:
    - Multi-provider support via LiteLLM
    - Token counting with tiktoken (falls back to heuristic)
    - Retry logic with exponential backoff
    - Cost tracking per model and per day
    - Streaming support
    - Graceful fallback when litellm is not installed

    Attributes:
        mock_mode: True when litellm is not installed and the provider is
            returning mock responses.  Other code can check this flag to
            alter behaviour (e.g. skip real trading).
    """

    # Class-level flag — set to True when litellm is unavailable
    mock_mode: bool = False

    def __init__(
        self,
        default_model: str = "gpt-4o",
        temperature: float = 0.1,
        max_tokens: int = 4096,
        max_retries: int = 3,
        timeout: int = 120,
        cost_limit_daily: float = 100.0,
    ) -> None:
        self.default_model = default_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.timeout = timeout
        self.cost_limit_daily = cost_limit_daily
        self.cost_tracker = CostTracker()
        self._call_count = 0

    def _check_cost_limit(self) -> None:
        """Check if the daily cost limit has been exceeded."""
        daily_cost = self.cost_tracker.get_daily_cost()
        if daily_cost >= self.cost_limit_daily:
            raise LLMTokensExceededError(
                f"Daily cost limit exceeded: ${daily_cost:.2f} >= ${self.cost_limit_daily:.2f}",
                tokens_used=int(daily_cost * 1000),
                token_limit=int(self.cost_limit_daily * 1000),
            )

    def _count_tokens(self, messages: list[dict[str, Any]], model: Optional[str] = None) -> int:
        """Estimate token count for messages.

        Uses tiktoken when available, falls back to heuristic (~4 chars per token).
        """
        try:
            import tiktoken
            model_name = model or self.default_model
            try:
                encoding = tiktoken.encoding_for_model(model_name)
            except KeyError:
                encoding = tiktoken.get_encoding("cl100k_base")
            total = 0
            for msg in messages:
                total += len(encoding.encode(str(msg.get("content", ""))))
                total += 4  # Message overhead
            return total
        except ImportError:
            total = 0
            for msg in messages:
                total += len(str(msg.get("content", ""))) // 4 + 4
            return total

    async def chat(
        self,
        messages: list[dict[str, Any]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[list[dict[str, Any]]] = None,
        tool_choice: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send a chat completion request.

        Args:
            messages: List of message dicts in OpenAI format.
            model: Override the default model.
            temperature: Override the default temperature.
            max_tokens: Override the default max tokens.
            tools: Optional list of tool schemas.
            tool_choice: Optional tool choice configuration.
            **kwargs: Additional arguments for the LLM API.

        Returns:
            LLMResponse with the completion result.

        Raises:
            LLMError: If the LLM call fails after retries.
            LLMRateLimitError: If rate limited.
            LLMTokensExceededError: If cost limit exceeded.
        """
        self._check_cost_limit()

        use_model = model or self.default_model
        use_temperature = temperature if temperature is not None else self.temperature
        use_max_tokens = max_tokens or self.max_tokens

        # Build kwargs for litellm
        call_kwargs: dict[str, Any] = {
            "model": use_model,
            "messages": messages,
            "temperature": use_temperature,
            "max_tokens": use_max_tokens,
            "timeout": self.timeout,
        }
        if tools:
            call_kwargs["tools"] = tools
        if tool_choice:
            call_kwargs["tool_choice"] = tool_choice
        call_kwargs.update(kwargs)

        last_error: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                response = await self._call_litellm(call_kwargs)
                latency = time.time() - start_time

                # Parse response
                choice = response.choices[0]
                content = choice.message.content or ""
                tool_calls_list = []

                if choice.message.tool_calls:
                    for tc in choice.message.tool_calls:
                        tool_calls_list.append({
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        })

                usage = LLMUsage(
                    prompt_tokens=getattr(response.usage, "prompt_tokens", 0) or 0,
                    completion_tokens=getattr(response.usage, "completion_tokens", 0) or 0,
                    total_tokens=getattr(response.usage, "total_tokens", 0) or 0,
                )

                cost = self.cost_tracker.calculate_cost(use_model, usage)
                self.cost_tracker.record(use_model, usage, cost)
                self._call_count += 1

                return LLMResponse(
                    content=content,
                    tool_calls=tool_calls_list,
                    usage=usage,
                    model=use_model,
                    finish_reason=choice.finish_reason,
                    cost=cost,
                    latency=latency,
                )

            except LLMTokensExceededError:
                raise
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                if "rate_limit" in error_str or "rate limit" in error_str:
                    wait_time = min(2**attempt * 1.0, 60.0)
                    logger.warning("llm_rate_limited", attempt=attempt, wait=wait_time)
                    await asyncio.sleep(wait_time)
                    continue
                elif "context_length" in error_str or "token" in error_str:
                    raise LLMTokensExceededError(str(e)) from e
                elif attempt < self.max_retries - 1:
                    wait_time = 2**attempt * 0.5
                    logger.warning("llm_retry", attempt=attempt, error=str(e))
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    break

        raise LLMError(
            f"LLM call failed after {self.max_retries} retries: {last_error}",
            model=use_model,
        )

    async def _call_litellm(self, kwargs: dict[str, Any]) -> Any:
        """Make the actual LiteLLM API call.

        Falls back to a mock response when litellm is not installed.

        Args:
            kwargs: Arguments for litellm.acompletion.

        Returns:
            The LiteLLM response.
        """
        try:
            import litellm
            # If we were previously in mock mode, clear the flag
            if self.mock_mode:
                logger.warning("llm_mock_mode_deactivated", message="litellm became available, switching off mock mode")
                self.mock_mode = False
            return await litellm.acompletion(**kwargs)
        except ImportError:
            if not self.mock_mode:
                # First time falling back — emit a LOUD warning
                logger.warning(
                    "llm_mock_mode_activated",
                    message=(
                        "⚠️  litellm is NOT installed — LLMProvider is in MOCK MODE. "
                        "All LLM responses will be simulated. "
                        "Install litellm (`pip install litellm`) to enable real LLM calls."
                    ),
                )
                self.mock_mode = True
            return await self._mock_completion(kwargs)

    async def _mock_completion(self, kwargs: dict[str, Any]) -> Any:
        """Mock completion for testing without a real LLM.

        All mock responses are prefixed with [MOCK] so consumers can
        detect and handle simulated data.
        """
        from types import SimpleNamespace

        messages = kwargs.get("messages", [])
        last_content = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_content = msg.get("content", "")
                break

        # Log every mock call so it's impossible to miss
        logger.warning(
            "llm_mock_response_generated",
            model=kwargs.get("model", "unknown"),
            prompt_preview=last_content[:80],
            message="Returning [MOCK] response — litellm is not installed",
        )

        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=f"[MOCK] Mock response to: {last_content[:100]}",
                        tool_calls=None,
                    ),
                    finish_reason="stop",
                )
            ],
            usage=SimpleNamespace(
                prompt_tokens=len(str(messages)) // 4,
                completion_tokens=50,
                total_tokens=len(str(messages)) // 4 + 50,
            ),
        )

    async def chat_stream(
        self,
        messages: list[dict[str, Any]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream a chat completion response.

        Args:
            messages: Messages in OpenAI format.
            model: Override model.
            temperature: Override temperature.
            **kwargs: Additional arguments.

        Yields:
            Chunks of the response content.
        """
        use_model = model or self.default_model
        use_temperature = temperature if temperature is not None else self.temperature

        try:
            import litellm
            call_kwargs: dict[str, Any] = {
                "model": use_model,
                "messages": messages,
                "temperature": use_temperature,
                "stream": True,
                "timeout": self.timeout,
            }
            call_kwargs.update(kwargs)

            async for chunk in await litellm.acompletion(**call_kwargs):
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except ImportError:
            logger.warning(
                "llm_mock_stream_activated",
                message="litellm not installed — returning [MOCK] streaming response",
            )
            self.mock_mode = True
            yield "[MOCK] Mock streaming response"

    def get_stats(self) -> dict[str, Any]:
        """Get provider statistics.

        Returns:
            Dictionary with usage statistics.
        """
        return {
            "total_calls": self._call_count,
            "total_cost": self.cost_tracker.total_cost,
            "daily_cost": self.cost_tracker.get_daily_cost(),
            "per_model_costs": dict(self.cost_tracker.per_model_costs),
            "default_model": self.default_model,
        }

    def reset_stats(self) -> None:
        """Reset all statistics."""
        self.cost_tracker = CostTracker()
        self._call_count = 0

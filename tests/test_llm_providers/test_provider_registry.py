"""Tests for ProviderRegistry — multi-provider failover with circuit-breakers.

All provider calls are mocked — no real API keys required.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock

import pytest

from ai_multicolony.core.llm_providers.circuit_breaker import CircuitBreaker, CircuitState
from ai_multicolony.core.llm_providers.provider_registry import (
    ProviderHealth,
    ProviderRegistry,
    _ProviderEntry,
)
from ai_multicolony.exceptions import (
    CircuitOpenError,
    ProviderError,
    ProviderUnavailableError,
)


# ======================================================================
# Helpers
# ======================================================================


class FakeProvider:
    """Minimal provider that returns a canned response or raises."""

    def __init__(self, name: str, response: str = "ok", *, fail: bool = False) -> None:
        self.name = name
        self._response = response
        self._fail = fail
        self.call_count: int = 0

    async def complete(self, messages: list[dict[str, Any]], **kwargs: Any) -> str:
        self.call_count += 1
        if self._fail:
            raise ProviderError(provider=self.name, message=f"{self.name} failed")
        return self._response

    async def health_check(self) -> bool:
        return not self._fail


# ======================================================================
# Fixtures
# ======================================================================


@pytest.fixture
def registry() -> ProviderRegistry:
    return ProviderRegistry()


@pytest.fixture
def registry_with_providers() -> ProviderRegistry:
    reg = ProviderRegistry()
    reg.register("nim", FakeProvider("nim", "nim-response"), priority=0)
    reg.register("groq", FakeProvider("groq", "groq-response"), priority=1)
    reg.register("openrouter", FakeProvider("openrouter", "or-response"), priority=2)
    reg.register("openai", FakeProvider("openai", "oai-response"), priority=3)
    return reg


# ======================================================================
# Registration
# ======================================================================


class TestRegistration:
    def test_register_single_provider(self, registry: ProviderRegistry) -> None:
        registry.register("nim", FakeProvider("nim"), priority=0)
        assert "nim" in registry.provider_names
        assert registry.active_provider == "nim"

    def test_register_multiple_priority_order(self, registry: ProviderRegistry) -> None:
        registry.register("groq", FakeProvider("groq"), priority=1)
        registry.register("nim", FakeProvider("nim"), priority=0)
        # nim has lower priority number → should be first
        assert registry.provider_names == ["nim", "groq"]

    def test_unregister(self, registry: ProviderRegistry) -> None:
        registry.register("nim", FakeProvider("nim"), priority=0)
        assert registry.unregister("nim") is True
        assert "nim" not in registry.provider_names

    def test_unregister_nonexistent(self, registry: ProviderRegistry) -> None:
        assert registry.unregister("nope") is False

    def test_unregister_active_falls_to_next(self, registry: ProviderRegistry) -> None:
        registry.register("nim", FakeProvider("nim"), priority=0)
        registry.register("groq", FakeProvider("groq"), priority=1)
        registry.unregister("nim")
        assert registry.active_provider == "groq"


# ======================================================================
# Complete — happy path
# ======================================================================


class TestComplete:
    @pytest.mark.asyncio
    async def test_complete_uses_highest_priority(self, registry_with_providers: ProviderRegistry) -> None:
        result = await registry_with_providers.complete([{"role": "user", "content": "hi"}])
        assert result == "nim-response"

    @pytest.mark.asyncio
    async def test_complete_records_call_count(self, registry_with_providers: ProviderRegistry) -> None:
        await registry_with_providers.complete([{"role": "user", "content": "hi"}])
        nim_entry = registry_with_providers._providers["nim"]
        assert nim_entry.total_calls == 1


# ======================================================================
# Failover
# ======================================================================


class TestFailover:
    @pytest.mark.asyncio
    async def test_failover_on_provider_error(self, registry: ProviderRegistry) -> None:
        registry.register("nim", FakeProvider("nim", fail=True), priority=0)
        registry.register("groq", FakeProvider("groq", "groq-response"), priority=1)

        result = await registry.complete([{"role": "user", "content": "hi"}])
        assert result == "groq-response"
        assert registry.active_provider == "groq"

    @pytest.mark.asyncio
    async def test_failover_skips_open_circuit(self, registry: ProviderRegistry) -> None:
        """A provider with an open circuit should be skipped entirely."""
        nim = FakeProvider("nim", "nim-response")
        groq = FakeProvider("groq", "groq-response")

        registry.register("nim", nim, priority=0)
        registry.register("groq", groq, priority=1)

        # Force nim's circuit open
        entry = registry._providers["nim"]
        for _ in range(entry.circuit_breaker.failure_threshold):
            entry.circuit_breaker._failure_count += 1
            await entry.circuit_breaker._on_failure()

        assert entry.circuit_breaker.state == CircuitState.OPEN

        result = await registry.complete([{"role": "user", "content": "hi"}])
        assert result == "groq-response"

    @pytest.mark.asyncio
    async def test_all_providers_fail_raises(self, registry: ProviderRegistry) -> None:
        registry.register("nim", FakeProvider("nim", fail=True), priority=0)
        registry.register("groq", FakeProvider("groq", fail=True), priority=1)

        with pytest.raises(ProviderUnavailableError):
            await registry.complete([{"role": "user", "content": "hi"}])

    @pytest.mark.asyncio
    async def test_failover_logs_provider_switch(self, registry: ProviderRegistry) -> None:
        registry.register("nim", FakeProvider("nim", fail=True), priority=0)
        registry.register("groq", FakeProvider("groq", "groq-ok"), priority=1)

        await registry.complete([{"role": "user", "content": "hi"}])
        # After failover, active should be groq
        assert registry.active_provider == "groq"

    @pytest.mark.asyncio
    async def test_cascading_failover(self, registry: ProviderRegistry) -> None:
        """Fails through multiple providers to find a working one."""
        registry.register("nim", FakeProvider("nim", fail=True), priority=0)
        registry.register("groq", FakeProvider("groq", fail=True), priority=1)
        registry.register("openrouter", FakeProvider("or", fail=True), priority=2)
        registry.register("openai", FakeProvider("oai", "oai-ok"), priority=3)

        result = await registry.complete([{"role": "user", "content": "hi"}])
        assert result == "oai-ok"
        assert registry.active_provider == "openai"


# ======================================================================
# Health
# ======================================================================


class TestHealth:
    def test_get_health_empty_registry(self, registry: ProviderRegistry) -> None:
        health = registry.get_health()
        assert health == {}

    def test_get_health_returns_all_providers(self, registry_with_providers: ProviderRegistry) -> None:
        health = registry_with_providers.get_health()
        assert set(health.keys()) == {"nim", "groq", "openrouter", "openai"}
        for h in health.values():
            assert isinstance(h, ProviderHealth)
            assert h.available is True

    @pytest.mark.asyncio
    async def test_health_reflects_errors(self, registry: ProviderRegistry) -> None:
        registry.register("nim", FakeProvider("nim", fail=True), priority=0)
        registry.register("groq", FakeProvider("groq", "groq-ok"), priority=1)

        # Trigger a failure
        try:
            await registry.complete([{"role": "user", "content": "hi"}])
        except Exception:
            pass

        health = registry.get_health()
        assert health["nim"].error_rate > 0

    def test_provider_health_to_dict(self) -> None:
        h = ProviderHealth(name="test", available=True, latency_ms=42.0, error_rate=0.1)
        d = h.to_dict()
        assert d["name"] == "test"
        assert d["available"] is True
        assert d["latency_ms"] == 42.0
        assert d["circuit_state"] == "closed"


# ======================================================================
# Metrics
# ======================================================================


class TestMetrics:
    @pytest.mark.asyncio
    async def test_latency_tracked(self, registry_with_providers: ProviderRegistry) -> None:
        await registry_with_providers.complete([{"role": "user", "content": "hi"}])
        entry = registry_with_providers._providers["nim"]
        assert entry.total_latency_ms > 0

    @pytest.mark.asyncio
    async def test_failure_tracked(self, registry: ProviderRegistry) -> None:
        registry.register("broken", FakeProvider("broken", fail=True), priority=-1)
        registry.register("nim", FakeProvider("nim", "nim-ok"), priority=0)

        # broken will fail, nim will succeed — no ProviderUnavailableError
        await registry.complete([{"role": "user", "content": "hi"}])

        entry = registry._providers["broken"]
        assert entry.total_failures > 0

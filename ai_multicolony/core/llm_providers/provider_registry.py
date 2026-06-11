"""Multi-provider registry with automatic failover.

Manages a priority-ordered collection of LLM providers and transparently
switches to the next available provider when the current one fails.  Each
provider is wrapped in its own :class:`CircuitBreaker` so that repeated
failures quickly open the circuit and prevent wasted latency.

Default failover chain: **NIM → Groq → OpenRouter → OpenAI**
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Optional

import structlog

from ai_multicolony.exceptions import (
    ProviderError,
    ProviderUnavailableError,
)
from ai_multicolony.core.llm_providers.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
)

logger = structlog.get_logger(__name__)


# ── Provider protocol (structural typing) ────────────────────────────────────

class ProviderProtocol:
    """Minimal interface a provider must implement.

    Used as documentation / type hint; not enforced at runtime.
    """

    async def complete(self, messages: list[dict[str, Any]], **kwargs: Any) -> str: ...
    async def health_check(self) -> bool: ...


# ── Health data model ────────────────────────────────────────────────────────


@dataclass
class ProviderHealth:
    """Snapshot of a provider's health status."""

    name: str
    available: bool = True
    latency_ms: float = 0.0
    error_rate: float = 0.0
    last_check: float = field(default_factory=time.monotonic)
    circuit_state: CircuitState = CircuitState.CLOSED

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "available": self.available,
            "latency_ms": self.latency_ms,
            "error_rate": self.error_rate,
            "last_check": self.last_check,
            "circuit_state": self.circuit_state.value,
        }


# ── Internal entry ───────────────────────────────────────────────────────────


@dataclass
class _ProviderEntry:
    """Internal bookkeeping for a registered provider."""

    name: str
    provider: Any  # ProviderProtocol (Any to avoid Protocol issues)
    priority: int
    circuit_breaker: CircuitBreaker = field(default_factory=CircuitBreaker)
    total_calls: int = 0
    total_failures: int = 0
    total_latency_ms: float = 0.0
    last_error: str | None = None


# ── Registry ─────────────────────────────────────────────────────────────────


# Default failover chain (lower priority number = higher priority)
_DEFAULT_FAILOVER_CHAIN: list[tuple[str, int]] = [
    ("nim", 0),
    ("groq", 1),
    ("openrouter", 2),
    ("openai", 3),
]


class ProviderRegistry:
    """Priority-ordered LLM provider registry with circuit-breaker failover.

    Usage::

        from ai_multicolony.core.llm_providers import NIMProvider, ProviderRegistry

        registry = ProviderRegistry()
        registry.register("nim", NIMProvider(api_key="..."), priority=0)
        registry.register("groq", GroqProvider(api_key="..."), priority=1)

        answer = await registry.complete([{"role": "user", "content": "Hello"}])
    """

    def __init__(self) -> None:
        self._providers: dict[str, _ProviderEntry] = {}
        self._sorted_names: list[str] = []  # cached priority order
        self._active_provider: str | None = None

    # ── Registration ─────────────────────────────────────────────

    def register(
        self,
        name: str,
        provider: Any,
        priority: int = 0,
    ) -> None:
        """Register a provider with the given *priority*.

        Lower priority numbers are tried first.

        Parameters
        ----------
        name:
            Unique provider identifier (e.g. ``"nim"``, ``"groq"``).
        provider:
            Object implementing at least ``complete(messages, **kwargs)`` and
            ``health_check()``.
        priority:
            Ordering priority — 0 is highest.
        """
        entry = _ProviderEntry(
            name=name,
            provider=provider,
            priority=priority,
            circuit_breaker=CircuitBreaker(
                failure_threshold=5,
                recovery_timeout=30.0,
            ),
        )
        self._providers[name] = entry
        self._rebuild_sorted()

        # Auto-select first provider if none active
        if self._active_provider is None:
            self._active_provider = self._sorted_names[0] if self._sorted_names else None

        logger.info(
            "provider_registered",
            name=name,
            priority=priority,
            active=self._active_provider,
        )

    def unregister(self, name: str) -> bool:
        """Remove a provider from the registry.

        Returns ``True`` if the provider was found and removed.
        """
        if name not in self._providers:
            return False
        del self._providers[name]
        self._rebuild_sorted()

        if self._active_provider == name:
            self._active_provider = self._sorted_names[0] if self._sorted_names else None

        logger.info("provider_unregistered", name=name)
        return True

    # ── Core API ─────────────────────────────────────────────────

    async def complete(
        self,
        messages: list[dict[str, Any]],
        **kwargs: Any,
    ) -> str:
        """Try providers in priority order until one succeeds.

        If the active provider's circuit is open, automatically fails over
        to the next available provider.

        Raises
        ------
        ProviderUnavailableError
            If every registered provider is unavailable.
        """
        tried: list[str] = []

        for name in self._sorted_names:
            entry = self._providers[name]

            if not entry.circuit_breaker.is_available:
                logger.debug(
                    "provider_circuit_open",
                    provider=name,
                    state=entry.circuit_breaker.state.value,
                )
                continue

            tried.append(name)
            start = time.monotonic()

            try:
                result = await entry.circuit_breaker.call(
                    entry.provider.complete, messages, **kwargs
                )
                latency = (time.monotonic() - start) * 1000
                self._record_success(entry, latency)

                # Switch active provider if we failed over
                if name != self._active_provider:
                    self._failover(self._active_provider, name)

                return result

            except Exception as exc:
                latency = (time.monotonic() - start) * 1000
                self._record_failure(entry, str(exc), latency)
                logger.warning(
                    "provider_call_failed",
                    provider=name,
                    error=str(exc),
                    latency_ms=round(latency, 1),
                )
                continue

        raise ProviderUnavailableError(
            f"All providers unavailable — tried: {tried or list(self._providers.keys())}"
        )

    # ── Failover ─────────────────────────────────────────────────

    def _failover(
        self,
        current_name: str | None,
        new_name: str,
    ) -> Optional[str]:
        """Switch the active provider from *current_name* to *new_name*.

        Returns the new provider name (or ``None`` if no suitable provider
        was found).
        """
        old = self._active_provider
        self._active_provider = new_name

        logger.info(
            "provider_failover",
            old_provider=old,
            new_provider=new_name,
        )
        return new_name

    def _get_available_provider(self) -> tuple[str, Any] | None:
        """Return ``(name, provider)`` for the highest-priority available provider."""
        for name in self._sorted_names:
            entry = self._providers[name]
            if entry.circuit_breaker.is_available:
                return name, entry.provider
        return None

    # ── Health ───────────────────────────────────────────────────

    def get_health(self) -> dict[str, ProviderHealth]:
        """Return health snapshots for all registered providers."""
        health: dict[str, ProviderHealth] = {}
        for name, entry in self._providers.items():
            error_rate = (
                entry.total_failures / entry.total_calls
                if entry.total_calls > 0
                else 0.0
            )
            avg_latency = (
                entry.total_latency_ms / entry.total_calls
                if entry.total_calls > 0
                else 0.0
            )
            health[name] = ProviderHealth(
                name=name,
                available=entry.circuit_breaker.is_available,
                latency_ms=round(avg_latency, 2),
                error_rate=round(error_rate, 4),
                last_check=time.monotonic(),
                circuit_state=entry.circuit_breaker.state,
            )
        return health

    @property
    def active_provider(self) -> str | None:
        """Name of the currently active provider."""
        return self._active_provider

    @property
    def provider_names(self) -> list[str]:
        """Registered provider names in priority order."""
        return list(self._sorted_names)

    # ── Metrics helpers ──────────────────────────────────────────

    @staticmethod
    def _record_success(entry: _ProviderEntry, latency_ms: float) -> None:
        entry.total_calls += 1
        entry.total_latency_ms += latency_ms
        entry.last_error = None

    @staticmethod
    def _record_failure(entry: _ProviderEntry, error: str, latency_ms: float) -> None:
        entry.total_calls += 1
        entry.total_failures += 1
        entry.total_latency_ms += latency_ms
        entry.last_error = error

    # ── Internal ─────────────────────────────────────────────────

    def _rebuild_sorted(self) -> None:
        """Re-sort provider names by priority (ascending)."""
        self._sorted_names = sorted(
            self._providers.keys(),
            key=lambda n: self._providers[n].priority,
        )

"""Circuit-breaker pattern for LLM provider failover.

Implements the three-state circuit-breaker pattern to protect against
cascading failures when LLM providers become unavailable.  Thread-safe
via ``asyncio.Lock`` so it can be shared across concurrent coroutines
inside a single event loop.

States
------
CLOSED
    Normal operation – all calls pass through.
OPEN
    Failure threshold exceeded – calls are rejected immediately until
    *recovery_timeout* seconds have elapsed.
HALF_OPEN
    Trial mode – a limited number of probe calls are allowed; success
    resets the breaker to CLOSED, another failure reopens it.
"""

from __future__ import annotations

import asyncio
import enum
import time
from typing import Any, Callable, Coroutine, TypeVar

import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T")


# ── Enum ──────────────────────────────────────────────────────────────────────


class CircuitState(str, enum.Enum):
    """Circuit-breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


# ── Circuit Breaker ──────────────────────────────────────────────────────────


class CircuitBreaker:
    """Async circuit-breaker with automatic state transitions.

    Parameters
    ----------
    failure_threshold:
        Consecutive failures required to transition CLOSED → OPEN.
    recovery_timeout:
        Seconds to wait in OPEN state before transitioning to HALF_OPEN.
    half_open_max:
        Maximum consecutive successes in HALF_OPEN before transitioning
        back to CLOSED.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max: int = 1,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max = half_open_max

        self._state: CircuitState = CircuitState.CLOSED
        self._failure_count: int = 0
        self._success_count: int = 0
        self._last_failure_time: float | None = None
        self._last_state_change: float = time.monotonic()
        self._lock = asyncio.Lock()

    # ── Public properties ────────────────────────────────────────

    @property
    def state(self) -> CircuitState:
        """Current circuit state (may auto-transition from OPEN to HALF_OPEN)."""
        if self._state == CircuitState.OPEN and self._last_failure_time is not None:
            elapsed = time.monotonic() - self._last_failure_time
            if elapsed >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._last_state_change = time.monotonic()
                self._success_count = 0
                logger.info(
                    "circuit_breaker_state_change",
                    new_state=CircuitState.HALF_OPEN.value,
                    elapsed=round(elapsed, 2),
                )
        return self._state

    @property
    def is_available(self) -> bool:
        """Whether calls are currently allowed through the breaker."""
        current = self.state
        if current == CircuitState.CLOSED:
            return True
        if current == CircuitState.HALF_OPEN:
            return self._success_count < self.half_open_max
        return False

    @property
    def failure_count(self) -> int:
        return self._failure_count

    @property
    def success_count(self) -> int:
        return self._success_count

    @property
    def last_failure_time(self) -> float | None:
        return self._last_failure_time

    @property
    def last_state_change(self) -> float:
        return self._last_state_change

    # ── Core API ─────────────────────────────────────────────────

    async def call(
        self,
        func: Callable[..., Coroutine[Any, Any, T]],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Execute *func* with circuit-breaker protection.

        Raises
        ------
        CircuitOpenError
            If the breaker is OPEN and not yet ready for a probe.
        """
        from ai_multicolony.exceptions import CircuitOpenError

        async with self._lock:
            if not self.is_available:
                raise CircuitOpenError(
                    provider="circuit_breaker",
                    recovery_timeout=self.recovery_timeout,
                )

        try:
            result = await func(*args, **kwargs)
        except Exception:
            await self._on_failure()
            raise
        else:
            await self._on_success()
            return result

    # ── State transitions ────────────────────────────────────────

    async def _on_success(self) -> None:
        """Record a successful call and potentially close the circuit."""
        async with self._lock:
            self._success_count += 1

            if self._state == CircuitState.HALF_OPEN:
                if self._success_count >= self.half_open_max:
                    self._transition_to(CircuitState.CLOSED)
                    self._failure_count = 0
            elif self._state == CircuitState.CLOSED:
                # Reset failure count on success in closed state
                self._failure_count = 0

    async def _on_failure(self) -> None:
        """Record a failed call and potentially open the circuit."""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()

            if self._state == CircuitState.HALF_OPEN:
                self._transition_to(CircuitState.OPEN)
            elif self._failure_count >= self.failure_threshold:
                self._transition_to(CircuitState.OPEN)

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to *new_state* with logging."""
        old_state = self._state
        self._state = new_state
        self._last_state_change = time.monotonic()

        if new_state == CircuitState.HALF_OPEN:
            self._success_count = 0

        logger.info(
            "circuit_breaker_transition",
            old_state=old_state.value,
            new_state=new_state.value,
            failure_count=self._failure_count,
            success_count=self._success_count,
        )

    # ── Utility ──────────────────────────────────────────────────

    def reset(self) -> None:
        """Force the breaker back to CLOSED (e.g. for admin override)."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        self._last_state_change = time.monotonic()
        logger.info("circuit_breaker_reset")

    def to_dict(self) -> dict[str, Any]:
        """Serialise breaker state for health endpoints."""
        return {
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "last_failure_time": self._last_failure_time,
            "last_state_change": self._last_state_change,
            "is_available": self.is_available,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
        }

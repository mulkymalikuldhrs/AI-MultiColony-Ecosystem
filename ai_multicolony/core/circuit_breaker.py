"""Reusable CircuitBreaker for guarding external service calls.

Implements the Circuit Breaker pattern with three states:
- CLOSED: Normal operation — calls pass through, failures are counted.
- OPEN:  Too many failures — calls are rejected immediately with a fallback.
- HALF_OPEN: Timeout elapsed — a single probe call is allowed to test recovery.

Usage::

    from ai_multicolony.core.circuit_breaker import CircuitBreaker

    cb = CircuitBreaker(failure_threshold=5, timeout_seconds=60)

    if cb.can_execute():
        try:
            result = await external_call()
            cb.record_success()
            return result
        except Exception:
            cb.record_failure()
            return fallback()

This module also provides :class:`CircuitBreakerMiddleware` which wraps
an async callable with circuit-breaker protection automatically.
"""

from __future__ import annotations

import enum
import logging
import time
from typing import Any, Callable, Coroutine, Optional, TypeVar

logger = logging.getLogger(__name__)


class CircuitState(enum.Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


T = TypeVar("T")


class CircuitBreaker:
    """Thread-safe circuit breaker with configurable threshold and timeout.

    Parameters
    ----------
    name : str
        Human-readable name used in log messages.
    failure_threshold : int
        Number of consecutive failures before the circuit opens.
    timeout_seconds : float
        Seconds to wait in OPEN state before transitioning to HALF_OPEN.
    half_open_max_calls : int
        Number of successful calls in HALF_OPEN needed to close the circuit.
    """

    def __init__(
        self,
        name: str = "default",
        failure_threshold: int = 5,
        timeout_seconds: float = 60.0,
        half_open_max_calls: int = 1,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.half_open_max_calls = half_open_max_calls

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._half_open_successes = 0
        self._last_failure_time: Optional[float] = None
        self._last_state_change_time: float = time.monotonic()

    # ── Public properties ───────────────────────────────────────────────

    @property
    def state(self) -> CircuitState:
        """Current state, automatically transitioning OPEN → HALF_OPEN after timeout."""
        if self._state == CircuitState.OPEN and self._last_failure_time is not None:
            if (time.monotonic() - self._last_failure_time) > self.timeout_seconds:
                self._transition(CircuitState.HALF_OPEN)
        return self._state

    @property
    def is_open(self) -> bool:
        """True when the circuit is OPEN (calls should be rejected)."""
        return self.state == CircuitState.OPEN

    @property
    def failure_count(self) -> int:
        return self._failure_count

    @property
    def success_count(self) -> int:
        return self._success_count

    # ── State checks ────────────────────────────────────────────────────

    def can_execute(self) -> bool:
        """Return True if a call is allowed to proceed."""
        return self.state in (CircuitState.CLOSED, CircuitState.HALF_OPEN)

    # ── Recording outcomes ──────────────────────────────────────────────

    def record_success(self) -> None:
        """Record a successful call."""
        self._success_count += 1

        if self._state == CircuitState.HALF_OPEN:
            self._half_open_successes += 1
            if self._half_open_successes >= self.half_open_max_calls:
                self._transition(CircuitState.CLOSED)
                logger.info(
                    "CircuitBreaker[%s]: CLOSED after %d successful half-open probes",
                    self.name, self._half_open_successes,
                )

        elif self._state == CircuitState.CLOSED:
            # Reset consecutive failure count on success
            self._failure_count = 0

    def record_failure(self) -> None:
        """Record a failed call."""
        self._failure_count += 1
        self._last_failure_time = time.monotonic()

        if self._state == CircuitState.HALF_OPEN:
            # A single failure in half-open immediately reopens
            self._transition(CircuitState.OPEN)
            logger.warning(
                "CircuitBreaker[%s]: re-opened after failure during half-open probe",
                self.name,
            )
        elif self._failure_count >= self.failure_threshold:
            self._transition(CircuitState.OPEN)
            logger.warning(
                "CircuitBreaker[%s]: OPEN after %d consecutive failures (threshold=%d)",
                self.name, self._failure_count, self.failure_threshold,
            )

    # ── Manual control ──────────────────────────────────────────────────

    def reset(self) -> None:
        """Force the circuit back to CLOSED state."""
        self._transition(CircuitState.CLOSED)
        logger.info("CircuitBreaker[%s]: manually reset to CLOSED", self.name)

    # ── Introspection ───────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable snapshot of the circuit state."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "failure_threshold": self.failure_threshold,
            "timeout_seconds": self.timeout_seconds,
            "last_failure_time": self._last_failure_time,
        }

    # ── Internal helpers ────────────────────────────────────────────────

    def _transition(self, new_state: CircuitState) -> None:
        if new_state == self._state:
            return
        old = self._state
        self._state = new_state
        self._last_state_change_time = time.monotonic()

        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._half_open_successes = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._half_open_successes = 0

        logger.debug(
            "CircuitBreaker[%s]: %s → %s", self.name, old.value, new_state.value,
        )


class CircuitBreakerMiddleware:
    """Wrap an async callable with circuit-breaker protection.

    Parameters
    ----------
    breaker : CircuitBreaker
        The circuit breaker instance to use.
    fallback : callable
        A zero-argument async callable (or plain callable) returned when
        the circuit is OPEN.

    Usage::

        cb = CircuitBreaker(name="crucix", failure_threshold=3)
        mw = CircuitBreakerMiddleware(cb, fallback=lambda: SweepData())

        result = await mw.call(external_fetch_func, arg1, arg2)
    """

    def __init__(
        self,
        breaker: CircuitBreaker,
        fallback: Callable[[], Any],
    ) -> None:
        self.breaker = breaker
        self.fallback = fallback

    async def call(self, fn: Callable[..., Coroutine], *args: Any, **kwargs: Any) -> Any:
        """Execute *fn* with circuit-breaker protection.

        If the circuit is OPEN, the fallback is returned instead.
        Successes and failures are recorded automatically.
        """
        if not self.breaker.can_execute():
            logger.warning(
                "CircuitBreaker[%s]: circuit OPEN — returning fallback",
                self.breaker.name,
            )
            result = self.fallback()
            if result is not None and hasattr(result, "__await__"):
                result = await result
            return result

        try:
            result = await fn(*args, **kwargs)
            self.breaker.record_success()
            return result
        except Exception as exc:
            self.breaker.record_failure()
            raise

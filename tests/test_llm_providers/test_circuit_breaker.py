"""Tests for the CircuitBreaker — all in-process, no I/O."""

from __future__ import annotations

import asyncio
import time

import pytest

from ai_multicolony.core.llm_providers.circuit_breaker import CircuitBreaker, CircuitState
from ai_multicolony.exceptions import CircuitOpenError


# ======================================================================
# Fixtures
# ======================================================================


@pytest.fixture
def cb() -> CircuitBreaker:
    """Fresh circuit breaker with low thresholds for testing."""
    return CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=0.2,  # 200 ms — fast for tests
        half_open_max=1,
    )


# ======================================================================
# Initial state
# ======================================================================


class TestInitialState:
    def test_starts_closed(self, cb: CircuitBreaker) -> None:
        assert cb.state == CircuitState.CLOSED

    def test_starts_available(self, cb: CircuitBreaker) -> None:
        assert cb.is_available is True

    def test_zero_failure_count(self, cb: CircuitBreaker) -> None:
        assert cb.failure_count == 0

    def test_zero_success_count(self, cb: CircuitBreaker) -> None:
        assert cb.success_count == 0


# ======================================================================
# Success path
# ======================================================================


class TestSuccessPath:
    @pytest.mark.asyncio
    async def test_call_returns_result(self, cb: CircuitBreaker) -> None:
        async def good() -> str:
            return "ok"

        result = await cb.call(good)
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_success_resets_failure_count_in_closed(self, cb: CircuitBreaker) -> None:
        # Manually set a failure count
        cb._failure_count = 2

        async def good() -> str:
            return "ok"

        await cb.call(good)
        assert cb.failure_count == 0


# ======================================================================
# Failure path — CLOSED → OPEN
# ======================================================================


class TestFailurePath:
    @pytest.mark.asyncio
    async def test_failure_increments_counter(self, cb: CircuitBreaker) -> None:
        async def bad() -> None:
            raise RuntimeError("boom")

        with pytest.raises(RuntimeError):
            await cb.call(bad)

        assert cb.failure_count == 1

    @pytest.mark.asyncio
    async def test_opens_after_threshold(self, cb: CircuitBreaker) -> None:
        async def bad() -> None:
            raise RuntimeError("boom")

        for _ in range(cb.failure_threshold):
            with pytest.raises(RuntimeError):
                await cb.call(bad)

        assert cb.state == CircuitState.OPEN
        assert cb.is_available is False

    @pytest.mark.asyncio
    async def test_open_circuit_raises_circuit_open_error(self, cb: CircuitBreaker) -> None:
        async def bad() -> None:
            raise RuntimeError("boom")

        # Open the circuit
        for _ in range(cb.failure_threshold):
            with pytest.raises(RuntimeError):
                await cb.call(bad)

        # Now calling should raise CircuitOpenError
        with pytest.raises(CircuitOpenError):
            await cb.call(bad)


# ======================================================================
# Recovery — OPEN → HALF_OPEN → CLOSED
# ======================================================================


class TestRecovery:
    @pytest.mark.asyncio
    async def test_transitions_to_half_open_after_timeout(self, cb: CircuitBreaker) -> None:
        async def bad() -> None:
            raise RuntimeError("boom")

        # Open the circuit
        for _ in range(cb.failure_threshold):
            with pytest.raises(RuntimeError):
                await cb.call(bad)

        assert cb.state == CircuitState.OPEN

        # Wait for recovery timeout
        await asyncio.sleep(cb.recovery_timeout + 0.05)

        # State should auto-transition to HALF_OPEN on read
        assert cb.state == CircuitState.HALF_OPEN
        assert cb.is_available is True  # can attempt a probe

    @pytest.mark.asyncio
    async def test_half_open_success_closes_circuit(self, cb: CircuitBreaker) -> None:
        call_count = 0

        async def flaky() -> str:
            nonlocal call_count
            call_count += 1
            if call_count <= cb.failure_threshold:
                raise RuntimeError("boom")
            return "recovered"

        # Open the circuit
        for _ in range(cb.failure_threshold):
            with pytest.raises(RuntimeError):
                await cb.call(flaky)

        # Wait for recovery
        await asyncio.sleep(cb.recovery_timeout + 0.05)

        # One success in HALF_OPEN should close the circuit
        result = await cb.call(flaky)
        assert result == "recovered"
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_half_open_failure_reopens_circuit(self, cb: CircuitBreaker) -> None:
        async def bad() -> None:
            raise RuntimeError("boom")

        # Open the circuit
        for _ in range(cb.failure_threshold):
            with pytest.raises(RuntimeError):
                await cb.call(bad)

        # Wait for recovery
        await asyncio.sleep(cb.recovery_timeout + 0.05)
        assert cb.state == CircuitState.HALF_OPEN

        # A failure in HALF_OPEN reopens
        with pytest.raises(RuntimeError):
            await cb.call(bad)

        assert cb.state == CircuitState.OPEN


# ======================================================================
# Reset
# ======================================================================


class TestReset:
    @pytest.mark.asyncio
    async def test_reset_returns_to_closed(self, cb: CircuitBreaker) -> None:
        async def bad() -> None:
            raise RuntimeError("boom")

        for _ in range(cb.failure_threshold):
            with pytest.raises(RuntimeError):
                await cb.call(bad)

        assert cb.state == CircuitState.OPEN
        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.is_available is True


# ======================================================================
# to_dict
# ======================================================================


class TestToDict:
    def test_returns_expected_keys(self, cb: CircuitBreaker) -> None:
        d = cb.to_dict()
        expected = {
            "state", "failure_count", "success_count",
            "last_failure_time", "last_state_change",
            "is_available", "failure_threshold", "recovery_timeout",
        }
        assert set(d.keys()) == expected

    def test_state_value_is_string(self, cb: CircuitBreaker) -> None:
        d = cb.to_dict()
        assert d["state"] == "closed"

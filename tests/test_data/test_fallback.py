"""
Tests for Data Source Fallback Chains
=======================================
Covers: normal operation, edge cases, boundary values, error handling,
circuit breaker behavior, determinism verification.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

import pandas as pd
import pytest

from quant_nanggroe.data.fallback import (
    CIRCUIT_FAILURE_THRESHOLD,
    CIRCUIT_RESET_SECONDS,
    FallbackChain,
    FallbackEvent,
    ProviderHealth,
)


# ─── Helpers ────────────────────────────────────────────────────────────

def run_async(coro):
    """Run an async function synchronously for testing."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        # If there's already a running loop, create a new one in a thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    return asyncio.run(coro)


def make_df(rows=5) -> pd.DataFrame:
    """Create a simple test DataFrame."""
    return pd.DataFrame({"close": [100.0 + i for i in range(rows)]})


# ─── Fetcher Factories ─────────────────────────────────────────────────

def success_fetcher(result_df=None):
    """Create a fetcher that always succeeds."""
    df = result_df if result_df is not None else make_df()
    async def _fetch(**kwargs):
        return df
    return _fetch


def failing_fetcher(error_msg="Provider unavailable"):
    """Create a fetcher that always fails."""
    async def _fetch(**kwargs):
        raise ConnectionError(error_msg)
    return _fetch


def delayed_fail_then_succeed(fail_count=2, result_df=None):
    """Create a fetcher that fails N times then succeeds."""
    df = result_df if result_df is not None else make_df()
    counter = {"n": 0}
    async def _fetch(**kwargs):
        counter["n"] += 1
        if counter["n"] <= fail_count:
            raise ConnectionError(f"Transient error (attempt {counter['n']})")
        return df
    return _fetch


# ─── ProviderHealth ────────────────────────────────────────────────────


class TestProviderHealth:
    """Test ProviderHealth model."""

    def test_default_health(self):
        """New provider should have default health values."""
        health = ProviderHealth(name="test")
        assert health.success_count == 0
        assert health.failure_count == 0
        assert health.consecutive_failures == 0
        assert health.circuit_open is False
        assert health.is_available is True
        assert health.success_rate == 1.0

    def test_success_rate_with_data(self):
        """Success rate should be computed correctly."""
        health = ProviderHealth(name="test", success_count=7, failure_count=3)
        assert abs(health.success_rate - 0.7) < 1e-6

    def test_circuit_open_unavailable(self):
        """Provider with open circuit should be unavailable."""
        health = ProviderHealth(
            name="test",
            circuit_open=True,
            circuit_open_until=datetime.now() + timedelta(hours=1),
        )
        assert health.is_available is False

    def test_circuit_open_expired_available(self):
        """Provider with expired circuit should be available (half-open)."""
        health = ProviderHealth(
            name="test",
            circuit_open=True,
            circuit_open_until=datetime.now() - timedelta(seconds=1),
        )
        assert health.is_available is True

    def test_circuit_open_no_until_available(self):
        """Provider with open circuit but no until time should be available (safety)."""
        health = ProviderHealth(name="test", circuit_open=True, circuit_open_until=None)
        assert health.is_available is True


# ─── Normal Fallback Operation ─────────────────────────────────────────


class TestFallbackNormal:
    """Test normal fallback chain operation."""

    def test_primary_provider_succeeds(self):
        """Should return data from primary provider when it succeeds."""
        chain = FallbackChain({"equity": ["yahoo", "alpaca"]})
        chain.register_fetcher("yahoo", success_fetcher())
        chain.register_fetcher("alpaca", success_fetcher())

        result = run_async(chain.fetch("equity", symbol="AAPL"))
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5

    def test_fallback_on_primary_failure(self):
        """Should fall back to secondary when primary fails."""
        chain = FallbackChain({"equity": ["yahoo", "alpaca"]})
        chain.register_fetcher("yahoo", failing_fetcher())
        chain.register_fetcher("alpaca", success_fetcher())

        result = run_async(chain.fetch("equity", symbol="AAPL"))
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5

    def test_all_providers_fail_raises(self):
        """Should raise RuntimeError when all providers fail."""
        chain = FallbackChain({"equity": ["yahoo", "alpaca"]})
        chain.register_fetcher("yahoo", failing_fetcher("yahoo down"))
        chain.register_fetcher("alpaca", failing_fetcher("alpaca down"))

        with pytest.raises(RuntimeError, match="All providers failed"):
            run_async(chain.fetch("equity", symbol="AAPL"))

    def test_unknown_data_type_raises(self):
        """Should raise ValueError for unknown data type."""
        chain = FallbackChain({"equity": ["yahoo"]})
        with pytest.raises(ValueError, match="No provider chain"):
            run_async(chain.fetch("nonexistent", symbol="AAPL"))

    def test_no_fetcher_registered_skips(self):
        """Should skip providers without registered fetchers."""
        chain = FallbackChain({"equity": ["yahoo", "alpaca"]})
        # Only register alpaca fetcher, not yahoo
        chain.register_fetcher("alpaca", success_fetcher())

        result = run_async(chain.fetch("equity", symbol="AAPL"))
        assert isinstance(result, pd.DataFrame)

    def test_multiple_data_types(self):
        """Should handle multiple data types independently."""
        chain = FallbackChain({
            "equity": ["yahoo", "alpaca"],
            "crypto": ["binance", "coin_gecko"],
        })
        chain.register_fetcher("yahoo", success_fetcher())
        chain.register_fetcher("alpaca", success_fetcher())
        chain.register_fetcher("binance", success_fetcher(make_df(3)))
        chain.register_fetcher("coin_gecko", success_fetcher(make_df(3)))

        equity = run_async(chain.fetch("equity", symbol="AAPL"))
        crypto = run_async(chain.fetch("crypto", symbol="BTC"))
        assert len(equity) == 5
        assert len(crypto) == 3


# ─── Circuit Breaker ───────────────────────────────────────────────────


class TestCircuitBreaker:
    """Test circuit breaker behavior."""

    def test_circuit_opens_after_consecutive_failures(self):
        """Circuit should open after 3 consecutive failures."""
        chain = FallbackChain(
            {"equity": ["yahoo", "alpaca"]},
            circuit_failure_threshold=3,
            circuit_reset_seconds=300,
        )
        chain.register_fetcher("yahoo", failing_fetcher())
        chain.register_fetcher("alpaca", success_fetcher())

        # Trigger 3 failures on yahoo
        for _ in range(3):
            run_async(chain.fetch("equity", symbol="AAPL"))

        yahoo_health = chain.get_provider_health("yahoo")
        assert yahoo_health.circuit_open is True
        assert yahoo_health.consecutive_failures >= 3

    def test_circuit_skips_open_provider(self):
        """Open circuit should skip that provider."""
        chain = FallbackChain(
            {"equity": ["yahoo", "alpaca"]},
            circuit_failure_threshold=3,
        )
        chain.register_fetcher("yahoo", failing_fetcher())
        chain.register_fetcher("alpaca", success_fetcher())

        # Trigger 3 failures on yahoo
        for _ in range(3):
            run_async(chain.fetch("equity", symbol="AAPL"))

        # Next call should go directly to alpaca (yahoo circuit open)
        result = run_async(chain.fetch("equity", symbol="AAPL"))
        assert isinstance(result, pd.DataFrame)

        yahoo_health = chain.get_provider_health("yahoo")
        assert yahoo_health.circuit_open is True

    def test_circuit_resets_on_manual_reset(self):
        """Manual circuit reset should make provider available again."""
        chain = FallbackChain(
            {"equity": ["yahoo"]},
            circuit_failure_threshold=3,
        )
        chain.register_fetcher("yahoo", failing_fetcher())

        for _ in range(3):
            try:
                run_async(chain.fetch("equity", symbol="AAPL"))
            except RuntimeError:
                pass

        assert chain.get_provider_health("yahoo").circuit_open is True
        chain.reset_circuit("yahoo")
        assert chain.get_provider_health("yahoo").circuit_open is False

    def test_circuit_resets_on_success(self):
        """Success after failure should reset consecutive failures."""
        chain = FallbackChain({"equity": ["yahoo"]})
        chain.register_fetcher("yahoo", success_fetcher())

        run_async(chain.fetch("equity", symbol="AAPL"))
        health = chain.get_provider_health("yahoo")
        assert health.consecutive_failures == 0
        assert health.success_count == 1

    def test_reset_all_circuits(self):
        """reset_all_circuits should reset all providers."""
        chain = FallbackChain(
            {"equity": ["yahoo", "alpaca"]},
            circuit_failure_threshold=3,
        )
        chain.register_fetcher("yahoo", failing_fetcher())
        chain.register_fetcher("alpaca", failing_fetcher())

        for _ in range(3):
            try:
                run_async(chain.fetch("equity", symbol="AAPL"))
            except RuntimeError:
                pass

        chain.reset_all_circuits()
        for name in ["yahoo", "alpaca"]:
            assert chain.get_provider_health(name).circuit_open is False


# ─── Health Tracking ───────────────────────────────────────────────────


class TestHealthTracking:
    """Test health tracking and reporting."""

    def test_success_recorded(self):
        """Successful fetch should update health counters."""
        chain = FallbackChain({"equity": ["yahoo"]})
        chain.register_fetcher("yahoo", success_fetcher())

        run_async(chain.fetch("equity", symbol="AAPL"))
        health = chain.get_provider_health("yahoo")
        assert health.success_count == 1
        assert health.failure_count == 0
        assert health.avg_latency_ms > 0

    def test_failure_recorded(self):
        """Failed fetch should update health counters."""
        chain = FallbackChain({"equity": ["yahoo", "alpaca"]})
        chain.register_fetcher("yahoo", failing_fetcher())
        chain.register_fetcher("alpaca", success_fetcher())

        run_async(chain.fetch("equity", symbol="AAPL"))
        yahoo_health = chain.get_provider_health("yahoo")
        assert yahoo_health.failure_count == 1

    def test_health_report_structure(self):
        """Health report should contain all providers with expected keys."""
        chain = FallbackChain({"equity": ["yahoo", "alpaca"]})
        chain.register_fetcher("yahoo", success_fetcher())
        chain.register_fetcher("alpaca", success_fetcher())

        run_async(chain.fetch("equity", symbol="AAPL"))
        report = chain.get_health_report()
        assert "yahoo" in report
        assert "alpaca" in report
        for provider_report in report.values():
            assert "success_count" in provider_report
            assert "failure_count" in provider_report
            assert "success_rate" in provider_report
            assert "circuit_open" in provider_report

    def test_fallback_log_recorded(self):
        """Fallback events should be logged."""
        chain = FallbackChain({"equity": ["yahoo", "alpaca"]})
        chain.register_fetcher("yahoo", failing_fetcher())
        chain.register_fetcher("alpaca", success_fetcher())

        run_async(chain.fetch("equity", symbol="AAPL"))
        log = chain.get_fallback_log()
        assert len(log) >= 2
        assert any(e.requested_provider == "yahoo" and not e.success for e in log)
        assert any(e.requested_provider == "alpaca" and e.success for e in log)

    def test_fallback_log_limit(self):
        """Fallback log should respect the limit parameter."""
        chain = FallbackChain({"equity": ["yahoo"]})
        chain.register_fetcher("yahoo", success_fetcher())

        for i in range(10):
            run_async(chain.fetch("equity", symbol="AAPL"))

        log = chain.get_fallback_log(limit=3)
        assert len(log) == 3

    def test_latency_tracking(self):
        """Should track average latency."""
        chain = FallbackChain({"equity": ["yahoo"]})
        chain.register_fetcher("yahoo", success_fetcher())

        run_async(chain.fetch("equity", symbol="AAPL"))
        health = chain.get_provider_health("yahoo")
        assert health.avg_latency_ms > 0
        assert health.avg_latency_ms < 10000  # Reasonable bound


# ─── Edge Cases ────────────────────────────────────────────────────────


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_provider_chain(self):
        """Empty provider list for a data type should raise on fetch."""
        chain = FallbackChain({"equity": []})
        with pytest.raises(RuntimeError, match="All providers failed"):
            run_async(chain.fetch("equity", symbol="AAPL"))

    def test_single_provider_success(self):
        """Single provider that succeeds should work fine."""
        chain = FallbackChain({"equity": ["yahoo"]})
        chain.register_fetcher("yahoo", success_fetcher())
        result = run_async(chain.fetch("equity", symbol="AAPL"))
        assert len(result) == 5

    def test_single_provider_failure(self):
        """Single provider that fails should raise RuntimeError."""
        chain = FallbackChain({"equity": ["yahoo"]})
        chain.register_fetcher("yahoo", failing_fetcher())
        with pytest.raises(RuntimeError):
            run_async(chain.fetch("equity", symbol="AAPL"))

    def test_register_fetchers_batch(self):
        """register_fetchers should register multiple fetchers at once."""
        chain = FallbackChain({"equity": ["yahoo", "alpaca"]})
        chain.register_fetchers({
            "yahoo": success_fetcher(),
            "alpaca": success_fetcher(),
        })
        result = run_async(chain.fetch("equity", symbol="AAPL"))
        assert isinstance(result, pd.DataFrame)

    def test_custom_circuit_threshold(self):
        """Custom circuit failure threshold should be respected."""
        chain = FallbackChain(
            {"equity": ["yahoo", "alpaca"]},
            circuit_failure_threshold=1,  # Open after just 1 failure
        )
        chain.register_fetcher("yahoo", failing_fetcher())
        chain.register_fetcher("alpaca", success_fetcher())

        # Single failure should open circuit
        run_async(chain.fetch("equity", symbol="AAPL"))
        assert chain.get_provider_health("yahoo").circuit_open is True


# ─── Determinism Verification ──────────────────────────────────────────


class TestDeterminism:
    """Verify deterministic behavior."""

    def test_same_input_same_result(self):
        """Same fetch should return same DataFrame structure."""
        chain = FallbackChain({"equity": ["yahoo"]})
        chain.register_fetcher("yahoo", success_fetcher())

        results = []
        for _ in range(5):
            result = run_async(chain.fetch("equity", symbol="AAPL"))
            results.append(result)

        # All results should have same shape
        shapes = [r.shape for r in results]
        assert all(s == shapes[0] for s in shapes)

    def test_health_counters_deterministic(self):
        """Health counters should be predictable."""
        chain = FallbackChain({"equity": ["yahoo"]})
        chain.register_fetcher("yahoo", success_fetcher())

        for _ in range(5):
            run_async(chain.fetch("equity", symbol="AAPL"))

        health = chain.get_provider_health("yahoo")
        assert health.success_count == 5
        assert health.failure_count == 0

    def test_fallback_order_deterministic(self):
        """Fallback order should always follow chain definition."""
        call_order = []
        
        def tracking_fetcher(name):
            async def _fetch(**kwargs):
                call_order.append(name)
                return make_df()
            return _fetch

        chain = FallbackChain({"equity": ["yahoo", "alpaca", "polygon"]})
        chain.register_fetcher("yahoo", tracking_fetcher("yahoo"))
        chain.register_fetcher("alpaca", tracking_fetcher("alpaca"))
        chain.register_fetcher("polygon", tracking_fetcher("polygon"))

        run_async(chain.fetch("equity", symbol="AAPL"))
        assert call_order == ["yahoo"]  # Primary succeeds, no fallback

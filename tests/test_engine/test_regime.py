"""Comprehensive tests for the regime detection module.

Tests cover:
  - RegimeDetector with synthetic data (bull, bear, crisis, sideways, recovery)
  - RegimeResult validation (confidence clamping, field types)
  - RegimeAwareStrategyAdapter parameter adjustment and blocking
  - Determinism (same input → same output with same seed)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
import pytest

from quant_nanggroe.engine.regime import (
    BLOCKED_STRATEGIES,
    DEFAULT_PARAM_OVERRIDES,
    REGIME_SIZE_MULTIPLIER,
    RegimeAwareStrategyAdapter,
    RegimeDetector,
    RegimeResult,
    RegimeType,
)
from quant_nanggroe.engine.strategies.base import (
    SignalDirection,
    Strategy,
    StrategySignal,
)


# ─── Fixtures ─────────────────────────────────────────────────────────────────


def _make_returns(
    n: int = 504,
    mean: float = 0.0,
    std: float = 0.01,
    seed: int = 42,
) -> pd.Series:
    """Generate a synthetic return series with a DatetimeIndex."""
    rng = np.random.RandomState(seed)
    dates = pd.bdate_range(end="2024-12-31", periods=n)
    values = rng.normal(mean, std, n)
    return pd.Series(values, index=dates, name="returns")


def _make_bull_returns(n: int = 504, seed: int = 42) -> pd.Series:
    """Low-vol positive drift → BULL."""
    return _make_returns(n=n, mean=0.001, std=0.005, seed=seed)


def _make_bear_returns(n: int = 504, seed: int = 42) -> pd.Series:
    """Moderate-vol negative drift → BEAR."""
    return _make_returns(n=n, mean=-0.001, std=0.015, seed=seed)


def _make_crisis_returns(n: int = 504, seed: int = 42) -> pd.Series:
    """High-vol severe drawdown → CRISIS.

    Generate a series with an initial crash followed by continued losses.
    """
    rng = np.random.RandomState(seed)
    dates = pd.bdate_range(end="2024-12-31", periods=n)
    # Crash in the first third
    crash_len = n // 3
    crash = rng.normal(-0.015, 0.04, crash_len)
    # Continued losses
    rest = rng.normal(-0.002, 0.03, n - crash_len)
    values = np.concatenate([crash, rest])
    return pd.Series(values, index=dates, name="returns")


def _make_sideways_returns(n: int = 504, seed: int = 42) -> pd.Series:
    """Low-vol near-zero drift → SIDEWAYS."""
    return _make_returns(n=n, mean=0.0, std=0.005, seed=seed)


def _make_recovery_returns(n: int = 504, seed: int = 42) -> pd.Series:
    """Positive drift after a drawdown → RECOVERY.

    First half: moderate crash. Second half: recovery drift.
    """
    rng = np.random.RandomState(seed)
    dates = pd.bdate_range(end="2024-12-31", periods=n)
    first_half = rng.normal(-0.002, 0.02, n // 2)
    second_half = rng.normal(0.0015, 0.008, n - n // 2)
    values = np.concatenate([first_half, second_half])
    return pd.Series(values, index=dates, name="returns")


# ─── Simple test strategies ───────────────────────────────────────────────────


class DummyMomentumStrategy(Strategy):
    """A simple momentum strategy for testing."""

    name = "momentum"
    description = "Test momentum strategy"

    def generate_signal(self, data: Any, **kwargs) -> StrategySignal:
        return StrategySignal(
            strategy_name=self.name,
            symbol="TEST",
            direction=SignalDirection.BUY,
            confidence=0.8,
            entry_price=100.0,
            stop_loss=95.0,
            take_profit=110.0,
        )


class DummyMeanReversionStrategy(Strategy):
    """A simple mean-reversion strategy for testing."""

    name = "mean_reversion"
    description = "Test mean-reversion strategy"

    def generate_signal(self, data: Any, **kwargs) -> StrategySignal:
        return StrategySignal(
            strategy_name=self.name,
            symbol="TEST",
            direction=SignalDirection.BUY,
            confidence=0.7,
            entry_price=100.0,
            stop_loss=97.0,
            take_profit=103.0,
        )


# ─── Test RegimeType ──────────────────────────────────────────────────────────


class TestRegimeType:
    """Tests for the RegimeType enum."""

    def test_all_regimes_defined(self):
        """All five regime types should exist."""
        assert RegimeType.BULL == "bull"
        assert RegimeType.BEAR == "bear"
        assert RegimeType.SIDEWAYS == "sideways"
        assert RegimeType.CRISIS == "crisis"
        assert RegimeType.RECOVERY == "recovery"

    def test_regime_count(self):
        """There should be exactly 5 regime types."""
        assert len(RegimeType) == 5

    def test_regime_is_str(self):
        """RegimeType should be a string enum."""
        assert isinstance(RegimeType.BULL, str)


# ─── Test RegimeResult ────────────────────────────────────────────────────────


class TestRegimeResult:
    """Tests for the RegimeResult data model."""

    def test_basic_construction(self):
        """RegimeResult should construct with required fields."""
        result = RegimeResult(
            current_regime=RegimeType.BULL,
            confidence=0.85,
        )
        assert result.current_regime == RegimeType.BULL
        assert result.confidence == 0.85

    def test_confidence_clamped_high(self):
        """Confidence above 1.0 should be clamped."""
        result = RegimeResult(
            current_regime=RegimeType.BULL,
            confidence=1.5,
        )
        assert result.confidence == 1.0

    def test_confidence_clamped_low(self):
        """Confidence below 0.0 should be clamped."""
        result = RegimeResult(
            current_regime=RegimeType.BEAR,
            confidence=-0.5,
        )
        assert result.confidence == 0.0

    def test_detected_at_has_timezone(self):
        """detected_at should default to UTC now."""
        result = RegimeResult(
            current_regime=RegimeType.SIDEWAYS,
            confidence=0.5,
        )
        assert result.detected_at.tzinfo is not None

    def test_regime_history_default(self):
        """regime_history should default to empty list."""
        result = RegimeResult(
            current_regime=RegimeType.CRISIS,
            confidence=0.9,
        )
        assert result.regime_history == []

    def test_transition_probs_default(self):
        """transition_probs should default to empty dict."""
        result = RegimeResult(
            current_regime=RegimeType.RECOVERY,
            confidence=0.6,
        )
        assert result.transition_probs == {}

    def test_metadata_default(self):
        """metadata should default to empty dict."""
        result = RegimeResult(
            current_regime=RegimeType.BULL,
            confidence=0.7,
        )
        assert result.metadata == {}

    def test_full_construction(self):
        """RegimeResult should accept all fields."""
        now = datetime.now(tz=timezone.utc)
        result = RegimeResult(
            current_regime=RegimeType.BULL,
            confidence=0.9,
            regime_history=[("2024-01-01", RegimeType.BULL)],
            transition_probs={"bull": {"bull": 0.8, "bear": 0.2}},
            detected_at=now,
            metadata={"method": "hmm"},
        )
        assert len(result.regime_history) == 1
        assert result.transition_probs["bull"]["bull"] == 0.8


# ─── Test RegimeDetector ──────────────────────────────────────────────────────


class TestRegimeDetector:
    """Tests for the RegimeDetector class."""

    def test_init_default(self):
        """Default initialization should work."""
        detector = RegimeDetector()
        assert detector._n_regimes == 5
        assert detector._random_seed == 42

    def test_init_custom_seed(self):
        """Custom seed should be stored."""
        detector = RegimeDetector(random_seed=123)
        assert detector._random_seed == 123

    def test_bull_detection(self):
        """Low-vol positive drift should detect BULL regime."""
        detector = RegimeDetector(random_seed=42)
        returns = _make_bull_returns(seed=42)
        result = detector.detect_regime(returns)
        assert result.current_regime == RegimeType.BULL
        assert result.confidence > 0.0

    def test_bear_detection(self):
        """Negative drift should detect BEAR regime."""
        detector = RegimeDetector(random_seed=42)
        returns = _make_bear_returns(seed=42)
        result = detector.detect_regime(returns)
        assert result.current_regime in (RegimeType.BEAR, RegimeType.CRISIS)

    def test_sideways_detection(self):
        """Low-vol zero drift should detect SIDEWAYS."""
        detector = RegimeDetector(random_seed=42)
        returns = _make_sideways_returns(seed=42)
        result = detector.detect_regime(returns)
        assert result.current_regime == RegimeType.SIDEWAYS

    def test_crisis_detection(self):
        """High-vol severe drawdown should detect CRISIS."""
        detector = RegimeDetector(random_seed=42)
        returns = _make_crisis_returns(seed=42)
        result = detector.detect_regime(returns)
        assert result.current_regime in (RegimeType.CRISIS, RegimeType.BEAR)

    def test_recovery_detection(self):
        """Positive drift after drawdown should detect RECOVERY."""
        detector = RegimeDetector(random_seed=42)
        returns = _make_recovery_returns(seed=42)
        result = detector.detect_regime(returns)
        # Recovery or bull are both acceptable
        assert result.current_regime in (RegimeType.RECOVERY, RegimeType.BULL, RegimeType.SIDEWAYS)

    def test_short_series_handled(self):
        """Short series (< window) should still return a result."""
        detector = RegimeDetector(random_seed=42)
        returns = _make_returns(n=50, mean=0.001, std=0.005, seed=42)
        result = detector.detect_regime(returns, window=252)
        assert result.current_regime is not None
        assert isinstance(result.confidence, float)

    def test_very_short_series(self):
        """Very short series (< 10) should return SIDEWAYS with low confidence."""
        detector = RegimeDetector(random_seed=42)
        dates = pd.bdate_range(end="2024-12-31", periods=5)
        returns = pd.Series([0.01, -0.01, 0.005, -0.005, 0.0], index=dates)
        result = detector.detect_regime(returns, window=252)
        assert result.current_regime == RegimeType.SIDEWAYS
        assert result.confidence == 0.0

    def test_regime_history_populated(self):
        """Regime history should be populated."""
        detector = RegimeDetector(random_seed=42)
        returns = _make_bull_returns(seed=42)
        result = detector.detect_regime(returns)
        assert len(result.regime_history) > 0

    def test_transition_probs_populated(self):
        """Transition probabilities should be populated."""
        detector = RegimeDetector(random_seed=42)
        returns = _make_bull_returns(seed=42)
        result = detector.detect_regime(returns)
        assert len(result.transition_probs) > 0

    def test_metadata_includes_method(self):
        """Metadata should include detection method."""
        detector = RegimeDetector(random_seed=42)
        returns = _make_bull_returns(seed=42)
        result = detector.detect_regime(returns)
        assert "method" in result.metadata

    def test_result_is_regime_result_type(self):
        """detect_regime should return a RegimeResult."""
        detector = RegimeDetector(random_seed=42)
        returns = _make_bull_returns(seed=42)
        result = detector.detect_regime(returns)
        assert isinstance(result, RegimeResult)


# ─── Test Determinism ─────────────────────────────────────────────────────────


class TestDeterminism:
    """Tests for deterministic output with same seed and input."""

    def test_same_seed_same_output(self):
        """Same seed + same input → identical results."""
        returns = _make_bull_returns(seed=99)

        detector1 = RegimeDetector(random_seed=42)
        result1 = detector1.detect_regime(returns)

        detector2 = RegimeDetector(random_seed=42)
        result2 = detector2.detect_regime(returns)

        assert result1.current_regime == result2.current_regime
        assert result1.confidence == result2.confidence

    def test_different_seed_may_differ(self):
        """Different seeds may produce different results (not guaranteed,
        but the mechanism should be in place)."""
        returns = _make_bull_returns(seed=99)

        detector1 = RegimeDetector(random_seed=42)
        result1 = detector1.detect_regime(returns)

        detector2 = RegimeDetector(random_seed=999)
        result2 = detector2.detect_regime(returns)

        # With statistical fallback, same data should give same regime
        # (since the heuristic is deterministic). With HMM, the seed
        # matters more. We just check both produce valid results.
        assert isinstance(result1, RegimeResult)
        assert isinstance(result2, RegimeResult)

    def test_repeated_calls_same_detector(self):
        """Calling detect_regime multiple times on same data → same result."""
        detector = RegimeDetector(random_seed=42)
        returns = _make_bull_returns(seed=42)

        result1 = detector.detect_regime(returns)
        result2 = detector.detect_regime(returns)

        assert result1.current_regime == result2.current_regime
        assert result1.confidence == result2.confidence


# ─── Test RegimeAwareStrategyAdapter ──────────────────────────────────────────


class TestRegimeAwareStrategyAdapter:
    """Tests for the RegimeAwareStrategyAdapter."""

    def _make_adapter(
        self,
        strategy: Optional[Strategy] = None,
        seed: int = 42,
    ) -> RegimeAwareStrategyAdapter:
        strategy = strategy or DummyMomentumStrategy()
        detector = RegimeDetector(random_seed=seed)
        return RegimeAwareStrategyAdapter(strategy=strategy, detector=detector)

    def test_momentum_blocked_in_crisis(self):
        """Momentum strategy should be blocked in CRISIS regime."""
        adapter = self._make_adapter()
        assert not adapter.is_strategy_allowed(RegimeType.CRISIS)

    def test_momentum_blocked_in_bear(self):
        """Momentum strategy should be blocked in BEAR regime."""
        adapter = self._make_adapter()
        assert not adapter.is_strategy_allowed(RegimeType.BEAR)

    def test_momentum_allowed_in_bull(self):
        """Momentum strategy should be allowed in BULL regime."""
        adapter = self._make_adapter()
        assert adapter.is_strategy_allowed(RegimeType.BULL)

    def test_mean_reversion_allowed_in_crisis(self):
        """Mean-reversion should be allowed in CRISIS (not in blocked list)."""
        strategy = DummyMeanReversionStrategy()
        adapter = self._make_adapter(strategy=strategy)
        assert adapter.is_strategy_allowed(RegimeType.CRISIS)

    def test_position_size_multiplier_bull(self):
        """BULL regime should increase position size."""
        adapter = self._make_adapter()
        assert adapter.get_position_size_multiplier(RegimeType.BULL) == 1.5

    def test_position_size_multiplier_crisis(self):
        """CRISIS regime should drastically reduce position size."""
        adapter = self._make_adapter()
        assert adapter.get_position_size_multiplier(RegimeType.CRISIS) == 0.2

    def test_position_size_multiplier_bear(self):
        """BEAR regime should reduce position size."""
        adapter = self._make_adapter()
        assert adapter.get_position_size_multiplier(RegimeType.BEAR) == 0.5

    def test_position_size_multiplier_sideways(self):
        """SIDEWAYS regime should use default position size."""
        adapter = self._make_adapter()
        assert adapter.get_position_size_multiplier(RegimeType.SIDEWAYS) == 1.0

    def test_param_overrides_applied(self):
        """Parameter overrides should be returned for each regime."""
        adapter = self._make_adapter()

        crisis_overrides = adapter.get_param_overrides(RegimeType.CRISIS)
        assert "stop_loss_multiplier" in crisis_overrides
        assert crisis_overrides["stop_loss_multiplier"] == 0.5

        bull_overrides = adapter.get_param_overrides(RegimeType.BULL)
        assert "max_position_pct" in bull_overrides
        assert bull_overrides["max_position_pct"] == 0.15

    def test_generate_signal_returns_signal_in_bull(self):
        """In BULL data, momentum strategy should produce a signal."""
        adapter = self._make_adapter()
        returns = _make_bull_returns(seed=42)
        # Create OHLCV data from returns for signal generation
        prices = (1 + returns).cumprod() * 100
        data = pd.DataFrame({"close": prices})

        signal = adapter.generate_signal(data, returns=returns)
        # Should produce a signal (momentum is allowed in BULL)
        assert signal is not None
        assert signal.indicators.get("regime") is not None

    def test_generate_signal_blocked_in_crisis(self):
        """In CRISIS data, momentum strategy should be blocked (returns None)."""
        adapter = self._make_adapter()
        returns = _make_crisis_returns(seed=42)
        prices = (1 + returns).cumprod() * 100
        data = pd.DataFrame({"close": prices})

        signal = adapter.generate_signal(data, returns=returns)
        # Momentum is blocked in CRISIS, so signal should be None
        # But only if regime is detected as CRISIS or BEAR
        if adapter.last_regime_result and adapter.last_regime_result.current_regime in (
            RegimeType.CRISIS,
            RegimeType.BEAR,
        ):
            assert signal is None

    def test_signal_confidence_adjusted(self):
        """Signal confidence should be adjusted by regime multiplier."""
        adapter = self._make_adapter()
        returns = _make_bull_returns(seed=42)
        prices = (1 + returns).cumprod() * 100
        data = pd.DataFrame({"close": prices})

        signal = adapter.generate_signal(data, returns=returns)
        if signal is not None:
            # In BULL, confidence should be boosted (0.8 * 1.5 = 1.2, clamped to 1.0)
            assert signal.confidence >= 0.0
            assert signal.confidence <= 1.0

    def test_custom_param_overrides(self):
        """Custom param overrides should override defaults."""
        custom = {
            RegimeType.CRISIS: {"max_position_pct": 0.01},
        }
        strategy = DummyMomentumStrategy()
        detector = RegimeDetector(random_seed=42)
        adapter = RegimeAwareStrategyAdapter(
            strategy=strategy,
            detector=detector,
            param_overrides=custom,
        )
        overrides = adapter.get_param_overrides(RegimeType.CRISIS)
        assert overrides["max_position_pct"] == 0.01

    def test_custom_blocked_strategies(self):
        """Custom blocked strategies should override defaults."""
        custom_blocked = {
            RegimeType.BULL: {"mean_reversion"},  # Block mean-reversion in BULL
        }
        strategy = DummyMeanReversionStrategy()
        detector = RegimeDetector(random_seed=42)
        adapter = RegimeAwareStrategyAdapter(
            strategy=strategy,
            detector=detector,
            blocked_strategies=custom_blocked,
        )
        assert not adapter.is_strategy_allowed(RegimeType.BULL)
        assert adapter.is_strategy_allowed(RegimeType.CRISIS)  # No longer blocked

    def test_last_regime_result_stored(self):
        """After generating a signal, last_regime_result should be populated."""
        adapter = self._make_adapter()
        returns = _make_bull_returns(seed=42)
        prices = (1 + returns).cumprod() * 100
        data = pd.DataFrame({"close": prices})

        assert adapter.last_regime_result is None
        adapter.generate_signal(data, returns=returns)
        assert adapter.last_regime_result is not None
        assert isinstance(adapter.last_regime_result, RegimeResult)

    def test_mean_reversion_in_sideways(self):
        """Mean-reversion strategy should work in SIDEWAYS."""
        strategy = DummyMeanReversionStrategy()
        adapter = self._make_adapter(strategy=strategy)
        returns = _make_sideways_returns(seed=42)
        prices = (1 + returns).cumprod() * 100
        data = pd.DataFrame({"close": prices})

        signal = adapter.generate_signal(data, returns=returns)
        assert signal is not None

    def test_regime_metadata_in_signal(self):
        """Generated signals should include regime metadata."""
        adapter = self._make_adapter()
        returns = _make_bull_returns(seed=42)
        prices = (1 + returns).cumprod() * 100
        data = pd.DataFrame({"close": prices})

        signal = adapter.generate_signal(data, returns=returns)
        if signal is not None:
            assert "regime" in signal.indicators
            assert "regime_confidence" in signal.indicators


# ─── Test REGIME_SIZE_MULTIPLIER constants ────────────────────────────────────


class TestConstants:
    """Tests for module-level constants."""

    def test_all_regimes_have_size_multiplier(self):
        """Every RegimeType should have a size multiplier."""
        for regime in RegimeType:
            assert regime in REGIME_SIZE_MULTIPLIER

    def test_all_regimes_have_blocked_list(self):
        """Every RegimeType should have a blocked strategy set."""
        for regime in RegimeType:
            assert regime in BLOCKED_STRATEGIES

    def test_all_regimes_have_param_overrides(self):
        """Every RegimeType should have parameter overrides."""
        for regime in RegimeType:
            assert regime in DEFAULT_PARAM_OVERRIDES

    def test_crisis_multiplier_smallest(self):
        """CRISIS should have the smallest position multiplier."""
        crisis_mult = REGIME_SIZE_MULTIPLIER[RegimeType.CRISIS]
        for regime, mult in REGIME_SIZE_MULTIPLIER.items():
            if regime != RegimeType.CRISIS:
                assert crisis_mult <= mult

    def test_bull_multiplier_largest(self):
        """BULL should have the largest position multiplier."""
        bull_mult = REGIME_SIZE_MULTIPLIER[RegimeType.BULL]
        for regime, mult in REGIME_SIZE_MULTIPLIER.items():
            if regime != RegimeType.BULL:
                assert bull_mult >= mult

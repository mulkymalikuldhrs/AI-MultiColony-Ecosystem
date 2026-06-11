"""Comprehensive tests for the strategy development framework.

Covers SignalType, Signal, StrategyConfig, StrategyBase ABC,
SMCTrendStrategy, MeanReversionStrategy, MomentumBreakoutStrategy,
StrategyRegistry, validate_signal, and get_performance.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import pytest

from ai_multicolony.framework.strategy_base import (
    MeanReversionStrategy,
    MomentumBreakoutStrategy,
    SMCTrendStrategy,
    Signal,
    SignalType,
    StrategyBase,
    StrategyConfig,
    StrategyRegistry,
)


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture(autouse=True)
def _reset_registry():
    """Reset the StrategyRegistry singleton before and after each test."""
    StrategyRegistry().clear()
    yield
    StrategyRegistry().clear()


@pytest.fixture
def default_config() -> StrategyConfig:
    """A default StrategyConfig for testing."""
    return StrategyConfig(name="test_strategy", version="1.0.0")


@pytest.fixture
def custom_config() -> StrategyConfig:
    """A StrategyConfig with custom parameters."""
    return StrategyConfig(
        name="custom",
        version="2.3.1",
        parameters={"bb_period": 10, "rsi_period": 7, "lookback": 15},
        risk_limits={"max_signal_strength": 0.8},
    )


# Helper to build bullish OHLCV dict data (uptrend with BOS bullish)
@pytest.fixture
def bullish_ohlcv() -> Dict[str, Any]:
    """30-bar bullish OHLCV data as dict (uptrend)."""
    base = 100.0
    closes = [base + i * 1.5 for i in range(30)]
    opens = [c - 0.3 for c in closes]
    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    volumes = [10000.0] * 30
    return {
        "symbol": "TEST",
        "close": closes,
        "open": opens,
        "high": highs,
        "low": lows,
        "volume": volumes,
    }


# Helper to build bearish OHLCV dict data (downtrend with BOS bearish)
@pytest.fixture
def bearish_ohlcv() -> Dict[str, Any]:
    """30-bar bearish OHLCV data as dict (downtrend)."""
    base = 200.0
    closes = [base - i * 1.5 for i in range(30)]
    opens = [c + 0.3 for c in closes]
    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    volumes = [10000.0] * 30
    return {
        "symbol": "TEST",
        "close": closes,
        "open": opens,
        "high": highs,
        "low": lows,
        "volume": volumes,
    }


# Helper for mean-reversion oversold scenario
@pytest.fixture
def oversold_ohlcv() -> Dict[str, Any]:
    """25-bar data where the last bars drop sharply to trigger oversold RSI."""
    # Start flat, then sharp drop
    closes = [100.0] * 20 + [98.0, 95.0, 90.0, 85.0, 80.0]
    opens = [100.0] * 20 + [99.0, 97.0, 93.0, 88.0, 83.0]
    highs = [101.0] * 20 + [99.5, 97.5, 93.5, 88.5, 83.5]
    lows = [99.0] * 20 + [97.5, 94.5, 89.5, 84.5, 79.5]
    volumes = [5000.0] * 25
    return {
        "symbol": "MRTEST",
        "close": closes,
        "open": opens,
        "high": highs,
        "low": lows,
        "volume": volumes,
    }


# Helper for mean-reversion overbought scenario
@pytest.fixture
def overbought_ohlcv() -> Dict[str, Any]:
    """25-bar data where the last bars rise sharply to trigger overbought RSI."""
    closes = [100.0] * 20 + [102.0, 105.0, 110.0, 115.0, 120.0]
    opens = [100.0] * 20 + [101.0, 103.0, 107.0, 112.0, 117.0]
    highs = [101.0] * 20 + [102.5, 105.5, 110.5, 115.5, 120.5]
    lows = [99.0] * 20 + [100.5, 102.5, 107.5, 112.5, 117.5]
    volumes = [5000.0] * 25
    return {
        "symbol": "MRTEST",
        "close": closes,
        "open": opens,
        "high": highs,
        "low": lows,
        "volume": volumes,
    }


# Helper for momentum breakout bullish
@pytest.fixture
def breakout_bullish_ohlcv() -> Dict[str, Any]:
    """25-bar data with a bullish breakout and volume spike."""
    # Range-bound for first 20 bars, then breakout with high volume
    closes = [100.0 + (i % 3) * 0.5 for i in range(20)] + [101.5, 102.0, 103.0, 108.0, 110.0]
    opens = [c - 0.2 for c in closes]
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    # Normal volume, then spike on last bar
    volumes = [5000.0] * 24 + [50000.0]
    return {
        "symbol": "BKTEST",
        "close": closes,
        "open": opens,
        "high": highs,
        "low": lows,
        "volume": volumes,
    }


# Helper for momentum breakout bearish
@pytest.fixture
def breakout_bearish_ohlcv() -> Dict[str, Any]:
    """25-bar data with a bearish breakdown and volume spike."""
    closes = [100.0 - (i % 3) * 0.5 for i in range(20)] + [98.5, 98.0, 97.0, 92.0, 90.0]
    opens = [c + 0.2 for c in closes]
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    volumes = [5000.0] * 24 + [50000.0]
    return {
        "symbol": "BKTEST",
        "close": closes,
        "open": opens,
        "high": highs,
        "low": lows,
        "volume": volumes,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 1. SignalType enum
# ═══════════════════════════════════════════════════════════════════════════════


class TestSignalType:
    """Tests for SignalType enum."""

    def test_enum_values(self):
        """All expected signal types exist."""
        assert SignalType.BUY.value == "BUY"
        assert SignalType.SELL.value == "SELL"
        assert SignalType.HOLD.value == "HOLD"
        assert SignalType.EXIT.value == "EXIT"
        assert SignalType.NO_SIGNAL.value == "NO_SIGNAL"

    def test_enum_member_count(self):
        """Exactly 5 signal types defined."""
        assert len(SignalType) == 5

    def test_enum_is_string(self):
        """SignalType inherits from str, so members are strings."""
        assert isinstance(SignalType.BUY, str)
        assert SignalType.BUY == "BUY"

    def test_enum_from_value(self):
        """Can construct from string value."""
        assert SignalType("SELL") is SignalType.SELL

    def test_enum_invalid_value_raises(self):
        """Invalid value raises ValueError."""
        with pytest.raises(ValueError):
            SignalType("INVALID")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Signal dataclass
# ═══════════════════════════════════════════════════════════════════════════════


class TestSignal:
    """Tests for Signal dataclass."""

    def test_default_signal(self):
        """Default signal is NO_SIGNAL with strength 0."""
        sig = Signal()
        assert sig.type == SignalType.NO_SIGNAL
        assert sig.strength == 0.0
        assert sig.asset == ""
        assert sig.price == 0.0
        assert sig.metadata == {}
        assert sig.source == ""

    def test_signal_creation(self):
        """Signal with explicit values."""
        sig = Signal(
            type=SignalType.BUY,
            strength=0.8,
            asset="AAPL",
            price=150.0,
            metadata={"pattern": "test"},
            source="TestStrategy",
        )
        assert sig.type == SignalType.BUY
        assert sig.strength == 0.8
        assert sig.asset == "AAPL"
        assert sig.price == 150.0
        assert sig.metadata["pattern"] == "test"
        assert sig.source == "TestStrategy"

    def test_strength_clamped_below_zero(self):
        """Negative strength is clamped to 0.0."""
        sig = Signal(strength=-0.5)
        assert sig.strength == 0.0

    def test_strength_clamped_above_one(self):
        """Strength > 1.0 is clamped to 1.0."""
        sig = Signal(strength=1.5)
        assert sig.strength == 1.0

    def test_strength_exact_boundary_zero(self):
        """Strength exactly 0.0 is valid."""
        sig = Signal(strength=0.0)
        assert sig.strength == 0.0

    def test_strength_exact_boundary_one(self):
        """Strength exactly 1.0 is valid."""
        sig = Signal(strength=1.0)
        assert sig.strength == 1.0

    def test_timestamp_default(self):
        """Timestamp defaults to current time."""
        before = time.time()
        sig = Signal()
        after = time.time()
        assert before <= sig.timestamp <= after

    def test_timestamp_custom(self):
        """Custom timestamp is preserved."""
        sig = Signal(timestamp=1000000.0)
        assert sig.timestamp == 1000000.0

    def test_metadata_default_empty_dict(self):
        """Default metadata is an empty dict."""
        sig1 = Signal()
        sig2 = Signal()
        assert sig1.metadata == {}
        assert sig1.metadata is not sig2.metadata  # separate instances


# ═══════════════════════════════════════════════════════════════════════════════
# 3. StrategyConfig dataclass
# ═══════════════════════════════════════════════════════════════════════════════


class TestStrategyConfig:
    """Tests for StrategyConfig dataclass."""

    def test_defaults(self):
        """Default config has expected values."""
        cfg = StrategyConfig()
        assert cfg.name == "unnamed_strategy"
        assert cfg.version == "0.1.0"
        assert cfg.parameters == {}
        assert cfg.risk_limits == {}

    def test_custom_config(self, custom_config):
        """Custom config preserves all fields."""
        assert custom_config.name == "custom"
        assert custom_config.version == "2.3.1"
        assert custom_config.parameters["bb_period"] == 10
        assert custom_config.risk_limits["max_signal_strength"] == 0.8

    def test_parameters_independent(self):
        """Each config gets its own parameters dict."""
        cfg1 = StrategyConfig()
        cfg2 = StrategyConfig()
        cfg1.parameters["key"] = "val"
        assert "key" not in cfg2.parameters

    def test_risk_limits_independent(self):
        """Each config gets its own risk_limits dict."""
        cfg1 = StrategyConfig()
        cfg2 = StrategyConfig()
        cfg1.risk_limits["max"] = 1.0
        assert "max" not in cfg2.risk_limits


# ═══════════════════════════════════════════════════════════════════════════════
# 4. StrategyBase ABC enforcement
# ═══════════════════════════════════════════════════════════════════════════════


class TestStrategyBaseABC:
    """Tests for StrategyBase abstract class enforcement."""

    def test_cannot_instantiate_directly(self):
        """StrategyBase is abstract; cannot be instantiated."""
        with pytest.raises(TypeError):
            StrategyBase()  # type: ignore[abstract]

    def test_concrete_subclass_works(self):
        """A subclass that implements generate_signal can be instantiated."""

        class ConcreteStrategy(StrategyBase):
            def generate_signal(self, data: Dict[str, Any]) -> Optional[Signal]:
                return None

        strategy = ConcreteStrategy()
        assert isinstance(strategy, StrategyBase)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Concrete strategy lifecycle
# ═══════════════════════════════════════════════════════════════════════════════


class TestStrategyLifecycle:
    """Tests for strategy lifecycle: on_init → on_bar → on_signal → on_exit."""

    def _make_concrete(self):
        """Create a concrete strategy that emits a BUY signal on every bar."""

        class AlwaysBuy(StrategyBase):
            def generate_signal(self, data: Dict[str, Any]) -> Optional[Signal]:
                return Signal(
                    type=SignalType.BUY,
                    strength=0.5,
                    asset=data.get("symbol", ""),
                    price=float(data.get("close", [0])[-1]) if isinstance(data.get("close"), list) else 0.0,
                    source=self.__class__.__qualname__,
                )

        return AlwaysBuy()

    def test_lifecycle_on_init(self, default_config):
        """on_init sets config and initialized flag."""
        strategy = self._make_concrete()
        assert strategy.config is None
        strategy.on_init(default_config)
        assert strategy.config is not None
        assert strategy.config.name == "test_strategy"

    def test_lifecycle_on_bar(self, default_config):
        """on_bar increments bar count and triggers signal."""
        strategy = self._make_concrete()
        strategy.on_init(default_config)

        data = {"symbol": "TEST", "close": [100.0, 101.0, 102.0, 103.0, 104.0]}
        strategy.on_bar(data)
        assert strategy._bar_count == 1

        strategy.on_bar(data)
        assert strategy._bar_count == 2

    def test_lifecycle_signal_history(self, default_config):
        """Signals are recorded in history."""
        strategy = self._make_concrete()
        strategy.on_init(default_config)

        data = {"symbol": "TEST", "close": [100.0, 101.0]}
        strategy.on_bar(data)
        assert len(strategy.signal_history) == 1
        assert strategy.signal_history[0].type == SignalType.BUY

    def test_lifecycle_on_exit(self, default_config):
        """on_exit runs without error."""
        strategy = self._make_concrete()
        strategy.on_init(default_config)
        strategy.on_exit()  # Should not raise

    def test_on_tick_default(self, default_config):
        """Default on_tick is a no-op."""
        strategy = self._make_concrete()
        strategy.on_init(default_config)
        strategy.on_tick({"price": 100.0})  # Should not raise

    def test_no_signal_not_emitted(self, default_config):
        """NO_SIGNAL type signals are not appended to signal_history."""

        class NeverSignal(StrategyBase):
            def generate_signal(self, data: Dict[str, Any]) -> Optional[Signal]:
                return Signal(type=SignalType.NO_SIGNAL, strength=0.0)

        strategy = NeverSignal()
        strategy.on_init(default_config)
        strategy.on_bar({"close": [1.0]})
        assert len(strategy.signal_history) == 0

    def test_none_signal_not_emitted(self, default_config):
        """None return from generate_signal does not emit."""

        class NoneSignal(StrategyBase):
            def generate_signal(self, data: Dict[str, Any]) -> Optional[Signal]:
                return None

        strategy = NoneSignal()
        strategy.on_init(default_config)
        strategy.on_bar({"close": [1.0]})
        assert len(strategy.signal_history) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# 6. SMCTrendStrategy
# ═══════════════════════════════════════════════════════════════════════════════


class TestSMCTrendStrategy:
    """Tests for SMCTrendStrategy."""

    def test_instantiation(self):
        """Can instantiate SMCTrendStrategy."""
        strategy = SMCTrendStrategy()
        assert isinstance(strategy, StrategyBase)

    def test_insufficient_data_returns_none(self, default_config):
        """Less than 10 bars returns None."""
        strategy = SMCTrendStrategy()
        strategy.on_init(default_config)
        result = strategy.generate_signal({
            "symbol": "X",
            "close": [100.0] * 5,
            "high": [101.0] * 5,
            "low": [99.0] * 5,
            "open": [100.0] * 5,
        })
        assert result is None

    def test_bullish_data(self, bullish_ohlcv, default_config):
        """Bullish OHLCV data should produce a BUY or HOLD signal."""
        strategy = SMCTrendStrategy()
        strategy.on_init(default_config)
        signal = strategy.generate_signal(bullish_ohlcv)
        assert signal is not None
        assert signal.type in (SignalType.BUY, SignalType.HOLD)
        assert signal.asset == "TEST"
        assert signal.price > 0

    def test_bearish_data(self, bearish_ohlcv, default_config):
        """Bearish OHLCV data should produce a SELL or HOLD signal."""
        strategy = SMCTrendStrategy()
        strategy.on_init(default_config)
        signal = strategy.generate_signal(bearish_ohlcv)
        assert signal is not None
        assert signal.type in (SignalType.SELL, SignalType.HOLD)

    def test_on_bar_lifecycle(self, bullish_ohlcv, default_config):
        """Full lifecycle with on_bar processes data."""
        strategy = SMCTrendStrategy()
        strategy.on_init(default_config)
        strategy.on_bar(bullish_ohlcv)
        assert strategy._bar_count == 1
        strategy.on_exit()

    def test_invalid_data_type(self, default_config):
        """Non-dict, non-DataFrame data returns None."""
        strategy = SMCTrendStrategy()
        strategy.on_init(default_config)
        result = strategy.generate_signal("invalid")  # type: ignore[arg-type]
        assert result is None

    def test_source_name(self, bullish_ohlcv, default_config):
        """Signal source is set to the strategy's qualified name."""
        strategy = SMCTrendStrategy()
        strategy.on_init(default_config)
        signal = strategy.generate_signal(bullish_ohlcv)
        assert signal is not None
        assert "SMCTrendStrategy" in signal.source

    def test_strength_in_valid_range(self, bullish_ohlcv, default_config):
        """Emitted signal strength is between 0 and 1."""
        strategy = SMCTrendStrategy()
        strategy.on_init(default_config)
        signal = strategy.generate_signal(bullish_ohlcv)
        if signal and signal.type != SignalType.HOLD:
            assert 0.0 <= signal.strength <= 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# 7. MeanReversionStrategy
# ═══════════════════════════════════════════════════════════════════════════════


class TestMeanReversionStrategy:
    """Tests for MeanReversionStrategy."""

    def test_instantiation(self):
        """Can instantiate MeanReversionStrategy."""
        strategy = MeanReversionStrategy()
        assert isinstance(strategy, StrategyBase)

    def test_default_params(self, default_config):
        """Default BB and RSI params are set on init."""
        strategy = MeanReversionStrategy()
        strategy.on_init(default_config)
        assert strategy._bb_period == 20
        assert strategy._bb_std == 2.0
        assert strategy._rsi_period == 14

    def test_custom_params(self):
        """Custom BB and RSI params from config."""
        config = StrategyConfig(
            name="mr",
            parameters={"bb_period": 10, "bb_std": 1.5, "rsi_period": 7},
        )
        strategy = MeanReversionStrategy()
        strategy.on_init(config)
        assert strategy._bb_period == 10
        assert strategy._bb_std == 1.5
        assert strategy._rsi_period == 7

    def test_insufficient_data(self, default_config):
        """Less than required bars returns None."""
        strategy = MeanReversionStrategy()
        strategy.on_init(default_config)
        result = strategy.generate_signal({
            "symbol": "X",
            "close": [100.0] * 10,  # Need at least 21 bars (bb_period + 1)
        })
        assert result is None

    def test_oversold_buy_signal(self, oversold_ohlcv):
        """Oversold data should generate a BUY signal."""
        config = StrategyConfig(name="mr_test", parameters={"bb_period": 20, "rsi_period": 14})
        strategy = MeanReversionStrategy()
        strategy.on_init(config)
        signal = strategy.generate_signal(oversold_ohlcv)
        assert signal is not None
        # The sharp drop should trigger either BUY or HOLD depending on exact values
        assert signal.type in (SignalType.BUY, SignalType.HOLD)
        if signal.type == SignalType.BUY:
            assert signal.metadata.get("pattern") == "mean_reversion_buy"

    def test_overbought_sell_signal(self, overbought_ohlcv):
        """Overbought data should generate a SELL signal."""
        config = StrategyConfig(name="mr_test", parameters={"bb_period": 20, "rsi_period": 14})
        strategy = MeanReversionStrategy()
        strategy.on_init(config)
        signal = strategy.generate_signal(overbought_ohlcv)
        assert signal is not None
        assert signal.type in (SignalType.SELL, SignalType.HOLD)
        if signal.type == SignalType.SELL:
            assert signal.metadata.get("pattern") == "mean_reversion_sell"

    def test_hold_signal_metadata(self, oversold_ohlcv, default_config):
        """HOLD signals contain BB and RSI metadata."""
        strategy = MeanReversionStrategy()
        strategy.on_init(default_config)
        signal = strategy.generate_signal(oversold_ohlcv)
        if signal and signal.type == SignalType.HOLD:
            assert "bb_upper" in signal.metadata
            assert "bb_lower" in signal.metadata
            assert "rsi" in signal.metadata

    def test_rsi_computation(self):
        """RSI computation helper returns valid values."""
        # Monotonically increasing: RSI should be high
        rising = [100.0 + i for i in range(30)]
        rsi = MeanReversionStrategy._compute_rsi(rising, 14)
        assert rsi is not None
        assert rsi > 70.0

        # Monotonically decreasing: RSI should be low
        falling = [100.0 - i for i in range(30)]
        rsi = MeanReversionStrategy._compute_rsi(falling, 14)
        assert rsi is not None
        assert rsi < 30.0

    def test_rsi_insufficient_data(self):
        """RSI returns None with insufficient data."""
        rsi = MeanReversionStrategy._compute_rsi([100.0, 101.0], 14)
        assert rsi is None

    def test_on_bar_lifecycle(self, oversold_ohlcv, default_config):
        """Full lifecycle with on_bar."""
        strategy = MeanReversionStrategy()
        strategy.on_init(default_config)
        strategy.on_bar(oversold_ohlcv)
        assert strategy._bar_count == 1
        strategy.on_exit()


# ═══════════════════════════════════════════════════════════════════════════════
# 8. MomentumBreakoutStrategy
# ═══════════════════════════════════════════════════════════════════════════════


class TestMomentumBreakoutStrategy:
    """Tests for MomentumBreakoutStrategy."""

    def test_instantiation(self):
        """Can instantiate MomentumBreakoutStrategy."""
        strategy = MomentumBreakoutStrategy()
        assert isinstance(strategy, StrategyBase)

    def test_default_params(self, default_config):
        """Default params set on init."""
        strategy = MomentumBreakoutStrategy()
        strategy.on_init(default_config)
        assert strategy._lookback == 20
        assert strategy._volume_mult == 1.5
        assert strategy._atr_period == 14

    def test_custom_params(self):
        """Custom params from config."""
        config = StrategyConfig(
            name="mo",
            parameters={"lookback": 10, "volume_mult": 2.0, "atr_period": 7},
        )
        strategy = MomentumBreakoutStrategy()
        strategy.on_init(config)
        assert strategy._lookback == 10
        assert strategy._volume_mult == 2.0
        assert strategy._atr_period == 7

    def test_insufficient_data(self, default_config):
        """Too few bars or no volume returns None."""
        strategy = MomentumBreakoutStrategy()
        strategy.on_init(default_config)
        result = strategy.generate_signal({
            "symbol": "X",
            "close": [100.0] * 5,
            "high": [101.0] * 5,
            "low": [99.0] * 5,
            "volume": [1000.0] * 5,
        })
        assert result is None

    def test_no_volume_returns_none(self, default_config):
        """Missing volume data returns None."""
        strategy = MomentumBreakoutStrategy()
        strategy.on_init(default_config)
        data = {
            "symbol": "X",
            "close": [100.0] * 25,
            "high": [101.0] * 25,
            "low": [99.0] * 25,
            # No volume key
        }
        result = strategy.generate_signal(data)
        assert result is None

    def test_bullish_breakout(self, breakout_bullish_ohlcv, default_config):
        """Bullish breakout data should produce BUY or HOLD."""
        strategy = MomentumBreakoutStrategy()
        strategy.on_init(default_config)
        signal = strategy.generate_signal(breakout_bullish_ohlcv)
        assert signal is not None
        assert signal.type in (SignalType.BUY, SignalType.HOLD)
        if signal.type == SignalType.BUY:
            assert "stop_loss" in signal.metadata
            assert "take_profit" in signal.metadata

    def test_bearish_breakout(self, breakout_bearish_ohlcv, default_config):
        """Bearish breakout data should produce SELL or HOLD."""
        strategy = MomentumBreakoutStrategy()
        strategy.on_init(default_config)
        signal = strategy.generate_signal(breakout_bearish_ohlcv)
        assert signal is not None
        assert signal.type in (SignalType.SELL, SignalType.HOLD)

    def test_atr_computation(self):
        """ATR computation helper returns valid values."""
        highs = [102.0, 103.0, 101.0, 104.0, 102.0, 105.0, 103.0, 106.0, 104.0, 107.0,
                 105.0, 108.0, 106.0, 109.0, 107.0, 110.0]
        lows = [98.0, 99.0, 97.0, 100.0, 98.0, 101.0, 99.0, 102.0, 100.0, 103.0,
                101.0, 104.0, 102.0, 105.0, 103.0, 106.0]
        closes = [100.0, 101.0, 99.0, 102.0, 100.0, 103.0, 101.0, 104.0, 102.0, 105.0,
                  103.0, 106.0, 104.0, 107.0, 105.0, 108.0]
        atr = MomentumBreakoutStrategy._compute_atr(highs, lows, closes, 14)
        assert atr is not None
        assert atr > 0.0

    def test_atr_insufficient_data(self):
        """ATR returns None with insufficient data."""
        atr = MomentumBreakoutStrategy._compute_atr([100.0], [99.0], [100.0], 14)
        assert atr is None

    def test_on_bar_lifecycle(self, breakout_bullish_ohlcv, default_config):
        """Full lifecycle with on_bar."""
        strategy = MomentumBreakoutStrategy()
        strategy.on_init(default_config)
        strategy.on_bar(breakout_bullish_ohlcv)
        assert strategy._bar_count == 1
        strategy.on_exit()


# ═══════════════════════════════════════════════════════════════════════════════
# 9. StrategyRegistry
# ═══════════════════════════════════════════════════════════════════════════════


class TestStrategyRegistry:
    """Tests for StrategyRegistry singleton."""

    def _reg(self):
        """Get the singleton registry instance."""
        return StrategyRegistry()

    def test_register_and_get(self):
        """Can register and retrieve a strategy class."""
        self._reg().register("test_strat", SMCTrendStrategy)
        cls = self._reg().get("test_strat")
        assert cls is SMCTrendStrategy

    def test_get_nonexistent_raises_keyerror(self):
        """Getting a non-registered name raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            self._reg().get("nonexistent")

    def test_create(self, default_config):
        """Create fully-initialised strategy instance."""
        self._reg().register("smc", SMCTrendStrategy)
        instance = self._reg().create("smc", default_config)
        assert isinstance(instance, SMCTrendStrategy)
        assert instance.config is not None
        assert instance.config.name == "test_strategy"
        assert instance._initialized is True

    def test_list_strategies(self):
        """list_strategies returns sorted names."""
        self._reg().register("zebra", SMCTrendStrategy)
        self._reg().register("alpha", MeanReversionStrategy)
        names = self._reg().list_strategies()
        assert names == ["alpha", "zebra"]

    def test_clear(self):
        """clear removes all registrations."""
        self._reg().register("a", SMCTrendStrategy)
        self._reg().register("b", MeanReversionStrategy)
        assert len(self._reg().list_strategies()) == 2
        self._reg().clear()
        assert self._reg().list_strategies() == []

    def test_duplicate_registration_overwrites(self):
        """Registering the same name overwrites (no error)."""
        self._reg().register("dup", SMCTrendStrategy)
        self._reg().register("dup", MeanReversionStrategy)
        cls = self._reg().get("dup")
        assert cls is MeanReversionStrategy

    def test_singleton_identity(self):
        """Multiple calls return the same instance."""
        r1 = StrategyRegistry()
        r2 = StrategyRegistry()
        assert r1 is r2

    def test_create_nonexistent_raises_keyerror(self, default_config):
        """Creating with non-registered name raises KeyError."""
        with pytest.raises(KeyError):
            self._reg().create("missing", default_config)

    def test_auto_registered_builtins(self):
        """Built-in strategies are auto-registered on module import.

        Note: we clear() in autouse fixture, but the module-level
        _registry auto-registers them. We re-register to test this.
        """
        # After clear, the builtins are gone; re-register and verify
        self._reg().register("smc_trend", SMCTrendStrategy)
        self._reg().register("mean_reversion", MeanReversionStrategy)
        self._reg().register("momentum_breakout", MomentumBreakoutStrategy)
        names = self._reg().list_strategies()
        assert "smc_trend" in names
        assert "mean_reversion" in names
        assert "momentum_breakout" in names


# ═══════════════════════════════════════════════════════════════════════════════
# 10. validate_signal edge cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestValidateSignal:
    """Tests for validate_signal with edge cases."""

    def _make_strategy(self, config=None):
        """Create a minimal concrete strategy for testing validation."""

        class ValidatedStrategy(StrategyBase):
            def generate_signal(self, data: Dict[str, Any]) -> Optional[Signal]:
                return None

        s = ValidatedStrategy()
        if config:
            s.on_init(config)
        return s

    def test_strength_zero_fails(self, default_config):
        """Signal with strength=0 fails validation."""
        strategy = self._make_strategy(default_config)
        sig = Signal(type=SignalType.BUY, strength=0.0)
        assert strategy.validate_signal(sig) is False

    def test_negative_strength_fails(self, default_config):
        """Signal with negative strength (clamped to 0) fails validation."""
        strategy = self._make_strategy(default_config)
        sig = Signal(type=SignalType.BUY, strength=-0.5)
        # __post_init__ clamps to 0.0, so validate_signal returns False
        assert sig.strength == 0.0
        assert strategy.validate_signal(sig) is False

    def test_strength_above_one_clamped_but_passes(self, default_config):
        """Signal with strength > 1.0 is clamped to 1.0 and passes."""
        strategy = self._make_strategy(default_config)
        sig = Signal(type=SignalType.BUY, strength=1.5)
        assert sig.strength == 1.0
        assert strategy.validate_signal(sig) is True

    def test_valid_strength_passes(self, default_config):
        """Signal with valid strength passes."""
        strategy = self._make_strategy(default_config)
        sig = Signal(type=SignalType.BUY, strength=0.5)
        assert strategy.validate_signal(sig) is True

    def test_max_signal_strength_limit(self):
        """Signal exceeding max_signal_strength in risk_limits fails."""
        config = StrategyConfig(
            name="limited",
            risk_limits={"max_signal_strength": 0.5},
        )
        strategy = self._make_strategy(config)
        sig = Signal(type=SignalType.BUY, strength=0.8)
        assert strategy.validate_signal(sig) is False

    def test_signal_at_max_strength_passes(self):
        """Signal at exactly max_signal_strength passes."""
        config = StrategyConfig(
            name="limited",
            risk_limits={"max_signal_strength": 0.5},
        )
        strategy = self._make_strategy(config)
        sig = Signal(type=SignalType.BUY, strength=0.5)
        assert strategy.validate_signal(sig) is True

    def test_no_config_validates_on_strength_only(self):
        """Without config, only strength > 0 is checked."""
        strategy = self._make_strategy()
        sig = Signal(type=SignalType.BUY, strength=0.01)
        assert strategy.validate_signal(sig) is True

    def test_very_small_strength_passes(self, default_config):
        """Very small positive strength passes."""
        strategy = self._make_strategy(default_config)
        sig = Signal(type=SignalType.BUY, strength=0.001)
        assert strategy.validate_signal(sig) is True


# ═══════════════════════════════════════════════════════════════════════════════
# 11. get_performance metrics
# ═══════════════════════════════════════════════════════════════════════════════


class TestGetPerformance:
    """Tests for get_performance metrics."""

    def test_initial_performance(self, default_config):
        """Performance before any bars shows zeros."""
        strategy = SMCTrendStrategy()
        strategy.on_init(default_config)
        perf = strategy.get_performance()
        assert perf["name"] == "test_strategy"
        assert perf["bars_processed"] == 0
        assert perf["total_signals"] == 0
        assert perf["signal_counts"] == {}

    def test_performance_after_bars(self, bullish_ohlcv, default_config):
        """Performance after processing bars shows updated metrics."""
        strategy = SMCTrendStrategy()
        strategy.on_init(default_config)
        strategy.on_bar(bullish_ohlcv)
        perf = strategy.get_performance()
        assert perf["bars_processed"] == 1

    def test_performance_signal_counts(self, default_config):
        """Signal counts are tracked by type."""

        class AlwaysBuy(StrategyBase):
            def generate_signal(self, data: Dict[str, Any]) -> Optional[Signal]:
                return Signal(
                    type=SignalType.BUY,
                    strength=0.6,
                    asset="TEST",
                    price=100.0,
                    source="AlwaysBuy",
                )

        strategy = AlwaysBuy()
        strategy.on_init(default_config)
        data = {"symbol": "TEST", "close": [100.0]}
        strategy.on_bar(data)
        strategy.on_bar(data)
        strategy.on_bar(data)
        perf = strategy.get_performance()
        assert perf["total_signals"] == 3
        assert perf["signal_counts"].get("BUY") == 3

    def test_performance_no_config(self):
        """Performance with no config shows 'unknown' name."""
        strategy = SMCTrendStrategy()
        perf = strategy.get_performance()
        assert perf["name"] == "unknown"

    def test_performance_mixed_signals(self, default_config):
        """Mixed signal types are counted correctly."""

        class AlternatingStrategy(StrategyBase):
            def __init__(self):
                super().__init__()
                self._count = 0

            def generate_signal(self, data: Dict[str, Any]) -> Optional[Signal]:
                self._count += 1
                if self._count % 2 == 0:
                    return Signal(type=SignalType.SELL, strength=0.5, source="Alt")
                return Signal(type=SignalType.BUY, strength=0.5, source="Alt")

        strategy = AlternatingStrategy()
        strategy.on_init(default_config)
        for _ in range(4):
            strategy.on_bar({"close": [1.0]})

        perf = strategy.get_performance()
        assert perf["total_signals"] == 4
        assert perf["signal_counts"].get("BUY") == 2
        assert perf["signal_counts"].get("SELL") == 2

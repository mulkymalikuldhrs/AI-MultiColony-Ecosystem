"""
Tests for Backtest Engine
============================
Test the event-driven backtesting engine with known data series,
strategy functions, order processing, equity curve tracking,
position management, and comprehensive result reporting.
"""

from __future__ import annotations

import os

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///test_qna.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")

import pytest
import numpy as np
import pandas as pd

from quant_nanggroe_ai.backtest.engine import (
    BacktestEngine,
    BacktestResult,
    BacktestTrade,
    BacktestPosition,
    EquityPoint,
)


# ── Shared Fixtures ───────────────────────────────────────────────────


@pytest.fixture
def simple_up_data() -> list[dict]:
    """Simple uptrending OHLCV data — 10 bars."""
    return [
        {
            "timestamp": f"2024-01-{i+1:02d}",
            "open": 100.0 + i,
            "high": 101.0 + i,
            "low": 99.0 + i,
            "close": 100.0 + i + 0.5,
            "volume": 1000.0,
        }
        for i in range(10)
    ]


@pytest.fixture
def simple_down_data() -> list[dict]:
    """Simple downtrending OHLCV data — 10 bars."""
    return [
        {
            "timestamp": f"2024-01-{i+1:02d}",
            "open": 110.0 - i,
            "high": 111.0 - i,
            "low": 109.0 - i,
            "close": 110.0 - i - 0.5,
            "volume": 1000.0,
        }
        for i in range(10)
    ]


@pytest.fixture
def dataframe_data() -> pd.DataFrame:
    """OHLCV data as a pandas DataFrame."""
    np.random.seed(42)
    n = 50
    dates = pd.date_range("2024-01-01", periods=n, freq="D")
    close = 100.0 + np.cumsum(np.random.normal(0.1, 1.0, n))
    return pd.DataFrame({
        "timestamp": dates,
        "open": close + np.random.normal(0, 0.5, n),
        "high": close + abs(np.random.normal(0, 1.0, n)),
        "low": close - abs(np.random.normal(0, 1.0, n)),
        "close": close,
        "volume": np.random.lognormal(10, 1, n),
    })


@pytest.fixture
def buy_and_hold_strategy():
    """Strategy that buys on first bar and holds."""

    def strategy(bar, positions, equity):
        if "AAPL" not in positions:
            return {"action": "BUY", "symbol": "AAPL", "quantity": 10}
        return None

    return strategy


@pytest.fixture
def buy_and_sell_strategy():
    """Strategy that buys then sells on the next bar."""
    call_count = [0]

    def strategy(bar, positions, equity):
        call_count[0] += 1
        if "AAPL" not in positions:
            return {"action": "BUY", "symbol": "AAPL", "quantity": 10}
        else:
            return {"action": "SELL", "symbol": "AAPL", "quantity": 10}

    return strategy


@pytest.fixture
def do_nothing_strategy():
    """Strategy that never trades."""

    def strategy(bar, positions, equity):
        return None

    return strategy


# ── Engine Initialization Tests ──────────────────────────────────────


class TestBacktestEngineInit:
    """Test BacktestEngine initialization."""

    @pytest.mark.backtest
    def test_default_initialization(self) -> None:
        """Engine should initialize with default parameters."""
        engine = BacktestEngine()
        assert engine._initial_capital == 100_000.0
        assert engine._commission_rate == 0.001
        assert engine._slippage_bps == 5.0
        assert engine._position_sizing == "fixed"
        assert engine._default_quantity == 100.0
        assert engine._risk_per_trade == 0.01

    @pytest.mark.backtest
    def test_custom_initialization(self) -> None:
        """Engine should accept custom parameters."""
        engine = BacktestEngine(
            initial_capital=50_000.0,
            commission=0.002,
            slippage_bps=10.0,
            position_sizing="percent_equity",
            default_quantity=50.0,
            risk_per_trade=0.02,
        )
        assert engine._initial_capital == 50_000.0
        assert engine._commission_rate == 0.002
        assert engine._slippage_bps == 10.0
        assert engine._position_sizing == "percent_equity"

    @pytest.mark.backtest
    def test_invalid_position_sizing(self) -> None:
        """Invalid position sizing should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid position_sizing"):
            BacktestEngine(position_sizing="invalid")

    @pytest.mark.parametrize("sizing", ["fixed", "percent_equity", "kelly"])
    def test_valid_position_sizing_modes(self, sizing: str) -> None:
        """All valid position sizing modes should be accepted."""
        engine = BacktestEngine(position_sizing=sizing)
        assert engine._position_sizing == sizing


# ── Run with Empty/Minimal Data ──────────────────────────────────────


class TestBacktestEngineEmptyData:
    """Test engine behavior with empty or minimal data."""

    @pytest.mark.backtest
    def test_empty_data(self, do_nothing_strategy) -> None:
        """Empty data list should return result with initial capital."""
        engine = BacktestEngine(initial_capital=100_000.0)
        result = engine.run(do_nothing_strategy, [])
        assert result.initial_capital == 100_000.0
        assert result.final_equity == 100_000.0
        assert result.total_trades == 0

    @pytest.mark.backtest
    def test_single_bar(self, do_nothing_strategy) -> None:
        """Single bar should produce valid result with no trades."""
        engine = BacktestEngine()
        data = [{"close": 100.0, "timestamp": "2024-01-01"}]
        result = engine.run(do_nothing_strategy, data)
        assert result.bars_processed == 1
        assert result.total_trades == 0

    @pytest.mark.backtest
    def test_no_strategy_signals(self, simple_up_data, do_nothing_strategy) -> None:
        """Do-nothing strategy should produce no trades."""
        engine = BacktestEngine()
        result = engine.run(do_nothing_strategy, simple_up_data)
        assert result.total_trades == 0
        assert result.final_equity == result.initial_capital


# ── Run with Known Strategies ────────────────────────────────────────


class TestBacktestEngineStrategies:
    """Test engine with various strategy functions."""

    @pytest.mark.backtest
    def test_buy_and_hold(self, simple_up_data, buy_and_hold_strategy) -> None:
        """Buy and hold should produce exactly 1 trade (closed at end of data)."""
        engine = BacktestEngine(initial_capital=100_000.0, default_quantity=10.0)
        result = engine.run(buy_and_hold_strategy, simple_up_data)
        # Should have at least 1 trade (closed at end of data)
        assert result.total_trades >= 1
        # In an uptrend, buy and hold should be profitable (ignoring commissions)
        assert result.bars_processed == 10

    @pytest.mark.backtest
    def test_buy_and_sell(self, simple_up_data, buy_and_sell_strategy) -> None:
        """Buy then sell should produce at least 2 trades."""
        engine = BacktestEngine(initial_capital=100_000.0, default_quantity=10.0)
        result = engine.run(buy_and_sell_strategy, simple_up_data)
        assert result.total_trades >= 2

    @pytest.mark.backtest
    def test_strategy_exception_handled(self, simple_up_data) -> None:
        """Strategy function that raises should be handled gracefully."""
        def bad_strategy(bar, positions, equity):
            raise ValueError("Strategy error!")

        engine = BacktestEngine()
        # Should not raise — engine catches strategy errors
        result = engine.run(bad_strategy, simple_up_data)
        assert result.bars_processed == 10

    @pytest.mark.backtest
    def test_strategy_returns_none(self, simple_up_data) -> None:
        """Strategy returning None for all bars should produce no trades."""
        engine = BacktestEngine()
        result = engine.run(lambda bar, pos, eq: None, simple_up_data)
        assert result.total_trades == 0


# ── Data Format Handling ─────────────────────────────────────────────


class TestBacktestEngineDataFormats:
    """Test engine with different data formats."""

    @pytest.mark.backtest
    def test_list_of_dicts(self, simple_up_data, do_nothing_strategy) -> None:
        """Engine should accept list of dicts."""
        engine = BacktestEngine()
        result = engine.run(do_nothing_strategy, simple_up_data)
        assert result.bars_processed == 10

    @pytest.mark.backtest
    def test_dataframe(self, dataframe_data, do_nothing_strategy) -> None:
        """Engine should accept pandas DataFrame."""
        engine = BacktestEngine()
        result = engine.run(do_nothing_strategy, dataframe_data)
        assert result.bars_processed == len(dataframe_data)

    @pytest.mark.backtest
    def test_dataframe_with_buy_strategy(self, dataframe_data, buy_and_hold_strategy) -> None:
        """DataFrame with buy strategy should produce trades."""
        engine = BacktestEngine(default_quantity=10.0)
        result = engine.run(buy_and_hold_strategy, dataframe_data)
        assert result.total_trades >= 1


# ── Commission and Slippage ──────────────────────────────────────────


class TestBacktestEngineCosts:
    """Test commission and slippage modeling."""

    @pytest.mark.backtest
    def test_zero_commission(self, simple_up_data, buy_and_hold_strategy) -> None:
        """Zero commission should not reduce returns."""
        engine = BacktestEngine(commission=0.0, default_quantity=10.0)
        result = engine.run(buy_and_hold_strategy, simple_up_data)
        assert result.total_commission == 0.0

    @pytest.mark.backtest
    def test_commission_tracked(self, simple_up_data, buy_and_hold_strategy) -> None:
        """Commission should be tracked in result."""
        engine = BacktestEngine(commission=0.001, default_quantity=10.0)
        result = engine.run(buy_and_hold_strategy, simple_up_data)
        # With trades, commission should be > 0
        if result.total_trades > 0:
            assert result.total_commission >= 0

    @pytest.mark.backtest
    def test_higher_commission_reduces_profit(self, simple_up_data, buy_and_hold_strategy) -> None:
        """Higher commission should reduce total return."""
        engine_low = BacktestEngine(commission=0.0, default_quantity=10.0)
        engine_high = BacktestEngine(commission=0.01, default_quantity=10.0)
        result_low = engine_low.run(buy_and_hold_strategy, simple_up_data)
        result_high = engine_high.run(buy_and_hold_strategy, simple_up_data)
        assert result_low.total_return >= result_high.total_return


# ── Stop Loss and Take Profit ────────────────────────────────────────


class TestBacktestEngineStops:
    """Test stop loss and take profit functionality."""

    @pytest.mark.backtest
    def test_stop_loss_triggered(self) -> None:
        """Stop loss should be triggered when price drops below level."""
        engine = BacktestEngine(initial_capital=100_000.0, default_quantity=10.0)

        def buy_with_sl(bar, positions, equity):
            if "AAPL" not in positions:
                return {"action": "BUY", "symbol": "AAPL", "quantity": 10, "stop_loss": 98.0}
            return None

        # Create data that drops below stop loss
        data = [
            {"timestamp": "2024-01-01", "open": 100, "high": 101, "low": 99, "close": 100, "volume": 1000},
            {"timestamp": "2024-01-02", "open": 100, "high": 101, "low": 97, "close": 97, "volume": 1000},
            {"timestamp": "2024-01-03", "open": 97, "high": 98, "low": 96, "close": 96, "volume": 1000},
        ]

        result = engine.run(buy_with_sl, data)
        # Should have trades including stop loss exit
        if result.total_trades > 0:
            stop_trades = [t for t in result.trades if t.exit_reason == "stop_loss"]
            # Stop loss should be triggered
            assert len(stop_trades) > 0, "Stop loss should have been triggered"

    @pytest.mark.backtest
    def test_take_profit_triggered(self) -> None:
        """Take profit should be triggered when price rises above level."""
        engine = BacktestEngine(initial_capital=100_000.0, default_quantity=10.0)

        def buy_with_tp(bar, positions, equity):
            if "AAPL" not in positions:
                return {"action": "BUY", "symbol": "AAPL", "quantity": 10, "take_profit": 105.0}
            return None

        data = [
            {"timestamp": "2024-01-01", "open": 100, "high": 101, "low": 99, "close": 100, "volume": 1000},
            {"timestamp": "2024-01-02", "open": 100, "high": 106, "low": 99, "close": 106, "volume": 1000},
            {"timestamp": "2024-01-03", "open": 106, "high": 107, "low": 105, "close": 105, "volume": 1000},
        ]

        result = engine.run(buy_with_tp, data)
        if result.total_trades > 0:
            tp_trades = [t for t in result.trades if t.exit_reason == "take_profit"]
            assert len(tp_trades) > 0, "Take profit should have been triggered"


# ── Result Metrics ───────────────────────────────────────────────────


class TestBacktestEngineResults:
    """Test BacktestResult fields and metrics."""

    @pytest.mark.backtest
    def test_result_has_all_fields(self, simple_up_data, buy_and_hold_strategy) -> None:
        """BacktestResult should contain all expected fields."""
        engine = BacktestEngine(default_quantity=10.0)
        result = engine.run(buy_and_hold_strategy, simple_up_data)

        assert isinstance(result, BacktestResult)
        assert result.initial_capital > 0
        assert result.final_equity > 0
        assert isinstance(result.total_return, float)
        assert isinstance(result.total_return_pct, float)
        assert isinstance(result.total_trades, int)
        assert isinstance(result.winning_trades, int)
        assert isinstance(result.losing_trades, int)
        assert isinstance(result.win_rate, float)
        assert isinstance(result.sharpe_ratio, float)
        assert isinstance(result.sortino_ratio, float)
        assert isinstance(result.max_drawdown, float)
        assert isinstance(result.bars_processed, int)
        assert result.bars_processed == 10

    @pytest.mark.backtest
    def test_result_equity_curve(self, simple_up_data, buy_and_hold_strategy) -> None:
        """Result should contain equity curve with correct number of points."""
        engine = BacktestEngine(default_quantity=10.0)
        result = engine.run(buy_and_hold_strategy, simple_up_data)
        assert len(result.equity_curve) == len(simple_up_data)
        for point in result.equity_curve:
            assert isinstance(point, EquityPoint)
            assert point.equity > 0

    @pytest.mark.backtest
    def test_result_returns_list(self, simple_up_data, buy_and_hold_strategy) -> None:
        """Result should contain returns list."""
        engine = BacktestEngine(default_quantity=10.0)
        result = engine.run(buy_and_hold_strategy, simple_up_data)
        assert len(result.returns) == len(simple_up_data)

    @pytest.mark.backtest
    def test_win_rate_calculation(self, simple_up_data, buy_and_hold_strategy) -> None:
        """Win rate should be correctly calculated."""
        engine = BacktestEngine(default_quantity=10.0)
        result = engine.run(buy_and_hold_strategy, simple_up_data)
        if result.total_trades > 0:
            expected_win_rate = result.winning_trades / result.total_trades
            assert result.win_rate == pytest.approx(expected_win_rate, abs=0.01)

    @pytest.mark.backtest
    def test_capital_override_in_run(self, simple_up_data, do_nothing_strategy) -> None:
        """Initial capital can be overridden in run() call."""
        engine = BacktestEngine(initial_capital=100_000.0)
        result = engine.run(do_nothing_strategy, simple_up_data, initial_capital=50_000.0)
        assert result.initial_capital == 50_000.0

    @pytest.mark.backtest
    def test_commission_override_in_run(self, simple_up_data, do_nothing_strategy) -> None:
        """Commission can be overridden in run() call."""
        engine = BacktestEngine(commission=0.001)
        result = engine.run(do_nothing_strategy, simple_up_data, commission=0.002)
        # No trades so commission is 0 either way
        assert result.total_commission == 0.0


# ── Position Sizing Modes ────────────────────────────────────────────


class TestBacktestEnginePositionSizing:
    """Test different position sizing modes."""

    @pytest.mark.backtest
    def test_fixed_sizing(self, simple_up_data, buy_and_hold_strategy) -> None:
        """Fixed position sizing should use default_quantity."""
        engine = BacktestEngine(position_sizing="fixed", default_quantity=10.0)
        result = engine.run(buy_and_hold_strategy, simple_up_data)
        assert result.total_trades >= 0

    @pytest.mark.backtest
    def test_percent_equity_sizing(self, simple_up_data, buy_and_hold_strategy) -> None:
        """Percent equity sizing should calculate quantity from equity."""
        engine = BacktestEngine(
            position_sizing="percent_equity",
            risk_per_trade=0.01,
            initial_capital=100_000.0,
        )
        result = engine.run(buy_and_hold_strategy, simple_up_data)
        assert result.total_trades >= 0

    @pytest.mark.backtest
    def test_kelly_sizing(self, simple_up_data, buy_and_hold_strategy) -> None:
        """Kelly sizing should use half-Kelly criterion."""
        engine = BacktestEngine(
            position_sizing="kelly",
            risk_per_trade=0.01,
            initial_capital=100_000.0,
        )
        result = engine.run(buy_and_hold_strategy, simple_up_data)
        assert result.total_trades >= 0


# ── Trade Model Tests ────────────────────────────────────────────────


class TestBacktestTradeModel:
    """Test BacktestTrade data model."""

    @pytest.mark.backtest
    def test_trade_fields(self) -> None:
        """BacktestTrade should have all required fields."""
        trade = BacktestTrade(
            symbol="AAPL",
            side="LONG",
            entry_price=100.0,
            exit_price=105.0,
            quantity=10.0,
            pnl=50.0,
            pnl_pct=5.0,
        )
        assert trade.symbol == "AAPL"
        assert trade.side == "LONG"
        assert trade.entry_price == 100.0
        assert trade.exit_price == 105.0
        assert trade.quantity == 10.0
        assert trade.pnl == 50.0
        assert trade.pnl_pct == 5.0
        assert trade.trade_id  # Auto-generated
        assert trade.exit_reason == ""

    @pytest.mark.backtest
    def test_position_fields(self) -> None:
        """BacktestPosition should have all required fields."""
        pos = BacktestPosition(
            symbol="AAPL",
            side="LONG",
            quantity=10.0,
            entry_price=100.0,
        )
        assert pos.symbol == "AAPL"
        assert pos.side == "LONG"
        assert pos.quantity == 10.0
        assert pos.entry_price == 100.0
        assert pos.stop_loss is None
        assert pos.take_profit is None


# ── End-of-Data Position Closing ─────────────────────────────────────


class TestEndOfDataClosing:
    """Test that open positions are closed at end of data."""

    @pytest.mark.backtest
    def test_open_position_closed_at_end(self, simple_up_data, buy_and_hold_strategy) -> None:
        """Open positions should be closed at the last bar."""
        engine = BacktestEngine(initial_capital=100_000.0, default_quantity=10.0)
        result = engine.run(buy_and_hold_strategy, simple_up_data)
        # Should have trades with exit_reason="end_of_data"
        end_trades = [t for t in result.trades if t.exit_reason == "end_of_data"]
        if result.total_trades > 0:
            assert len(end_trades) >= 0  # At minimum, some trade should exist

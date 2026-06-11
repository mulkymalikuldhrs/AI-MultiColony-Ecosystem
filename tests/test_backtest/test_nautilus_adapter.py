"""Tests for NautilusTrader Adapter."""

import numpy as np
import pandas as pd
import pytest

from quant_nanggroe.engine.backtest.nautilus_adapter import (
    AdapterOrder,
    AdapterFill,
    OrderSide,
    OrderType,
    OrderStatus,
    PurePythonSimulationAdapter,
    create_trading_adapter,
    TradingAdapter,
    _NAUTILUS_AVAILABLE,
)


@pytest.fixture
def sample_prices():
    """Sample price data."""
    dates = pd.bdate_range("2023-01-01", periods=100)
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.normal(0, 1, size=(100, 2)), axis=0)
    return pd.DataFrame(prices, index=dates, columns=["AAPL", "MSFT"])


@pytest.fixture
def sample_signals():
    """Sample signal data."""
    dates = pd.bdate_range("2023-01-01", periods=100)
    np.random.seed(42)
    signals = np.random.choice([-0.5, 0, 0.5], size=(100, 2))
    return pd.DataFrame(signals, index=dates, columns=["AAPL", "MSFT"])


class TestPurePythonAdapter:
    """Test PurePythonSimulationAdapter."""

    def test_run_basic(self, sample_prices, sample_signals):
        """Basic run should produce results."""
        adapter = PurePythonSimulationAdapter(initial_capital=1_000_000)
        result = adapter.run(sample_prices, sample_signals)

        assert result.equity_curve is not None
        assert len(result.equity_curve) == len(sample_prices)
        assert result.final_equity > 0
        assert isinstance(result.metrics, dict)

    def test_run_without_signals(self, sample_prices):
        """Run without signals should work (no trades)."""
        adapter = PurePythonSimulationAdapter(initial_capital=1_000_000)
        result = adapter.run(sample_prices)

        assert result.equity_curve is not None
        assert result.final_equity == 1_000_000  # No trades, equity unchanged

    def test_load_data(self, sample_prices, sample_signals):
        """load_data should store data."""
        adapter = PurePythonSimulationAdapter()
        adapter.load_data(sample_prices, sample_signals)
        assert adapter._prices is not None
        assert adapter._signals is not None

    def test_submit_order(self):
        """submit_order should return order ID."""
        adapter = PurePythonSimulationAdapter()
        order = AdapterOrder(
            order_id="",
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
        )
        order_id = adapter.submit_order(order)
        assert order_id.startswith("ORD-")

    def test_cancel_order(self):
        """cancel_order should work for pending orders."""
        adapter = PurePythonSimulationAdapter()
        order = AdapterOrder(
            order_id="TEST-001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=100,
            price=150.0,
        )
        adapter.submit_order(order)
        result = adapter.cancel_order("TEST-001")
        assert result is True

    def test_get_position_no_portfolio(self):
        """get_position should return None when no portfolio."""
        adapter = PurePythonSimulationAdapter()
        assert adapter.get_position("AAPL") is None

    def test_get_equity_default(self):
        """get_equity should return initial capital before run."""
        adapter = PurePythonSimulationAdapter(initial_capital=500_000)
        assert adapter.get_equity() == 500_000

    def test_get_fills(self, sample_prices, sample_signals):
        """get_fills should return fill events."""
        adapter = PurePythonSimulationAdapter(initial_capital=1_000_000)
        result = adapter.run(sample_prices, sample_signals)
        fills = adapter.get_fills()
        assert isinstance(fills, list)

    def test_reset(self, sample_prices, sample_signals):
        """reset should clear state."""
        adapter = PurePythonSimulationAdapter(initial_capital=1_000_000)
        adapter.run(sample_prices, sample_signals)
        adapter.reset()
        assert adapter._portfolio is None
        assert adapter._prices is None
        assert len(adapter._fills) == 0

    def test_metrics_present(self, sample_prices, sample_signals):
        """Run should produce standard metrics."""
        adapter = PurePythonSimulationAdapter(initial_capital=1_000_000)
        result = adapter.run(sample_prices, sample_signals)

        assert "sharpe_ratio" in result.metrics
        assert "total_return" in result.metrics
        assert "max_drawdown" in result.metrics


class TestAdapterOrder:
    """Test AdapterOrder dataclass."""

    def test_default_values(self):
        """Default values should be set correctly."""
        order = AdapterOrder(
            order_id="TEST",
            symbol="AAPL",
            side=OrderSide.BUY,
        )
        assert order.order_type == OrderType.MARKET
        assert order.quantity == 0.0
        assert order.status == OrderStatus.PENDING

    def test_order_types(self):
        """All order types should be valid."""
        for ot in OrderType:
            order = AdapterOrder(order_id="T", symbol="X", side=OrderSide.BUY, order_type=ot)
            assert order.order_type == ot


class TestAdapterFactory:
    """Test adapter factory function."""

    def test_create_pure_python(self):
        """Factory should create pure Python adapter."""
        adapter = create_trading_adapter("pure_python", initial_capital=500_000)
        assert isinstance(adapter, PurePythonSimulationAdapter)

    def test_create_auto(self):
        """Auto should create pure Python when NautilusTrader unavailable."""
        adapter = create_trading_adapter("auto")
        assert isinstance(adapter, TradingAdapter)

    def test_create_invalid_type(self):
        """Invalid type should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown adapter type"):
            create_trading_adapter("invalid")


class TestAdapterInterface:
    """Test that the adapter implements the TradingAdapter interface."""

    def test_implements_interface(self):
        """PurePythonSimulationAdapter should implement TradingAdapter."""
        adapter = PurePythonSimulationAdapter()
        assert isinstance(adapter, TradingAdapter)

    def test_abstract_methods_exist(self):
        """TradingAdapter should define all required abstract methods."""
        required = ["load_data", "submit_order", "cancel_order",
                     "get_position", "get_equity", "get_fills", "run", "reset"]
        for method in required:
            assert hasattr(TradingAdapter, method)

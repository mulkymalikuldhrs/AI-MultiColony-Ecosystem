"""Tests for Advanced Walk-Forward Analysis."""

import numpy as np
import pandas as pd
import pytest

from quant_nanggroe.engine.backtest.walk_forward import (
    WalkForwardAnalyzer,
    WFMethod,
    OptimizationCriterion,
    ParameterGrid,
    WFResult,
)
from quant_nanggroe.engine.backtest.engine import BacktestEngine, BacktestConfig


@pytest.fixture
def engine():
    """Create a BacktestEngine for testing."""
    return BacktestEngine(BacktestConfig(initial_capital=1_000_000))


@pytest.fixture
def price_data():
    """Generate price data for walk-forward testing."""
    dates = pd.bdate_range("2020-01-01", periods=756)  # 3 years
    np.random.seed(42)
    # Simple trending price
    prices = 100 + np.cumsum(np.random.normal(0.05, 1.5, size=756))
    prices = np.maximum(prices, 10)  # Prevent negative
    return pd.DataFrame({"AAPL": prices}, index=dates)


@pytest.fixture
def signal_data(price_data):
    """Generate signal data aligned with prices."""
    np.random.seed(123)
    signals = np.random.choice([-0.3, 0, 0.3], size=len(price_data))
    return pd.DataFrame({"AAPL": signals}, index=price_data.index)


class TestParameterGrid:
    """Test ParameterGrid."""

    def test_combinations(self):
        """Should generate all combinations."""
        grid = ParameterGrid({"a": [1, 2], "b": [3, 4]})
        combos = grid.combinations()
        assert len(combos) == 4
        assert {"a": 1, "b": 3} in combos

    def test_empty_grid(self):
        """Empty grid should return single empty dict."""
        grid = ParameterGrid({})
        combos = grid.combinations()
        assert combos == [{}]

    def test_random_combinations(self):
        """Random combinations should return correct number."""
        grid = ParameterGrid({"a": list(range(10)), "b": list(range(10))})
        combos = grid.random_combinations(5, random_seed=42)
        assert len(combos) == 5


class TestRollingWalkForward:
    """Test rolling walk-forward analysis."""

    def test_basic_rolling(self, engine, price_data, signal_data):
        """Basic rolling WF should produce results."""
        analyzer = WalkForwardAnalyzer(
            engine=engine,
            train_window=252,
            test_window=63,
            method=WFMethod.ROLLING,
            embargo_bars=5,
        )
        result = analyzer.analyze(price_data, signal_data)

        assert isinstance(result, WFResult)
        assert result.method == WFMethod.ROLLING
        assert len(result.windows) > 0

    def test_insufficient_data(self, engine):
        """Insufficient data should return empty result."""
        dates = pd.bdate_range("2023-01-01", periods=50)
        prices = pd.DataFrame({"AAPL": np.ones(50) * 100}, index=dates)
        signals = pd.DataFrame({"AAPL": np.zeros(50)}, index=dates)

        analyzer = WalkForwardAnalyzer(
            engine=engine, train_window=252, test_window=63,
        )
        result = analyzer.analyze(prices, signals)
        assert len(result.windows) == 0

    def test_aggregate_stats(self, engine, price_data, signal_data):
        """Aggregate stats should be calculated."""
        analyzer = WalkForwardAnalyzer(
            engine=engine,
            train_window=252,
            test_window=63,
            method=WFMethod.ROLLING,
        )
        result = analyzer.analyze(price_data, signal_data)

        assert "num_windows" in result.aggregate
        assert "avg_oos_return" in result.aggregate
        assert "avg_oos_sharpe" in result.aggregate
        assert "win_rate" in result.aggregate

    def test_degradation_stats(self, engine, price_data, signal_data):
        """Degradation stats should be calculated."""
        analyzer = WalkForwardAnalyzer(
            engine=engine,
            train_window=252,
            test_window=63,
            method=WFMethod.ROLLING,
        )
        result = analyzer.analyze(price_data, signal_data)

        assert "avg_degradation" in result.degradation_stats
        assert "pass_rate" in result.degradation_stats


class TestAnchoredWalkForward:
    """Test anchored walk-forward analysis."""

    def test_anchored(self, engine, price_data, signal_data):
        """Anchored WF should use expanding window."""
        analyzer = WalkForwardAnalyzer(
            engine=engine,
            train_window=252,
            test_window=63,
            method=WFMethod.ANCHORED,
            embargo_bars=5,
        )
        result = analyzer.analyze(price_data, signal_data)

        assert isinstance(result, WFResult)
        assert result.method == WFMethod.ANCHORED
        assert len(result.windows) > 0

        # First window should start from index 0
        assert result.windows[0].train_start == price_data.index[0]


class TestPurgedKFold:
    """Test purged k-fold cross-validation."""

    def test_purged_kfold(self, engine, price_data, signal_data):
        """Purged k-fold should produce results."""
        analyzer = WalkForwardAnalyzer(
            engine=engine,
            train_window=252,
            test_window=63,
            method=WFMethod.PURGED_KFOLD,
            embargo_bars=5,
        )
        result = analyzer.analyze(price_data, signal_data)

        assert isinstance(result, WFResult)
        assert result.method == WFMethod.PURGED_KFOLD
        assert len(result.windows) > 0


class TestCPCV:
    """Test combinatorial purged cross-validation."""

    def test_cpcv(self, engine, price_data, signal_data):
        """CPCV should produce multiple backtest paths."""
        analyzer = WalkForwardAnalyzer(
            engine=engine,
            train_window=252,
            test_window=63,
            method=WFMethod.CPCV,
            embargo_bars=3,
        )
        result = analyzer.analyze(price_data, signal_data, n_groups=4, n_test_groups=1)

        assert isinstance(result, WFResult)
        assert result.method == WFMethod.CPCV
        # Should have multiple windows (combinations)
        assert len(result.windows) >= 4  # C(4,1) = 4


class TestOverfittingDetection:
    """Test overfitting detection in walk-forward."""

    def test_overfitting_detection(self, engine, price_data, signal_data):
        """Overfitting detection should be present in results."""
        analyzer = WalkForwardAnalyzer(
            engine=engine,
            train_window=252,
            test_window=63,
            method=WFMethod.ROLLING,
        )
        result = analyzer.analyze(price_data, signal_data)

        assert "is_overfit" in result.overfitting_detection
        assert "overfit_severity" in result.overfitting_detection
        assert "avg_degradation" in result.overfitting_detection

    def test_significance_tests(self, engine, price_data, signal_data):
        """Significance tests should be present when enough windows."""
        analyzer = WalkForwardAnalyzer(
            engine=engine,
            train_window=100,
            test_window=50,
            method=WFMethod.ROLLING,
        )
        result = analyzer.analyze(price_data, signal_data)

        assert isinstance(result.significance_tests, dict)


class TestParameterOptimization:
    """Test parameter optimization in walk-forward."""

    def test_with_param_grid(self, engine, price_data, signal_data):
        """Walk-forward with parameter grid should optimize."""
        grid = ParameterGrid({"threshold": [0.1, 0.3, 0.5]})

        analyzer = WalkForwardAnalyzer(
            engine=engine,
            train_window=252,
            test_window=63,
            method=WFMethod.ROLLING,
            param_grid=grid,
        )
        result = analyzer.analyze(price_data, signal_data)

        assert len(result.windows) > 0
        # Each window should have best_params
        for w in result.windows:
            assert isinstance(w.best_params, dict)

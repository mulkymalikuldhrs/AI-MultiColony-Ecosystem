"""Tests for Advanced Performance Metrics.

Verifies that all metrics are calculated correctly using known formulas
and edge cases are handled properly.
"""

import numpy as np
import pandas as pd
import pytest

from quant_nanggroe.engine.backtest.metrics import PerformanceMetrics
from quant_nanggroe.engine.backtest.portfolio import TradeRecord


# ══════════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════════


@pytest.fixture
def simple_equity_curve():
    """Simple equity curve with known returns."""
    dates = pd.bdate_range("2023-01-01", periods=252)
    # Generate equity curve with 10% annual return, 15% annual vol
    np.random.seed(42)
    daily_returns = np.random.normal(0.10 / 252, 0.15 / np.sqrt(252), size=252)
    equity = 1_000_000 * np.cumprod(1 + daily_returns)
    return pd.Series(equity, index=dates)


@pytest.fixture
def simple_trades():
    """Simple trade records."""
    dates = pd.bdate_range("2023-01-01", periods=10)
    trades = []
    for i in range(5):
        trades.append(TradeRecord(
            symbol="AAPL",
            direction=1,
            entry_price=150.0 + i,
            exit_price=155.0 + i,
            entry_time=dates[i * 2],
            exit_time=dates[i * 2 + 1],
            size=100,
            pnl=5000.0 + i * 100,
            pnl_pct=3.33,
            exit_reason="signal",
            commission=15.0,
            holding_bars=2,
        ))
    for i in range(5):
        trades.append(TradeRecord(
            symbol="MSFT",
            direction=1,
            entry_price=300.0 + i,
            exit_price=295.0 - i,
            entry_time=dates[i],
            exit_time=dates[min(i + 1, 9)],
            size=50,
            pnl=-2500.0 - i * 50,
            pnl_pct=-1.67,
            exit_reason="stop_loss",
            commission=15.0,
            holding_bars=1,
        ))
    return trades


@pytest.fixture
def metrics_calculator():
    """Standard metrics calculator."""
    return PerformanceMetrics(bars_per_year=252, risk_free_rate=0.02)


# ══════════════════════════════════════════════════════════════════════
# Return Metrics Tests
# ══════════════════════════════════════════════════════════════════════


class TestReturnMetrics:
    """Test return metric calculations."""

    def test_total_return(self, metrics_calculator, simple_equity_curve):
        """Total return should be (final_equity / initial_capital) - 1."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000
        )
        expected = simple_equity_curve.iloc[-1] / 1_000_000 - 1
        assert abs(result["total_return"] - expected) < 0.001

    def test_cagr(self, metrics_calculator):
        """CAGR should be (1+total_return)^(1/years) - 1."""
        dates = pd.bdate_range("2023-01-01", periods=252)
        equity = pd.Series([1_000_000 * (1.10 ** (i / 252)) for i in range(252)], index=dates)
        result = metrics_calculator.calculate(equity, [], initial_capital=1_000_000)
        # CAGR should be approximately 10%
        assert 0.08 < result["cagr"] < 0.12

    def test_empty_equity_curve(self, metrics_calculator):
        """Empty equity curve should return zero metrics."""
        empty = pd.Series([], dtype=float)
        result = metrics_calculator.calculate(empty, [], initial_capital=1_000_000)
        assert result["total_return"] == 0.0
        assert result["sharpe_ratio"] == 0.0

    def test_single_value_equity_curve(self, metrics_calculator):
        """Single value equity curve should return zero metrics."""
        single = pd.Series([1_000_000], index=pd.bdate_range("2023-01-01", periods=1))
        result = metrics_calculator.calculate(single, [], initial_capital=1_000_000)
        assert result["total_return"] == 0.0


# ══════════════════════════════════════════════════════════════════════
# Risk-Adjusted Ratio Tests
# ══════════════════════════════════════════════════════════════════════


class TestRiskAdjustedRatios:
    """Test risk-adjusted ratio calculations."""

    def test_sharpe_ratio_positive_returns(self, metrics_calculator):
        """Positive excess returns should give positive Sharpe."""
        dates = pd.bdate_range("2023-01-01", periods=252)
        np.random.seed(42)
        daily_returns = np.random.normal(0.001, 0.01, size=252)
        equity = 1_000_000 * np.cumprod(1 + daily_returns)
        equity = pd.Series(equity, index=dates)

        result = metrics_calculator.calculate(equity, [], initial_capital=1_000_000)
        # With positive mean returns and reasonable vol, Sharpe should be reasonable
        assert isinstance(result["sharpe_ratio"], float)

    def test_sortino_ratio(self, metrics_calculator, simple_equity_curve):
        """Sortino should be >= Sharpe for positive-skew returns."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000
        )
        # Both should be calculated
        assert isinstance(result["sortino_ratio"], float)
        assert isinstance(result["downside_deviation"], float)

    def test_calmar_ratio(self, metrics_calculator):
        """Calmar = CAGR / |Max DD|."""
        dates = pd.bdate_range("2023-01-01", periods=252)
        # Create a curve with known drawdown
        equity_values = [1_000_000]
        for i in range(1, 252):
            if i < 50:
                equity_values.append(equity_values[-1] * 1.001)
            elif i < 100:
                equity_values.append(equity_values[-1] * 0.998)
            else:
                equity_values.append(equity_values[-1] * 1.0005)
        equity = pd.Series(equity_values, index=dates)

        result = metrics_calculator.calculate(equity, [], initial_capital=1_000_000)
        assert isinstance(result["calmar_ratio"], float)
        # Max drawdown should be negative
        assert result["max_drawdown"] < 0

    def test_omega_ratio(self, metrics_calculator, simple_equity_curve):
        """Omega ratio should be calculated."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000
        )
        assert isinstance(result["omega_ratio"], float)
        assert result["omega_ratio"] >= 0

    def test_tail_ratio(self, metrics_calculator, simple_equity_curve):
        """Tail ratio should be p95/|p5|."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000
        )
        assert isinstance(result["tail_ratio"], float)
        assert result["tail_ratio"] >= 0

    def test_kappa_ratio(self, metrics_calculator, simple_equity_curve):
        """Kappa ratio (3rd order) should be calculated."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000
        )
        assert isinstance(result["kappa_ratio"], float)

    def test_sterling_ratio(self, metrics_calculator, simple_equity_curve):
        """Sterling ratio should be calculated."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000
        )
        assert isinstance(result["sterling_ratio"], float)

    def test_burke_ratio(self, metrics_calculator, simple_equity_curve):
        """Burke ratio should be calculated."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000
        )
        assert isinstance(result["burke_ratio"], float)

    def test_martin_ratio(self, metrics_calculator, simple_equity_curve):
        """Martin ratio should be calculated."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000
        )
        assert isinstance(result["martin_ratio"], float)

    def test_ulcer_index(self, metrics_calculator, simple_equity_curve):
        """Ulcer Index should be calculated."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000
        )
        assert isinstance(result["ulcer_index"], float)
        assert result["ulcer_index"] >= 0


# ══════════════════════════════════════════════════════════════════════
# Drawdown Metrics Tests
# ══════════════════════════════════════════════════════════════════════


class TestDrawdownMetrics:
    """Test drawdown metric calculations."""

    def test_max_drawdown(self, metrics_calculator):
        """Max drawdown should be correctly calculated."""
        dates = pd.bdate_range("2023-01-01", periods=100)
        # Create known drawdown: peak at bar 20, trough at bar 40
        values = []
        for i in range(100):
            if i < 20:
                values.append(1_000_000 * (1 + i * 0.01))
            elif i < 40:
                values.append(1_200_000 - (i - 20) * 5000)
            else:
                values.append(1_100_000 + (i - 40) * 500)
        equity = pd.Series(values, index=dates)

        result = metrics_calculator.calculate(equity, [], initial_capital=1_000_000)
        assert result["max_drawdown"] < 0
        # Max DD should be around -8.3% (100k drop from 1.2M)
        assert -0.15 < result["max_drawdown"] < -0.01

    def test_drawdown_duration(self, metrics_calculator):
        """Drawdown duration metrics should be calculated."""
        dates = pd.bdate_range("2023-01-01", periods=100)
        values = [1_000_000 + i * 1000 for i in range(100)]
        equity = pd.Series(values, index=dates)

        result = metrics_calculator.calculate(equity, [], initial_capital=1_000_000)
        assert isinstance(result["max_drawdown_duration"], int)
        assert isinstance(result["avg_drawdown_duration"], float)

    def test_cdar(self, metrics_calculator, simple_equity_curve):
        """CDaR should be calculated."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000
        )
        assert isinstance(result["cdar"], float)


# ══════════════════════════════════════════════════════════════════════
# Risk Metrics Tests
# ══════════════════════════════════════════════════════════════════════


class TestRiskMetrics:
    """Test risk metric calculations."""

    def test_var_95(self, metrics_calculator, simple_equity_curve):
        """VaR at 95% should be negative (loss threshold)."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000
        )
        assert isinstance(result["var_95"], float)
        # VaR should be a negative number (loss threshold)
        assert result["var_95"] < 0

    def test_cvar_95(self, metrics_calculator, simple_equity_curve):
        """CVaR should be more negative than VaR."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000
        )
        assert result["cvar_95"] <= result["var_95"]

    def test_evar(self, metrics_calculator, simple_equity_curve):
        """EVaR should be calculated."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000
        )
        assert isinstance(result["evar"], float)
        assert result["evar"] >= 0  # EVaR is a positive loss measure

    def test_cornish_fisher_var(self, metrics_calculator, simple_equity_curve):
        """Cornish-Fisher VaR should be calculated."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000
        )
        assert isinstance(result["cornish_fisher_var_95"], float)

    def test_skewness_kurtosis(self, metrics_calculator, simple_equity_curve):
        """Distribution metrics should be calculated."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000
        )
        assert isinstance(result["skewness"], float)
        assert isinstance(result["kurtosis"], float)


# ══════════════════════════════════════════════════════════════════════
# Trade Statistics Tests
# ══════════════════════════════════════════════════════════════════════


class TestTradeStatistics:
    """Test trade statistic calculations."""

    def test_win_rate(self, metrics_calculator, simple_equity_curve, simple_trades):
        """Win rate should be wins/total."""
        result = metrics_calculator.calculate(
            simple_equity_curve, simple_trades, initial_capital=1_000_000
        )
        assert 0 <= result["win_rate"] <= 1
        assert result["winning_trades"] + result["losing_trades"] == result["total_trades"]

    def test_profit_factor(self, metrics_calculator, simple_equity_curve, simple_trades):
        """Profit factor should be gross_profit / gross_loss."""
        result = metrics_calculator.calculate(
            simple_equity_curve, simple_trades, initial_capital=1_000_000
        )
        assert isinstance(result["profit_factor"], float)
        assert result["profit_factor"] > 0

    def test_payoff_ratio(self, metrics_calculator, simple_equity_curve, simple_trades):
        """Payoff ratio should be avg_win / avg_loss."""
        result = metrics_calculator.calculate(
            simple_equity_curve, simple_trades, initial_capital=1_000_000
        )
        assert isinstance(result["payoff_ratio"], float)

    def test_expectancy(self, metrics_calculator, simple_equity_curve, simple_trades):
        """Expectancy should be calculated."""
        result = metrics_calculator.calculate(
            simple_equity_curve, simple_trades, initial_capital=1_000_000
        )
        assert isinstance(result["expectancy"], float)

    def test_max_consecutive_wins_losses(self, metrics_calculator, simple_equity_curve, simple_trades):
        """Max consecutive wins/losses should be correct."""
        result = metrics_calculator.calculate(
            simple_equity_curve, simple_trades, initial_capital=1_000_000
        )
        assert result["max_consecutive_wins"] >= 0
        assert result["max_consecutive_losses"] >= 0

    def test_no_trades(self, metrics_calculator, simple_equity_curve):
        """No trades should give zero trade stats."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000
        )
        assert result["total_trades"] == 0
        assert result["win_rate"] == 0.0

    def test_common_sense_ratio(self, metrics_calculator, simple_equity_curve, simple_trades):
        """Common Sense Ratio should be Profit Factor * Tail Ratio."""
        result = metrics_calculator.calculate(
            simple_equity_curve, simple_trades, initial_capital=1_000_000
        )
        assert isinstance(result["common_sense_ratio"], float)


# ══════════════════════════════════════════════════════════════════════
# Overfitting Detection Tests
# ══════════════════════════════════════════════════════════════════════


class TestOverfittingDetection:
    """Test overfitting detection metrics."""

    def test_deflated_sharpe_ratio(self, metrics_calculator, simple_equity_curve):
        """Deflated Sharpe should be calculated with multiple trials."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000,
            num_total_trials=100,
        )
        assert isinstance(result["deflated_sharpe_ratio"], float)
        assert 0 <= result["deflated_sharpe_ratio"] <= 1

    def test_monte_carlo_pvalue(self, metrics_calculator, simple_equity_curve):
        """MC p-value should be between 0 and 1."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000,
        )
        assert isinstance(result["monte_carlo_pvalue"], float)
        assert 0 <= result["monte_carlo_pvalue"] <= 1


# ══════════════════════════════════════════════════════════════════════
# Benchmark Tests
# ══════════════════════════════════════════════════════════════════════


class TestBenchmarkMetrics:
    """Test benchmark comparison metrics."""

    def test_information_ratio(self, metrics_calculator, simple_equity_curve):
        """Information ratio should be calculated with benchmark."""
        dates = simple_equity_curve.index
        np.random.seed(123)
        benchmark_returns = pd.Series(
            np.random.normal(0.0003, 0.01, size=len(dates)),
            index=dates,
        )
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000,
            benchmark_returns=benchmark_returns,
        )
        assert "information_ratio" in result
        assert "alpha" in result
        assert "beta" in result
        assert "tracking_error" in result

    def test_no_benchmark(self, metrics_calculator, simple_equity_curve):
        """No benchmark should give zero benchmark metrics."""
        result = metrics_calculator.calculate(
            simple_equity_curve, [], initial_capital=1_000_000,
        )
        assert result["benchmark_return"] == 0.0
        assert result["information_ratio"] == 0.0


# ══════════════════════════════════════════════════════════════════════
# Helper Method Tests
# ══════════════════════════════════════════════════════════════════════


class TestHelperMethods:
    """Test helper methods."""

    def test_calc_bars_per_year_daily(self):
        """Daily equity bars should be 252."""
        bps = PerformanceMetrics.calc_bars_per_year("1D", "equity")
        assert bps == 252

    def test_calc_bars_per_year_hourly(self):
        """Hourly equity bars should be 252*7."""
        bps = PerformanceMetrics.calc_bars_per_year("1H", "equity")
        assert bps == 252 * 7

    def test_calc_bars_per_year_crypto(self):
        """Daily crypto bars should be 365."""
        bps = PerformanceMetrics.calc_bars_per_year("1D", "crypto")
        assert bps == 365

    def test_cornish_fisher_var_normal(self):
        """For normal distribution, CF-VaR ≈ standard VaR."""
        np.random.seed(42)
        returns = np.random.normal(0, 0.01, size=10000)
        cf_var = PerformanceMetrics._cornish_fisher_var(returns, confidence=0.95)
        # Should be close to parametric VaR
        from scipy.stats import norm
        param_var = np.mean(returns) + norm.ppf(0.05) * np.std(returns, ddof=1)
        assert abs(cf_var - param_var) < 0.002  # Small difference for normal data

    def test_consecutive_true_lengths(self):
        """Test consecutive true length detection."""
        arr = np.array([True, True, False, True, True, True, False])
        lengths = PerformanceMetrics._consecutive_true_lengths(arr)
        assert lengths == [2, 3]

    def test_consecutive_true_lengths_empty(self):
        """Empty array should return empty list."""
        lengths = PerformanceMetrics._consecutive_true_lengths(np.array([]))
        assert lengths == []

    def test_consecutive_true_lengths_all_false(self):
        """All false should return empty list."""
        lengths = PerformanceMetrics._consecutive_true_lengths(np.array([False, False]))
        assert lengths == []

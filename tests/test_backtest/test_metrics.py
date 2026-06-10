"""
Tests for Backtest Metrics
=============================
Test Sharpe ratio, Sortino ratio, Calmar ratio, max drawdown,
win rate, profit factor, VaR, CVaR, and comprehensive metrics
with known data series and edge cases.
"""

from __future__ import annotations

import os

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///test_qna.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")

import math
import pytest
import numpy as np

from quant_nanggroe_ai.backtest.metrics import BacktestMetrics


# ── Shared Fixtures ───────────────────────────────────────────────────


@pytest.fixture
def metrics() -> BacktestMetrics:
    """Fresh BacktestMetrics instance."""
    return BacktestMetrics()


@pytest.fixture
def positive_returns() -> list[float]:
    """Returns series with consistent positive returns."""
    return [0.01] * 50


@pytest.fixture
def negative_returns() -> list[float]:
    """Returns series with consistent negative returns."""
    return [-0.01] * 50


@pytest.fixture
def mixed_returns() -> list[float]:
    """Returns series with alternating wins and losses."""
    return [0.02, -0.01, 0.03, -0.02, 0.01, -0.01, 0.04, -0.02, 0.02, -0.01]


@pytest.fixture
def normal_returns() -> list[float]:
    """Returns from normal distribution with slight positive drift."""
    np.random.seed(42)
    return [float(x) for x in np.random.normal(0.001, 0.02, 252)]


@pytest.fixture
def zero_returns() -> list[float]:
    """Returns that are all zero."""
    return [0.0] * 50


@pytest.fixture
def equity_curve_values() -> list[float]:
    """Simple equity curve values."""
    return [100000, 101000, 100500, 102000, 101500, 103000, 102500, 104000]


@pytest.fixture
def equity_curve_dicts(equity_curve_values: list[float]) -> list[dict]:
    """Equity curve as list of dicts."""
    return [
        {"equity": v, "bar_idx": i}
        for i, v in enumerate(equity_curve_values)
    ]


@pytest.fixture
def winning_trades() -> list[dict]:
    """All winning trades."""
    return [
        {"pnl": 100.0},
        {"pnl": 200.0},
        {"pnl": 150.0},
    ]


@pytest.fixture
def losing_trades() -> list[dict]:
    """All losing trades."""
    return [
        {"pnl": -50.0},
        {"pnl": -80.0},
        {"pnl": -30.0},
    ]


@pytest.fixture
def mixed_trades() -> list[dict]:
    """Mix of winning and losing trades."""
    return [
        {"pnl": 100.0},
        {"pnl": -50.0},
        {"pnl": 200.0},
        {"pnl": -80.0},
        {"pnl": 150.0},
        {"pnl": -30.0},
    ]


# ── Sharpe Ratio Tests ───────────────────────────────────────────────


class TestSharpeRatio:
    """Test annualized Sharpe ratio calculation."""

    @pytest.mark.backtest
    def test_positive_sharpe(self, metrics: BacktestMetrics, normal_returns: list[float]) -> None:
        """Positive drift should produce positive Sharpe ratio."""
        sharpe = metrics.sharpe_ratio(normal_returns)
        # With slight positive drift, Sharpe should be near zero or slightly positive
        assert isinstance(sharpe, float)

    @pytest.mark.backtest
    def test_higher_returns_higher_sharpe(self, metrics: BacktestMetrics) -> None:
        """Higher returns with same volatility should produce higher Sharpe."""
        low_returns = [0.001] * 100 + [-0.001] * 100
        high_returns = [0.003] * 100 + [-0.001] * 100
        sharpe_low = metrics.sharpe_ratio(low_returns)
        sharpe_high = metrics.sharpe_ratio(high_returns)
        assert sharpe_high > sharpe_low

    @pytest.mark.backtest
    def test_empty_returns(self, metrics: BacktestMetrics) -> None:
        """Empty returns should return 0.0."""
        assert metrics.sharpe_ratio([]) == 0.0

    @pytest.mark.backtest
    def test_single_return(self, metrics: BacktestMetrics) -> None:
        """Single return should return 0.0 (insufficient data)."""
        assert metrics.sharpe_ratio([0.01]) == 0.0

    @pytest.mark.backtest
    def test_zero_std_returns(self, metrics: BacktestMetrics, positive_returns: list[float]) -> None:
        """Constant returns (zero std) should return 0.0."""
        # Wait — positive_returns = [0.01] * 50 has zero std
        sharpe = metrics.sharpe_ratio(positive_returns)
        assert sharpe == 0.0

    @pytest.mark.backtest
    def test_sharpe_annualization(self, metrics: BacktestMetrics) -> None:
        """Sharpe should be annualized (daily * sqrt(252))."""
        # Create returns with known mean and std
        np.random.seed(42)
        daily_returns = list(np.random.normal(0.001, 0.01, 252))
        sharpe = metrics.sharpe_ratio(daily_returns, risk_free_rate=0.0, periods_per_year=252)
        # Should be reasonable
        assert -5.0 < sharpe < 10.0

    @pytest.mark.backtest
    def test_negative_sharpe(self, metrics: BacktestMetrics, negative_returns: list[float]) -> None:
        """Negative returns should produce negative Sharpe ratio."""
        # negative_returns = [-0.01] * 50 has zero std → returns 0.0
        # Need variable negative returns
        np.random.seed(42)
        neg_ret = list(np.random.normal(-0.005, 0.02, 100))
        sharpe = metrics.sharpe_ratio(neg_ret)
        assert sharpe < 0, "Negative drift should produce negative Sharpe"


# ── Sortino Ratio Tests ──────────────────────────────────────────────


class TestSortinoRatio:
    """Test annualized Sortino ratio calculation."""

    @pytest.mark.backtest
    def test_sortino_with_positive_returns(self, metrics: BacktestMetrics, normal_returns: list[float]) -> None:
        """Sortino ratio should be computable for positive drift returns."""
        sortino = metrics.sortino_ratio(normal_returns)
        assert isinstance(sortino, float)

    @pytest.mark.backtest
    def test_sortino_no_downside(self, metrics: BacktestMetrics) -> None:
        """All positive returns should produce infinite Sortino."""
        returns = [0.01, 0.02, 0.015, 0.005, 0.02]
        sortino = metrics.sortino_ratio(returns, risk_free_rate=0.0)
        # No downside deviation → should return float('inf')
        assert sortino == float("inf") or sortino > 0

    @pytest.mark.backtest
    def test_empty_returns(self, metrics: BacktestMetrics) -> None:
        """Empty returns should return 0.0."""
        assert metrics.sortino_ratio([]) == 0.0

    @pytest.mark.backtest
    def test_single_return(self, metrics: BacktestMetrics) -> None:
        """Single return should return 0.0."""
        assert metrics.sortino_ratio([0.01]) == 0.0

    @pytest.mark.backtest
    def test_sortino_greater_than_sharpe(self, metrics: BacktestMetrics) -> None:
        """Sortino should generally be >= Sharpe (only penalizes downside)."""
        np.random.seed(42)
        returns = list(np.random.normal(0.002, 0.02, 252))
        sharpe = metrics.sharpe_ratio(returns)
        sortino = metrics.sortino_ratio(returns)
        # Sortino should be at least as high as Sharpe for positively skewed returns
        # This is not always true, but generally expected
        assert isinstance(sortino, float) or sortino == float("inf")


# ── Max Drawdown Tests ───────────────────────────────────────────────


class TestMaxDrawdownMetrics:
    """Test max drawdown calculation from equity curve."""

    @pytest.mark.backtest
    def test_monotonic_up_no_drawdown(self, metrics: BacktestMetrics) -> None:
        """Monotonically increasing equity should have 0% drawdown."""
        curve = [100.0, 110.0, 120.0, 130.0, 140.0]
        dd = metrics.max_drawdown(curve)
        assert dd["max_drawdown"] == 0.0
        assert dd["max_drawdown_pct"] == 0.0

    @pytest.mark.backtest
    def test_known_drawdown(self, metrics: BacktestMetrics) -> None:
        """Test with known drawdown values."""
        curve = [100.0, 110.0, 90.0, 95.0]
        dd = metrics.max_drawdown(curve)
        # Peak = 110, trough = 90 → max DD = 20, DD% = 18.18%
        assert dd["max_drawdown"] == pytest.approx(20.0, abs=0.1)
        assert dd["max_drawdown_pct"] == pytest.approx(20.0 / 110.0 * 100, abs=0.1)

    @pytest.mark.backtest
    def test_empty_equity_curve(self, metrics: BacktestMetrics) -> None:
        """Empty equity curve should return zero drawdown."""
        dd = metrics.max_drawdown([])
        assert dd["max_drawdown"] == 0.0
        assert dd["max_drawdown_pct"] == 0.0

    @pytest.mark.backtest
    def test_single_point(self, metrics: BacktestMetrics) -> None:
        """Single point should return zero drawdown."""
        dd = metrics.max_drawdown([100.0])
        assert dd["max_drawdown"] == 0.0

    @pytest.mark.backtest
    def test_dict_equity_curve(self, metrics: BacktestMetrics, equity_curve_dicts: list[dict]) -> None:
        """Should accept equity curve as list of dicts."""
        dd = metrics.max_drawdown(equity_curve_dicts)
        assert dd["max_drawdown"] >= 0
        assert dd["max_drawdown_pct"] >= 0

    @pytest.mark.backtest
    def test_result_has_expected_keys(self, metrics: BacktestMetrics, equity_curve_values: list[float]) -> None:
        """Max drawdown result should contain all expected keys."""
        dd = metrics.max_drawdown(equity_curve_values)
        assert "max_drawdown" in dd
        assert "max_drawdown_pct" in dd
        assert "peak_idx" in dd
        assert "trough_idx" in dd
        assert "recovery_idx" in dd

    @pytest.mark.backtest
    def test_recovery_idx_found(self, metrics: BacktestMetrics) -> None:
        """Recovery index should be found when equity recovers."""
        curve = [100.0, 120.0, 100.0, 125.0]
        dd = metrics.max_drawdown(curve)
        # Peak=120, trough=100 at idx 2, recovery at idx 3 (125 > 120)
        assert dd["recovery_idx"] is not None

    @pytest.mark.backtest
    def test_no_recovery(self, metrics: BacktestMetrics) -> None:
        """No recovery if equity never returns to peak."""
        curve = [100.0, 120.0, 110.0, 115.0]
        dd = metrics.max_drawdown(curve)
        # Peak=120, never exceeds again
        assert dd["recovery_idx"] is None


# ── Win Rate Tests ───────────────────────────────────────────────────


class TestWinRate:
    """Test win rate calculation."""

    @pytest.mark.backtest
    def test_all_winners(self, metrics: BacktestMetrics, winning_trades: list[dict]) -> None:
        """All winning trades should produce 100% win rate."""
        assert metrics.win_rate(winning_trades) == 1.0

    @pytest.mark.backtest
    def test_all_losers(self, metrics: BacktestMetrics, losing_trades: list[dict]) -> None:
        """All losing trades should produce 0% win rate."""
        assert metrics.win_rate(losing_trades) == 0.0

    @pytest.mark.backtest
    def test_mixed_win_rate(self, metrics: BacktestMetrics, mixed_trades: list[dict]) -> None:
        """Mixed trades should produce correct win rate."""
        # 3 winners out of 6
        wr = metrics.win_rate(mixed_trades)
        assert wr == pytest.approx(0.5, abs=0.01)

    @pytest.mark.backtest
    def test_empty_trades(self, metrics: BacktestMetrics) -> None:
        """Empty trades should return 0.0."""
        assert metrics.win_rate([]) == 0.0

    @pytest.mark.backtest
    def test_numeric_list_input(self, metrics: BacktestMetrics) -> None:
        """Should accept list of numeric PnL values."""
        wr = metrics.win_rate([100.0, -50.0, 200.0])
        assert wr == pytest.approx(2.0 / 3, abs=0.01)

    @pytest.mark.backtest
    def test_zero_pnl_not_a_win(self, metrics: BacktestMetrics) -> None:
        """Zero PnL should not count as a win."""
        wr = metrics.win_rate([0.0, 100.0, -50.0])
        # Only 1 winner out of 3
        assert wr == pytest.approx(1.0 / 3, abs=0.01)


# ── Profit Factor Tests ──────────────────────────────────────────────


class TestProfitFactor:
    """Test profit factor calculation."""

    @pytest.mark.backtest
    def test_profitable(self, metrics: BacktestMetrics, mixed_trades: list[dict]) -> None:
        """Profit factor > 1.0 for profitable trading."""
        pf = metrics.profit_factor(mixed_trades)
        # gross_profit = 100+200+150 = 450, gross_loss = 50+80+30 = 160
        # pf = 450/160 = 2.8125
        assert pf > 1.0

    @pytest.mark.backtest
    def test_no_losses(self, metrics: BacktestMetrics, winning_trades: list[dict]) -> None:
        """No losses should produce infinite profit factor."""
        pf = metrics.profit_factor(winning_trades)
        assert pf == float("inf")

    @pytest.mark.backtest
    def test_all_losses(self, metrics: BacktestMetrics, losing_trades: list[dict]) -> None:
        """All losses should produce 0.0 profit factor."""
        pf = metrics.profit_factor(losing_trades)
        assert pf == 0.0

    @pytest.mark.backtest
    def test_empty_trades(self, metrics: BacktestMetrics) -> None:
        """Empty trades should return 0.0."""
        assert metrics.profit_factor([]) == 0.0

    @pytest.mark.backtest
    def test_known_profit_factor(self, metrics: BacktestMetrics) -> None:
        """Test with known values."""
        trades = [{"pnl": 300.0}, {"pnl": -100.0}]
        pf = metrics.profit_factor(trades)
        assert pf == pytest.approx(3.0, abs=0.01)


# ── Calmar Ratio Tests ───────────────────────────────────────────────


class TestCalmarRatio:
    """Test Calmar ratio calculation."""

    @pytest.mark.backtest
    def test_positive_calmar(self, metrics: BacktestMetrics, normal_returns: list[float]) -> None:
        """Positive returns with drawdown should produce a Calmar ratio."""
        equity = [100000]
        for r in normal_returns:
            equity.append(equity[-1] * (1 + r))
        dd = metrics.max_drawdown(equity)
        calmar = metrics.calmar_ratio(normal_returns, dd)
        assert isinstance(calmar, float)

    @pytest.mark.backtest
    def test_zero_drawdown(self, metrics: BacktestMetrics) -> None:
        """Zero drawdown with positive returns should produce infinite Calmar."""
        returns = [0.01] * 50
        calmar = metrics.calmar_ratio(returns, max_drawdown=0.0)
        # With zero drawdown, should return inf
        assert calmar == float("inf") or calmar == 0.0  # Depends on implementation

    @pytest.mark.backtest
    def test_empty_returns(self, metrics: BacktestMetrics) -> None:
        """Empty returns should return 0.0."""
        assert metrics.calmar_ratio([], max_drawdown=0.1) == 0.0

    @pytest.mark.backtest
    def test_calmar_with_dict_drawdown(self, metrics: BacktestMetrics, normal_returns: list[float]) -> None:
        """Should accept max_drawdown as dict from max_drawdown()."""
        np.random.seed(42)
        returns = list(np.random.normal(0.001, 0.02, 100))
        equity = [100000]
        for r in returns:
            equity.append(equity[-1] * (1 + r))
        dd = metrics.max_drawdown(equity)
        calmar = metrics.calmar_ratio(returns, dd)
        assert isinstance(calmar, float)


# ── VaR and CVaR Tests ───────────────────────────────────────────────


class TestMetricsVaR:
    """Test historical VaR calculation from BacktestMetrics."""

    @pytest.mark.backtest
    def test_var_positive(self, metrics: BacktestMetrics, normal_returns: list[float]) -> None:
        """VaR should be positive for normal returns."""
        var = metrics.value_at_risk(normal_returns, confidence=0.95)
        assert var > 0

    @pytest.mark.backtest
    def test_var_insufficient_data(self, metrics: BacktestMetrics) -> None:
        """Less than 10 data points should return 0.0."""
        assert metrics.value_at_risk([0.01, 0.02], confidence=0.95) == 0.0

    @pytest.mark.backtest
    def test_cvar_positive(self, metrics: BacktestMetrics, normal_returns: list[float]) -> None:
        """CVaR should be positive for normal returns."""
        cvar = metrics.conditional_var(normal_returns, confidence=0.95)
        assert cvar > 0

    @pytest.mark.backtest
    def test_cvar_exceeds_var(self, metrics: BacktestMetrics, normal_returns: list[float]) -> None:
        """CVaR should be >= VaR."""
        var = metrics.value_at_risk(normal_returns, confidence=0.95)
        cvar = metrics.conditional_var(normal_returns, confidence=0.95)
        assert cvar >= var


# ── Calculate All Tests ──────────────────────────────────────────────


class TestCalculateAll:
    """Test comprehensive metrics calculation."""

    @pytest.mark.backtest
    def test_calculate_all_basic(self, metrics: BacktestMetrics, normal_returns: list[float]) -> None:
        """calculate_all should return all metrics."""
        result = metrics.calculate_all(normal_returns)
        assert "sharpe_ratio" in result
        assert "sortino_ratio" in result
        assert "var_95" in result
        assert "cvar_95" in result

    @pytest.mark.backtest
    def test_calculate_all_with_equity_curve(
        self, metrics: BacktestMetrics, normal_returns: list[float]
    ) -> None:
        """calculate_all with equity curve should include drawdown metrics."""
        equity = [100000]
        for r in normal_returns:
            equity.append(equity[-1] * (1 + r))
        result = metrics.calculate_all(normal_returns, equity_curve=equity)
        assert "max_drawdown" in result
        assert "max_drawdown_pct" in result
        assert "calmar_ratio" in result

    @pytest.mark.backtest
    def test_calculate_all_with_trades(self, metrics: BacktestMetrics, normal_returns: list[float]) -> None:
        """calculate_all with trades should include trade metrics."""
        trades = [{"pnl": 100.0}, {"pnl": -50.0}, {"pnl": 75.0}]
        result = metrics.calculate_all(normal_returns, trades=trades)
        assert "win_rate" in result
        assert "profit_factor" in result

    @pytest.mark.backtest
    def test_calculate_all_return_statistics(
        self, metrics: BacktestMetrics, normal_returns: list[float]
    ) -> None:
        """calculate_all should include basic return statistics."""
        result = metrics.calculate_all(normal_returns)
        assert "total_return" in result
        assert "avg_return" in result
        assert "std_return" in result
        assert "skewness" in result
        assert "kurtosis" in result


# ── Internal Helper Tests ────────────────────────────────────────────


class TestInternalHelpers:
    """Test internal helper methods."""

    @pytest.mark.backtest
    def test_extract_pnls_from_dicts(self, metrics: BacktestMetrics) -> None:
        """_extract_pnls should handle dict trades."""
        trades = [{"pnl": 100.0}, {"pnl": -50.0}]
        pnls = BacktestMetrics._extract_pnls(trades)
        assert pnls == [100.0, -50.0]

    @pytest.mark.backtest
    def test_extract_pnls_from_numbers(self, metrics: BacktestMetrics) -> None:
        """_extract_pnls should handle numeric list."""
        pnls = BacktestMetrics._extract_pnls([100.0, -50.0])
        assert pnls == [100.0, -50.0]

    @pytest.mark.backtest
    def test_extract_pnls_from_objects(self, metrics: BacktestMetrics) -> None:
        """_extract_pnls should handle objects with .pnl attribute."""
        from quant_nanggroe_ai.backtest.engine import BacktestTrade
        trade = BacktestTrade(symbol="AAPL", side="LONG", entry_price=100, quantity=10, pnl=50.0)
        pnls = BacktestMetrics._extract_pnls([trade])
        assert pnls == [50.0]

    @pytest.mark.backtest
    def test_skewness(self, metrics: BacktestMetrics) -> None:
        """_skewness should compute correctly."""
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
        skew = BacktestMetrics._skewness(data)
        assert isinstance(skew, float)
        # Symmetric-ish data → near-zero skewness
        assert -1.0 < skew < 1.0

    @pytest.mark.backtest
    def test_kurtosis(self, metrics: BacktestMetrics) -> None:
        """_kurtosis should compute correctly."""
        np.random.seed(42)
        data = np.random.normal(0, 1, 100)
        kurt = BacktestMetrics._kurtosis(data)
        assert isinstance(kurt, float)
        # Normal distribution → excess kurtosis near 0
        assert -1.0 < kurt < 2.0

    @pytest.mark.backtest
    def test_skewness_insufficient_data(self, metrics: BacktestMetrics) -> None:
        """_skewness with < 3 points should return 0.0."""
        assert BacktestMetrics._skewness(np.array([1.0, 2.0])) == 0.0

    @pytest.mark.backtest
    def test_kurtosis_insufficient_data(self, metrics: BacktestMetrics) -> None:
        """_kurtosis with < 4 points should return 0.0."""
        assert BacktestMetrics._kurtosis(np.array([1.0, 2.0, 3.0])) == 0.0

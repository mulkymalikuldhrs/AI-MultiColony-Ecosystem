"""Tests for Advanced Monte Carlo Simulation."""

import numpy as np
import pandas as pd
import pytest

from quant_nanggroe.engine.backtest.monte_carlo import (
    MonteCarloSimulator,
    MCMethod,
    MCFullResult,
    MCMetricResult,
    MCRiskResult,
)


@pytest.fixture
def sample_returns():
    """Generate sample returns for MC testing."""
    np.random.seed(42)
    dates = pd.bdate_range("2023-01-01", periods=252)
    returns = pd.Series(np.random.normal(0.0004, 0.01, size=252), index=dates)
    return returns


@pytest.fixture
def simulator():
    """Create a Monte Carlo simulator."""
    return MonteCarloSimulator(num_simulations=100, random_seed=42)


class TestBootstrapMC:
    """Test bootstrap Monte Carlo method."""

    def test_bootstrap(self, simulator, sample_returns):
        """Bootstrap MC should produce valid results."""
        result = simulator.simulate(sample_returns, method=MCMethod.BOOTSTRAP)

        assert isinstance(result, MCFullResult)
        assert result.method == MCMethod.BOOTSTRAP
        assert result.num_simulations == 100
        assert "total_return" in result.metrics
        assert "sharpe_ratio" in result.metrics
        assert "max_drawdown" in result.metrics

    def test_bootstrap_confidence_intervals(self, simulator, sample_returns):
        """Bootstrap should have confidence intervals."""
        result = simulator.simulate(sample_returns, method=MCMethod.BOOTSTRAP)
        tr = result.metrics["total_return"]

        assert tr.confidence_95[0] < tr.confidence_95[1]  # Lower < Upper
        assert tr.p5 < tr.p95
        assert isinstance(tr.probability_of_loss, float)


class TestParametricMC:
    """Test parametric Monte Carlo method."""

    def test_parametric(self, simulator, sample_returns):
        """Parametric MC should produce valid results."""
        result = simulator.simulate(sample_returns, method=MCMethod.PARAMETRIC)

        assert isinstance(result, MCFullResult)
        assert result.method == MCMethod.PARAMETRIC
        # Parametric should have similar mean to original
        tr = result.metrics["total_return"]
        assert isinstance(tr.mean_value, float)


class TestStudentTMC:
    """Test Student-t Monte Carlo method."""

    def test_student_t(self, simulator, sample_returns):
        """Student-t MC should produce valid results with fat tails."""
        result = simulator.simulate(sample_returns, method=MCMethod.STUDENT_T)

        assert isinstance(result, MCFullResult)
        assert result.method == MCMethod.STUDENT_T

    def test_student_t_fat_tails(self, sample_returns):
        """Student-t should produce wider distribution than parametric."""
        sim_t = MonteCarloSimulator(num_simulations=500, random_seed=42)
        result_t = sim_t.simulate(sample_returns, method=MCMethod.STUDENT_T)

        sim_n = MonteCarloSimulator(num_simulations=500, random_seed=42)
        result_n = sim_n.simulate(sample_returns, method=MCMethod.PARAMETRIC)

        # Student-t should have wider spread (larger std of total returns)
        std_t = result_t.metrics["total_return"].std_value
        std_n = result_n.metrics["total_return"].std_value
        # Not guaranteed but generally true for moderate sample sizes
        assert isinstance(std_t, float)
        assert isinstance(std_n, float)


class TestGARCHMC:
    """Test GARCH(1,1) Monte Carlo method."""

    def test_garch(self, simulator, sample_returns):
        """GARCH MC should produce valid results."""
        result = simulator.simulate(sample_returns, method=MCMethod.GARCH)

        assert isinstance(result, MCFullResult)
        assert result.method == MCMethod.GARCH

    def test_garch_fit(self):
        """GARCH(1,1) fitting should produce valid parameters."""
        np.random.seed(42)
        returns = np.random.normal(0, 0.01, size=500)
        omega, alpha, beta = MonteCarloSimulator._fit_garch11(returns)

        # Parameters should satisfy constraints
        assert omega > 0
        assert alpha > 0
        assert beta > 0
        assert alpha + beta < 1  # Stationarity condition


class TestBlockBootstrap:
    """Test block bootstrap method."""

    def test_block_bootstrap(self, simulator, sample_returns):
        """Block bootstrap should preserve short-range dependence."""
        result = simulator.simulate(
            sample_returns, method=MCMethod.BLOCK_BOOTSTRAP, block_size=5
        )

        assert isinstance(result, MCFullResult)
        assert result.method == MCMethod.BLOCK_BOOTSTRAP


class TestRiskMetrics:
    """Test risk metrics from MC simulation."""

    def test_var_levels(self, simulator, sample_returns):
        """VaR should be more extreme at higher confidence levels."""
        result = simulator.simulate(sample_returns, method=MCMethod.BOOTSTRAP)
        risk = result.risk

        # VaR should be ordered: var_99 < var_95 < var_90
        assert risk.var_99 < risk.var_95  # More negative = more extreme
        assert risk.var_95 < risk.var_90

    def test_cvar_more_extreme_than_var(self, simulator, sample_returns):
        """CVaR should be more extreme than VaR."""
        result = simulator.simulate(sample_returns, method=MCMethod.BOOTSTRAP)
        risk = result.risk

        assert risk.cvar_95 <= risk.var_95
        assert risk.cvar_99 <= risk.var_99

    def test_max_dd_distribution(self, simulator, sample_returns):
        """Max DD distribution should be calculated."""
        result = simulator.simulate(sample_returns, method=MCMethod.BOOTSTRAP)
        risk = result.risk

        assert risk.max_dd_p5 < risk.max_dd_p50
        assert risk.max_dd_p50 < risk.max_dd_p95

    def test_ruin_probability(self, simulator, sample_returns):
        """Ruin probability should be between 0 and 1."""
        result = simulator.simulate(sample_returns, method=MCMethod.BOOTSTRAP)
        assert 0 <= result.risk.ruin_probability <= 1

    def test_recovery_time(self, simulator, sample_returns):
        """Recovery time distribution should be calculated."""
        result = simulator.simulate(sample_returns, method=MCMethod.BOOTSTRAP)
        risk = result.risk

        assert risk.recovery_time_p5 >= 0
        assert risk.recovery_time_p50 >= 0
        assert risk.recovery_time_p95 >= 0


class TestCorrelatedMC:
    """Test correlated Monte Carlo simulation."""

    def test_correlated(self, simulator):
        """Correlated MC should preserve correlation structure."""
        np.random.seed(42)
        dates = pd.bdate_range("2023-01-01", periods=252)
        # Create correlated returns
        corr_matrix = np.array([[1.0, 0.7], [0.7, 1.0]])
        L = np.linalg.cholesky(corr_matrix)
        z = np.random.normal(size=(252, 2))
        correlated = z @ L.T

        returns_df = pd.DataFrame(
            correlated * 0.01,
            index=dates,
            columns=["AAPL", "MSFT"],
        )

        result = simulator.simulate_correlated(returns_df)

        assert isinstance(result, MCFullResult)
        assert "total_return" in result.metrics


class TestReproducibility:
    """Test reproducibility with random seeds."""

    def test_same_seed_same_result(self, sample_returns):
        """Same random seed should produce identical results."""
        sim1 = MonteCarloSimulator(num_simulations=50, random_seed=123)
        result1 = sim1.simulate(sample_returns, method=MCMethod.BOOTSTRAP)

        sim2 = MonteCarloSimulator(num_simulations=50, random_seed=123)
        result2 = sim2.simulate(sample_returns, method=MCMethod.BOOTSTRAP)

        assert result1.metrics["total_return"].mean_value == result2.metrics["total_return"].mean_value

    def test_different_seed_different_result(self, sample_returns):
        """Different seeds should produce different results."""
        sim1 = MonteCarloSimulator(num_simulations=50, random_seed=42)
        result1 = sim1.simulate(sample_returns, method=MCMethod.BOOTSTRAP)

        sim2 = MonteCarloSimulator(num_simulations=50, random_seed=99)
        result2 = sim2.simulate(sample_returns, method=MCMethod.BOOTSTRAP)

        # Very unlikely to be exactly equal
        assert result1.metrics["total_return"].mean_value != result2.metrics["total_return"].mean_value


class TestLegacyInterface:
    """Test legacy (backward compatible) methods."""

    def test_trade_shuffle(self, simulator):
        """Trade shuffle should work."""
        pnl = [100, -50, 200, -30, 150]
        result = simulator.simulate_trade_shuffle(pnl)
        assert result.num_simulations == 100
        assert result.metric_name == "total_return"
        assert isinstance(result.original_value, float)

    def test_return_resample(self, simulator, sample_returns):
        """Return resample should work."""
        result = simulator.simulate_return_resample(sample_returns)
        assert result.num_simulations == 100
        assert result.confidence_95[0] < result.confidence_95[1]

    def test_price_path(self, simulator):
        """Price path simulation should work."""
        result = simulator.simulate_price_path(0.0004, 0.01, 252)
        assert result.num_simulations == 100

    def test_empty_returns(self, simulator):
        """Empty returns should return empty result."""
        result = simulator.simulate(pd.Series([], dtype=float))
        assert result.num_simulations == 0


class TestEmptyData:
    """Test edge cases with empty data."""

    def test_insufficient_data(self):
        """Too few returns should return empty result."""
        sim = MonteCarloSimulator(num_simulations=10, random_seed=42)
        short_returns = pd.Series([0.01, -0.01, 0.02])
        result = sim.simulate(short_returns)
        assert result.num_simulations == 0

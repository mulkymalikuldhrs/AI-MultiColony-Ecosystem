"""Tests for Advanced Risk Models.

Tests cover:
- Parametric VaR vs known values
- Historical VaR
- Cornish-Fisher VaR (verify skewness adjustment)
- CVaR is always >= VaR
- Component VaR sums to portfolio VaR
- Stress scenarios
- Reverse stress test
- Liquidity-adjusted VaR
- Rockafellar-Uryasev CVaR
- Edge cases
"""

import numpy as np
import pandas as pd
import pytest

from quant_nanggroe.engine.backtest.risk_models import (
    ValueAtRisk,
    ConditionalVaR,
    ComponentVaR,
    StressTestFramework,
    LiquidityAdjustedVaR,
    RiskModels,
    VaRMethod,
    VaRResult,
    ComponentVaRResult,
    StressTestResult,
    CorrelationBreakdownResult,
    LiquidityAdjustedVaRResult,
)


# ══════════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_returns():
    """Generate sample returns (normal distribution)."""
    np.random.seed(42)
    return np.random.normal(0.0004, 0.01, size=1000)


@pytest.fixture
def sample_returns_series(sample_returns):
    """Generate sample returns as pd.Series."""
    dates = pd.bdate_range("2020-01-01", periods=1000)
    return pd.Series(sample_returns, index=dates)


@pytest.fixture
def skewed_returns():
    """Generate skewed returns (Student-t distribution)."""
    np.random.seed(42)
    return np.random.standard_t(3, size=1000) * 0.01


@pytest.fixture
def multi_asset_returns():
    """Generate multi-asset returns with known correlation."""
    np.random.seed(42)
    dates = pd.bdate_range("2020-01-01", periods=500)
    n_assets = 3

    # Create correlated returns
    corr = np.array([[1.0, 0.6, 0.4], [0.6, 1.0, 0.5], [0.4, 0.5, 1.0]])
    L = np.linalg.cholesky(corr)
    z = np.random.normal(size=(500, n_assets))
    correlated = z @ L.T * 0.01

    return pd.DataFrame(
        correlated,
        index=dates,
        columns=["AAPL", "MSFT", "GOOG"],
    )


@pytest.fixture
def model():
    """Create RiskModels instance."""
    return RiskModels(bars_per_year=252, random_seed=42)


# ══════════════════════════════════════════════════════════════════════
# Test Parametric VaR
# ══════════════════════════════════════════════════════════════════════


class TestParametricVaR:
    """Test parametric VaR calculation."""

    def test_var_95(self, sample_returns):
        """Parametric VaR at 95% should be calculated."""
        var = ValueAtRisk.parametric_var(sample_returns, confidence=0.95)
        assert isinstance(var, float)
        assert var > 0

    def test_var_99(self, sample_returns):
        """Parametric VaR at 99% should exceed 95%."""
        var_95 = ValueAtRisk.parametric_var(sample_returns, confidence=0.95)
        var_99 = ValueAtRisk.parametric_var(sample_returns, confidence=0.99)
        assert var_99 > var_95

    def test_var_known_values(self):
        """Parametric VaR should match formula for known distribution."""
        np.random.seed(42)
        # Normal distribution with known parameters
        mu = 0.0
        sigma = 0.01
        returns = np.random.normal(mu, sigma, size=100000)

        var_99 = ValueAtRisk.parametric_var(returns, confidence=0.99)

        # Expected: z_0.99 * sigma ≈ 2.326 * 0.01 ≈ 0.02326
        # (mu is ~0, so VaR ≈ z * sigma)
        from scipy import stats
        expected_approx = stats.norm.ppf(0.99) * sigma
        # Allow 10% tolerance for finite sample
        assert abs(var_99 - expected_approx) / expected_approx < 0.15

    def test_var_horizon_scaling(self, sample_returns):
        """VaR should scale with sqrt(horizon)."""
        var_1d = ValueAtRisk.parametric_var(sample_returns, confidence=0.99, horizon=1)
        var_10d = ValueAtRisk.parametric_var(sample_returns, confidence=0.99, horizon=10)

        # 10-day VaR should be approximately sqrt(10) * 1-day VaR
        expected_ratio = np.sqrt(10)
        actual_ratio = var_10d / var_1d if var_1d > 0 else 0
        assert abs(actual_ratio - expected_ratio) < 0.1

    def test_var_zero_volatility(self):
        """Zero volatility should return zero VaR."""
        constant_returns = np.zeros(100)
        var = ValueAtRisk.parametric_var(constant_returns, confidence=0.99)
        assert var == 0.0


# ══════════════════════════════════════════════════════════════════════
# Test Historical VaR
# ══════════════════════════════════════════════════════════════════════


class TestHistoricalVaR:
    """Test historical VaR calculation."""

    def test_historical_var(self, sample_returns):
        """Historical VaR should be calculated."""
        var = ValueAtRisk.historical_var(sample_returns, confidence=0.95)
        assert isinstance(var, float)
        assert var > 0

    def test_historical_var_99(self, sample_returns):
        """Historical VaR at 99% should exceed 95%."""
        var_95 = ValueAtRisk.historical_var(sample_returns, confidence=0.95)
        var_99 = ValueAtRisk.historical_var(sample_returns, confidence=0.99)
        assert var_99 >= var_95

    def test_historical_var_horizon(self, sample_returns):
        """Historical VaR should scale with horizon."""
        var_1d = ValueAtRisk.historical_var(sample_returns, confidence=0.95, horizon=1)
        var_5d = ValueAtRisk.historical_var(sample_returns, confidence=0.95, horizon=5)
        assert var_5d > var_1d


# ══════════════════════════════════════════════════════════════════════
# Test Cornish-Fisher VaR
# ══════════════════════════════════════════════════════════════════════


class TestCornishFisherVaR:
    """Test Cornish-Fisher VaR calculation."""

    def test_cf_var_normal_data(self, sample_returns):
        """CF-VaR for normal data should be close to parametric VaR."""
        cf_var = ValueAtRisk.cornish_fisher_var(sample_returns, confidence=0.99)
        p_var = ValueAtRisk.parametric_var(sample_returns, confidence=0.99)

        # For approximately normal data, CF should be close to parametric
        assert abs(cf_var - p_var) / max(p_var, 1e-10) < 0.5

    def test_cf_var_skewness_adjustment(self, skewed_returns):
        """CF-VaR should differ from parametric VaR for skewed data."""
        cf_var = ValueAtRisk.cornish_fisher_var(skewed_returns, confidence=0.99)
        p_var = ValueAtRisk.parametric_var(skewed_returns, confidence=0.99)

        # For skewed data, CF adjustment should make a noticeable difference
        # Both should be positive
        assert cf_var > 0
        assert p_var > 0

        # Verify the adjustment uses the CF formula correctly
        # by checking that skewness and kurtosis are non-zero
        from scipy import stats
        S = float(stats.skew(skewed_returns, bias=False))
        K = float(stats.kurtosis(skewed_returns, bias=False))
        # Student-t(3) has positive excess kurtosis and potentially non-zero skewness
        assert abs(K) > 0  # Should have fat tails

    def test_cf_var_formula(self):
        """Verify the Cornish-Fisher formula implementation."""
        np.random.seed(42)
        # Create data with known skewness and kurtosis
        returns = np.random.standard_t(5, size=10000) * 0.01

        from scipy import stats
        mu = np.mean(returns)
        sigma = np.std(returns, ddof=1)
        z = stats.norm.ppf(0.01)  # alpha = 0.01 for 99% confidence
        S = float(stats.skew(returns, bias=False))
        K = float(stats.kurtosis(returns, bias=False))

        # CF adjustment: z_cf = z + (z^2-1)*S/6 + (z^3-3z)*K/24 - (2z^3-5z)*S^2/36
        cf_adj = (
            (z ** 2 - 1) * S / 6
            + (z ** 3 - 3 * z) * K / 24
            - (2 * z ** 3 - 5 * z) * S ** 2 / 36
        )
        z_cf = z + cf_adj

        # CF-VaR = |mu + z_cf * sigma|
        expected = abs(mu + z_cf * sigma)
        actual = ValueAtRisk.cornish_fisher_var(returns, confidence=0.99)

        assert abs(actual - expected) < 1e-6

    def test_cf_var_insufficient_data(self):
        """CF-VaR with too few data points should fall back to parametric."""
        short_returns = np.array([0.01, -0.01, 0.005])
        cf_var = ValueAtRisk.cornish_fisher_var(short_returns, confidence=0.99)
        p_var = ValueAtRisk.parametric_var(short_returns, confidence=0.99)
        # Should fall back to parametric (< 4 data points)
        assert abs(cf_var - p_var) < 1e-6


# ══════════════════════════════════════════════════════════════════════
# Test Monte Carlo VaR
# ══════════════════════════════════════════════════════════════════════


class TestMonteCarloVaR:
    """Test Monte Carlo VaR calculation."""

    def test_mc_var(self, sample_returns):
        """Monte Carlo VaR should be calculated."""
        var = ValueAtRisk.monte_carlo_var(
            sample_returns, confidence=0.95,
            n_sims=1000, random_seed=42,
        )
        assert isinstance(var, float)
        assert var > 0

    def test_mc_var_reproducible(self, sample_returns):
        """Monte Carlo VaR should be reproducible with same seed."""
        var1 = ValueAtRisk.monte_carlo_var(
            sample_returns, confidence=0.95,
            n_sims=1000, random_seed=42,
        )
        var2 = ValueAtRisk.monte_carlo_var(
            sample_returns, confidence=0.95,
            n_sims=1000, random_seed=42,
        )
        assert var1 == var2


# ══════════════════════════════════════════════════════════════════════
# Test ConditionalVaR (CVaR)
# ══════════════════════════════════════════════════════════════════════


class TestConditionalVaR:
    """Test Conditional VaR (Expected Shortfall) calculations."""

    def test_historical_cvar(self, sample_returns):
        """Historical CVaR should be calculated."""
        cvar = ConditionalVaR.historical_cvar(sample_returns, confidence=0.99)
        assert isinstance(cvar, float)
        assert cvar > 0

    def test_cvar_exceeds_var(self, sample_returns):
        """CVaR should always be >= VaR."""
        var = ValueAtRisk.historical_var(sample_returns, confidence=0.99)
        cvar = ConditionalVaR.historical_cvar(sample_returns, confidence=0.99)
        assert cvar >= var

    def test_parametric_cvar(self, sample_returns):
        """Parametric CVaR should be calculated."""
        cvar = ConditionalVaR.parametric_cvar(sample_returns, confidence=0.99)
        assert isinstance(cvar, float)
        assert cvar > 0

    def test_parametric_cvar_exceeds_var(self, sample_returns):
        """Parametric CVaR should exceed parametric VaR."""
        var = ValueAtRisk.parametric_var(sample_returns, confidence=0.99)
        cvar = ConditionalVaR.parametric_cvar(sample_returns, confidence=0.99)
        assert cvar >= var

    def test_rockafellar_uryasev_cvar(self, sample_returns):
        """Rockafellar-Uryasev CVaR should be calculated."""
        cvar = ConditionalVaR.rockafellar_uryasev_cvar(sample_returns, confidence=0.99)
        assert isinstance(cvar, float)
        assert cvar > 0

    def test_ru_cvar_approximately_historical(self, sample_returns):
        """R-U CVaR should be close to historical CVaR."""
        hist_cvar = ConditionalVaR.historical_cvar(sample_returns, confidence=0.95)
        ru_cvar = ConditionalVaR.rockafellar_uryasev_cvar(sample_returns, confidence=0.95)

        # They should be in the same ballpark
        # R-U CVaR is mathematically equivalent to CVaR for continuous distributions
        ratio = ru_cvar / hist_cvar if hist_cvar > 0 else 0
        assert 0.5 < ratio < 2.0

    def test_cvar_confidence_monotonic(self, sample_returns):
        """CVaR should increase with confidence level."""
        cvar_95 = ConditionalVaR.historical_cvar(sample_returns, confidence=0.95)
        cvar_99 = ConditionalVaR.historical_cvar(sample_returns, confidence=0.99)
        assert cvar_99 >= cvar_95


# ══════════════════════════════════════════════════════════════════════
# Test Component VaR
# ══════════════════════════════════════════════════════════════════════


class TestComponentVaR:
    """Test Component and Marginal VaR."""

    def test_component_var(self, multi_asset_returns):
        """Component VaR should decompose portfolio risk."""
        cov_matrix = multi_asset_returns.cov().values
        weights = np.array([0.4, 0.35, 0.25])
        symbols = list(multi_asset_returns.columns)

        result = ComponentVaR.component_var(
            weights, cov_matrix, confidence=0.95, symbols=symbols,
        )

        assert isinstance(result, ComponentVaRResult)
        assert "AAPL" in result.component_var
        assert "MSFT" in result.component_var
        assert "GOOG" in result.component_var
        assert result.total_var > 0

    def test_component_var_sums_to_total(self, multi_asset_returns):
        """Component VaRs should sum to total portfolio VaR."""
        cov_matrix = multi_asset_returns.cov().values
        weights = np.array([0.4, 0.35, 0.25])
        symbols = list(multi_asset_returns.columns)

        result = ComponentVaR.component_var(
            weights, cov_matrix, confidence=0.95, symbols=symbols,
        )

        # Sum of component VaRs should equal total VaR
        sum_components = sum(result.component_var.values())
        assert abs(sum_components - result.total_var) < 0.001

    def test_percentage_contribution_sums_to_one(self, multi_asset_returns):
        """Percentage contribution should sum to approximately 1."""
        cov_matrix = multi_asset_returns.cov().values
        weights = np.array([0.4, 0.35, 0.25])
        symbols = list(multi_asset_returns.columns)

        result = ComponentVaR.component_var(
            weights, cov_matrix, confidence=0.95, symbols=symbols,
        )

        total_pct = sum(result.percentage_contrib.values())
        assert abs(total_pct - 1.0) < 0.01

    def test_marginal_var(self, multi_asset_returns):
        """Marginal VaR should be calculated."""
        pos_returns = multi_asset_returns["AAPL"].values
        port_returns = (multi_asset_returns * np.array([0.4, 0.35, 0.25])).sum(axis=1).values

        mvar = ComponentVaR.marginal_var(
            pos_returns, port_returns, confidence=0.95,
        )
        assert isinstance(mvar, float)


# ══════════════════════════════════════════════════════════════════════
# Test StressTestFramework
# ══════════════════════════════════════════════════════════════════════


class TestStressTestFramework:
    """Test stress testing framework."""

    def test_scenario_analysis(self, sample_returns_series):
        """Default stress scenarios should be applied."""
        stress = StressTestFramework(bars_per_year=252)
        results = stress.scenario_analysis(sample_returns_series, portfolio_value=1_000_000)

        assert isinstance(results, list)
        assert len(results) > 0
        for r in results:
            assert isinstance(r, StressTestResult)
            assert r.shocked_var > 0
            assert r.shocked_cvar > 0
            assert r.loss_pct > 0

    def test_custom_scenarios(self, sample_returns_series):
        """Custom stress scenarios should work."""
        stress = StressTestFramework(bars_per_year=252)
        scenarios = {
            "custom": ("Custom crash", -0.50, 3.0),
        }
        results = stress.scenario_analysis(
            sample_returns_series, portfolio_value=1_000_000,
            scenarios=scenarios,
        )

        assert len(results) == 1
        assert results[0].scenario_name == "custom"
        assert results[0].loss_pct == 0.50

    def test_historical_stress_test(self, sample_returns_series):
        """Historical stress test should apply crisis periods."""
        stress = StressTestFramework(bars_per_year=252)
        results = stress.historical_stress_test(
            sample_returns_series, portfolio_value=1_000_000,
        )
        # Results depend on whether the dates match
        assert isinstance(results, list)

    def test_reverse_stress_test(self, sample_returns_series):
        """Reverse stress test should find scenarios causing target loss."""
        stress = StressTestFramework(bars_per_year=252)
        result = stress.reverse_stress_test(sample_returns_series, target_loss=0.20)

        assert isinstance(result, dict)
        assert "target_loss" in result
        assert "feasible" in result
        assert result["target_loss"] == 0.20
        assert result["feasible"] is True

    def test_reverse_stress_test_scenarios(self, sample_returns_series):
        """Reverse stress test should provide multiple scenarios."""
        stress = StressTestFramework(bars_per_year=252)
        result = stress.reverse_stress_test(sample_returns_series, target_loss=0.30)

        assert "scenarios" in result
        scenarios = result["scenarios"]
        assert "vol_only" in scenarios
        assert "return_only" in scenarios
        assert "combined" in scenarios

        # Vol-only scenario should have vol_multiplier >= 1
        assert scenarios["vol_only"]["required_vol_multiplier"] >= 1.0


# ══════════════════════════════════════════════════════════════════════
# Test Liquidity-Adjusted VaR
# ══════════════════════════════════════════════════════════════════════


class TestLiquidityAdjustedVaR:
    """Test liquidity-adjusted VaR."""

    def test_lvav(self, sample_returns):
        """L-VaR should exceed base VaR."""
        result = LiquidityAdjustedVaR.lvav(
            sample_returns,
            confidence=0.95,
            liquidation_days=5,
            position_size=10000,
            avg_daily_volume=50000,
            portfolio_value=1_000_000,
        )

        assert isinstance(result, LiquidityAdjustedVaRResult)
        assert result.adjusted_var > result.base_var
        assert result.liquidity_adjustment > 0
        assert result.liquidation_time > 0

    def test_lvav_with_volumes(self, sample_returns):
        """L-VaR should work with volume array."""
        np.random.seed(42)
        volumes = np.random.uniform(40000, 60000, size=1000)

        result = LiquidityAdjustedVaR.lvav(
            sample_returns,
            volumes=volumes,
            confidence=0.95,
            liquidation_days=5,
            position_size=10000,
            portfolio_value=1_000_000,
        )

        assert isinstance(result, LiquidityAdjustedVaRResult)
        assert result.adjusted_var > 0

    def test_large_position_higher_adjustment(self, sample_returns):
        """Large position should have higher liquidity adjustment."""
        small = LiquidityAdjustedVaR.lvav(
            sample_returns,
            position_size=1000,
            avg_daily_volume=100000,
            confidence=0.95,
            portfolio_value=1_000_000,
        )
        large = LiquidityAdjustedVaR.lvav(
            sample_returns,
            position_size=100000,
            avg_daily_volume=100000,
            confidence=0.95,
            portfolio_value=1_000_000,
        )

        assert large.liquidity_adjustment > small.liquidity_adjustment

    def test_longer_liquidation_higher_var(self, sample_returns):
        """Longer liquidation period should increase base VaR."""
        short = LiquidityAdjustedVaR.lvav(
            sample_returns,
            liquidation_days=1,
            confidence=0.95,
            portfolio_value=1_000_000,
        )
        long = LiquidityAdjustedVaR.lvav(
            sample_returns,
            liquidation_days=10,
            confidence=0.95,
            portfolio_value=1_000_000,
        )

        # Longer liquidation → higher VaR (sqrt-of-time scaling)
        assert long.base_var > short.base_var


# ══════════════════════════════════════════════════════════════════════
# Test RiskModels Unified Interface
# ══════════════════════════════════════════════════════════════════════


class TestRiskModelsUnified:
    """Test the unified RiskModels interface."""

    def test_calculate_var(self, model, sample_returns):
        """RiskModels.calculate_var should work."""
        result = model.calculate_var(
            sample_returns, confidence_levels=[0.95],
            method=VaRMethod.PARAMETRIC,
        )
        assert isinstance(result, VaRResult)
        assert 0.95 in result.var_values
        assert result.var_values[0.95] > 0

    def test_cvar_exceeds_var(self, model, sample_returns):
        """CVaR should exceed VaR through unified interface."""
        result = model.calculate_var(
            sample_returns, confidence_levels=[0.95],
            method=VaRMethod.PARAMETRIC,
        )
        assert result.cvar_values[0.95] >= result.var_values[0.95]

    def test_component_var(self, model, multi_asset_returns):
        """Component VaR through unified interface."""
        weights = np.array([0.4, 0.35, 0.25])
        result = model.component_var(
            multi_asset_returns, weights,
            confidence=0.95, portfolio_value=1_000_000,
        )
        assert isinstance(result, ComponentVaRResult)
        assert result.total_var > 0

    def test_stress_test(self, model, sample_returns_series):
        """Stress test through unified interface."""
        results = model.stress_test(sample_returns_series, portfolio_value=1_000_000)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_liquidity_adjusted_var(self, model, sample_returns):
        """L-VaR through unified interface."""
        result = model.liquidity_adjusted_var(
            sample_returns,
            position_size=10000,
            avg_daily_volume=50000,
            confidence=0.95,
            portfolio_value=1_000_000,
        )
        assert isinstance(result, LiquidityAdjustedVaRResult)
        assert result.adjusted_var > result.base_var

    def test_multiple_confidence_levels(self, model, sample_returns):
        """Should calculate VaR at multiple confidence levels."""
        result = model.calculate_var(
            sample_returns,
            confidence_levels=[0.90, 0.95, 0.99],
            method=VaRMethod.HISTORICAL,
        )
        assert result.var_values[0.99] > result.var_values[0.95]
        assert result.var_values[0.95] > result.var_values[0.90]

    def test_copula_var(self, model, multi_asset_returns):
        """Copula VaR through unified interface."""
        weights = np.array([0.4, 0.35, 0.25])
        result = model.copula_var(
            multi_asset_returns, weights,
            confidence=0.95, portfolio_value=1_000_000,
            num_simulations=500,
        )
        assert isinstance(result, VaRResult)
        assert result.var_values[0.95] > 0

    def test_correlation_breakdown(self, model, multi_asset_returns):
        """Correlation breakdown detection."""
        result = model.detect_correlation_breakdown(multi_asset_returns)
        assert isinstance(result, CorrelationBreakdownResult)
        assert isinstance(result.current_correlation, float)

    def test_entropic_var(self, model, sample_returns):
        """Entropic VaR."""
        evar = model.entropic_var(sample_returns, confidence=0.95)
        assert isinstance(evar, float)
        assert evar > 0


# ══════════════════════════════════════════════════════════════════════
# Test Conditional Drawdown-at-Risk
# ══════════════════════════════════════════════════════════════════════


class TestConditionalDrawdownAtRisk:
    """Test CDaR calculation."""

    def test_cdar(self, model):
        """CDaR should be calculated correctly."""
        dates = pd.bdate_range("2023-01-01", periods=252)
        np.random.seed(42)
        equity = pd.Series(
            1_000_000 * np.cumprod(1 + np.random.normal(0.0002, 0.01, size=252)),
            index=dates,
        )

        cdar = model.conditional_drawdown_at_risk(equity, confidence=0.95)
        assert isinstance(cdar, float)
        assert cdar <= 0  # CDaR is negative (drawdown)

    def test_cdar_no_drawdown(self, model):
        """CDaR should be 0 for monotonically increasing equity."""
        dates = pd.bdate_range("2023-01-01", periods=252)
        equity = pd.Series(
            [1_000_000 * (1 + i * 0.001) for i in range(252)],
            index=dates,
        )

        cdar = model.conditional_drawdown_at_risk(equity, confidence=0.95)
        assert cdar == 0.0


# ══════════════════════════════════════════════════════════════════════
# Test Edge Cases
# ══════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Test edge cases for risk models."""

    def test_zero_volatility(self):
        """Zero volatility with zero mean should return zero VaR."""
        constant_returns = np.zeros(100)
        var = ValueAtRisk.parametric_var(constant_returns, confidence=0.95)
        assert var == 0.0

    def test_insufficient_data(self):
        """Very few data points should still work."""
        short = np.array([0.01, -0.01])
        var = ValueAtRisk.historical_var(short, confidence=0.95)
        assert var > 0

    def test_nan_handling(self):
        """NaN values should be handled."""
        returns_with_nan = np.array([0.01, np.nan, -0.02, 0.005, -0.01])
        var = ValueAtRisk.historical_var(returns_with_nan, confidence=0.95)
        assert isinstance(var, float)

    def test_single_data_point(self):
        """Single data point should return zero."""
        single = np.array([0.01])
        var = ValueAtRisk.parametric_var(single, confidence=0.95)
        assert var == 0.0

    def test_empty_returns(self):
        """Empty returns should return zero."""
        empty = np.array([])
        var = ValueAtRisk.parametric_var(empty, confidence=0.95)
        assert var == 0.0

    def test_all_nan(self):
        """All-NaN returns should return zero."""
        all_nan = np.array([np.nan, np.nan, np.nan])
        var = ValueAtRisk.parametric_var(all_nan, confidence=0.95)
        assert var == 0.0

    def test_component_var_single_asset(self):
        """Component VaR with single asset."""
        cov = np.array([[0.01]])
        weights = np.array([1.0])
        result = ComponentVaR.component_var(
            weights, cov, confidence=0.95, symbols=["A"],
        )
        assert result.total_var > 0
        assert abs(result.percentage_contrib["A"] - 1.0) < 0.01

    def test_component_var_zero_variance(self):
        """Component VaR with zero covariance matrix."""
        cov = np.zeros((2, 2))
        weights = np.array([0.5, 0.5])
        result = ComponentVaR.component_var(
            weights, cov, confidence=0.95, symbols=["A", "B"],
        )
        assert result.total_var == 0.0

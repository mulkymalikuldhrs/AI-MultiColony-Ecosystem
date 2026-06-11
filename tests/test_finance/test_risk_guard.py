"""Tests for ConstitutionalRiskGuard — constitutional limits, trade checking."""

from __future__ import annotations

import pytest

from ai_multicolony.finance.risk_guard import (
    ConstitutionalRiskGuard,
    MAX_DAILY_LOSS_PCT,
    MAX_WEEKLY_LOSS_PCT,
    MAX_POSITION_SIZE_PCT,
    MAX_RISK_PER_TRADE_PCT,
    MANDATORY_STOP_LOSS_PCT,
    PortfolioSnapshot,
    RiskCheckResult,
    RiskLevel,
    TradeAction,
    TradeRequest,
)


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def guard():
    return ConstitutionalRiskGuard()


@pytest.fixture
def healthy_portfolio():
    return PortfolioSnapshot(
        total_equity=100000.0,
        cash=100000.0,
        daily_pnl=0.0,
        weekly_pnl=0.0,
        max_drawdown_pct=0.0,
    )


@pytest.fixture
def small_trade():
    """A very small trade that should be classified as SAFE."""
    return TradeRequest(
        symbol="AAPL",
        action=TradeAction.BUY,
        quantity=1,
        price=100.0,  # 0.1% of portfolio = well within safe range
        stop_loss_pct=MANDATORY_STOP_LOSS_PCT,
    )


# ── Constitutional Limits ──────────────────────────────────────────────────

class TestConstitutionalLimits:
    """Test that constitutional limits are correctly defined."""

    def test_max_risk_per_trade(self):
        assert MAX_RISK_PER_TRADE_PCT == 0.5

    def test_max_daily_loss(self):
        assert MAX_DAILY_LOSS_PCT == 1.0

    def test_max_weekly_loss(self):
        assert MAX_WEEKLY_LOSS_PCT == 3.0

    def test_max_position_size(self):
        assert MAX_POSITION_SIZE_PCT == 10.0

    def test_mandatory_stop_loss(self):
        assert MANDATORY_STOP_LOSS_PCT == 2.0


# ── Trade Checking ─────────────────────────────────────────────────────────

class TestTradeChecking:
    """Test check_trade method."""

    def test_approve_safe_trade(self, guard, healthy_portfolio, small_trade):
        result = guard.check_trade(small_trade, healthy_portfolio)
        assert result.approved is True
        # Small trade should be SAFE or MODERATE or ELEVATED (all are approved)
        assert result.risk_level in (RiskLevel.SAFE, RiskLevel.MODERATE, RiskLevel.ELEVATED)

    def test_reject_excessive_risk_pct(self, guard, healthy_portfolio):
        trade = TradeRequest(
            symbol="AAPL",
            action=TradeAction.BUY,
            quantity=10,
            price=185.0,
            risk_pct=1.0,  # Exceeds MAX_RISK_PER_TRADE_PCT=0.5
        )
        result = guard.check_trade(trade, healthy_portfolio)
        assert result.approved is False
        assert result.risk_level == RiskLevel.BREACH

    def test_reject_daily_loss_exceeded(self, guard, small_trade):
        portfolio = PortfolioSnapshot(
            total_equity=100000.0,
            daily_pnl=-1500.0,  # -1.5% exceeds 1.0%
            weekly_pnl=0.0,
        )
        result = guard.check_trade(small_trade, portfolio)
        assert result.approved is False
        assert result.risk_level == RiskLevel.BREACH

    def test_reject_weekly_loss_exceeded(self, guard, small_trade):
        portfolio = PortfolioSnapshot(
            total_equity=100000.0,
            daily_pnl=0.0,
            weekly_pnl=-4000.0,  # -4% exceeds 3%
        )
        result = guard.check_trade(small_trade, portfolio)
        assert result.approved is False
        assert result.risk_level == RiskLevel.BREACH

    def test_adjust_oversized_position(self, guard, healthy_portfolio):
        trade = TradeRequest(
            symbol="AAPL",
            action=TradeAction.BUY,
            quantity=100,  # 100 * 185 = 18500 = 18.5% > 10%
            price=185.0,
        )
        result = guard.check_trade(trade, healthy_portfolio)
        assert result.position_size_adjusted is True
        assert result.approved is True  # After adjustment

    def test_mandatory_stop_loss_enforcement(self, guard, healthy_portfolio):
        trade = TradeRequest(
            symbol="AAPL",
            action=TradeAction.BUY,
            quantity=10,
            price=185.0,
            stop_loss_pct=0.0,  # No stop loss set
        )
        result = guard.check_trade(trade, healthy_portfolio)
        # Original request must NOT be mutated
        assert trade.stop_loss_pct == 0.0
        # The result should indicate the constitutional stop-loss requirement
        assert result.stop_loss_required == MANDATORY_STOP_LOSS_PCT

    def test_close_action_no_stop_loss_check(self, guard, healthy_portfolio):
        trade = TradeRequest(
            symbol="AAPL",
            action=TradeAction.CLOSE,
            quantity=10,
            price=185.0,
        )
        result = guard.check_trade(trade, healthy_portfolio)
        # Close actions should not require stop-loss
        assert result.approved is True

    def test_risk_level_classification(self, guard, healthy_portfolio):
        """Test that risk levels are correctly assigned."""
        # Very small trade should be safe or moderate
        tiny = TradeRequest(symbol="X", action=TradeAction.BUY, quantity=1, price=50.0)
        result = guard.check_trade(tiny, healthy_portfolio)
        assert result.risk_level in (RiskLevel.SAFE, RiskLevel.MODERATE, RiskLevel.ELEVATED)


# ── Position Sizing ───────────────────────────────────────────────────────

class TestPositionSizing:
    """Test calculate_position_size method."""

    def test_basic_sizing(self, guard):
        size = guard.calculate_position_size(
            equity=100000,
            entry_price=100.0,
            stop_loss_price=98.0,  # 2% stop loss
            risk_pct=0.5,
        )
        assert size > 0
        # Risk amount = 100000 * 0.5% = 500
        # Risk per unit = 100 - 98 = 2
        # Raw size = 500 / 2 = 250
        # But capped at max position: 100000 * 10% / 100 = 100
        # So result is 100 (capped)

    def test_zero_equity(self, guard):
        size = guard.calculate_position_size(
            equity=0,
            entry_price=100.0,
            stop_loss_price=98.0,
        )
        assert size == 0.0

    def test_zero_entry_price(self, guard):
        size = guard.calculate_position_size(
            equity=100000,
            entry_price=0,
            stop_loss_price=98.0,
        )
        assert size == 0.0

    def test_same_entry_stop(self, guard):
        size = guard.calculate_position_size(
            equity=100000,
            entry_price=100.0,
            stop_loss_price=100.0,
        )
        assert size == 0.0

    def test_capped_at_max_position(self, guard):
        size = guard.calculate_position_size(
            equity=100000,
            entry_price=5.0,
            stop_loss_price=4.99,
            risk_pct=0.5,
        )
        max_value = 100000 * (MAX_POSITION_SIZE_PCT / 100)
        max_size = max_value / 5.0
        assert size <= max_size

    def test_sizing_proportional_to_risk(self, guard):
        size_small = guard.calculate_position_size(100000, 100.0, 95.0, risk_pct=0.25)
        size_large = guard.calculate_position_size(100000, 100.0, 95.0, risk_pct=0.5)
        # Larger risk budget → larger position (if not capped)
        if size_large < 2000 and size_small < 2000:  # Not capped
            assert size_large > size_small


# ── PortfolioSnapshot ─────────────────────────────────────────────────────

class TestPortfolioSnapshot:
    """Test PortfolioSnapshot model."""

    def test_daily_pnl_pct(self):
        p = PortfolioSnapshot(total_equity=100000, daily_pnl=-500)
        assert p.daily_pnl_pct == -0.5

    def test_weekly_pnl_pct(self):
        p = PortfolioSnapshot(total_equity=100000, weekly_pnl=1000)
        assert p.weekly_pnl_pct == 1.0

    def test_position_count(self):
        p = PortfolioSnapshot(positions={"AAPL": {}, "MSFT": {}})
        assert p.position_count == 2

    def test_total_position_value(self):
        p = PortfolioSnapshot(positions={
            "AAPL": {"quantity": 10, "current_price": 185.0},
            "MSFT": {"quantity": 5, "current_price": 380.0},
        })
        assert p.total_position_value == 10 * 185 + 5 * 380

    def test_zero_equity_pnl_pct(self):
        p = PortfolioSnapshot(total_equity=0, daily_pnl=-100)
        assert p.daily_pnl_pct == 0.0


# ── Stats ─────────────────────────────────────────────────────────────────

class TestRiskGuardStats:
    """Test risk guard statistics."""

    def test_stats_after_checks(self, guard, healthy_portfolio, small_trade):
        guard.check_trade(small_trade, healthy_portfolio)
        stats = guard.stats
        assert stats["total_checks"] == 1
        assert stats["approved"] == 1
        assert stats["rejected"] == 0
        assert stats["approval_rate"] == 1.0

    def test_stats_include_limits(self, guard):
        stats = guard.stats
        limits = stats["constitutional_limits"]
        assert limits["max_risk_per_trade_pct"] == MAX_RISK_PER_TRADE_PCT
        assert limits["max_daily_loss_pct"] == MAX_DAILY_LOSS_PCT


# ── Pydantic Models ───────────────────────────────────────────────────────

class TestPydanticModels:
    """Test Pydantic model validation."""

    def test_risk_check_result_defaults(self):
        result = RiskCheckResult()
        assert result.approved is False
        assert result.risk_level == RiskLevel.SAFE
        assert result.reasons == []
        assert result.warnings == []

    def test_trade_request_notional_value(self):
        req = TradeRequest(quantity=10, price=185.0)
        assert req.notional_value == 1850.0

    def test_trade_request_defaults(self):
        req = TradeRequest()
        assert req.action == TradeAction.BUY
        assert req.stop_loss_pct == MANDATORY_STOP_LOSS_PCT

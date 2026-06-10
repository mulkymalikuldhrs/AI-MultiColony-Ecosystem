"""
Tests for Constitutional Risk Guard — 9-Checkpoint VETO System
================================================================
"""

from __future__ import annotations

import pytest
from datetime import datetime

from quant_nanggroe_ai.engine.risk_guard import RiskGuard, RiskDecision


class TestRiskGuardCheckpoints:
    """Test each of the 9 constitutional checkpoints."""

    @pytest.fixture
    def guard(self) -> RiskGuard:
        return RiskGuard(
            max_trade_pct=0.005,     # 0.5% per trade
            max_daily_pct=0.01,      # 1% per day
            max_weekly_pct=0.03,     # 3% per week
            max_position_pct=0.20,   # 20% per position
            max_correlation=0.70,    # 70% max correlation
            max_drawdown_pct=0.15,   # 15% max drawdown
            max_leverage=1.0,        # No leverage
            max_open_positions=10,
            min_cash_reserve_pct=0.10,  # 10% cash reserve
        )

    def test_trade_within_limits_approved(self, guard: RiskGuard) -> None:
        """Small trade within all limits should be APPROVED."""
        result = guard.evaluate(
            symbol="AAPL",
            side="BUY",
            quantity=1,
            price=150.0,
            portfolio_equity=100000.0,
            current_daily_loss=0.0,
            current_weekly_loss=0.0,
            current_drawdown_pct=0.0,
            position_count=1,
            cash_available=50000.0,
            existing_positions={},
        )
        assert result.decision == RiskDecision.APPROVED

    def test_trade_exceeds_max_per_trade_veto(self, guard: RiskGuard) -> None:
        """Trade > 0.5% of equity should be VETO'd."""
        result = guard.evaluate(
            symbol="AAPL",
            side="BUY",
            quantity=10,
            price=150.0,  # $1500 = 1.5% of $100K
            portfolio_equity=100000.0,
            current_daily_loss=0.0,
            current_weekly_loss=0.0,
            current_drawdown_pct=0.0,
            position_count=1,
            cash_available=50000.0,
            existing_positions={},
        )
        assert result.decision == RiskDecision.VETO
        assert "trade_size" in result.reason.lower() or "0.5%" in result.reason

    def test_daily_limit_exceeded_veto(self, guard: RiskGuard) -> None:
        """Trade when daily loss > 1% should be VETO'd."""
        result = guard.evaluate(
            symbol="AAPL",
            side="BUY",
            quantity=1,
            price=150.0,
            portfolio_equity=100000.0,
            current_daily_loss=1200.0,  # 1.2% daily loss > 1% limit
            current_weekly_loss=0.0,
            current_drawdown_pct=0.0,
            position_count=1,
            cash_available=50000.0,
            existing_positions={},
        )
        assert result.decision == RiskDecision.VETO
        assert "daily" in result.reason.lower()

    def test_weekly_limit_exceeded_veto(self, guard: RiskGuard) -> None:
        """Trade when weekly loss > 3% should be VETO'd."""
        result = guard.evaluate(
            symbol="AAPL",
            side="BUY",
            quantity=1,
            price=150.0,
            portfolio_equity=100000.0,
            current_daily_loss=0.0,
            current_weekly_loss=3500.0,  # 3.5% weekly loss > 3% limit
            current_drawdown_pct=0.0,
            position_count=1,
            cash_available=50000.0,
            existing_positions={},
        )
        assert result.decision == RiskDecision.VETO
        assert "weekly" in result.reason.lower()

    def test_drawdown_exceeded_veto(self, guard: RiskGuard) -> None:
        """Trade when drawdown > 15% should be VETO'd."""
        result = guard.evaluate(
            symbol="AAPL",
            side="BUY",
            quantity=1,
            price=150.0,
            portfolio_equity=100000.0,
            current_daily_loss=0.0,
            current_weekly_loss=0.0,
            current_drawdown_pct=16.0,  # 16% > 15% limit
            position_count=1,
            cash_available=50000.0,
            existing_positions={},
        )
        assert result.decision == RiskDecision.VETO
        assert "drawdown" in result.reason.lower()

    def test_max_positions_exceeded_veto(self, guard: RiskGuard) -> None:
        """Trade when already at max positions should be VETO'd."""
        existing = {f"STOCK{i}": 5000.0 for i in range(10)}
        result = guard.evaluate(
            symbol="AAPL",
            side="BUY",
            quantity=1,
            price=150.0,
            portfolio_equity=100000.0,
            current_daily_loss=0.0,
            current_weekly_loss=0.0,
            current_drawdown_pct=0.0,
            position_count=10,
            cash_available=50000.0,
            existing_positions=existing,
        )
        assert result.decision == RiskDecision.VETO
        assert "position" in result.reason.lower()

    def test_cash_reserve_insufficient_veto(self, guard: RiskGuard) -> None:
        """Trade when it would leave < 10% cash should be VETO'd."""
        result = guard.evaluate(
            symbol="AAPL",
            side="BUY",
            quantity=1,
            price=150.0,
            portfolio_equity=100000.0,
            current_daily_loss=0.0,
            current_weekly_loss=0.0,
            current_drawdown_pct=0.0,
            position_count=1,
            cash_available=8000.0,  # 8% of equity < 10% reserve
            existing_positions={},
        )
        assert result.decision == RiskDecision.VETO
        assert "cash" in result.reason.lower()

    def test_audit_trail_present(self, guard: RiskGuard) -> None:
        """Every evaluation must produce an audit trail."""
        result = guard.evaluate(
            symbol="AAPL",
            side="BUY",
            quantity=1,
            price=150.0,
            portfolio_equity=100000.0,
            current_daily_loss=0.0,
            current_weekly_loss=0.0,
            current_drawdown_pct=0.0,
            position_count=1,
            cash_available=50000.0,
            existing_positions={},
        )
        assert result.audit_id is not None
        assert result.timestamp is not None
        assert len(result.checkpoints) > 0

"""
Tests for Hierarchical Approval Chain
=======================================
Covers: normal operation, edge cases, boundary values, error handling,
determinism verification, and mode-specific behavior.
"""

from __future__ import annotations

import asyncio
import pytest
from datetime import datetime

from quant_nanggroe.engine.risk.approval import (
    ApprovalChain,
    ApprovalDecision,
    ApprovalMode,
    ApprovalRecord,
    ApprovalTier,
    RISK_MANAGER,
    PORTFOLIO_MANAGER,
    SENIOR_TRADER,
    SMALL_THRESHOLD,
    MEDIUM_THRESHOLD,
)


# ─── Helpers ────────────────────────────────────────────────────────────

def run_async(coro):
    """Run an async function synchronously for testing."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        # If there's already a running loop, create a new one in a thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    return asyncio.run(coro)


def make_trade_request(**overrides) -> dict:
    """Build a standard trade request dict with sensible defaults."""
    base = {
        "trade_id": "test-001",
        "symbol": "AAPL",
        "side": "buy",
        "position_pct": 0.003,
        "portfolio_value": 100000.0,
        "reason": "Test trade",
        "strategy": "momentum",
        "confidence": 0.8,
    }
    base.update(overrides)
    return base


# ─── Tier Classification ───────────────────────────────────────────────


class TestClassifyTier:
    """Test tier classification logic."""

    def test_small_tier_below_threshold(self):
        """Position < 0.5% should classify as SMALL."""
        chain = ApprovalChain()
        assert chain.classify_tier(0.001) == ApprovalTier.SMALL
        assert chain.classify_tier(0.004) == ApprovalTier.SMALL
        assert chain.classify_tier(0.00499) == ApprovalTier.SMALL

    def test_medium_tier_range(self):
        """Position 0.5%–2% should classify as MEDIUM."""
        chain = ApprovalChain()
        assert chain.classify_tier(0.005) == ApprovalTier.MEDIUM
        assert chain.classify_tier(0.01) == ApprovalTier.MEDIUM
        assert chain.classify_tier(0.01999) == ApprovalTier.MEDIUM

    def test_large_tier_above_threshold(self):
        """Position > 2% should classify as LARGE."""
        chain = ApprovalChain()
        assert chain.classify_tier(0.02) == ApprovalTier.LARGE
        assert chain.classify_tier(0.05) == ApprovalTier.LARGE
        assert chain.classify_tier(0.10) == ApprovalTier.LARGE

    def test_boundary_at_small_threshold(self):
        """Exactly at 0.5% should be MEDIUM, not SMALL."""
        chain = ApprovalChain()
        assert chain.classify_tier(SMALL_THRESHOLD) == ApprovalTier.MEDIUM

    def test_boundary_at_medium_threshold(self):
        """Exactly at 2% should be LARGE, not MEDIUM."""
        chain = ApprovalChain()
        assert chain.classify_tier(MEDIUM_THRESHOLD) == ApprovalTier.LARGE

    def test_zero_position_pct(self):
        """0% position should be SMALL."""
        chain = ApprovalChain()
        assert chain.classify_tier(0.0) == ApprovalTier.SMALL

    def test_negative_position_pct_raises(self):
        """Negative position_pct should raise ValueError."""
        chain = ApprovalChain()
        with pytest.raises(ValueError, match="non-negative"):
            chain.classify_tier(-0.01)

    def test_custom_thresholds(self):
        """Custom thresholds should override defaults."""
        chain = ApprovalChain(config={"small_threshold": 0.01, "medium_threshold": 0.05})
        assert chain.classify_tier(0.005) == ApprovalTier.SMALL
        assert chain.classify_tier(0.02) == ApprovalTier.MEDIUM
        assert chain.classify_tier(0.06) == ApprovalTier.LARGE


# ─── Approval Decisions ────────────────────────────────────────────────


class TestApprovalDecisions:
    """Test approval/rejection logic in various modes."""

    def test_backtest_mode_auto_approves_small(self):
        """Backtest mode should auto-approve SMALL trades."""
        chain = ApprovalChain(config={"mode": "backtest"})
        record = run_async(chain.evaluate(make_trade_request(position_pct=0.003)))
        assert record.final_decision == ApprovalDecision.APPROVED
        assert record.mode == ApprovalMode.BACKTEST

    def test_backtest_mode_auto_approves_large(self):
        """Backtest mode should auto-approve even LARGE trades."""
        chain = ApprovalChain(config={"mode": "backtest"})
        record = run_async(chain.evaluate(make_trade_request(position_pct=0.05)))
        assert record.final_decision == ApprovalDecision.APPROVED

    def test_live_mode_auto_approves_small(self):
        """Live mode should auto-approve SMALL trades."""
        chain = ApprovalChain(config={"mode": "live"})
        record = run_async(chain.evaluate(make_trade_request(position_pct=0.003)))
        assert record.final_decision == ApprovalDecision.APPROVED
        assert record.tier == ApprovalTier.SMALL

    def test_live_mode_medium_approved(self):
        """Live mode MEDIUM trade with good params should be approved."""
        chain = ApprovalChain(config={"mode": "live"})
        record = run_async(chain.evaluate(make_trade_request(
            position_pct=0.01, confidence=0.8, current_drawdown=0.02
        )))
        assert record.final_decision == ApprovalDecision.APPROVED
        assert record.tier == ApprovalTier.MEDIUM

    def test_live_mode_medium_rejected_drawdown(self):
        """Live mode MEDIUM trade with high drawdown should be rejected."""
        chain = ApprovalChain(config={"mode": "live"})
        record = run_async(chain.evaluate(make_trade_request(
            position_pct=0.01, confidence=0.8, current_drawdown=0.20
        )))
        assert record.final_decision == ApprovalDecision.REJECTED

    def test_live_mode_large_approved(self):
        """Live mode LARGE trade with good params should be approved."""
        chain = ApprovalChain(config={"mode": "live"})
        record = run_async(chain.evaluate(make_trade_request(
            position_pct=0.03, confidence=0.8, current_drawdown=0.02,
            correlated_positions=1, strategy_win_rate=0.6,
        )))
        assert record.final_decision == ApprovalDecision.APPROVED
        assert record.tier == ApprovalTier.LARGE

    def test_live_mode_large_rejected_by_risk_manager(self):
        """Live mode LARGE trade should be rejected by Risk Manager if position > 10%."""
        chain = ApprovalChain(config={"mode": "live"})
        record = run_async(chain.evaluate(make_trade_request(
            position_pct=0.12, confidence=0.9, current_drawdown=0.02,
        )))
        assert record.final_decision == ApprovalDecision.REJECTED

    def test_live_mode_large_rejected_by_portfolio_manager(self):
        """LARGE trade rejected by Portfolio Manager for too many correlated positions."""
        chain = ApprovalChain(config={"mode": "live"})
        record = run_async(chain.evaluate(make_trade_request(
            position_pct=0.03, confidence=0.8, current_drawdown=0.02,
            correlated_positions=3, strategy_win_rate=0.6,
        )))
        assert record.final_decision == ApprovalDecision.REJECTED


# ─── Approver Chain Details ────────────────────────────────────────────


class TestApproverChain:
    """Test specific approver behaviors."""

    def test_risk_manager_veto_on_daily_loss(self):
        """Risk Manager should reject trades when daily loss > 1%."""
        chain = ApprovalChain(config={"mode": "live"})
        record = run_async(chain.evaluate(make_trade_request(
            position_pct=0.01, confidence=0.8, daily_loss_pct=0.015,
        )))
        assert record.final_decision == ApprovalDecision.REJECTED
        assert any(d["approver"] == RISK_MANAGER for d in record.decisions)

    def test_risk_manager_escalate_low_confidence(self):
        """Risk Manager should escalate when confidence < 0.65."""
        chain = ApprovalChain(config={"mode": "live"})
        record = run_async(chain.evaluate(make_trade_request(
            position_pct=0.01, confidence=0.5, current_drawdown=0.02,
            correlated_positions=0, strategy_win_rate=0.6,
        )))
        # Should still get approved after escalation to Portfolio Manager
        assert any(
            d["decision"] == ApprovalDecision.ESCALATED
            for d in record.decisions
            if d["approver"] == RISK_MANAGER
        )

    def test_portfolio_manager_rejects_low_win_rate(self):
        """Portfolio Manager should reject if strategy win rate < 40%."""
        chain = ApprovalChain(config={"mode": "live"})
        record = run_async(chain.evaluate(make_trade_request(
            position_pct=0.03, confidence=0.8, current_drawdown=0.02,
            strategy_win_rate=0.3, correlated_positions=0,
        )))
        assert record.final_decision == ApprovalDecision.REJECTED

    def test_senior_trader_rejects_very_low_confidence_large_position(self):
        """Senior Trader rejects very low confidence + very large position."""
        chain = ApprovalChain(config={"mode": "live"})
        record = run_async(chain.evaluate(make_trade_request(
            position_pct=0.09, confidence=0.4, current_drawdown=0.02,
            correlated_positions=0, strategy_win_rate=0.6,
        )))
        assert record.final_decision == ApprovalDecision.REJECTED

    def test_decisions_logged_with_timestamp(self):
        """Every decision should have a timestamp."""
        chain = ApprovalChain(config={"mode": "live"})
        record = run_async(chain.evaluate(make_trade_request(position_pct=0.003)))
        for decision in record.decisions:
            assert "timestamp" in decision
            assert decision["timestamp"] is not None

    def test_approver_decisions_include_reason(self):
        """Every decision should include a reason string."""
        chain = ApprovalChain(config={"mode": "live"})
        record = run_async(chain.evaluate(make_trade_request(position_pct=0.003)))
        for decision in record.decisions:
            assert "reason" in decision
            assert isinstance(decision["reason"], str)
            assert len(decision["reason"]) > 0


# ─── Statistics and History ────────────────────────────────────────────


class TestStatsAndHistory:
    """Test history tracking and statistics."""

    def test_empty_stats(self):
        """Stats should return zeros when no trades evaluated."""
        chain = ApprovalChain()
        stats = chain.get_stats()
        assert stats["total"] == 0
        assert stats["approved"] == 0
        assert stats["rejected"] == 0
        assert stats["approval_rate"] == 0.0

    def test_history_records_trades(self):
        """History should accumulate approval records."""
        chain = ApprovalChain(config={"mode": "backtest"})
        run_async(chain.evaluate(make_trade_request(trade_id="t1")))
        run_async(chain.evaluate(make_trade_request(trade_id="t2")))
        history = chain.get_history()
        assert len(history) == 2

    def test_stats_counts(self):
        """Stats should correctly count approvals and rejections."""
        chain = ApprovalChain(config={"mode": "live"})
        # One approved (small)
        run_async(chain.evaluate(make_trade_request(trade_id="t1", position_pct=0.003)))
        # One rejected (large, over 10%)
        run_async(chain.evaluate(make_trade_request(trade_id="t2", position_pct=0.12)))
        stats = chain.get_stats()
        assert stats["total"] == 2
        assert stats["approved"] == 1
        assert stats["rejected"] == 1
        assert stats["approval_rate"] == 0.5

    def test_stats_by_tier(self):
        """Stats should include breakdown by tier."""
        chain = ApprovalChain(config={"mode": "backtest"})
        run_async(chain.evaluate(make_trade_request(position_pct=0.003)))
        run_async(chain.evaluate(make_trade_request(position_pct=0.01)))
        run_async(chain.evaluate(make_trade_request(position_pct=0.05)))
        stats = chain.get_stats()
        assert stats["by_tier"]["small"] == 1
        assert stats["by_tier"]["medium"] == 1
        assert stats["by_tier"]["large"] == 1

    def test_history_limit(self):
        """get_history should respect the limit parameter."""
        chain = ApprovalChain(config={"mode": "backtest"})
        for i in range(10):
            run_async(chain.evaluate(make_trade_request(trade_id=f"t{i}")))
        history = chain.get_history(limit=3)
        assert len(history) == 3


# ─── Determinism Verification ──────────────────────────────────────────


class TestDeterminism:
    """Verify that the approval chain produces deterministic results."""

    def test_same_input_same_output(self):
        """Same trade request should always produce same tier classification."""
        chain = ApprovalChain()
        for _ in range(100):
            assert chain.classify_tier(0.007) == ApprovalTier.MEDIUM

    def test_same_input_same_decision(self):
        """Same trade request should produce same approval decision."""
        chain = ApprovalChain(config={"mode": "live"})
        req = make_trade_request(position_pct=0.003)
        results = []
        for _ in range(5):
            record = run_async(chain.evaluate({**req, "trade_id": f"determ-{_}"}))
            results.append(record.final_decision)
        assert all(r == results[0] for r in results)

    def test_record_tier_matches_classify(self):
        """Record tier should match what classify_tier returns."""
        chain = ApprovalChain(config={"mode": "backtest"})
        for pct in [0.001, 0.005, 0.01, 0.02, 0.05]:
            record = run_async(chain.evaluate(make_trade_request(
                position_pct=pct, trade_id=f"pct-{pct}",
            )))
            assert record.tier == chain.classify_tier(pct)

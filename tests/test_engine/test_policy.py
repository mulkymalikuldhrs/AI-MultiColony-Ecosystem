"""
Tests for Deterministic Policy Layer
======================================
Covers: normal operation, edge cases, boundary values, error handling,
determinism verification, confidence gating, rule overrides.
"""

from __future__ import annotations

import pytest

from quant_nanggroe.engine.policy import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_DRAWDOWN_LIMIT,
    PolicyDecision,
    PolicyLayer,
)


# ─── Helpers ────────────────────────────────────────────────────────────

def make_llm_output(**overrides) -> dict:
    """Build a standard LLM output dict."""
    base = {
        "action": "BUY",
        "confidence": 0.8,
        "position_size_pct": 0.02,
        "reasoning": "Strong momentum signal",
        "strategy": "momentum",
    }
    base.update(overrides)
    return base


def make_context(**overrides) -> dict:
    """Build a standard context dict."""
    base = {
        "regime": "TRENDING_UP",
        "current_drawdown": 0.05,
        "daily_loss_pct": 0.002,
        "volatility_level": "NORMAL",
        "position_count": 2,
        "correlation_count": 1,
    }
    base.update(overrides)
    return base


# ─── Confidence Gating ─────────────────────────────────────────────────


class TestConfidenceGate:
    """Test confidence gating logic."""

    def test_high_confidence_passes(self):
        """High confidence output should pass through unchanged."""
        policy = PolicyLayer()
        result = policy.apply(make_llm_output(confidence=0.9), make_context())
        assert result["action"] == "BUY"
        assert result["overridden"] is False

    def test_low_confidence_gated(self):
        """Low confidence output should be overridden to HOLD."""
        policy = PolicyLayer()
        result = policy.apply(make_llm_output(confidence=0.3), make_context())
        assert result["action"] == "HOLD"
        assert result["overridden"] is True

    def test_exact_threshold_passes(self):
        """Confidence at exact threshold should pass."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(confidence=DEFAULT_CONFIDENCE_THRESHOLD),
            make_context(),
        )
        assert result["overridden"] is False

    def test_just_below_threshold_gated(self):
        """Confidence just below threshold should be gated."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(confidence=DEFAULT_CONFIDENCE_THRESHOLD - 0.01),
            make_context(),
        )
        assert result["overridden"] is True

    def test_custom_threshold(self):
        """Custom confidence threshold should override default."""
        policy = PolicyLayer(config={"confidence_threshold": 0.8})
        # 0.7 would pass default 0.65 but fail custom 0.8
        result = policy.apply(make_llm_output(confidence=0.7), make_context())
        assert result["overridden"] is True

    def test_zero_confidence_always_gated(self):
        """Zero confidence should always be gated."""
        policy = PolicyLayer()
        result = policy.apply(make_llm_output(confidence=0.0), make_context())
        assert result["action"] == "HOLD"
        assert result["overridden"] is True

    def test_confidence_gate_with_hold_action(self):
        """Low confidence HOLD should remain HOLD (no change in action)."""
        policy = PolicyLayer()
        result = policy.apply(make_llm_output(action="HOLD", confidence=0.3), make_context())
        assert result["action"] == "HOLD"


# ─── Rule Overrides ────────────────────────────────────────────────────


class TestRuleOverrides:
    """Test deterministic rule overrides."""

    def test_no_trade_regime_overrides(self):
        """NO_TRADE regime should force HOLD regardless of LLM."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(action="BUY", confidence=0.9),
            make_context(regime="NO_TRADE"),
        )
        assert result["action"] == "HOLD"
        assert result["overridden"] is True
        assert any("NO_TRADE" in r for r in result["override_reasons"])

    def test_panic_regime_overrides(self):
        """PANIC regime should force HOLD."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(action="BUY", confidence=0.9),
            make_context(regime="PANIC"),
        )
        assert result["action"] == "HOLD"
        assert result["overridden"] is True

    def test_drawdown_limit_overrides(self):
        """Drawdown > 15% should force HOLD."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(action="BUY", confidence=0.9),
            make_context(current_drawdown=0.20),
        )
        assert result["action"] == "HOLD"
        assert result["overridden"] is True

    def test_daily_loss_overrides(self):
        """Daily loss > 1% should force HOLD."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(action="BUY", confidence=0.9),
            make_context(daily_loss_pct=0.02),
        )
        assert result["action"] == "HOLD"
        assert result["overridden"] is True

    def test_risk_off_regime_overrides_buy(self):
        """RISK_OFF regime should downgrade BUY to HOLD."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(action="BUY", confidence=0.8),
            make_context(regime="RISK_OFF"),
        )
        assert result["action"] == "HOLD"
        assert result["overridden"] is True

    def test_extreme_volatility_overrides(self):
        """EXTREME volatility should downgrade BUY to HOLD."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(action="BUY", confidence=0.8),
            make_context(volatility_level="EXTREME"),
        )
        assert result["action"] == "HOLD"
        assert result["overridden"] is True

    def test_too_many_positions_overrides(self):
        """Position count >= 10 should force HOLD."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(action="BUY", confidence=0.8),
            make_context(position_count=10),
        )
        assert result["action"] == "HOLD"
        assert result["overridden"] is True

    def test_normal_regime_no_override(self):
        """Normal conditions should not trigger overrides."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(action="BUY", confidence=0.8),
            make_context(regime="TRENDING_UP", current_drawdown=0.02),
        )
        assert result["action"] == "BUY"
        assert result["overridden"] is False


# ─── Fallback Table ────────────────────────────────────────────────────


class TestFallbackTable:
    """Test fallback table for low-confidence outputs."""

    def test_default_fallback_table_loaded(self):
        """Default fallback table should be loaded."""
        policy = PolicyLayer()
        table = policy.get_fallback_table()
        assert "momentum" in table
        assert table["momentum"] == "HOLD"
        assert "mean_reversion" in table

    def test_strategy_specific_fallback(self):
        """Low-confidence output with known strategy should use fallback."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(action="BUY", confidence=0.3, strategy="momentum"),
            make_context(),
        )
        assert result["action"] == "HOLD"  # momentum fallback

    def test_unknown_strategy_fallback(self):
        """Unknown strategy should use general HOLD fallback."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(action="BUY", confidence=0.3, strategy="unknown_strategy"),
            make_context(),
        )
        assert result["action"] == "HOLD"

    def test_add_custom_fallback(self):
        """add_fallback should add/update entries."""
        policy = PolicyLayer()
        policy.add_fallback("custom_strat", "REDUCE")
        table = policy.get_fallback_table()
        assert table["custom_strat"] == "REDUCE"

    def test_hold_action_low_confidence_stays_hold(self):
        """HOLD with low confidence should remain HOLD."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(action="HOLD", confidence=0.3),
            make_context(),
        )
        assert result["action"] == "HOLD"


# ─── Position Size Capping ─────────────────────────────────────────────


class TestPositionSizeCapping:
    """Test position size capping logic."""

    def test_normal_regime_no_cap(self):
        """Normal regime should not cap position size."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(position_size_pct=0.05),
            make_context(regime="TRENDING_UP"),
        )
        assert result["position_size_pct"] == 0.05

    def test_risk_off_caps_position(self):
        """RISK_OFF regime should cap position size."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(action="HOLD", position_size_pct=0.05),
            make_context(regime="RISK_OFF"),
        )
        assert result["position_size_pct"] < 0.05

    def test_panic_zeroes_position(self):
        """PANIC regime should zero out position size."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(action="HOLD", position_size_pct=0.05),
            make_context(regime="PANIC"),
        )
        assert result["position_size_pct"] == 0.0

    def test_no_trade_zeroes_position(self):
        """NO_TRADE regime should zero out position size."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(action="HOLD", position_size_pct=0.05),
            make_context(regime="NO_TRADE"),
        )
        assert result["position_size_pct"] == 0.0

    def test_volatile_caps_at_50pct(self):
        """VOLATILE regime should cap large positions at DEFAULT_POSITION_CAP_PCT."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(action="HOLD", position_size_pct=0.80),
            make_context(regime="VOLATILE"),
        )
        assert result["position_size_pct"] == 0.50  # DEFAULT_POSITION_CAP_PCT

    def test_volatile_small_position_uncapped(self):
        """VOLATILE regime should not cap small positions."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(action="HOLD", position_size_pct=0.03),
            make_context(regime="VOLATILE"),
        )
        assert result["position_size_pct"] == 0.03


# ─── Policy Hash & Reproducibility ─────────────────────────────────────


class TestDeterminism:
    """Verify deterministic policy behavior."""

    def test_same_input_same_hash(self):
        """Same inputs should produce the same policy hash."""
        policy = PolicyLayer()
        result1 = policy.apply(make_llm_output(confidence=0.8), make_context())
        result2 = policy.apply(make_llm_output(confidence=0.8), make_context())
        assert result1["policy_hash"] == result2["policy_hash"]

    def test_different_input_different_hash(self):
        """Different inputs should produce different policy hashes."""
        policy = PolicyLayer()
        result1 = policy.apply(make_llm_output(confidence=0.8), make_context())
        result2 = policy.apply(make_llm_output(confidence=0.5), make_context())
        assert result1["policy_hash"] != result2["policy_hash"]

    def test_same_input_same_action(self):
        """Same inputs should always produce the same action."""
        policy = PolicyLayer()
        actions = []
        for _ in range(10):
            result = policy.apply(make_llm_output(confidence=0.8), make_context())
            actions.append(result["action"])
        assert all(a == actions[0] for a in actions)

    def test_policy_decision_record_immutability(self):
        """Original action should be preserved even when overridden."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(action="BUY", confidence=0.3),
            make_context(),
        )
        assert result["original_action"] == "BUY"
        assert result["action"] == "HOLD"
        assert result["overridden"] is True


# ─── Statistics & Logging ──────────────────────────────────────────────


class TestStatsAndLogging:
    """Test statistics and logging."""

    def test_empty_stats(self):
        """Stats should return zeros when no decisions made."""
        policy = PolicyLayer()
        stats = policy.get_stats()
        assert stats["total"] == 0
        assert stats["overridden"] == 0

    def test_stats_after_decisions(self):
        """Stats should correctly count overrides."""
        policy = PolicyLayer()
        policy.apply(make_llm_output(confidence=0.8), make_context())  # No override
        policy.apply(make_llm_output(confidence=0.3), make_context())  # Override
        stats = policy.get_stats()
        assert stats["total"] == 2
        assert stats["overridden"] == 1

    def test_decision_log(self):
        """Decision log should track all decisions."""
        policy = PolicyLayer()
        policy.apply(make_llm_output(confidence=0.8), make_context())
        policy.apply(make_llm_output(confidence=0.3), make_context())
        log = policy.get_decision_log()
        assert len(log) == 2

    def test_decision_log_limit(self):
        """Decision log should respect limit parameter."""
        policy = PolicyLayer()
        for i in range(10):
            policy.apply(make_llm_output(confidence=0.8), make_context())
        log = policy.get_decision_log(limit=3)
        assert len(log) == 3

    def test_override_reasons_populated(self):
        """Override reasons should be populated when overridden."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(confidence=0.3),
            make_context(),
        )
        assert len(result["override_reasons"]) > 0

    def test_no_override_reasons_when_passed(self):
        """No override reasons when policy passes through."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(confidence=0.9),
            make_context(regime="TRENDING_UP", current_drawdown=0.02),
        )
        assert len(result["override_reasons"]) == 0


# ─── Edge Cases ────────────────────────────────────────────────────────


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_missing_action_defaults_to_hold(self):
        """Missing action should default to HOLD."""
        policy = PolicyLayer()
        result = policy.apply({"confidence": 0.8}, make_context())
        assert result["original_action"] == "HOLD"

    def test_missing_confidence_defaults_to_zero(self):
        """Missing confidence should default to 0.0 (gated)."""
        policy = PolicyLayer()
        result = policy.apply({"action": "BUY"}, make_context())
        assert result["overridden"] is True
        assert result["action"] == "HOLD"

    def test_empty_context_no_crash(self):
        """Empty context should not crash (defaults used)."""
        policy = PolicyLayer()
        result = policy.apply(make_llm_output(confidence=0.8), {})
        assert "action" in result

    def test_empty_llm_output(self):
        """Empty LLM output should default to HOLD with low confidence."""
        policy = PolicyLayer()
        result = policy.apply({}, make_context())
        assert result["action"] == "HOLD"
        assert result["overridden"] is True

    def test_custom_drawdown_limit(self):
        """Custom drawdown limit should override default."""
        policy = PolicyLayer(config={"drawdown_limit": 0.10})
        result = policy.apply(
            make_llm_output(action="BUY", confidence=0.9),
            make_context(current_drawdown=0.12),
        )
        assert result["action"] == "HOLD"
        assert result["overridden"] is True

    def test_multiple_overrides_stacked(self):
        """Multiple override conditions should all be recorded."""
        policy = PolicyLayer()
        result = policy.apply(
            make_llm_output(action="BUY", confidence=0.3),
            make_context(regime="NO_TRADE"),
        )
        assert result["overridden"] is True
        assert len(result["override_reasons"]) >= 1

    def test_action_case_insensitive(self):
        """Actions should be case-insensitive."""
        policy = PolicyLayer()
        result1 = policy.apply(make_llm_output(action="buy", confidence=0.8), make_context())
        result2 = policy.apply(make_llm_output(action="BUY", confidence=0.8), make_context())
        assert result1["action"] == result2["action"]

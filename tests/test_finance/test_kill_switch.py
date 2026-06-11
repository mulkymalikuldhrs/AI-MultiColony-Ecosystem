"""Tests for KillSwitch — activation, auto-activation, deactivation, cooldown."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest

from ai_multicolony.finance.kill_switch import (
    KillSwitch,
    KillSwitchConfig,
    KillSwitchEvent,
    KillSwitchLevel,
    KillSwitchStatus,
    KillSwitchTrigger,
)


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def ks():
    return KillSwitch()


@pytest.fixture
def ks_no_cooldown():
    """KillSwitch with zero cooldown for easier testing."""
    return KillSwitch(config=KillSwitchConfig(
        cooldown_minutes=0,
        level_2_cooldown_minutes=0,
    ))


# ── Activation ────────────────────────────────────────────────────────────

class TestKillSwitchActivation:
    """Test manual activation."""

    def test_activate_level_1(self, ks):
        event = ks.activate(KillSwitchLevel.LEVEL_1, reason="Test")
        assert ks.current_level == KillSwitchLevel.LEVEL_1
        assert ks.is_active()
        assert not ks.can_trade()
        assert event.level == KillSwitchLevel.LEVEL_1
        assert event.auto_activated is False

    def test_activate_level_2(self, ks):
        ks.activate(KillSwitchLevel.LEVEL_2, reason="Test")
        assert ks.current_level == KillSwitchLevel.LEVEL_2
        assert not ks.can_trade()

    def test_activate_level_3(self, ks):
        ks.activate(KillSwitchLevel.LEVEL_3, reason="Test")
        assert ks.current_level == KillSwitchLevel.LEVEL_3
        assert not ks.can_trade()
        assert not ks.can_hold_positions()

    def test_activate_none_level_ignored(self, ks):
        event = ks.activate(KillSwitchLevel.NONE)
        assert event.level == KillSwitchLevel.NONE  # Returns empty event
        assert not ks.is_active()

    def test_activate_records_event(self, ks):
        ks.activate(KillSwitchLevel.LEVEL_1, reason="Test", trigger=KillSwitchTrigger.MANUAL)
        assert len(ks.events) == 1
        assert ks.events[0].trigger == KillSwitchTrigger.MANUAL

    def test_can_hold_positions_level_1(self, ks):
        ks.activate(KillSwitchLevel.LEVEL_1)
        assert ks.can_hold_positions()  # Level 1 allows holding

    def test_can_hold_positions_level_3(self, ks):
        ks.activate(KillSwitchLevel.LEVEL_3)
        assert not ks.can_hold_positions()  # Level 3 stops all


# ── Deactivation ──────────────────────────────────────────────────────────

class TestKillSwitchDeactivation:
    """Test deactivation with cooldown and approval."""

    def test_deactivate_not_active(self, ks):
        result = ks.deactivate()
        assert result is None

    def test_deactivate_level_1_no_cooldown(self, ks_no_cooldown):
        ks_no_cooldown.activate(KillSwitchLevel.LEVEL_1)
        event = ks_no_cooldown.deactivate()
        assert ks_no_cooldown.current_level == KillSwitchLevel.NONE
        assert not ks_no_cooldown.is_active()

    def test_deactivate_level_3_requires_approval(self, ks_no_cooldown):
        ks_no_cooldown.activate(KillSwitchLevel.LEVEL_3)
        # Without approval code
        result = ks_no_cooldown.deactivate()
        assert result is None  # Blocked
        assert ks_no_cooldown.is_active()

    def test_deactivate_level_3_with_approval(self, ks_no_cooldown, monkeypatch):
        ks_no_cooldown.activate(KillSwitchLevel.LEVEL_3)
        # Set the approval code via environment variable
        monkeypatch.setenv("MULTICOLONY_LEVEL3_APPROVAL_CODE", "test_approval_code_123")
        result = ks_no_cooldown.deactivate(
            approval_code="test_approval_code_123",
        )
        assert result is not None
        assert not ks_no_cooldown.is_active()

    def test_deactivate_resolves_event(self, ks_no_cooldown):
        ks_no_cooldown.activate(KillSwitchLevel.LEVEL_1)
        ks_no_cooldown.deactivate()
        # Last event should be resolved
        for event in reversed(ks_no_cooldown.events):
            if event.level == KillSwitchLevel.LEVEL_1:
                assert event.resolved is True
                break

    def test_deactivate_cooldown_not_elapsed(self, ks):
        # Use default config with 30 min cooldown
        ks.activate(KillSwitchLevel.LEVEL_1)
        result = ks.deactivate()
        assert result is None  # Cooldown not elapsed


# ── Auto-Activation ──────────────────────────────────────────────────────

class TestAutoActivation:
    """Test auto-activation on drawdown thresholds."""

    def test_auto_daily_loss(self, ks):
        event = ks.check_auto_activate(daily_pnl_pct=-1.5)  # Exceeds 1.5%
        assert event is not None
        assert event.auto_activated is True
        assert event.trigger == KillSwitchTrigger.DAILY_LOSS_EXCEEDED
        assert event.level == KillSwitchLevel.LEVEL_1

    def test_auto_weekly_loss(self, ks):
        event = ks.check_auto_activate(weekly_pnl_pct=-4.5)  # Exceeds 4%
        assert event is not None
        assert event.trigger == KillSwitchTrigger.WEEKLY_LOSS_EXCEEDED
        assert event.level == KillSwitchLevel.LEVEL_2

    def test_auto_drawdown(self, ks):
        event = ks.check_auto_activate(max_drawdown_pct=6.0)  # Exceeds 5%
        assert event is not None
        assert event.trigger == KillSwitchTrigger.DRAWDOWN_EXCEEDED
        assert event.level == KillSwitchLevel.LEVEL_2

    def test_auto_volatility_spike(self, ks):
        event = ks.check_auto_activate(volatility_pct=12.0)  # Exceeds 10%
        assert event is not None
        assert event.trigger == KillSwitchTrigger.VOLATILITY_SPIKE
        assert event.level == KillSwitchLevel.LEVEL_1

    def test_no_auto_activation_when_safe(self, ks):
        event = ks.check_auto_activate(
            daily_pnl_pct=-0.5,
            weekly_pnl_pct=-1.0,
            max_drawdown_pct=2.0,
            volatility_pct=5.0,
        )
        assert event is None

    def test_no_auto_activation_when_already_active(self, ks):
        ks.activate(KillSwitchLevel.LEVEL_1)
        event = ks.check_auto_activate(daily_pnl_pct=-5.0)
        assert event is None  # Already active, no new activation

    def test_daily_loss_priority(self, ks):
        """Daily loss check comes first."""
        event = ks.check_auto_activate(
            daily_pnl_pct=-2.0,  # Triggers daily
            weekly_pnl_pct=-5.0,  # Would also trigger weekly
            max_drawdown_pct=6.0,
        )
        assert event.trigger == KillSwitchTrigger.DAILY_LOSS_EXCEEDED


# ── Callbacks ────────────────────────────────────────────────────────────

class TestKillSwitchCallbacks:
    """Test activation callbacks."""

    def test_callback_called_on_activate(self, ks):
        called = []
        ks.on_activate(KillSwitchLevel.LEVEL_1, lambda e: called.append(e))
        ks.activate(KillSwitchLevel.LEVEL_1, reason="Test")
        assert len(called) == 1

    def test_callback_error_does_not_break(self, ks):
        def bad_callback(e):
            raise RuntimeError("Callback error")

        ks.on_activate(KillSwitchLevel.LEVEL_1, bad_callback)
        # Should not raise
        ks.activate(KillSwitchLevel.LEVEL_1, reason="Test")


# ── Pydantic Models ──────────────────────────────────────────────────────

class TestKillSwitchModels:
    """Test Pydantic model validation."""

    def test_kill_switch_event_defaults(self):
        event = KillSwitchEvent()
        assert event.level == KillSwitchLevel.NONE
        assert event.auto_activated is False
        assert event.resolved is False

    def test_kill_switch_config_defaults(self):
        config = KillSwitchConfig()
        assert config.auto_daily_loss_pct == 1.5
        assert config.auto_weekly_loss_pct == 4.0
        assert config.auto_max_drawdown_pct == 5.0
        assert config.cooldown_minutes == 30
        assert config.level_3_requires_approval is True

    def test_can_trade_initial(self, ks):
        assert ks.can_trade() is True

    def test_status_initial(self, ks):
        assert ks.status == KillSwitchStatus.INACTIVE


# ── Stats ─────────────────────────────────────────────────────────────────

class TestKillSwitchStats:
    """Test statistics."""

    def test_stats_initial(self, ks):
        stats = ks.stats
        assert stats["current_level"] == "none"
        assert stats["is_active"] is False
        assert stats["can_trade"] is True
        assert stats["total_events"] == 0

    def test_stats_after_activation(self, ks):
        ks.activate(KillSwitchLevel.LEVEL_1, trigger=KillSwitchTrigger.DAILY_LOSS_EXCEEDED, auto_activated=True)
        stats = ks.stats
        assert stats["is_active"] is True
        assert stats["auto_activations"] == 1
        assert stats["manual_activations"] == 0

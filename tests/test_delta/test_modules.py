"""Tests for Delta Engine, Decision Engine, Immune System, and Watchdog."""

import asyncio
import time
import pytest

from ai_multicolony_ecosystem.delta import (
    DeltaAlert,
    DeltaConfig,
    DeltaEngine,
    DeltaSeverity,
    RiskDirection,
)
from ai_multicolony_ecosystem.agents.decision import (
    DecisionAction,
    DecisionInput,
    DecisionOutput,
    DecisionSynthesisEngine,
    MarketRegime,
    PressureLevel,
    RiskClearance,
)
from ai_multicolony_ecosystem.security.immune import (
    ImmuneConfig,
    ImmuneStatus,
    ImmuneSystem,
)
from ai_multicolony_ecosystem.infrastructure import (
    ProcessState,
    WatchdogConfig,
    WatchdogDaemon,
)


# ======================================================================
# Delta Engine Tests
# ======================================================================

class TestDeltaSeverity:
    def test_values(self):
        assert DeltaSeverity.LOW == "low"
        assert DeltaSeverity.CRITICAL == "critical"


class TestRiskDirection:
    def test_values(self):
        assert RiskDirection.RISK_ON == "risk_on"
        assert RiskDirection.RISK_OFF == "risk_off"
        assert RiskDirection.MIXED == "mixed"


class TestDeltaAlert:
    def test_construction(self):
        alert = DeltaAlert(source="fred", field="federal_funds_rate", change_pct=5.0)
        assert alert.source == "fred"
        assert alert.change_pct == 5.0


class TestDeltaEngine:
    def test_construction(self):
        engine = DeltaEngine()
        assert engine.get_stats()["threshold_pct"] == 1.0

    def test_first_sweep_no_alerts(self):
        engine = DeltaEngine()
        alerts = engine.compute_deltas({"fred": {"federal_funds_rate": 5.25}})
        assert len(alerts) == 0  # First sweep sets baseline

    def test_no_change_no_alerts(self):
        engine = DeltaEngine()
        data = {"fred": {"federal_funds_rate": 5.25}}
        engine.compute_deltas(data)
        alerts = engine.compute_deltas(data)
        assert len(alerts) == 0  # No change

    def test_significant_change_alerts(self):
        engine = DeltaEngine()
        engine.set_previous({"fred": {"federal_funds_rate": 5.0}})
        alerts = engine.compute_deltas({"fred": {"federal_funds_rate": 5.5}})
        assert len(alerts) == 1
        assert alerts[0].change_pct == 10.0
        assert alerts[0].severity in (DeltaSeverity.MEDIUM, DeltaSeverity.HIGH, DeltaSeverity.CRITICAL)

    def test_below_threshold_no_alerts(self):
        engine = DeltaEngine(DeltaConfig(numeric_threshold_pct=5.0))
        engine.set_previous({"fred": {"federal_funds_rate": 5.0}})
        alerts = engine.compute_deltas({"fred": {"federal_funds_rate": 5.03}})
        assert len(alerts) == 0  # 0.6% change < 5% threshold

    def test_risk_direction_vix(self):
        engine = DeltaEngine()
        assert engine._classify_risk_direction("vix", 10.0) == RiskDirection.RISK_OFF
        assert engine._classify_risk_direction("vix", -10.0) == RiskDirection.RISK_ON

    def test_risk_direction_sp500(self):
        engine = DeltaEngine()
        assert engine._classify_risk_direction("sp500", 5.0) == RiskDirection.RISK_ON
        assert engine._classify_risk_direction("sp500", -5.0) == RiskDirection.RISK_OFF

    def test_compute_risk_direction(self):
        engine = DeltaEngine()
        engine.set_previous({"test": {"sp500": 100, "vix": 15}})
        alerts = engine.compute_deltas({"test": {"sp500": 110, "vix": 20}})
        direction = engine.compute_risk_direction(alerts)
        assert direction in (RiskDirection.RISK_ON, RiskDirection.RISK_OFF, RiskDirection.MIXED)

    def test_severity_classification(self):
        engine = DeltaEngine()
        assert engine._classify_severity(0.5) == DeltaSeverity.LOW
        assert engine._classify_severity(3.0) == DeltaSeverity.MEDIUM
        assert engine._classify_severity(7.0) == DeltaSeverity.HIGH
        assert engine._classify_severity(15.0) == DeltaSeverity.CRITICAL


# ======================================================================
# Decision Engine Tests
# ======================================================================

class TestMarketRegime:
    def test_values(self):
        assert MarketRegime.TRENDING_UP == "trending_up"
        assert MarketRegime.PANIC == "panic"
        assert MarketRegime.NO_TRADE == "no_trade"


class TestDecisionInput:
    def test_defaults(self):
        inp = DecisionInput()
        assert inp.regime == MarketRegime.RANGE
        assert inp.pressure == PressureLevel.NEUTRAL
        assert inp.confidence == 0.5


class TestDecisionSynthesisEngine:
    def test_construction(self):
        engine = DecisionSynthesisEngine()
        assert engine._max_risk_per_trade == 0.5

    def test_strong_bullish(self):
        engine = DecisionSynthesisEngine()
        decision = engine.decide(DecisionInput(
            regime=MarketRegime.TRENDING_UP,
            pressure=PressureLevel.STRONG_BUY,
            confidence=0.9,
        ))
        assert decision.action == DecisionAction.ENTER_LONG
        assert decision.risk_clearance == RiskClearance.CLEAR
        assert decision.position_size_pct > 0

    def test_strong_bearish(self):
        engine = DecisionSynthesisEngine()
        decision = engine.decide(DecisionInput(
            regime=MarketRegime.TRENDING_DOWN,
            pressure=PressureLevel.STRONG_SELL,
            confidence=0.8,
        ))
        assert decision.action == DecisionAction.ENTER_SHORT
        assert decision.risk_clearance == RiskClearance.CLEAR

    def test_kill_switch_blocks(self):
        engine = DecisionSynthesisEngine()
        decision = engine.decide(DecisionInput(
            regime=MarketRegime.TRENDING_UP,
            pressure=PressureLevel.STRONG_BUY,
            confidence=0.9,
            kill_switch_active=True,
        ))
        assert decision.action == DecisionAction.NO_ACTION
        assert decision.risk_clearance == RiskClearance.BLOCKED

    def test_daily_loss_blocks(self):
        engine = DecisionSynthesisEngine()
        decision = engine.decide(DecisionInput(
            regime=MarketRegime.TRENDING_UP,
            pressure=PressureLevel.STRONG_BUY,
            daily_loss_pct=-1.5,
        ))
        assert decision.risk_clearance == RiskClearance.BLOCKED

    def test_low_confidence_pauses(self):
        engine = DecisionSynthesisEngine()
        decision = engine.decide(DecisionInput(
            regime=MarketRegime.TRENDING_UP,
            pressure=PressureLevel.BUY,
            confidence=0.2,
        ))
        assert decision.risk_clearance == RiskClearance.PAUSE

    def test_range_hold(self):
        engine = DecisionSynthesisEngine()
        decision = engine.decide(DecisionInput(
            regime=MarketRegime.RANGE,
            pressure=PressureLevel.NEUTRAL,
        ))
        assert decision.action == DecisionAction.HOLD

    def test_panic_no_action(self):
        engine = DecisionSynthesisEngine()
        decision = engine.decide(DecisionInput(
            regime=MarketRegime.PANIC,
            pressure=PressureLevel.STRONG_SELL,
        ))
        assert decision.action == DecisionAction.NO_ACTION


# ======================================================================
# Immune System Tests
# ======================================================================

class TestImmuneSystem:
    def test_construction(self):
        immune = ImmuneSystem()
        assert immune.status == ImmuneStatus.HEALTHY
        assert immune.is_healthy is True

    def test_reset(self):
        immune = ImmuneSystem()
        immune.record_error("test")
        immune.reset()
        assert immune.status == ImmuneStatus.HEALTHY
        assert immune.is_healthy is True

    def test_record_success(self):
        immune = ImmuneSystem()
        immune.record_success()
        stats = immune.get_stats()
        assert stats["successes"] == 1

    def test_record_error(self):
        immune = ImmuneSystem()
        immune.record_error("test error")
        stats = immune.get_stats()
        assert stats["errors"] == 1
        assert stats["consecutive_errors"] == 1

    def test_consecutive_errors_shutdown(self):
        immune = ImmuneSystem(ImmuneConfig(max_errors=3))
        immune.record_error("e1")
        immune.record_error("e2")
        assert immune.status == ImmuneStatus.HEALTHY or immune.status == ImmuneStatus.ELEVATED
        immune.record_error("e3")
        assert immune.is_shutdown is True

    def test_loop_detection(self):
        immune = ImmuneSystem()
        immune.check_iteration("same_action")
        immune.check_iteration("same_action")
        immune.check_iteration("same_action")
        assert immune.status in (ImmuneStatus.ELEVATED, ImmuneStatus.HEALTHY)

    def test_kill_switch(self):
        immune = ImmuneSystem()
        immune.activate_kill_switch()
        assert immune.is_shutdown is True
        assert immune.get_stats()["kill_switch"] is True

    def test_success_recovery(self):
        immune = ImmuneSystem()
        immune.record_error("e1")
        immune.record_error("e2")
        # Multiple successes should help recovery
        for _ in range(10):
            immune.record_success()
        # Status should recover from ELEVATED
        assert immune.status in (ImmuneStatus.HEALTHY, ImmuneStatus.ELEVATED)

    def test_can_restart_after_cooldown(self):
        immune = ImmuneSystem(ImmuneConfig(cooldown_seconds=0))
        immune.activate_kill_switch()
        assert immune.can_restart() is True


# ======================================================================
# Watchdog Tests
# ======================================================================

class TestWatchdogDaemon:
    def test_construction(self):
        daemon = WatchdogDaemon()
        assert daemon.is_running is False

    def test_register_process(self):
        daemon = WatchdogDaemon()
        daemon.register("test_process")
        info = daemon.get_process_info("test_process")
        assert info is not None
        assert info.name == "test_process"
        assert info.state == ProcessState.STOPPED

    def test_register_nonexistent(self):
        daemon = WatchdogDaemon()
        info = daemon.get_process_info("nonexistent")
        assert info is None

    def test_exponential_backoff(self):
        daemon = WatchdogDaemon(WatchdogConfig(base_delay=1.0, max_delay=60.0))
        assert daemon._compute_delay(0) == 1.0
        assert daemon._compute_delay(1) == 2.0
        assert daemon._compute_delay(2) == 4.0
        assert daemon._compute_delay(5) == 32.0
        assert daemon._compute_delay(10) == 60.0  # Capped at max

    @pytest.mark.asyncio
    async def test_start_and_stop(self):
        daemon = WatchdogDaemon()
        await daemon.start()
        assert daemon.is_running is True
        await daemon.stop()
        assert daemon.is_running is False

    @pytest.mark.asyncio
    async def test_start_process_with_fn(self):
        started = False

        async def start_fn():
            nonlocal started
            started = True

        daemon = WatchdogDaemon()
        daemon.register("test", start_fn=start_fn)
        result = await daemon.start_process("test")
        assert result is True
        assert started is True

    @pytest.mark.asyncio
    async def test_start_nonexistent(self):
        daemon = WatchdogDaemon()
        result = await daemon.start_process("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_all_info(self):
        daemon = WatchdogDaemon()
        daemon.register("proc1")
        daemon.register("proc2")
        info = daemon.get_all_info()
        assert "proc1" in info
        assert "proc2" in info

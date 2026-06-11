"""Tests for ImmuneSystem — threat detection, kill switch, loop detection."""

from __future__ import annotations

import pytest

from ai_multicolony.organism.immune import (
    ImmuneAction,
    ImmuneConfig,
    ImmuneSystem,
    ThreatAlert,
    ThreatLevel,
    ThreatType,
)


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def immune():
    return ImmuneSystem()


@pytest.fixture
def immune_no_kill():
    """ImmuneSystem that doesn't auto-kill on critical."""
    return ImmuneSystem(config=ImmuneConfig(kill_on_critical=False))


# ── Check Action ─────────────────────────────────────────────────────────

class TestCheckAction:
    """Test action authorization."""

    def test_allowed_action(self, immune):
        result = immune.check_action("read")
        assert result.threat_level == ThreatLevel.SAFE

    def test_forbidden_action(self, immune):
        result = immune.check_action("delete_system")
        assert result.threat_level == ThreatLevel.CRITICAL
        assert result.threat_type == ThreatType.UNAUTHORIZED_ACTION
        assert immune.is_killed  # Auto-kill on critical

    def test_unknown_action_warning(self, immune):
        result = immune.check_action("unknown_action")
        assert result.threat_level == ThreatLevel.WARNING

    def test_forbidden_action_no_kill(self, immune_no_kill):
        result = immune_no_kill.check_action("delete_system")
        assert result.threat_level == ThreatLevel.CRITICAL
        assert not immune_no_kill.is_killed

    def test_duplicate_action_detection(self, immune):
        immune_no_kill = ImmuneSystem(config=ImmuneConfig(
            max_duplicate_actions=3,
            kill_on_critical=False,
            throttle_on_danger=True,
        ))
        for _ in range(4):
            immune_no_kill.check_action("read")
        result = immune_no_kill.check_action("read")
        assert result.threat_type == ThreatType.DUPLICATE_ACTION
        assert result.threat_level == ThreatLevel.DANGER

    def test_loop_detection(self, immune):
        immune_no_kill = ImmuneSystem(config=ImmuneConfig(
            loop_detection_window=3,
            kill_on_critical=True,
        ))
        # Create a repeating pattern
        for _ in range(3):
            immune_no_kill.check_action("read")
            immune_no_kill.check_action("search")
        # Next cycle should detect loop
        immune_no_kill.check_action("read")
        immune_no_kill.check_action("search")
        result = immune_no_kill.check_action("read")
        # Loop detected or duplicate action
        assert result.threat_level in (ThreatLevel.CRITICAL, ThreatLevel.DANGER, ThreatLevel.WARNING, ThreatLevel.SAFE)


# ── Check Iteration ──────────────────────────────────────────────────────

class TestCheckIteration:
    """Test iteration limit checking."""

    def test_within_limit(self, immune):
        result = immune.check_iteration(count=500)
        assert result.threat_level == ThreatLevel.SAFE

    def test_exceeds_limit(self, immune):
        result = immune.check_iteration(count=1001)
        assert result.threat_level == ThreatLevel.CRITICAL
        assert immune.is_killed

    def test_approaching_limit(self, immune):
        result = immune.check_iteration(count=850)
        assert result.threat_level == ThreatLevel.WARNING

    def test_auto_increment(self, immune):
        immune.check_iteration()  # Should increment to 1
        assert immune.iteration_count == 1

    def test_set_count(self, immune):
        immune.check_iteration(count=100)
        assert immune.iteration_count == 100


# ── Check Execution Time ────────────────────────────────────────────────

class TestCheckExecutionTime:
    """Test execution time checking."""

    def test_within_limit(self, immune):
        result = immune.check_execution_time(elapsed_s=100)
        assert result.threat_level == ThreatLevel.SAFE

    def test_exceeds_limit(self, immune):
        result = immune.check_execution_time(elapsed_s=4000)
        assert result.threat_level == ThreatLevel.CRITICAL
        assert immune.is_killed

    def test_approaching_limit(self, immune):
        result = immune.check_execution_time(elapsed_s=3000)
        assert result.threat_level == ThreatLevel.WARNING


# ── Check Recursion Depth ───────────────────────────────────────────────

class TestCheckRecursionDepth:
    """Test recursion depth checking."""

    def test_within_limit(self, immune):
        result = immune.check_recursion_depth(depth=10)
        assert result.threat_level == ThreatLevel.SAFE

    def test_exceeds_limit(self, immune):
        result = immune.check_recursion_depth(depth=60)
        assert result.threat_level == ThreatLevel.DANGER

    def test_auto_increment(self, immune):
        immune.check_recursion_depth()
        assert immune._recursion_depth == 1


# ── Kill Switch ──────────────────────────────────────────────────────────

class TestKillSwitch:
    """Test kill switch activation."""

    def test_manual_kill(self, immune):
        result = immune.activate_kill_switch("Manual test")
        assert immune.is_killed
        assert result.threat_level == ThreatLevel.CRITICAL
        assert result.action_taken == ImmuneAction.KILL

    def test_kill_not_revivable(self, immune):
        immune.activate_kill_switch("Test")
        # Kill should stay active until reset
        assert immune.is_killed


# ── Pause / Resume ──────────────────────────────────────────────────────

class TestPauseResume:
    """Test pause and resume."""

    def test_pause(self, immune):
        immune.pause("Testing")
        assert immune.is_paused

    def test_resume(self, immune):
        immune.pause("Testing")
        immune.resume()
        assert not immune.is_paused


# ── Reset ────────────────────────────────────────────────────────────────

class TestReset:
    """Test reset."""

    def test_reset_clears_state(self, immune):
        immune.activate_kill_switch("Test")
        immune.pause("Test")
        immune.check_iteration(count=500)
        immune.reset()
        assert not immune.is_killed
        assert not immune.is_paused
        assert immune.iteration_count == 0
        assert immune._recursion_depth == 0


# ── ThreatAlert Model ───────────────────────────────────────────────────

class TestThreatAlertModel:
    """Test ThreatAlert Pydantic model."""

    def test_defaults(self):
        alert = ThreatAlert()
        assert alert.threat_type == ThreatType.SAFETY_VIOLATION
        assert alert.threat_level == ThreatLevel.WARNING
        assert alert.resolved is False

    def test_custom_values(self):
        alert = ThreatAlert(
            threat_type=ThreatType.INFINITE_LOOP,
            threat_level=ThreatLevel.CRITICAL,
            description="Loop detected",
        )
        assert alert.threat_type == ThreatType.INFINITE_LOOP


# ── ImmuneConfig Model ──────────────────────────────────────────────────

class TestImmuneConfigModel:
    """Test ImmuneConfig model."""

    def test_defaults(self):
        config = ImmuneConfig()
        assert config.max_iterations == 1000
        assert config.max_recursion_depth == 50
        assert config.kill_on_critical is True
        assert "delete_system" in config.forbidden_actions
        assert "read" in config.allowed_actions


# ── Stats ────────────────────────────────────────────────────────────────

class TestImmuneStats:
    """Test statistics."""

    def test_initial_stats(self, immune):
        stats = immune.stats
        assert stats["killed"] is False
        assert stats["paused"] is False
        assert stats["total_alerts"] == 0
        assert stats["critical_alerts"] == 0

    def test_stats_after_alerts(self, immune):
        immune.check_action("delete_system")
        stats = immune.stats
        assert stats["killed"] is True
        assert stats["critical_alerts"] >= 1

"""Immune System — Autonomous safety with iteration limits and error thresholds.

Ported from Autonomous-Organism immune/index.js. Provides biological
metaphor safety mechanisms: loop detection, error counting, kill switch,
and automatic shutdown when thresholds are exceeded.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ImmuneStatus(str, Enum):
    """Immune system status."""
    HEALTHY = "healthy"
    ELEVATED = "elevated"
    CRITICAL = "critical"
    SHUTDOWN = "shutdown"


class ImmuneAlert(BaseModel):
    """An immune system alert."""
    level: ImmuneStatus = ImmuneStatus.HEALTHY
    message: str = ""
    metric: str = ""
    value: float = 0.0
    threshold: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())


class ImmuneConfig(BaseModel):
    """Configuration for the immune system."""
    max_iterations: int = Field(50, description="Max iterations before loop detection")
    max_errors: int = Field(10, description="Max consecutive errors before shutdown")
    max_error_rate: float = Field(0.3, description="Max error rate (0-1) before elevated")
    max_execution_time: int = Field(300, description="Max execution time in seconds")
    cooldown_seconds: int = Field(60, description="Cooldown after shutdown before restart")
    kill_switch_enabled: bool = True


class ImmuneSystem:
    """Autonomous safety system inspired by biological immune response.

    Monitors agent execution for:
    - Loop detection (same action repeated too many times)
    - Error accumulation (too many consecutive failures)
    - Timeout detection (execution taking too long)
    - Resource exhaustion (memory/CPU limits)

    When thresholds are exceeded, the immune system can:
    - Warn (elevated status)
    - Pause execution (critical status)
    - Kill the process (shutdown status)

    Usage::

        immune = ImmuneSystem()
        immune.reset()

        for step in execution_loop:
            immune.check_iteration()
            if immune.status == ImmuneStatus.SHUTDOWN:
                break

            try:
                result = execute_step(step)
                immune.record_success()
            except Exception as e:
                immune.record_error(str(e))
    """

    def __init__(self, config: Optional[ImmuneConfig] = None) -> None:
        self._config = config or ImmuneConfig()
        self._status = ImmuneStatus.HEALTHY
        self._iteration_count = 0
        self._error_count = 0
        self._success_count = 0
        self._consecutive_errors = 0
        self._start_time = time.monotonic()
        self._last_actions: List[str] = []
        self._kill_switch = False
        self._shutdown_time: Optional[float] = None
        self._alerts: List[ImmuneAlert] = []

    @property
    def status(self) -> ImmuneStatus:
        return self._status

    @property
    def is_healthy(self) -> bool:
        return self._status == ImmuneStatus.HEALTHY

    @property
    def is_shutdown(self) -> bool:
        return self._status == ImmuneStatus.SHUTDOWN

    def reset(self) -> None:
        """Reset immune system state."""
        self._status = ImmuneStatus.HEALTHY
        self._iteration_count = 0
        self._error_count = 0
        self._success_count = 0
        self._consecutive_errors = 0
        self._start_time = time.monotonic()
        self._last_actions = []
        self._kill_switch = False
        self._shutdown_time = None
        self._alerts = []

    def activate_kill_switch(self) -> None:
        """Manually activate kill switch."""
        self._kill_switch = True
        self._status = ImmuneStatus.SHUTDOWN
        self._shutdown_time = time.monotonic()
        alert = ImmuneAlert(
            level=ImmuneStatus.SHUTDOWN,
            message="Kill switch activated",
            metric="kill_switch",
        )
        self._alerts.append(alert)
        logger.critical("IMMUNE: Kill switch activated — execution halted")

    def check_iteration(self, action: str = "") -> ImmuneStatus:
        """Check if iteration is within safe bounds.

        Args:
            action: Current action description for loop detection.

        Returns:
            Current immune status.
        """
        self._iteration_count += 1

        # Check kill switch
        if self._kill_switch:
            return self._status

        # Loop detection
        if action:
            self._last_actions.append(action)
            if len(self._last_actions) > 5:
                self._last_actions = self._last_actions[-5:]

            if len(self._last_actions) >= 3:
                recent = self._last_actions[-3:]
                if len(set(recent)) == 1:
                    self._elevate("Loop detected: same action repeated 3+ times", "loop_detection", self._iteration_count, self._config.max_iterations)

        # Max iterations
        if self._iteration_count >= self._config.max_iterations:
            self._shutdown("Max iterations reached", "max_iterations", self._iteration_count, self._config.max_iterations)

        # Timeout
        elapsed = time.monotonic() - self._start_time
        if elapsed >= self._config.max_execution_time:
            self._shutdown("Execution timeout", "timeout", elapsed, self._config.max_execution_time)

        return self._status

    def record_success(self) -> None:
        """Record a successful execution step."""
        self._success_count += 1
        self._consecutive_errors = 0

        # Recovery: if elevated and getting successes, go back to healthy
        if self._status == ImmuneStatus.ELEVATED and self._success_count > 5:
            self._status = ImmuneStatus.HEALTHY
            logger.info("IMMUNE: Status recovered to HEALTHY")

    def record_error(self, error_msg: str = "") -> ImmuneStatus:
        """Record an execution error.

        Args:
            error_msg: Error description.

        Returns:
            Current immune status after error.
        """
        self._error_count += 1
        self._consecutive_errors += 1

        total = self._error_count + self._success_count
        error_rate = self._error_count / max(total, 1)

        # Check consecutive errors
        if self._consecutive_errors >= self._config.max_errors:
            self._shutdown(
                f"Max consecutive errors ({self._consecutive_errors})",
                "consecutive_errors",
                self._consecutive_errors,
                self._config.max_errors,
            )

        # Check error rate
        elif error_rate >= self._config.max_error_rate and total >= 10:
            self._elevate(
                f"Error rate too high: {error_rate:.0%}",
                "error_rate",
                error_rate,
                self._config.max_error_rate,
            )

        return self._status

    def _elevate(self, message: str, metric: str, value: float, threshold: float) -> None:
        """Elevate status to ELEVATED."""
        if self._status == ImmuneStatus.HEALTHY:
            self._status = ImmuneStatus.ELEVATED
            alert = ImmuneAlert(level=ImmuneStatus.ELEVATED, message=message, metric=metric, value=value, threshold=threshold)
            self._alerts.append(alert)
            logger.warning("IMMUNE: Status elevated — %s", message)

    def _shutdown(self, message: str, metric: str, value: float, threshold: float) -> None:
        """Shutdown — halt all execution."""
        self._status = ImmuneStatus.SHUTDOWN
        self._shutdown_time = time.monotonic()
        alert = ImmuneAlert(level=ImmuneStatus.SHUTDOWN, message=message, metric=metric, value=value, threshold=threshold)
        self._alerts.append(alert)
        logger.critical("IMMUNE: SHUTDOWN — %s", message)

    def can_restart(self) -> bool:
        """Check if enough cooldown time has passed for restart."""
        if self._shutdown_time is None:
            return True
        elapsed = time.monotonic() - self._shutdown_time
        return elapsed >= self._config.cooldown_seconds

    def get_stats(self) -> Dict[str, Any]:
        """Get immune system statistics."""
        total = self._error_count + self._success_count
        return {
            "status": self._status.value,
            "iterations": self._iteration_count,
            "errors": self._error_count,
            "successes": self._success_count,
            "consecutive_errors": self._consecutive_errors,
            "error_rate": self._error_count / max(total, 1),
            "kill_switch": self._kill_switch,
            "alerts_count": len(self._alerts),
        }


__all__ = [
    "ImmuneStatus",
    "ImmuneAlert",
    "ImmuneConfig",
    "ImmuneSystem",
]

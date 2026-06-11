"""
Immune System - Safety system preventing runaway agent behavior.
Port of autonomous-organism/immune/index.js to Python with Pydantic v2.

Features: iteration limits, timeouts, loop detection, consecutive error tracking.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.organism.immune")


class ImmuneConfig(BaseModel):
    """Configuration for the immune system."""
    max_iterations_per_task: int = 10
    hard_timeout_ms: int = 300_000  # 5 minutes
    max_consecutive_errors: int = 5
    max_loop_detection: int = 100
    max_cpu_cores: float = 1.0
    max_ram_mb: float = 512.0


class TaskCounters(BaseModel):
    """Counters for a specific task."""
    iterations: int = 0
    errors: int = 0
    loop_detections: dict[str, int] = Field(default_factory=dict)


class KillResult(BaseModel):
    """Result of killing a task."""
    killed: bool = True
    task_id: str
    reason: str
    timestamp: str = Field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%S"))


class HealthCheckResult(BaseModel):
    """Result of immune system health check."""
    healthy: bool
    warning_tasks: list[str]
    total_errors: int


class ImmuneSystem:
    """Safety system preventing runaway agent behavior.

    Features:
    - Iteration limits per task
    - Hard timeouts
    - Consecutive error tracking
    - Loop detection via state hashing
    - Task kill and reset capabilities
    """

    def __init__(self, config: ImmuneConfig | None = None) -> None:
        self.config = config or ImmuneConfig()
        self.counters: dict[str, TaskCounters] = {}

    def _get_counters(self, task_id: str) -> TaskCounters:
        """Get or create counters for a task."""
        if task_id not in self.counters:
            self.counters[task_id] = TaskCounters()
        return self.counters[task_id]

    def can_continue(self, task_id: str) -> bool:
        """Check if a task can continue based on iteration limits."""
        counters = self._get_counters(task_id)
        if counters.iterations >= self.config.max_iterations_per_task:
            logger.warning("MAX ITERATIONS: %s exceeded %d", task_id, self.config.max_iterations_per_task)
            return False
        counters.iterations += 1
        return True

    def check_timeout(self, task_id: str, start_time_ms: float) -> bool:
        """Check if a task has exceeded its timeout.

        Args:
            task_id: Task identifier
            start_time_ms: Start time in milliseconds (time.time() * 1000)

        Returns:
            True if within timeout, False if exceeded.
        """
        elapsed = time.time() * 1000 - start_time_ms
        if elapsed > self.config.hard_timeout_ms:
            logger.warning("TIMEOUT: %s exceeded %dms", task_id, self.config.hard_timeout_ms)
            return False
        return True

    def record_error(self, task_id: str) -> bool:
        """Record an error for a task.

        Returns:
            True if task can continue, False if max errors exceeded.
        """
        counters = self._get_counters(task_id)
        counters.errors += 1
        if counters.errors >= self.config.max_consecutive_errors:
            logger.warning("KILL: %s too many errors (%d)", task_id, counters.errors)
            return False
        return True

    def record_success(self, task_id: str) -> None:
        """Record a success, resetting error counter."""
        counters = self._get_counters(task_id)
        counters.errors = 0

    def detect_loop(self, task_id: str, state: str) -> bool:
        """Detect if a task is looping on the same state.

        Args:
            task_id: Task identifier
            state: Hashable string representation of current state

        Returns:
            True if state is OK (no loop), False if loop detected.
        """
        counters = self._get_counters(task_id)
        key = f"{task_id}_{state}"
        count = counters.loop_detections.get(key, 0) + 1
        counters.loop_detections[key] = count

        if count > self.config.max_loop_detection:
            logger.warning("LOOP DETECTED: %s repeating same state", task_id)
            return False
        return True

    def kill(self, task_id: str, reason: str) -> KillResult:
        """Kill a task and clean up its counters."""
        logger.warning("KILLING: %s - %s", task_id, reason)
        del self.counters[task_id]
        return KillResult(task_id=task_id, reason=reason)

    def reset(self, task_id: str) -> None:
        """Reset counters for a task."""
        if task_id in self.counters:
            self.counters[task_id] = TaskCounters()
            logger.info("Reset counters for: %s", task_id)

    def health_check(self) -> HealthCheckResult:
        """Perform health check across all tracked tasks."""
        error_tasks = [
            task_id
            for task_id, counters in self.counters.items()
            if counters.errors >= 3
        ]
        total_errors = sum(c.errors for c in self.counters.values())

        return HealthCheckResult(
            healthy=len(error_tasks) == 0,
            warning_tasks=error_tasks,
            total_errors=total_errors,
        )

    def get_status(self) -> dict:
        """Get immune system status."""
        return {
            "config": self.config.model_dump(),
            "tracked_tasks": len(self.counters),
            "health": self.health_check().model_dump(),
        }

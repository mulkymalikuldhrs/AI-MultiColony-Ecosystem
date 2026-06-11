"""
Organism Scheduler - Cycle-based task scheduling (hourly, daily, weekly, monthly).
Port of autonomous-organism/scheduler/index.js to Python with Pydantic v2.
"""

from __future__ import annotations

import asyncio
import logging
import time
from enum import Enum
from typing import Callable, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.organism.scheduler")


class CycleType(str, Enum):
    """Scheduler cycle types."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class CycleState(BaseModel):
    """State of a single cycle."""
    cycle_type: CycleType
    interval_ms: int
    run_count: int = 0
    last_run: float | None = None


class OrganismScheduler:
    """Cycle-based task scheduler for the organism.

    Supports hourly, daily, weekly, and monthly cycles with
    configurable intervals and async callback execution.
    """

    CYCLE_INTERVALS: dict[CycleType, int] = {
        CycleType.HOURLY: 3_600_000,
        CycleType.DAILY: 86_400_000,
        CycleType.WEEKLY: 604_800_000,
        CycleType.MONTHLY: 2_592_000_000,
    }

    def __init__(self) -> None:
        self.cycles: dict[CycleType, CycleState] = {
            ct: CycleState(cycle_type=ct, interval_ms=interval)
            for ct, interval in self.CYCLE_INTERVALS.items()
        }

    def should_run(self, cycle_type: CycleType) -> bool:
        """Check if a cycle should run based on its interval."""
        cycle = self.cycles[cycle_type]
        if cycle.last_run is None:
            return True
        return (time.time() * 1000 - cycle.last_run) > cycle.interval_ms

    async def run_cycle(self, cycle_type: CycleType, callback: Callable) -> bool:
        """Run a cycle's callback if the interval has elapsed.

        Returns True if the cycle was executed, False otherwise.
        """
        if not self.should_run(cycle_type):
            return False

        logger.info("[%s CYCLE]", cycle_type.value.upper())
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback()
            else:
                callback()
        except Exception as e:
            logger.error("Cycle %s failed: %s", cycle_type.value, e)
            return False

        cycle = self.cycles[cycle_type]
        cycle.last_run = time.time() * 1000
        cycle.run_count += 1
        return True

    async def run_all(self, callbacks: dict[CycleType, Callable]) -> dict[CycleType, bool]:
        """Run all eligible cycles with their callbacks.

        Args:
            callbacks: Mapping of cycle type to async callback.

        Returns:
            Mapping of cycle type to whether it was executed.
        """
        results: dict[CycleType, bool] = {}
        for cycle_type in CycleType:
            callback = callbacks.get(cycle_type)
            if callback:
                results[cycle_type] = await self.run_cycle(cycle_type, callback)
            else:
                results[cycle_type] = False
        return results

    def force_run(self, cycle_type: CycleType) -> None:
        """Force a cycle to be eligible for running (reset last_run)."""
        self.cycles[cycle_type].last_run = None

    def get_status(self) -> dict:
        """Get scheduler status."""
        return {
            "cycles": {
                ct.value: {
                    "run_count": cs.run_count,
                    "last_run": cs.last_run,
                    "should_run": self.should_run(ct),
                    "interval_ms": cs.interval_ms,
                }
                for ct, cs in self.cycles.items()
            },
        }

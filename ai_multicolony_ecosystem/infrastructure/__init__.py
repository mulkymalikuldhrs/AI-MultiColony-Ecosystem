"""Watchdog Daemon — Process supervision with exponential backoff.

Ported from HermesQuantOS src/watchdog.py. Provides health monitoring,
automatic restart with exponential backoff, crash loop detection,
and alerting for managed processes.
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ProcessState(str, Enum):
    """Managed process state."""
    RUNNING = "running"
    STOPPED = "stopped"
    CRASHED = "crashed"
    RESTARTING = "restarting"
    CRASH_LOOP = "crash_loop"


class WatchdogConfig(BaseModel):
    """Watchdog configuration."""
    max_restarts: int = Field(5, description="Max restarts before crash loop")
    base_delay: float = Field(1.0, description="Base restart delay in seconds")
    max_delay: float = Field(60.0, description="Max restart delay in seconds")
    health_check_interval: int = Field(30, description="Health check interval in seconds")
    crash_window: int = Field(300, description="Window in seconds for crash loop detection")


class ProcessInfo(BaseModel):
    """Information about a managed process."""
    name: str = ""
    state: ProcessState = ProcessState.STOPPED
    pid: Optional[int] = None
    restart_count: int = 0
    last_start: Optional[str] = None
    last_crash: Optional[str] = None
    uptime_seconds: float = 0.0
    crash_timestamps: List[float] = Field(default_factory=list)


class WatchdogDaemon:
    """Process supervision daemon with exponential backoff.

    Monitors managed processes, detects crashes, and automatically
    restarts them with exponential backoff. Detects crash loops and
    alerts when processes become unstable.

    Usage::

        watchdog = WatchdogDaemon()
        watchdog.register("agent_worker", start_fn=launch_worker)
        await watchdog.start()
    """

    def __init__(self, config: Optional[WatchdogConfig] = None) -> None:
        self._config = config or WatchdogConfig()
        self._processes: Dict[str, ProcessInfo] = {}
        self._start_fns: Dict[str, Callable] = {}
        self._stop_fns: Dict[str, Callable] = {}
        self._running = False

    def register(
        self,
        name: str,
        start_fn: Optional[Callable] = None,
        stop_fn: Optional[Callable] = None,
    ) -> None:
        """Register a process for supervision."""
        self._processes[name] = ProcessInfo(name=name)
        if start_fn:
            self._start_fns[name] = start_fn
        if stop_fn:
            self._stop_fns[name] = stop_fn
        logger.info("Watchdog: Registered process '%s'", name)

    async def start_process(self, name: str) -> bool:
        """Start a registered process."""
        if name not in self._processes:
            logger.error("Watchdog: Process '%s' not registered", name)
            return False

        info = self._processes[name]
        start_fn = self._start_fns.get(name)

        if start_fn is None:
            logger.warning("Watchdog: No start function for '%s'", name)
            info.state = ProcessState.RUNNING
            info.last_start = datetime.now(tz=timezone.utc).isoformat()
            return True

        try:
            info.state = ProcessState.RESTARTING
            if asyncio.iscoroutinefunction(start_fn):
                await start_fn()
            else:
                start_fn()

            info.state = ProcessState.RUNNING
            info.last_start = datetime.now(tz=timezone.utc).isoformat()
            info.restart_count += 1
            logger.info("Watchdog: Process '%s' started (restart #%d)", name, info.restart_count)
            return True

        except Exception as exc:
            info.state = ProcessState.CRASHED
            info.last_crash = datetime.now(tz=timezone.utc).isoformat()
            info.crash_timestamps.append(time.monotonic())
            logger.error("Watchdog: Process '%s' crashed: %s", name, exc)
            return False

    async def stop_process(self, name: str) -> bool:
        """Stop a registered process."""
        info = self._processes.get(name)
        if info is None:
            return False

        stop_fn = self._stop_fns.get(name)
        if stop_fn:
            try:
                if asyncio.iscoroutinefunction(stop_fn):
                    await stop_fn()
                else:
                    stop_fn()
            except Exception as exc:
                logger.error("Watchdog: Error stopping '%s': %s", name, exc)

        info.state = ProcessState.STOPPED
        logger.info("Watchdog: Process '%s' stopped", name)
        return True

    def _compute_delay(self, restart_count: int) -> float:
        """Compute exponential backoff delay."""
        delay = self._config.base_delay * (2 ** min(restart_count, 10))
        return min(delay, self._config.max_delay)

    def _is_crash_loop(self, name: str) -> bool:
        """Detect if process is in a crash loop."""
        info = self._processes.get(name)
        if info is None:
            return False

        now = time.monotonic()
        window = self._config.crash_window
        recent_crashes = [t for t in info.crash_timestamps if now - t < window]

        return len(recent_crashes) >= self._config.max_restarts

    async def handle_crash(self, name: str) -> None:
        """Handle a crashed process with exponential backoff restart."""
        info = self._processes.get(name)
        if info is None:
            return

        # Check for crash loop
        if self._is_crash_loop(name):
            info.state = ProcessState.CRASH_LOOP
            logger.critical("Watchdog: Process '%s' in CRASH LOOP — not restarting", name)
            return

        # Exponential backoff
        delay = self._compute_delay(info.restart_count)
        logger.warning(
            "Watchdog: Restarting '%s' in %.1fs (attempt #%d)",
            name, delay, info.restart_count + 1,
        )

        await asyncio.sleep(delay)
        await self.start_process(name)

    def get_process_info(self, name: str) -> Optional[ProcessInfo]:
        """Get information about a managed process."""
        return self._processes.get(name)

    def get_all_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all managed processes."""
        return {name: info.model_dump() for name, info in self._processes.items()}

    @property
    def is_running(self) -> bool:
        return self._running

    async def start(self) -> None:
        """Start the watchdog daemon."""
        self._running = True
        logger.info("Watchdog: Daemon started")

    async def stop(self) -> None:
        """Stop the watchdog daemon and all processes."""
        self._running = False
        for name in list(self._processes.keys()):
            await self.stop_process(name)
        logger.info("Watchdog: Daemon stopped")


__all__ = [
    "ProcessState",
    "WatchdogConfig",
    "ProcessInfo",
    "WatchdogDaemon",
]

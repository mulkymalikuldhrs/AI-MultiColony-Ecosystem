"""
Crucix API Gateway — intelligence data serving patterns.

Port of server.mjs gateway patterns to Python. This module provides
the intelligence-specific gateway layer (SSE, sweep triggers, health),
while the general gateway functionality is already covered by src/gateway/.

Key responsibilities:
- Serve intelligence sweep data via REST API
- Server-Sent Events (SSE) for live dashboard updates
- Sweep cycle orchestration (trigger, schedule)
- Health and status endpoints

Note: General API gateway (routing, auth, CSRF, etc.) is handled by
src/gateway/. This module adds only Crucix-specific intelligence patterns.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger("crucix.gateway")


# ── Models ────────────────────────────────────────────────────────────


class SweepStatus(str, Enum):
    """Status of a sweep cycle."""

    IDLE = "idle"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = "ok"
    uptime_seconds: int = 0
    last_sweep: Optional[str] = None
    next_sweep: Optional[str] = None
    sweep_in_progress: bool = False
    sources_ok: int = 0
    sources_failed: int = 0
    llm_enabled: bool = False
    llm_provider: Optional[str] = None
    language: str = "en"


class SweeepEvent(BaseModel):
    """SSE event for dashboard updates."""

    type: str  # "sweep_start" | "update" | "sweep_error" | "connected"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    data: Any = None
    error: Optional[str] = None


class BriefingSaveResult(BaseModel):
    """Result of saving a briefing to disk."""

    path: str
    timestamp: str
    size_bytes: int


# ── Sweep Orchestrator ────────────────────────────────────────────────


class SweepOrchestrator:
    """Orchestrates intelligence sweep cycles.

    Manages sweep state, timing, and SSE broadcasting.
    This is the Python equivalent of the sweep logic in server.mjs.
    """

    def __init__(self, refresh_interval_minutes: int = 15) -> None:
        self.refresh_interval_minutes = refresh_interval_minutes
        self._status: SweepStatus = SweepStatus.IDLE
        self._last_sweep_time: Optional[datetime] = None
        self._sweep_started_at: Optional[datetime] = None
        self._start_time = time.monotonic()
        self._current_data: Optional[dict[str, Any]] = None
        self._sse_clients: list[Any] = []  # In production, these would be Starlette/FastAPI response objects
        self._log = structlog.get_logger("crucix.gateway.orchestrator")

    @property
    def status(self) -> SweepStatus:
        return self._status

    @property
    def last_sweep_time(self) -> Optional[datetime]:
        return self._last_sweep_time

    @property
    def sweep_in_progress(self) -> bool:
        return self._status == SweepStatus.IN_PROGRESS

    @property
    def uptime_seconds(self) -> int:
        return int(time.monotonic() - self._start_time)

    @property
    def current_data(self) -> Optional[dict[str, Any]]:
        return self._current_data

    @property
    def next_sweep_time(self) -> Optional[datetime]:
        if self._last_sweep_time is None:
            return None
        from datetime import timedelta
        return self._last_sweep_time + timedelta(minutes=self.refresh_interval_minutes)

    def start_sweep(self) -> None:
        """Mark sweep as in progress."""
        if self._status == SweepStatus.IN_PROGRESS:
            self._log.warning("sweep_already_in_progress")
            return
        self._status = SweepStatus.IN_PROGRESS
        self._sweep_started_at = datetime.now(timezone.utc)
        self._log.info("sweep_started", timestamp=self._sweep_started_at.isoformat())

    def complete_sweep(self, data: dict[str, Any]) -> None:
        """Mark sweep as completed and store results."""
        self._status = SweepStatus.COMPLETED
        self._last_sweep_time = datetime.now(timezone.utc)
        self._current_data = data
        self._log.info(
            "sweep_completed",
            timestamp=self._last_sweep_time.isoformat(),
            sources_ok=data.get("meta", {}).get("sourcesOk", 0),
        )

    def fail_sweep(self, error: str) -> None:
        """Mark sweep as failed."""
        self._status = SweepStatus.FAILED
        self._log.error("sweep_failed", error=error)

    def get_health(self, llm_provider: str | None = None, language: str = "en") -> HealthResponse:
        """Generate a health check response."""
        meta = self._current_data.get("meta", {}) if self._current_data else {}
        return HealthResponse(
            uptime_seconds=self.uptime_seconds,
            last_sweep=self._last_sweep_time.isoformat() if self._last_sweep_time else None,
            next_sweep=self.next_sweep_time.isoformat() if self.next_sweep_time else None,
            sweep_in_progress=self.sweep_in_progress,
            sources_ok=meta.get("sourcesOk", 0),
            sources_failed=meta.get("sourcesFailed", 0),
            llm_enabled=bool(llm_provider),
            llm_provider=llm_provider,
            language=language,
        )

    def add_sse_client(self, client: Any) -> None:
        """Register an SSE client for live updates."""
        self._sse_clients.append(client)

    def remove_sse_client(self, client: Any) -> None:
        """Remove an SSE client."""
        if client in self._sse_clients:
            self._sse_clients.remove(client)

    def broadcast(self, event: SweeepEvent) -> int:
        """Broadcast an SSE event to all connected clients.

        Returns the number of clients that received the event.
        In production, this would write to the actual SSE response objects.
        """
        sent = 0
        dead_clients = []
        for client in self._sse_clients:
            try:
                # In production: await client.send(event.model_dump_json())
                sent += 1
            except Exception:
                dead_clients.append(client)
        for c in dead_clients:
            self.remove_sse_client(c)
        return sent

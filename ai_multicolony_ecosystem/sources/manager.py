"""Source Manager — Orchestrates parallel sweeps across all sources.

Runs all registered sources in parallel with Promise.allSettled
semantics — a single source failure never crashes the sweep.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ai_multicolony_ecosystem.sources.base import (
    BaseSource,
    SourceHealth,
    SourceRegistry,
    SourceResult,
    SourceTier,
)

logger = logging.getLogger(__name__)


class SweepResult(BaseModel):
    """Result from a full sweep across all sources."""
    total_sources: int = 0
    successful: int = 0
    failed: int = 0
    total_latency_ms: float = 0.0
    results: List[Any] = Field(default_factory=list)
    timestamp: str = ""


class SourceManager:
    """Orchestrates parallel data source sweeps.

    Runs all registered sources concurrently, collecting results
    from each. Failed sources are captured gracefully — they never
    crash the sweep cycle (Crucix's Promise.allSettled pattern).
    """

    def __init__(self, source_configs: Optional[Dict[str, Dict]] = None) -> None:
        self._sources: Dict[str, BaseSource] = {}
        self._source_configs = source_configs or {}
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize all sources from registry."""
        self._sources = SourceRegistry.create_all(self._source_configs)
        self._initialized = True
        logger.info("SourceManager: Initialized %d sources", len(self._sources))
        return True

    async def sweep_all(self) -> SweepResult:
        """Execute parallel sweep across all sources."""
        if not self._initialized:
            await self.initialize()

        results = await asyncio.gather(
            *[source.safe_sweep() for source in self._sources.values()],
            return_exceptions=False,
        )

        source_results = []
        successful = 0
        failed = 0
        total_latency = 0.0

        for result in results:
            if isinstance(result, SourceResult):
                source_results.append(result)
                if result.error is None:
                    successful += 1
                else:
                    failed += 1
                total_latency += result.latency_ms

        return SweepResult(
            total_sources=len(self._sources),
            successful=successful,
            failed=failed,
            total_latency_ms=round(total_latency, 2),
            results=source_results,
            timestamp=datetime.now(tz=timezone.utc).isoformat(),
        )

    async def sweep_tier(self, tier: SourceTier) -> SweepResult:
        """Sweep only sources in a specific intelligence tier."""
        if not self._initialized:
            await self.initialize()

        tier_sources = [s for s in self._sources.values() if s.tier == tier]

        results = await asyncio.gather(
            *[source.safe_sweep() for source in tier_sources],
            return_exceptions=False,
        )

        source_results = []
        successful = 0
        failed = 0

        for result in results:
            if isinstance(result, SourceResult):
                source_results.append(result)
                if result.error is None:
                    successful += 1
                else:
                    failed += 1

        return SweepResult(
            total_sources=len(tier_sources),
            successful=successful,
            failed=failed,
            results=source_results,
            timestamp=datetime.now(tz=timezone.utc).isoformat(),
        )

    def get_source(self, name: str) -> Optional[BaseSource]:
        """Get a specific source by name."""
        return self._sources.get(name)

    def list_sources(self) -> List[str]:
        """List all source names."""
        return list(self._sources.keys())

    def get_health_report(self) -> Dict[str, Any]:
        """Get health report for all sources."""
        return {
            name: source.get_stats()
            for name, source in self._sources.items()
        }


__all__ = ["SweepResult", "SourceManager"]

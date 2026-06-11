"""Base Source Interface — Abstract data source with health monitoring.

Defines the contract all intelligence data sources must implement,
with rate limiting, caching, health checks, and error handling.
"""

from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SourceTier(str, Enum):
    """Intelligence tier classification."""
    OSINT = "osint"
    ECONOMIC = "economic"
    WEATHER = "weather"
    SPACE = "space"
    MARKET = "market"
    CYBER = "cyber"


class SourceHealth(str, Enum):
    """Source health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


class SourceResult(BaseModel):
    """Result from a data source sweep."""
    source: str = Field(..., description="Source name")
    tier: SourceTier = Field(SourceTier.OSINT, description="Intelligence tier")
    data: Any = None
    error: Optional[str] = None
    latency_ms: float = 0.0
    timestamp: str = Field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseSource(ABC):
    """Abstract base class for all intelligence data sources.

    Each source must implement the sweep() method. The base class
    provides rate limiting, timeout, health tracking, and error handling.

    Ported from Crucix's runSource() pattern with Promise.allSettled
    semantics — sources never crash the sweep cycle.
    """

    name: str = "base_source"
    tier: SourceTier = SourceTier.OSINT
    timeout_seconds: int = 30
    rate_limit: int = 1  # requests per second

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = config or {}
        self._health = SourceHealth.UNKNOWN
        self._last_sweep: Optional[datetime] = None
        self._error_count = 0
        self._success_count = 0
        self._call_timestamps: List[float] = []
        self._lock = asyncio.Lock()

    @property
    def health(self) -> SourceHealth:
        return self._health

    @abstractmethod
    async def sweep(self) -> SourceResult:
        """Execute a data sweep. Must return SourceResult."""
        ...

    async def safe_sweep(self) -> SourceResult:
        """Execute sweep with timeout, rate limiting, and error handling.

        Guarantees a SourceResult is always returned — never raises.
        This mirrors Crucix's Promise.allSettled pattern.
        """
        start = time.monotonic()

        # Rate limiting
        async with self._lock:
            now = time.monotonic()
            self._call_timestamps = [t for t in self._call_timestamps if now - t < 1.0]
            if len(self._call_timestamps) >= self.rate_limit:
                wait = 1.0 - (now - self._call_timestamps[0])
                if wait > 0:
                    await asyncio.sleep(wait)
            self._call_timestamps.append(time.monotonic())

        try:
            result = await asyncio.wait_for(
                self.sweep(),
                timeout=self.timeout_seconds,
            )
            latency = (time.monotonic() - start) * 1000
            result.latency_ms = round(latency, 2)

            self._health = SourceHealth.HEALTHY
            self._success_count += 1
            self._last_sweep = datetime.now(tz=timezone.utc)

            return result

        except asyncio.TimeoutError:
            latency = (time.monotonic() - start) * 1000
            self._error_count += 1
            self._health = SourceHealth.DEGRADED
            logger.warning("Source %s timed out after %ds", self.name, self.timeout_seconds)

            return SourceResult(
                source=self.name,
                tier=self.tier,
                error=f"Timeout after {self.timeout_seconds}s",
                latency_ms=round(latency, 2),
            )

        except Exception as exc:
            latency = (time.monotonic() - start) * 1000
            self._error_count += 1
            self._health = SourceHealth.DOWN
            logger.error("Source %s error: %s", self.name, exc)

            return SourceResult(
                source=self.name,
                tier=self.tier,
                error=str(exc),
                latency_ms=round(latency, 2),
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get source statistics."""
        return {
            "name": self.name,
            "tier": self.tier.value,
            "health": self._health.value,
            "success_count": self._success_count,
            "error_count": self._error_count,
            "last_sweep": self._last_sweep.isoformat() if self._last_sweep else None,
        }


# Source Registry
_source_registry: Dict[str, type[BaseSource]] = {}


class SourceRegistry:
    """Registry for data source implementations."""

    @classmethod
    def register(cls, source_class: type[BaseSource]) -> type[BaseSource]:
        _source_registry[source_class.name] = source_class
        return source_class

    @classmethod
    def get(cls, name: str) -> Optional[type[BaseSource]]:
        return _source_registry.get(name)

    @classmethod
    def list_sources(cls) -> List[str]:
        return list(_source_registry.keys())

    @classmethod
    def create(cls, name: str, config: Optional[Dict] = None) -> Optional[BaseSource]:
        source_class = _source_registry.get(name)
        if source_class is None:
            return None
        return source_class(config=config)

    @classmethod
    def create_all(cls, configs: Optional[Dict[str, Dict]] = None) -> Dict[str, BaseSource]:
        configs = configs or {}
        sources = {}
        for name in _source_registry:
            source = cls.create(name, config=configs.get(name))
            if source is not None:
                sources[name] = source
        return sources

    @classmethod
    def count(cls) -> int:
        return len(_source_registry)


__all__ = [
    "SourceTier",
    "SourceHealth",
    "SourceResult",
    "BaseSource",
    "SourceRegistry",
]

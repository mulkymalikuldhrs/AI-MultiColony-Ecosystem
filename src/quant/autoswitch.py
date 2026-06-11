"""
AutoSwitch LLM Provider - Health-monitored API failover with exponential backoff.
Tracks success/failure per provider, auto-cooldown on errors.

Source: HermesQuantOS + Quant-Nanggroe-AI
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.quant.autoswitch")


class ProviderHealth(BaseModel):
    """Track health of a single LLM provider."""
    name: str
    success_count: int = 0
    failure_count: int = 0
    last_success: str | None = None
    last_failure: str | None = None
    cooldown_until: str | None = None
    avg_latency_ms: float = 0.0

    @property
    def score(self) -> float:
        """Health score: higher = better."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.5
        success_rate = self.success_count / total
        latency_penalty = min(self.avg_latency_ms / 10000, 0.2)
        return success_rate - latency_penalty

    @property
    def is_available(self) -> bool:
        """Check if provider is off cooldown."""
        if self.cooldown_until:
            return datetime.now() >= datetime.fromisoformat(self.cooldown_until)
        return True


class AutoSwitchEngine:
    """Intelligent LLM provider failover system."""

    def __init__(self) -> None:
        self.providers: dict[str, ProviderHealth] = {}
        self.request_log: list[dict] = []

    def register_provider(self, name: str) -> None:
        """Register a provider for health tracking."""
        if name not in self.providers:
            self.providers[name] = ProviderHealth(name=name)
            logger.info("AutoSwitch: Registered provider %s", name)

    def get_provider_order(self) -> list[str]:
        """Get providers sorted by health score (best first), excluding cooldown."""
        available = [(name, ph) for name, ph in self.providers.items() if ph.is_available]
        sorted_providers = sorted(
            available,
            key=lambda x: (x[1].score, x[1].success_count),
            reverse=True,
        )
        return [name for name, _ in sorted_providers]

    def record_success(self, provider_name: str, latency_ms: float) -> None:
        """Record successful API call."""
        if provider_name not in self.providers:
            self.register_provider(provider_name)

        ph = self.providers[provider_name]
        ph.success_count += 1
        ph.last_success = datetime.now().isoformat()
        # Update average latency (keep last 20)
        old_avg = ph.avg_latency_ms
        total = ph.success_count + ph.failure_count
        ph.avg_latency_ms = (old_avg * (total - 1) + latency_ms) / total if total > 0 else latency_ms
        ph.cooldown_until = None

        self.request_log.append({
            "provider": provider_name,
            "status": "success",
            "latency_ms": round(latency_ms, 0),
            "timestamp": datetime.now().isoformat(),
        })

    def record_failure(self, provider_name: str, error: str = "", status_code: int | None = None) -> None:
        """Record failed API call."""
        if provider_name not in self.providers:
            self.register_provider(provider_name)

        ph = self.providers[provider_name]
        ph.failure_count += 1
        ph.last_failure = datetime.now().isoformat()

        # Proactive cooldown after consecutive failures
        if ph.failure_count > 5 and ph.success_count < ph.failure_count:
            cooldown_minutes = min(2 ** (ph.failure_count - 5), 30)
            ph.cooldown_until = (datetime.now() + timedelta(minutes=cooldown_minutes)).isoformat()
            logger.warning("Provider %s cooldown for %dmin", provider_name, cooldown_minutes)

        # Extra cooldown on rate limits
        if status_code == 429:
            ph.cooldown_until = (datetime.now() + timedelta(minutes=5)).isoformat()
            logger.warning("Rate limit on %s, 5min cooldown", provider_name)

        self.request_log.append({
            "provider": provider_name,
            "status": "failure",
            "error": error[:200],
            "status_code": status_code,
            "timestamp": datetime.now().isoformat(),
        })

        if len(self.request_log) > 1000:
            self.request_log = self.request_log[-500:]

    def get_status(self) -> dict:
        """Get AutoSwitch status report."""
        return {
            "providers": {
                name: {
                    "name": ph.name,
                    "score": round(ph.score, 3),
                    "success": ph.success_count,
                    "failure": ph.failure_count,
                    "avg_latency_ms": round(ph.avg_latency_ms, 0),
                    "available": ph.is_available,
                    "cooldown_until": ph.cooldown_until,
                }
                for name, ph in self.providers.items()
            },
            "provider_order": self.get_provider_order(),
            "total_requests": len(self.request_log),
            "recent_errors": [r for r in self.request_log[-20:] if r["status"] == "failure"],
        }

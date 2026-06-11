"""Delta Engine — Change detection with configurable thresholds.

Ported from Crucix lib/delta/engine.mjs. Detects significant
changes between sweeps and classifies risk direction.

Features:
- Numeric percentage change detection
- Count change detection
- Semantic hashing for dedup
- Risk direction classification (risk-on/risk-off/mixed)
- Alert cooldown with decay tiers
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RiskDirection(str, Enum):
    """Risk direction classification."""
    RISK_ON = "risk_on"
    RISK_OFF = "risk_off"
    MIXED = "mixed"
    NEUTRAL = "neutral"


class DeltaSeverity(str, Enum):
    """Delta severity level."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DeltaAlert(BaseModel):
    """A detected change alert."""
    source: str = ""
    field: str = ""
    previous_value: Any = None
    current_value: Any = None
    change_pct: float = 0.0
    severity: DeltaSeverity = DeltaSeverity.LOW
    risk_direction: RiskDirection = RiskDirection.NEUTRAL
    timestamp: str = Field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())
    dedup_hash: str = ""


class DeltaConfig(BaseModel):
    """Configuration for delta detection thresholds."""
    numeric_threshold_pct: float = Field(1.0, description="Min % change to alert")
    count_threshold: int = Field(5, description="Min count change to alert")
    cooldown_tiers: Dict[str, int] = Field(
        default_factory=lambda: {"low": 21600, "medium": 43200, "high": 86400},
        description="Cooldown seconds per severity tier",
    )


# Risk-off indicators (higher = risk-off)
RISK_OFF_INDICATORS = {
    "vix", "yield_spread_10y2y", "unemployment", "cpi",
    "conflict", "sanctions", "outbreaks",
}

# Risk-on indicators (higher = risk-on)
RISK_ON_INDICATORS = {
    "sp500", "btc", "gold", "federal_funds_rate",
    "employment", "gdp",
}


class DeltaEngine:
    """Change detection engine with configurable thresholds.

    Detects significant changes between sweep results, deduplicates
    alerts with semantic hashing, and classifies risk direction.

    Usage::

        engine = DeltaEngine()
        engine.update_previous(sweep_results)
        alerts = engine.compute_deltas(current_sweep_results)
    """

    def __init__(self, config: Optional[DeltaConfig] = None) -> None:
        self._config = config or DeltaConfig()
        self._previous: Dict[str, Any] = {}
        self._alert_history: Dict[str, str] = {}  # hash -> timestamp
        self._cooldown_active: Dict[str, datetime] = {}

    def set_previous(self, data: Dict[str, Any]) -> None:
        """Set the baseline data for comparison."""
        self._previous = data

    def _compute_dedup_hash(self, source: str, field: str, change_pct: float) -> str:
        """Compute semantic hash for deduplication."""
        # Round to 1 decimal for dedup
        rounded = round(change_pct, 1)
        raw = f"{source}:{field}:{rounded}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]

    def _classify_severity(self, change_pct: float) -> DeltaSeverity:
        """Classify delta severity based on magnitude."""
        abs_change = abs(change_pct)
        if abs_change >= 10:
            return DeltaSeverity.CRITICAL
        elif abs_change >= 5:
            return DeltaSeverity.HIGH
        elif abs_change >= 2:
            return DeltaSeverity.MEDIUM
        return DeltaSeverity.LOW

    def _classify_risk_direction(self, field: str, change_pct: float) -> RiskDirection:
        """Classify risk direction based on indicator and change."""
        field_lower = field.lower()

        if field_lower in RISK_OFF_INDICATORS:
            return RiskDirection.RISK_OFF if change_pct > 0 else RiskDirection.RISK_ON
        elif field_lower in RISK_ON_INDICATORS:
            return RiskDirection.RISK_ON if change_pct > 0 else RiskDirection.RISK_OFF

        return RiskDirection.NEUTRAL

    def _is_cooled_down(self, dedup_hash: str, severity: DeltaSeverity) -> bool:
        """Check if alert has cooled down (not re-alerting too frequently)."""
        if dedup_hash not in self._cooldown_active:
            return True

        now = datetime.now(tz=timezone.utc)
        last_alert = self._cooldown_active[dedup_hash]
        cooldown_seconds = self._config.cooldown_tiers.get(severity.value, 43200)
        elapsed = (now - last_alert).total_seconds()

        return elapsed >= cooldown_seconds

    def compute_deltas(self, current: Dict[str, Any]) -> List[DeltaAlert]:
        """Compute deltas between previous and current sweep data.

        Args:
            current: Current sweep result data.

        Returns:
            List of DeltaAlert for significant changes.
        """
        if not self._previous:
            self._previous = current
            return []

        alerts = []
        threshold = self._config.numeric_threshold_pct

        for source_name, source_data in current.items():
            if not isinstance(source_data, dict):
                continue

            prev_source = self._previous.get(source_name, {})
            if not isinstance(prev_source, dict):
                continue

            for field, current_val in source_data.items():
                if not isinstance(current_val, (int, float)):
                    continue

                prev_val = prev_source.get(field)
                if prev_val is None or not isinstance(prev_val, (int, float)) or prev_val == 0:
                    continue

                change_pct = ((current_val - prev_val) / abs(prev_val)) * 100

                if abs(change_pct) >= threshold:
                    dedup_hash = self._compute_dedup_hash(source_name, field, change_pct)
                    severity = self._classify_severity(change_pct)
                    risk_direction = self._classify_risk_direction(field, change_pct)

                    if self._is_cooled_down(dedup_hash, severity):
                        alert = DeltaAlert(
                            source=source_name,
                            field=field,
                            previous_value=prev_val,
                            current_value=current_val,
                            change_pct=round(change_pct, 2),
                            severity=severity,
                            risk_direction=risk_direction,
                            dedup_hash=dedup_hash,
                        )
                        alerts.append(alert)
                        self._cooldown_active[dedup_hash] = datetime.now(tz=timezone.utc)

        # Update previous for next comparison
        self._previous = current
        return alerts

    def compute_risk_direction(self, alerts: List[DeltaAlert]) -> RiskDirection:
        """Compute overall risk direction from all alerts."""
        if not alerts:
            return RiskDirection.NEUTRAL

        risk_on_score = sum(1 for a in alerts if a.risk_direction == RiskDirection.RISK_ON)
        risk_off_score = sum(1 for a in alerts if a.risk_direction == RiskDirection.RISK_OFF)

        if risk_on_score > risk_off_score * 1.5:
            return RiskDirection.RISK_ON
        elif risk_off_score > risk_on_score * 1.5:
            return RiskDirection.RISK_OFF
        else:
            return RiskDirection.MIXED

    def get_stats(self) -> Dict[str, Any]:
        """Get delta engine statistics."""
        return {
            "previous_sources": len(self._previous),
            "active_cooldowns": len(self._cooldown_active),
            "threshold_pct": self._config.numeric_threshold_pct,
        }


__all__ = [
    "RiskDirection",
    "DeltaSeverity",
    "DeltaAlert",
    "DeltaConfig",
    "DeltaEngine",
]

"""Regime Detection Types — Enumerations and data models for market regime detection."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Tuple

from pydantic import BaseModel, Field, field_validator


class RegimeType(str, Enum):
    """Market regime classification.

    Based on research in hidden Markov models for financial regimes
    (e.g., Hamilton 1989, Ryden et al. 1998) extended with crisis
    and recovery states for modern market microstructure.
    """

    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    CRISIS = "crisis"
    RECOVERY = "recovery"


class RegimeResult(BaseModel):
    """Result of a regime detection analysis.

    Contains the current regime classification, confidence score,
    historical regime assignments, transition probabilities, and
    detection metadata.
    """

    current_regime: RegimeType
    confidence: float = Field(ge=-1.0, le=2.0)
    regime_history: List[Tuple[str, RegimeType]] = Field(default_factory=list)
    transition_probs: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    detected_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("confidence")
    @classmethod
    def _clamp_confidence(cls, v: float) -> float:
        """Ensure confidence is in [0.0, 1.0]."""
        return max(0.0, min(1.0, v))


__all__ = ["RegimeType", "RegimeResult"]

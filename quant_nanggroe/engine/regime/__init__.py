"""Regime Detection Module — market regime detection and strategy adaptation.

This module provides:
  - RegimeType: Enum of market regimes (BULL, BEAR, SIDEWAYS, CRISIS, RECOVERY)
  - RegimeResult: Data model for detection results
  - RegimeDetector: HMM-based and statistical fallback regime detection
  - RegimeAwareStrategyAdapter: Strategy wrapper that adjusts behavior by regime
"""

from quant_nanggroe.engine.regime.adapter import (
    BLOCKED_STRATEGIES,
    DEFAULT_PARAM_OVERRIDES,
    REGIME_SIZE_MULTIPLIER,
    RegimeAwareStrategyAdapter,
)
from quant_nanggroe.engine.regime.detector import RegimeDetector
from quant_nanggroe.engine.regime.types import RegimeResult, RegimeType

__all__ = [
    "RegimeType",
    "RegimeResult",
    "RegimeDetector",
    "RegimeAwareStrategyAdapter",
    "REGIME_SIZE_MULTIPLIER",
    "BLOCKED_STRATEGIES",
    "DEFAULT_PARAM_OVERRIDES",
]

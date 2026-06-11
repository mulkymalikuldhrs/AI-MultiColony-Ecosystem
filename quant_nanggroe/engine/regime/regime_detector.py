"""Regime Detector — Bridge module for regime detection.

Provides the RegimeDetector class used by the trading graph,
wrapping the core detection logic from quant_nanggroe.engine.regime.detector.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from quant_nanggroe.engine.regime.detector import RegimeDetector as _CoreDetector
from quant_nanggroe.engine.regime.types import RegimeType

logger = logging.getLogger(__name__)


class RegimeDetector:
    """High-level regime detector for the trading graph.

    Wraps the core RegimeDetector with a simplified interface
    for use in the LangGraph pipeline.
    """

    def __init__(self, lookback: int = 252) -> None:
        self._detector = _CoreDetector(lookback=lookback)

    def detect(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect the current market regime.

        Args:
            df: DataFrame with OHLCV data.

        Returns:
            Dict with regime type, confidence, and details.
        """
        try:
            result = self._detector.detect(df)
            return result
        except Exception as e:
            logger.warning("Regime detection failed: %s", e)
            return {
                "regime": RegimeType.RANGING.value,
                "confidence": 0.0,
                "error": str(e),
            }


__all__ = ["RegimeDetector"]

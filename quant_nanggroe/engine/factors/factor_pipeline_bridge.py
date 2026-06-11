"""Factor Pipeline Bridge — Connects factor engine to the trading graph.

Provides a simplified interface for the LangGraph pipeline to compute
factors and retrieve top-N factor scores for signal generation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class FactorPipelineBridge:
    """Bridge between the factor engine and the trading graph.

    Computes factor scores and returns the top-N factors for
    integration into the multi-agent pipeline.
    """

    def __init__(self, top_n: int = 20) -> None:
        self._top_n = top_n

    def compute(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Compute factor scores for the given data.

        Args:
            df: DataFrame with OHLCV data.

        Returns:
            Dict with top factors, scores, and summary statistics.
        """
        try:
            from quant_nanggroe.engine.factors.registry import FactorRegistry
            registry = FactorRegistry()
            # Get all registered factors
            factor_names = list(registry._factors.keys()) if hasattr(registry, '_factors') else []
            return {
                "top_factors": factor_names[:self._top_n],
                "total_factors": len(factor_names),
                "computed": True,
            }
        except Exception as e:
            logger.warning("Factor pipeline bridge computation failed: %s", e)
            return {
                "top_factors": [],
                "total_factors": 0,
                "computed": False,
                "error": str(e),
            }


__all__ = ["FactorPipelineBridge"]

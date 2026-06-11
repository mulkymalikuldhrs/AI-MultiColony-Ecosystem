"""
Pressure Normalization Engine - Converts all sensor/agent outputs to BUY/SELL pressure (0-1).

Source: HermesQuantOS + Quant-Nanggroe-AI
"""

from __future__ import annotations

import logging
from datetime import datetime

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.quant.pressure_engine")


class PressureResult(BaseModel):
    """Result of pressure normalization."""
    buy_pressure: float
    sell_pressure: float
    confidence: float
    verdict: str  # STRONG_BUY, BUY, STRONG_SELL, SELL, NEUTRAL
    raw_buy: float
    raw_sell: float
    sensor_inputs: dict = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class PressureNormalizationEngine:
    """Compiles all sensor outputs into normalized pressure vectors."""

    SENSOR_WEIGHTS: dict[str, float] = {
        "quant_scanner": 0.30,
        "smc_agent": 0.25,
        "news_sentinel": 0.20,
        "flow_agent": 0.25,
    }

    def __init__(self) -> None:
        self.buy_pressure = 0.0
        self.sell_pressure = 0.0
        self.confidence = 0.0
        self._last_result: PressureResult | None = None

    def compile_pressure(
        self,
        trend_direction: str = "neutral",
        trend_strength: float = 0.0,
        smc_signal: str = "none",
        displacement_strength: float = 0.0,
        liquidity_sweep: bool = False,
        news_impact: float = 0.0,
        news_uncertainty: float = 0.5,
        flow_imbalance: float = 0.0,
        flow_direction: str = "neutral",
    ) -> PressureResult:
        """Compile all sensor outputs into normalized pressure vectors."""
        buy = 0.0
        sell = 0.0

        # Quant Scanner contribution
        weight = self.SENSOR_WEIGHTS["quant_scanner"]
        if trend_direction == "bullish":
            buy += weight * trend_strength
        elif trend_direction == "bearish":
            sell += weight * trend_strength

        # SMC Agent contribution
        weight = self.SENSOR_WEIGHTS["smc_agent"]
        if smc_signal in ("bullish_bos", "bullish_choch"):
            buy += weight * displacement_strength
        elif smc_signal in ("bearish_bos", "bearish_choch"):
            sell += weight * displacement_strength

        if liquidity_sweep:
            buy += weight * 0.2 * displacement_strength
            sell += weight * 0.2 * displacement_strength

        # News Sentinel contribution
        weight = self.SENSOR_WEIGHTS["news_sentinel"]
        directional_factor = 1.0 - news_uncertainty
        buy += weight * news_impact * directional_factor
        sell += weight * news_impact * news_uncertainty

        # Flow Agent contribution
        weight = self.SENSOR_WEIGHTS["flow_agent"]
        if flow_direction == "long":
            buy += weight * flow_imbalance
        elif flow_direction == "short":
            sell += weight * flow_imbalance

        # Normalize
        total = buy + sell
        if total > 0:
            self.buy_pressure = buy / total
            self.sell_pressure = sell / total
            self.confidence = max(buy, sell) / total
        else:
            self.buy_pressure = 0.0
            self.sell_pressure = 0.0
            self.confidence = 0.0

        # Verdict
        if self.buy_pressure > 0.7:
            verdict = "STRONG_BUY"
        elif self.buy_pressure > 0.55:
            verdict = "BUY"
        elif self.sell_pressure > 0.7:
            verdict = "STRONG_SELL"
        elif self.sell_pressure > 0.55:
            verdict = "SELL"
        else:
            verdict = "NEUTRAL"

        result = PressureResult(
            buy_pressure=round(self.buy_pressure, 4),
            sell_pressure=round(self.sell_pressure, 4),
            confidence=round(self.confidence, 4),
            verdict=verdict,
            raw_buy=round(buy, 4),
            raw_sell=round(sell, 4),
            sensor_inputs={
                "trend": f"{trend_direction} ({trend_strength:.2f})",
                "smc": smc_signal,
                "displacement": f"{displacement_strength:.2f}",
                "liquidity_sweep": liquidity_sweep,
                "news_impact": f"{news_impact:.2f}",
                "flow": f"{flow_direction} ({flow_imbalance:.2f})",
            },
        )
        self._last_result = result
        return result

    def get_pressure(self) -> PressureResult | None:
        """Get current pressure state."""
        return self._last_result

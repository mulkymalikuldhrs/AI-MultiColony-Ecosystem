"""
Market State Engine - Regime detection: TRENDING|RANGE|MEAN_REVERT|RISK_OFF|PANIC|NO_TRADE.
Deterministic classification based on ADX, RSI, price change, volume.

Source: HermesQuantOS + Quant-Nanggroe-AI
"""

from __future__ import annotations

import logging
from datetime import datetime

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.quant.market_state")


class RegimeDetectionResult(BaseModel):
    """Result of regime detection."""
    symbol: str
    regime: str
    base_regime: str
    volatility: str  # LOW, NORMAL, HIGH
    liquidity: str  # THIN, NORMAL, DEEP
    no_trade_reasons: list[str] = Field(default_factory=list)
    inputs: dict = Field(default_factory=dict)
    trade_allowed: bool = True
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class MarketStateEngine:
    """Determines current market regime for decision gating.
    If NO_TRADE -> entire system stops.
    """

    def __init__(self) -> None:
        self.current_regime = "UNKNOWN"
        self.regime_history: list[RegimeDetectionResult] = []

    def detect_regime(
        self,
        symbol: str = "XAUUSD",
        price_change_5d: float = 0.0,
        adx: float = 20.0,
        rsi: float = 50.0,
        atr_pct: float = 1.0,
        volume_ratio: float = 1.0,
    ) -> RegimeDetectionResult:
        """Deterministic regime classification."""
        # Regime determination (priority order)
        if price_change_5d < -5.0:
            regime = "PANIC"
        elif price_change_5d < -2.0:
            regime = "RISK_OFF"
        elif adx > 25:
            regime = "TRENDING"
        elif rsi > 75 or rsi < 25:
            regime = "MEAN_REVERT"
        else:
            regime = "RANGE"

        # Volatility classification
        if atr_pct > 2.5:
            volatility = "HIGH"
        elif atr_pct < 0.5:
            volatility = "LOW"
        else:
            volatility = "NORMAL"

        # Liquidity classification
        if volume_ratio < 0.4:
            liquidity = "THIN"
        elif volume_ratio > 1.8:
            liquidity = "DEEP"
        else:
            liquidity = "NORMAL"

        # NO_TRADE override conditions
        no_trade_reasons: list[str] = []
        if regime == "PANIC":
            no_trade_reasons.append("Panic regime - extreme sell-off")
        if volatility == "HIGH" and liquidity == "THIN":
            no_trade_reasons.append("High volatility + thin liquidity = dangerous")
        if volume_ratio < 0.2:
            no_trade_reasons.append("Extremely low volume - no liquidity")

        final_regime = "NO_TRADE" if no_trade_reasons else regime

        result = RegimeDetectionResult(
            symbol=symbol,
            regime=final_regime,
            base_regime=regime,
            volatility=volatility,
            liquidity=liquidity,
            no_trade_reasons=no_trade_reasons,
            inputs={
                "price_change_5d": f"{price_change_5d:.2f}%",
                "adx": round(adx, 2),
                "rsi": round(rsi, 2),
                "atr_pct": f"{atr_pct:.2f}%",
                "volume_ratio": f"{volume_ratio:.2f}x",
            },
            trade_allowed=final_regime not in ["PANIC", "RISK_OFF", "NO_TRADE"],
        )

        self.current_regime = final_regime
        self.regime_history.append(result)
        if len(self.regime_history) > 100:
            self.regime_history = self.regime_history[-100:]

        logger.info("REGIME: %s | Vol: %s | Liq: %s", final_regime, volatility, liquidity)
        return result

    def get_regime(self) -> str:
        """Get current regime."""
        return self.current_regime

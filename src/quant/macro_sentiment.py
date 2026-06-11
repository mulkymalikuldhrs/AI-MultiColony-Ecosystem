"""
Macro/Fundamental + Sentiment Agent - Risk-on/off regime detection.

Source: HermesQuantOS
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.quant.macro_sentiment")


class RegimeResult(BaseModel):
    """Result of regime detection."""
    regime: str
    bias: str
    proxies: dict = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class MacroSentimentTool:
    """L2 Agent: Macro/Sentiment - Regime detection & sentiment analysis."""

    # Proxy assets for regime detection
    PROXY_ASSETS = {
        "SPX": "^GSPC",
        "VIX": "^VIX",
        "DXY": "DX-Y.NYB",
        "GOLD": "GC=F",
        "US10Y": "^TNX",
    }

    def __init__(self) -> None:
        self.regime_cache: dict = {}
        self.sentiment_cache: dict = {}

    def detect_regime_from_proxies(self, proxy_data: dict[str, dict]) -> RegimeResult:
        """Determine regime from proxy asset data.

        Args:
            proxy_data: Dict mapping proxy name to {"price": float, "change_5d": float}
        """
        spx_change = proxy_data.get("SPX", {}).get("change_5d", 0)
        vix_level = proxy_data.get("VIX", {}).get("price", 20)

        if isinstance(spx_change, (int, float)) and isinstance(vix_level, (int, float)):
            if spx_change > 1.0 and vix_level < 18:
                regime = "RISK-ON"
                bias = "Favor risk assets, equities, crypto"
            elif spx_change < -1.0 or vix_level > 25:
                regime = "RISK-OFF"
                bias = "Favor safe havens, gold, bonds"
            else:
                regime = "NEUTRAL"
                bias = "Balanced approach, selective entries"
        else:
            regime = "UNKNOWN"
            bias = "Insufficient data for regime detection"

        return RegimeResult(regime=regime, bias=bias, proxies=proxy_data)

    def analyze_sentiment(self, symbol: str = "XAUUSD",
                          news_impact: float = 0.0,
                          technical_score: float = 0.5,
                          volume_score: float = 0.5) -> dict:
        """Analyze sentiment combining news impact and technical indicators.

        Args:
            symbol: Trading symbol
            news_impact: Normalized news impact (0-1)
            technical_score: Technical analysis score (0-1, >0.5 = bullish)
            volume_score: Volume analysis score (0-1)
        """
        combined = technical_score * 0.4 + volume_score * 0.3 + (1 - news_impact) * 0.3
        if combined > 0.65:
            sentiment = "bullish"
        elif combined < 0.35:
            sentiment = "bearish"
        else:
            sentiment = "neutral"

        return {
            "symbol": symbol,
            "sentiment": sentiment,
            "confidence": round(abs(combined - 0.5) * 2, 4),
            "components": {
                "technical": round(technical_score, 4),
                "volume": round(volume_score, 4),
                "news_impact": round(news_impact, 4),
            },
            "timestamp": datetime.now().isoformat(),
        }

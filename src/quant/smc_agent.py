"""
SMC Agent Enhanced - Smart Money Concepts with proper data models.
ICT Concepts: Power of 3, Optimal Trade Entry (OTE), BOS, CHoCH, OB, FVG, Liquidity.

Source: HermesQuantOS + AI-MultiColony-Ecosystem
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.quant.smc_agent")


class MarketStructurePoint(BaseModel):
    """Represents a swing point in market structure."""
    index: int
    price: float
    point_type: str  # HH, HL, LH, LL, SH, SL
    timestamp: str = ""
    strength: float = 1.0


class OrderBlock(BaseModel):
    """Institutional order block."""
    index: int
    high: float
    low: float
    ob_type: str  # bullish_ob, bearish_ob
    strength: float = 0.5
    mitigated: bool = False
    mitigation_index: int = -1


class FairValueGap(BaseModel):
    """Fair Value Gap / Imbalance."""
    index: int
    top: float
    bottom: float
    fvg_type: str  # bullish_fvg, bearish_fvg
    size: float = 0.0
    filled: bool = False


class LiquidityLevel(BaseModel):
    """Liquidity pool at key price level."""
    price: float
    liq_type: str  # buy_side, sell_side, equal_level
    strength: float = 0.5
    swept: bool = False
    sweep_index: int = -1


class SmartMoneySetup(BaseModel):
    """Complete SMC trade setup."""
    setup_type: str  # OTE, BOS, MSS, FVG_OB
    direction: str  # BULLISH, BEARISH
    entry_zone: tuple[float, float]
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    take_profit_3: float
    probability: float
    confluences: list[str] = Field(default_factory=list)
    invalidation_level: float = 0.0


class SMCAgentEnhanced:
    """Enhanced Smart Money Concepts agent with proper data models."""

    RISK_PER_TRADE = 0.005  # 0.5%
    MAX_DAILY_RISK = 0.01   # 1%
    MIN_RR_RATIO = 1.5

    def __init__(self) -> None:
        self.swing_points: list[MarketStructurePoint] = []
        self.order_blocks: list[OrderBlock] = []
        self.fair_value_gaps: list[FairValueGap] = []
        self.liquidity_levels: list[LiquidityLevel] = []
        self.setups: list[SmartMoneySetup] = []

    def analyze(self, data: list[dict], symbol: str = "XAUUSD") -> dict:
        """Full SMC analysis with proper data models."""
        if len(data) < 20:
            return {"error": "Insufficient data for SMC analysis"}

        closes = [d["close"] for d in data]
        highs = [d["high"] for d in data]
        lows = [d["low"] for d in data]
        volumes = [d.get("volume", 0) for d in data]

        self._detect_swing_points(highs, lows, data)
        trend = self._determine_trend()
        self._detect_order_blocks(closes, highs, lows, volumes, data)
        self._detect_fair_value_gaps(highs, lows, data)
        self._detect_liquidity_levels(highs, lows, data)
        self._generate_setups(closes[-1], trend)

        return {
            "symbol": symbol,
            "latest_price": closes[-1],
            "trend": trend,
            "swing_points_count": len(self.swing_points),
            "recent_swings": [sp.model_dump() for sp in self.swing_points[-5:]],
            "order_blocks_count": len(self.order_blocks),
            "active_order_blocks": [ob.model_dump() for ob in self.order_blocks if not ob.mitigated][-5:],
            "fvgs_count": len(self.fair_value_gaps),
            "unfilled_fvgs": [fvg.model_dump() for fvg in self.fair_value_gaps if not fvg.filled][-5:],
            "liquidity_levels": [ll.model_dump() for ll in self.liquidity_levels[-5:]],
            "active_setups": [s.model_dump() for s in self.setups if s.probability > 0.5],
            "timestamp": datetime.now().isoformat(),
        }

    def _detect_swing_points(self, highs: list, lows: list, data: list) -> None:
        """Detect swing highs and lows with strength scoring."""
        self.swing_points = []
        for i in range(2, len(highs) - 2):
            if (highs[i] > highs[i-1] and highs[i] > highs[i+1] and
                highs[i] > highs[i-2] and highs[i] > highs[i+2]):
                strength = min(10, (highs[i] - min(highs[i-2:i+3])) / highs[i] * 100) if highs[i] > 0 else 1
                self.swing_points.append(MarketStructurePoint(
                    index=i, price=highs[i], point_type="SH",
                    timestamp=data[i].get("time", ""), strength=round(strength, 1)
                ))
            if (lows[i] < lows[i-1] and lows[i] < lows[i+1] and
                lows[i] < lows[i-2] and lows[i] < lows[i+2]):
                strength = min(10, (max(lows[i-2:i+3]) - lows[i]) / lows[i] * 100) if lows[i] > 0 else 1
                self.swing_points.append(MarketStructurePoint(
                    index=i, price=lows[i], point_type="SL",
                    timestamp=data[i].get("time", ""), strength=round(strength, 1)
                ))

        highs_list = [sp for sp in self.swing_points if sp.point_type == "SH"]
        lows_list = [sp for sp in self.swing_points if sp.point_type == "SL"]

        for i in range(1, len(highs_list)):
            highs_list[i].point_type = "HH" if highs_list[i].price > highs_list[i-1].price else "LH"

        for i in range(1, len(lows_list)):
            lows_list[i].point_type = "HL" if lows_list[i].price > lows_list[i-1].price else "LL"

    def _determine_trend(self) -> str:
        """Determine trend from swing point classification."""
        if len(self.swing_points) < 4:
            return "neutral"
        recent = self.swing_points[-4:]
        hh = sum(1 for sp in recent if sp.point_type == "HH")
        hl = sum(1 for sp in recent if sp.point_type == "HL")
        lh = sum(1 for sp in recent if sp.point_type == "LH")
        ll = sum(1 for sp in recent if sp.point_type == "LL")
        if hh >= 2 and hl >= 1:
            return "bullish"
        elif lh >= 2 and ll >= 1:
            return "bearish"
        return "neutral"

    def _detect_order_blocks(self, closes: list, highs: list, lows: list, volumes: list, data: list) -> None:
        """Detect institutional order blocks with volume confirmation."""
        self.order_blocks = []
        for i in range(3, len(closes)):
            body = abs(closes[i] - data[i].get("open", closes[i]))
            prev_body = abs(closes[i-1] - data[i-1].get("open", closes[i-1]))
            if prev_body == 0:
                continue
            if body > prev_body * 2:
                vol = volumes[i] if i < len(volumes) else 0
                avg_vol = sum(volumes[max(0,i-20):i]) / 20 if i >= 20 and sum(volumes[max(0,i-20):i]) > 0 else 1
                vol_strength = min(1.0, vol / avg_vol) if avg_vol > 0 else 0.5
                if closes[i] > data[i].get("open", closes[i]):
                    if closes[i-1] < data[i-1].get("open", closes[i-1]):
                        self.order_blocks.append(OrderBlock(
                            index=i-1, high=highs[i-1], low=lows[i-1],
                            ob_type="bullish_ob", strength=round(vol_strength, 2)
                        ))
                else:
                    if closes[i-1] > data[i-1].get("open", closes[i-1]):
                        self.order_blocks.append(OrderBlock(
                            index=i-1, high=highs[i-1], low=lows[i-1],
                            ob_type="bearish_ob", strength=round(vol_strength, 2)
                        ))

    def _detect_fair_value_gaps(self, highs: list, lows: list, data: list) -> None:
        """Detect Fair Value Gaps (3-candle imbalances)."""
        self.fair_value_gaps = []
        for i in range(2, len(data)):
            if lows[i] > highs[i-2]:
                self.fair_value_gaps.append(FairValueGap(
                    index=i-1, top=lows[i], bottom=highs[i-2],
                    fvg_type="bullish_fvg", size=round(lows[i] - highs[i-2], 5)
                ))
            if highs[i] < lows[i-2]:
                self.fair_value_gaps.append(FairValueGap(
                    index=i-1, top=lows[i-2], bottom=highs[i],
                    fvg_type="bearish_fvg", size=round(lows[i-2] - highs[i], 5)
                ))

    def _detect_liquidity_levels(self, highs: list, lows: list, data: list) -> None:
        """Detect liquidity pools at swing points and equal highs/lows."""
        self.liquidity_levels = []
        for sp in self.swing_points:
            liq_type = "buy_side" if sp.point_type in ("SH", "HH", "LH") else "sell_side"
            self.liquidity_levels.append(LiquidityLevel(
                price=sp.price, liq_type=liq_type, strength=sp.strength / 10
            ))
        prices = [sp.price for sp in self.swing_points]
        for i, p1 in enumerate(prices):
            for j, p2 in enumerate(prices):
                if i != j and p1 > 0 and abs(p1 - p2) / p1 < 0.001:
                    self.liquidity_levels.append(LiquidityLevel(
                        price=p1, liq_type="equal_level", strength=0.8
                    ))

    def _generate_setups(self, current_price: float, trend: str) -> None:
        """Generate trade setups based on SMC analysis."""
        self.setups = []
        active_obs = [ob for ob in self.order_blocks if not ob.mitigated]

        if trend == "bullish" and active_obs:
            bullish_obs = [ob for ob in active_obs if ob.ob_type == "bullish_ob"]
            if bullish_obs:
                ob = bullish_obs[-1]
                entry = (ob.high + ob.low) / 2
                sl = ob.low - (ob.high - ob.low) * 0.1
                confluences = ["Bullish OB", f"Trend: {trend}"]
                prob = min(0.9, 0.4 + len(confluences) * 0.1)
                self.setups.append(SmartMoneySetup(
                    setup_type="OTE", direction="BULLISH",
                    entry_zone=(ob.low, ob.high),
                    stop_loss=round(sl, 5),
                    take_profit_1=round(current_price, 5),
                    take_profit_2=round(current_price + (entry - sl) * 2, 5),
                    take_profit_3=round(current_price + (entry - sl) * 3, 5),
                    probability=round(prob, 2),
                    confluences=confluences,
                    invalidation_level=round(ob.low, 5),
                ))

        if trend == "bearish" and active_obs:
            bearish_obs = [ob for ob in active_obs if ob.ob_type == "bearish_ob"]
            if bearish_obs:
                ob = bearish_obs[-1]
                entry = (ob.high + ob.low) / 2
                sl = ob.high + (ob.high - ob.low) * 0.1
                confluences = ["Bearish OB", f"Trend: {trend}"]
                prob = min(0.9, 0.4 + len(confluences) * 0.1)
                self.setups.append(SmartMoneySetup(
                    setup_type="OTE", direction="BEARISH",
                    entry_zone=(ob.low, ob.high),
                    stop_loss=round(sl, 5),
                    take_profit_1=round(current_price, 5),
                    take_profit_2=round(current_price - (sl - entry) * 2, 5),
                    take_profit_3=round(current_price - (sl - entry) * 3, 5),
                    probability=round(prob, 2),
                    confluences=confluences,
                    invalidation_level=round(ob.high, 5),
                ))

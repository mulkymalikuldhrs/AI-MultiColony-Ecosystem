"""Decision Synthesis Engine — Deterministic decision table for entries.

Ported from HermesQuantOS tools/decision_engine.py. Provides a
machine-readable decision framework with risk clearance gates.

Features:
- 7-rule decision table mapping regime+pressure→action
- Risk clearance (CLEAR/BLOCKED/PAUSE)
- Deterministic — no LLM required for decision logic
- Extensible rule system
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MarketRegime(str, Enum):
    """Market regime classification."""
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGE = "range"
    MEAN_REVERT = "mean_revert"
    RISK_OFF = "risk_off"
    PANIC = "panic"
    NO_TRADE = "no_trade"


class PressureLevel(str, Enum):
    """Buy/sell pressure level."""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    NEUTRAL = "neutral"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


class RiskClearance(str, Enum):
    """Risk clearance status."""
    CLEAR = "clear"
    BLOCKED = "blocked"
    PAUSE = "pause"


class DecisionAction(str, Enum):
    """Decision action."""
    ENTER_LONG = "enter_long"
    ENTER_SHORT = "enter_short"
    EXIT = "exit"
    HOLD = "hold"
    REDUCE = "reduce"
    HEDGE = "hedge"
    NO_ACTION = "no_action"


class DecisionInput(BaseModel):
    """Input to the decision engine."""
    regime: MarketRegime = MarketRegime.RANGE
    pressure: PressureLevel = PressureLevel.NEUTRAL
    confidence: float = Field(0.5, ge=0.0, le=1.0)
    volatility: float = Field(0.5, ge=0.0, le=1.0)
    risk_score: float = Field(0.5, ge=0.0, le=1.0)
    sentiment: float = Field(0.0, ge=-1.0, le=1.0)
    kill_switch_active: bool = False
    daily_loss_pct: float = 0.0
    weekly_loss_pct: float = 0.0


class DecisionOutput(BaseModel):
    """Output from the decision engine."""
    action: DecisionAction = DecisionAction.HOLD
    risk_clearance: RiskClearance = RiskClearance.PAUSE
    rule_id: str = ""
    confidence: float = 0.0
    reasoning: str = ""
    position_size_pct: float = 0.0
    stop_loss_pct: float = 0.0
    take_profit_pct: float = 0.0


# Decision rules: (regime, pressure) → (action, position_pct, sl_pct, tp_pct)
DECISION_RULES = {
    # Rule 1: Trending up + strong buy → full long
    (MarketRegime.TRENDING_UP, PressureLevel.STRONG_BUY): (
        DecisionAction.ENTER_LONG, 2.0, 1.5, 3.0, "R1: Strong uptrend + strong buy signal"
    ),
    # Rule 2: Trending up + buy → moderate long
    (MarketRegime.TRENDING_UP, PressureLevel.BUY): (
        DecisionAction.ENTER_LONG, 1.0, 1.5, 3.0, "R2: Uptrend + buy signal"
    ),
    # Rule 3: Trending down + strong sell → full short
    (MarketRegime.TRENDING_DOWN, PressureLevel.STRONG_SELL): (
        DecisionAction.ENTER_SHORT, 2.0, 1.5, 3.0, "R3: Strong downtrend + strong sell"
    ),
    # Rule 4: Range + any pressure → hold/reduce
    (MarketRegime.RANGE, PressureLevel.NEUTRAL): (
        DecisionAction.HOLD, 0.0, 0.0, 0.0, "R4: Range + neutral → hold"
    ),
    # Rule 5: Risk-off → exit/hedge
    (MarketRegime.RISK_OFF, PressureLevel.SELL): (
        DecisionAction.HEDGE, 0.0, 0.0, 0.0, "R5: Risk-off regime → hedge"
    ),
    (MarketRegime.RISK_OFF, PressureLevel.STRONG_SELL): (
        DecisionAction.EXIT, 0.0, 0.0, 0.0, "R5b: Risk-off + strong sell → exit"
    ),
    # Rule 6: Panic → no action
    (MarketRegime.PANIC, PressureLevel.STRONG_SELL): (
        DecisionAction.NO_ACTION, 0.0, 0.0, 0.0, "R6: Panic → no action"
    ),
    # Rule 7: No trade → no action
    (MarketRegime.NO_TRADE, PressureLevel.NEUTRAL): (
        DecisionAction.NO_ACTION, 0.0, 0.0, 0.0, "R7: No-trade regime"
    ),
}


class DecisionSynthesisEngine:
    """Deterministic decision synthesis engine.

    Maps market regime + pressure → action using a fixed rule table,
    then applies risk clearance gates. No LLM needed for core logic.

    Usage::

        engine = DecisionSynthesisEngine()
        decision = engine.decide(DecisionInput(
            regime=MarketRegime.TRENDING_UP,
            pressure=PressureLevel.STRONG_BUY,
            confidence=0.8,
        ))
        if decision.risk_clearance == RiskClearance.CLEAR:
            execute(decision.action)
    """

    def __init__(self, max_risk_per_trade: float = 0.5, max_daily_loss: float = 1.0, max_weekly_loss: float = 3.0) -> None:
        self._max_risk_per_trade = max_risk_per_trade
        self._max_daily_loss = max_daily_loss
        self._max_weekly_loss = max_weekly_loss

    def _check_risk_clearance(self, inp: DecisionInput) -> RiskClearance:
        """Check risk clearance gates."""
        # Kill switch overrides everything
        if inp.kill_switch_active:
            return RiskClearance.BLOCKED

        # Daily loss limit
        if abs(inp.daily_loss_pct) >= self._max_daily_loss:
            return RiskClearance.BLOCKED

        # Weekly loss limit
        if abs(inp.weekly_loss_pct) >= self._max_weekly_loss:
            return RiskClearance.BLOCKED

        # Risk score too high
        if inp.risk_score >= 0.8:
            return RiskClearance.PAUSE

        # Confidence too low
        if inp.confidence < 0.3:
            return RiskClearance.PAUSE

        return RiskClearance.CLEAR

    def decide(self, inp: DecisionInput) -> DecisionOutput:
        """Make a decision based on input state.

        Args:
            inp: Decision input with regime, pressure, confidence, etc.

        Returns:
            DecisionOutput with action, risk clearance, and position sizing.
        """
        # Check risk gates first
        clearance = self._check_risk_clearance(inp)

        if clearance == RiskClearance.BLOCKED:
            return DecisionOutput(
                action=DecisionAction.NO_ACTION,
                risk_clearance=clearance,
                reasoning="Risk gate BLOCKED: kill switch or loss limit breached",
            )

        # Look up decision rule
        rule_key = (inp.regime, inp.pressure)
        rule = DECISION_RULES.get(rule_key)

        if rule is None:
            # Try with neutral pressure fallback
            rule_key_fallback = (inp.regime, PressureLevel.NEUTRAL)
            rule = DECISION_RULES.get(rule_key_fallback)

        if rule is None:
            return DecisionOutput(
                action=DecisionAction.HOLD,
                risk_clearance=clearance,
                reasoning=f"No rule for regime={inp.regime.value} pressure={inp.pressure.value}",
            )

        action, pos_pct, sl_pct, tp_pct, reasoning = rule

        # If PAUSE, reduce position size
        if clearance == RiskClearance.PAUSE:
            pos_pct *= 0.25
            reasoning += " [PAUSED: reduced to 25% size]"

        # Scale by confidence
        scaled_pos = pos_pct * inp.confidence

        return DecisionOutput(
            action=action,
            risk_clearance=clearance,
            rule_id=reasoning.split(":")[0].strip(),
            confidence=inp.confidence,
            reasoning=reasoning,
            position_size_pct=round(scaled_pos, 2),
            stop_loss_pct=sl_pct,
            take_profit_pct=tp_pct,
        )


__all__ = [
    "MarketRegime",
    "PressureLevel",
    "RiskClearance",
    "DecisionAction",
    "DecisionInput",
    "DecisionOutput",
    "DecisionSynthesisEngine",
]

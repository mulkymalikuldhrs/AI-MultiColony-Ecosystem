"""
Decision Synthesis Engine - Deterministic decision table for trade entry logic.
Compresses signals -> 1 Entry, 1 SL, 1-3 TPs.
Risk Clearance: CLEAR / BLOCKED / PAUSE.

Source: HermesQuantOS + Quant-Nanggroe-AI
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.quant.risk_officer import MAX_DAILY_LOSS

logger = logging.getLogger("ecosystem.quant.decision_engine")


class DecisionResult(BaseModel):
    """Result of decision synthesis."""
    action: str  # ALLOW_LONG, ALLOW_SHORT, NO_TRADE, WATCH_LONG, WATCH_SHORT
    risk_clearance: str  # CLEAR, BLOCKED, PAUSE
    reason: str
    regime: str
    buy_pressure: float
    sell_pressure: float
    confidence: float
    volatility: str = "NORMAL"
    matched_rules: list[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class DecisionSynthesisEngine:
    """Deterministic decision table that synthesizes pressure + regime -> trade decision."""

    DECISION_TABLE: list[dict] = [
        {
            "id": "DT001",
            "regime_allowed": ["TRENDING", "RANGE", "MEAN_REVERT"],
            "min_buy_pressure": 0.70,
            "max_sell_pressure": 0.30,
            "allowed_volatility": ["LOW", "NORMAL"],
            "min_confidence": 0.60,
            "action": "ALLOW_LONG",
            "description": "Strong bullish pressure in safe regime",
        },
        {
            "id": "DT002",
            "regime_allowed": ["TRENDING", "RANGE", "MEAN_REVERT"],
            "min_sell_pressure": 0.70,
            "max_buy_pressure": 0.30,
            "allowed_volatility": ["LOW", "NORMAL"],
            "min_confidence": 0.60,
            "action": "ALLOW_SHORT",
            "description": "Strong bearish pressure in safe regime",
        },
        {
            "id": "DT003",
            "regime_allowed": ["TRENDING"],
            "min_buy_pressure": 0.60,
            "max_sell_pressure": 0.40,
            "allowed_volatility": ["LOW", "NORMAL", "HIGH"],
            "min_confidence": 0.55,
            "action": "ALLOW_LONG_TRENDING",
            "description": "Moderate bullish in trending regime",
        },
        {
            "id": "DT004",
            "regime_allowed": ["TRENDING"],
            "min_sell_pressure": 0.60,
            "max_buy_pressure": 0.40,
            "allowed_volatility": ["LOW", "NORMAL", "HIGH"],
            "min_confidence": 0.55,
            "action": "ALLOW_SHORT_TRENDING",
            "description": "Moderate bearish in trending regime",
        },
        {
            "id": "DT005",
            "regime_allowed": ["PANIC", "RISK_OFF", "NO_TRADE"],
            "min_buy_pressure": 1.10,  # Impossible = always blocked
            "action": "NO_TRADE",
            "description": "Dangerous regime - all trading blocked",
        },
        {
            "id": "DT006",
            "regime_allowed": ["TRENDING", "RANGE", "MEAN_REVERT"],
            "min_buy_pressure": 0.55,
            "max_buy_pressure": 0.69,
            "allowed_volatility": ["LOW", "NORMAL"],
            "min_confidence": 0.55,
            "action": "WATCH_LONG",
            "description": "Weak bullish - monitor but don't enter",
        },
        {
            "id": "DT007",
            "regime_allowed": ["TRENDING", "RANGE", "MEAN_REVERT"],
            "min_sell_pressure": 0.55,
            "max_sell_pressure": 0.69,
            "allowed_volatility": ["LOW", "NORMAL"],
            "min_confidence": 0.55,
            "action": "WATCH_SHORT",
            "description": "Weak bearish - monitor but don't enter",
        },
    ]

    def __init__(self) -> None:
        self.last_decision: Optional[DecisionResult] = None

    def evaluate(
        self,
        regime: str,
        buy_pressure: float,
        sell_pressure: float,
        confidence: float,
        volatility: str = "NORMAL",
        daily_pnl_pct: float = 0.0,
    ) -> DecisionResult:
        """Evaluate market state against decision table."""
        matched_rules: list[str] = []

        for rule in self.DECISION_TABLE:
            if regime not in rule.get("regime_allowed", []):
                continue
            if buy_pressure < rule.get("min_buy_pressure", 0):
                continue
            if sell_pressure > rule.get("max_sell_pressure", 1.0):
                continue
            if sell_pressure < rule.get("min_sell_pressure", 0):
                continue
            if buy_pressure > rule.get("max_buy_pressure", 1.0):
                continue
            if volatility not in rule.get("allowed_volatility", ["LOW", "NORMAL", "HIGH"]):
                continue
            if confidence < rule.get("min_confidence", 0):
                continue
            matched_rules.append(rule["id"])

        if not matched_rules:
            action = "NO_TRADE"
            risk_clearance = "BLOCKED"
            reason = "No decision rule matched - conditions not met"
        else:
            best_rule = next(r for r in self.DECISION_TABLE if r["id"] == matched_rules[0])
            action = best_rule["action"]

            if abs(min(0, daily_pnl_pct)) >= MAX_DAILY_LOSS:
                risk_clearance = "BLOCKED"
                reason = f"Daily loss limit reached: {daily_pnl_pct:.2%}"
                action = "NO_TRADE"
            elif "ALLOW" in action:
                risk_clearance = "CLEAR"
                reason = best_rule["description"]
            elif "WATCH" in action:
                risk_clearance = "PAUSE"
                reason = f"Monitoring: {best_rule['description']}"
            else:
                risk_clearance = "BLOCKED"
                reason = best_rule["description"]

        decision = DecisionResult(
            action=action,
            risk_clearance=risk_clearance,
            reason=reason,
            regime=regime,
            buy_pressure=round(buy_pressure, 4),
            sell_pressure=round(sell_pressure, 4),
            confidence=round(confidence, 4),
            volatility=volatility,
            matched_rules=matched_rules,
        )

        self.last_decision = decision
        logger.info("DECISION: %s | Clearance: %s | Regime: %s", action, risk_clearance, regime)
        return decision

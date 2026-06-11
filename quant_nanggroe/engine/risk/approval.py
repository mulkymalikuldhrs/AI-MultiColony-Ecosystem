"""
Hierarchical Approval Chain
============================
From TradingAgents research — Multi-tier trade approval with veto power.

Approval hierarchy:
  1. Risk Manager  — VETO power (can block any trade)
  2. Portfolio Manager — reviews position sizing for large positions
  3. Senior Trader — advisory for extraordinary positions

Trade tiers:
  - SMALL:  < 0.5% of portfolio → auto-approved
  - MEDIUM: 0.5–2% of portfolio → Risk Manager review
  - LARGE:  > 2% of portfolio → Risk Manager + Portfolio Manager review

In backtest mode: auto-approve all (with logging).
In live mode: enforce full chain.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ─── Tier Thresholds (percentage of portfolio) ──────────────────────────

SMALL_THRESHOLD: float = 0.005   # 0.5% — below this, auto-approve
MEDIUM_THRESHOLD: float = 0.02   # 2.0% — above this, requires full chain


class ApprovalTier(str, Enum):
    """Trade size classification tier."""
    SMALL = "small"      # Auto-approved
    MEDIUM = "medium"    # Risk Manager review
    LARGE = "large"      # Risk + Portfolio Manager review


class ApprovalDecision(str, Enum):
    """Possible approval decisions."""
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"


class ApprovalMode(str, Enum):
    """Operating mode for the approval chain."""
    BACKTEST = "backtest"   # Auto-approve all with logging
    LIVE = "live"           # Enforce full approval chain


# ─── Approver identities ────────────────────────────────────────────────

RISK_MANAGER = "risk_manager"
PORTFOLIO_MANAGER = "portfolio_manager"
SENIOR_TRADER = "senior_trader"


class ApprovalRecord(BaseModel):
    """Immutable record of an approval decision."""
    trade_id: str
    tier: ApprovalTier
    decisions: List[Dict[str, Any]] = Field(default_factory=list)
    final_decision: ApprovalDecision = ApprovalDecision.REJECTED
    timestamp: datetime = Field(default_factory=datetime.now)
    mode: ApprovalMode = ApprovalMode.LIVE

    model_config = {"frozen": False}  # allow mutation during build


class ApprovalChain:
    """
    Hierarchical approval chain for trade requests.

    Inspired by TradingAgents architecture:
    - Risk Manager has VETO power (can block any trade regardless of tier)
    - Portfolio Manager reviews position sizing for LARGE tier
    - Senior Trader can be consulted for extraordinary situations

    All decisions are logged with reasoning for full audit trail.
    """

    def __init__(self, config: Optional[Dict] = None) -> None:
        """
        Initialize the approval chain.

        Args:
            config: Optional configuration dict with keys:
                - mode: 'backtest' or 'live' (default: 'live')
                - small_threshold: override 0.5% threshold
                - medium_threshold: override 2.0% threshold
                - auto_approve_rules: dict of auto-approve criteria
                - risk_manager_veto: whether RM has veto (default: True)
        """
        config = config or {}
        self._mode = ApprovalMode(config.get("mode", "live"))
        self._small_threshold = float(config.get("small_threshold", SMALL_THRESHOLD))
        self._medium_threshold = float(config.get("medium_threshold", MEDIUM_THRESHOLD))
        self._risk_manager_veto = bool(config.get("risk_manager_veto", True))
        self._auto_approve_rules = config.get("auto_approve_rules", {})
        self._history: List[ApprovalRecord] = []

    # ─── Public API ─────────────────────────────────────────────────────

    def classify_tier(self, position_pct: float) -> ApprovalTier:
        """
        Classify a trade into an approval tier by position size.

        Args:
            position_pct: Position size as fraction of portfolio (0.0–1.0).
                          E.g., 0.005 = 0.5% of portfolio.

        Returns:
            ApprovalTier: SMALL, MEDIUM, or LARGE
        """
        if position_pct < 0:
            raise ValueError(f"position_pct must be non-negative, got {position_pct}")
        if position_pct < self._small_threshold:
            return ApprovalTier.SMALL
        elif position_pct < self._medium_threshold:
            return ApprovalTier.MEDIUM
        else:
            return ApprovalTier.LARGE

    async def evaluate(self, trade_request: Dict) -> ApprovalRecord:
        """
        Evaluate a trade request through the approval chain.

        Args:
            trade_request: Dict with keys:
                - trade_id: str (optional, auto-generated if missing)
                - symbol: str
                - side: str ('buy' or 'sell')
                - position_pct: float (position as % of portfolio, 0.0–1.0)
                - portfolio_value: float (current portfolio value)
                - reason: str (trade rationale)
                - strategy: str (originating strategy name)
                - confidence: float (0.0–1.0, LLM confidence)

        Returns:
            ApprovalRecord with all decisions and final outcome
        """
        trade_id = trade_request.get("trade_id", str(uuid.uuid4())[:8])
        position_pct = float(trade_request.get("position_pct", 0.0))
        tier = self.classify_tier(position_pct)

        record = ApprovalRecord(
            trade_id=trade_id,
            tier=tier,
            mode=self._mode,
        )

        # ─── Backtest mode: auto-approve everything ─────────────────
        if self._mode == ApprovalMode.BACKTEST:
            decision_entry = self._make_decision(
                approver="backtest_auto",
                decision=ApprovalDecision.APPROVED,
                reason=f"Auto-approved in backtest mode (tier={tier.value})",
            )
            record.decisions.append(decision_entry)
            record.final_decision = ApprovalDecision.APPROVED
            self._history.append(record)
            logger.info(
                "[APPROVAL] trade=%s tier=%s auto-approved (backtest mode)",
                trade_id, tier.value,
            )
            return record

        # ─── Live mode: enforce full chain ──────────────────────────

        # Tier SMALL: auto-approve
        if tier == ApprovalTier.SMALL:
            decision_entry = self._make_decision(
                approver="auto_small",
                decision=ApprovalDecision.APPROVED,
                reason=f"Auto-approved: position {position_pct:.4f} < {self._small_threshold} (SMALL tier)",
            )
            record.decisions.append(decision_entry)
            record.final_decision = ApprovalDecision.APPROVED
            self._history.append(record)
            logger.info(
                "[APPROVAL] trade=%s tier=SMALL auto-approved (pct=%.4f)",
                trade_id, position_pct,
            )
            return record

        # Tier MEDIUM: Risk Manager review
        if tier == ApprovalTier.MEDIUM:
            rm_decision = await self._risk_manager_review(trade_request, tier)
            record.decisions.append(rm_decision)

            if rm_decision["decision"] == ApprovalDecision.REJECTED:
                record.final_decision = ApprovalDecision.REJECTED
                self._history.append(record)
                logger.warning(
                    "[APPROVAL] trade=%s tier=MEDIUM REJECTED by Risk Manager: %s",
                    trade_id, rm_decision["reason"],
                )
                return record

            if rm_decision["decision"] == ApprovalDecision.ESCALATED:
                # Escalate to Portfolio Manager
                pm_decision = await self._portfolio_manager_review(trade_request, tier)
                record.decisions.append(pm_decision)
                if pm_decision["decision"] == ApprovalDecision.REJECTED:
                    record.final_decision = ApprovalDecision.REJECTED
                    self._history.append(record)
                    logger.warning(
                        "[APPROVAL] trade=%s tier=MEDIUM REJECTED by Portfolio Manager (escalated): %s",
                        trade_id, pm_decision["reason"],
                    )
                    return record

            record.final_decision = ApprovalDecision.APPROVED
            self._history.append(record)
            logger.info(
                "[APPROVAL] trade=%s tier=MEDIUM APPROVED",
                trade_id,
            )
            return record

        # Tier LARGE: Risk Manager + Portfolio Manager
        if tier == ApprovalTier.LARGE:
            rm_decision = await self._risk_manager_review(trade_request, tier)
            record.decisions.append(rm_decision)

            if rm_decision["decision"] == ApprovalDecision.REJECTED:
                record.final_decision = ApprovalDecision.REJECTED
                self._history.append(record)
                logger.warning(
                    "[APPROVAL] trade=%s tier=LARGE REJECTED by Risk Manager: %s",
                    trade_id, rm_decision["reason"],
                )
                return record

            # Portfolio Manager always reviews LARGE
            pm_decision = await self._portfolio_manager_review(trade_request, tier)
            record.decisions.append(pm_decision)

            if pm_decision["decision"] == ApprovalDecision.REJECTED:
                record.final_decision = ApprovalDecision.REJECTED
                self._history.append(record)
                logger.warning(
                    "[APPROVAL] trade=%s tier=LARGE REJECTED by Portfolio Manager: %s",
                    trade_id, pm_decision["reason"],
                )
                return record

            if pm_decision["decision"] == ApprovalDecision.ESCALATED:
                # Escalate to Senior Trader
                st_decision = await self._senior_trader_review(trade_request, tier)
                record.decisions.append(st_decision)
                if st_decision["decision"] == ApprovalDecision.REJECTED:
                    record.final_decision = ApprovalDecision.REJECTED
                    self._history.append(record)
                    logger.warning(
                        "[APPROVAL] trade=%s tier=LARGE REJECTED by Senior Trader (escalated): %s",
                        trade_id, st_decision["reason"],
                    )
                    return record

            record.final_decision = ApprovalDecision.APPROVED
            self._history.append(record)
            logger.info(
                "[APPROVAL] trade=%s tier=LARGE APPROVED",
                trade_id,
            )
            return record

        # Should not reach here
        record.final_decision = ApprovalDecision.REJECTED
        self._history.append(record)
        return record

    def get_history(self, limit: int = 100) -> List[ApprovalRecord]:
        """Get recent approval history."""
        return self._history[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get approval chain statistics."""
        total = len(self._history)
        if total == 0:
            return {"total": 0, "approved": 0, "rejected": 0, "approval_rate": 0.0}
        approved = sum(1 for r in self._history if r.final_decision == ApprovalDecision.APPROVED)
        rejected = sum(1 for r in self._history if r.final_decision == ApprovalDecision.REJECTED)
        return {
            "total": total,
            "approved": approved,
            "rejected": rejected,
            "approval_rate": approved / total if total > 0 else 0.0,
            "by_tier": {
                tier.value: sum(1 for r in self._history if r.tier == tier)
                for tier in ApprovalTier
            },
        }

    # ─── Approver Simulations ───────────────────────────────────────────
    # In production, these would call real risk/portfolio APIs.
    # Here we implement rule-based logic that can be overridden.

    async def _risk_manager_review(
        self, trade_request: Dict, tier: ApprovalTier
    ) -> Dict[str, Any]:
        """
        Risk Manager review with VETO power.

        Checks:
        - Drawdown limits (reject if drawdown > 15%)
        - Daily loss limits (reject if daily loss > 1%)
        - Position concentration (reject if single position > 10%)
        - Confidence gating (escalate if confidence < 0.65)
        """
        confidence = float(trade_request.get("confidence", 0.5))
        position_pct = float(trade_request.get("position_pct", 0.0))

        # Hard rejection: position exceeds constitutional max
        if position_pct > 0.10:
            return self._make_decision(
                approver=RISK_MANAGER,
                decision=ApprovalDecision.REJECTED,
                reason=f"Position {position_pct:.2%} exceeds constitutional max 10%",
            )

        # Hard rejection: drawdown too high (from context if available)
        drawdown = float(trade_request.get("current_drawdown", 0.0))
        if drawdown > 0.15:
            return self._make_decision(
                approver=RISK_MANAGER,
                decision=ApprovalDecision.REJECTED,
                reason=f"Current drawdown {drawdown:.2%} exceeds 15% limit",
            )

        # Hard rejection: daily loss exceeded
        daily_loss = float(trade_request.get("daily_loss_pct", 0.0))
        if daily_loss > 0.01:
            return self._make_decision(
                approver=RISK_MANAGER,
                decision=ApprovalDecision.REJECTED,
                reason=f"Daily loss {daily_loss:.2%} exceeds 1% limit",
            )

        # Escalate: low confidence
        if confidence < 0.65:
            return self._make_decision(
                approver=RISK_MANAGER,
                decision=ApprovalDecision.ESCALATED,
                reason=f"Low confidence {confidence:.2f} < 0.65 threshold, escalating to Portfolio Manager",
            )

        # Approve
        return self._make_decision(
            approver=RISK_MANAGER,
            decision=ApprovalDecision.APPROVED,
            reason=f"Risk parameters acceptable (confidence={confidence:.2f}, drawdown={drawdown:.2%})",
        )

    async def _portfolio_manager_review(
        self, trade_request: Dict, tier: ApprovalTier
    ) -> Dict[str, Any]:
        """
        Portfolio Manager review for position sizing.

        Checks:
        - Portfolio concentration (reject if > 3 correlated positions)
        - Position sizing reasonableness
        - Strategy performance (reject if strategy is underperforming)
        """
        position_pct = float(trade_request.get("position_pct", 0.0))
        correlated = int(trade_request.get("correlated_positions", 0))
        strategy = trade_request.get("strategy", "unknown")

        # Hard rejection: too many correlated positions
        if correlated >= 3:
            return self._make_decision(
                approver=PORTFOLIO_MANAGER,
                decision=ApprovalDecision.REJECTED,
                reason=f"Too many correlated positions ({correlated}) ≥ 3 limit",
            )

        # Escalate for extraordinary positions (> 5% of portfolio)
        if position_pct > 0.05:
            return self._make_decision(
                approver=PORTFOLIO_MANAGER,
                decision=ApprovalDecision.ESCALATED,
                reason=f"Extraordinary position size {position_pct:.2%}, escalating to Senior Trader",
            )

        # Check strategy performance (if provided)
        strategy_win_rate = float(trade_request.get("strategy_win_rate", 0.5))
        if strategy_win_rate < 0.4:
            return self._make_decision(
                approver=PORTFOLIO_MANAGER,
                decision=ApprovalDecision.REJECTED,
                reason=f"Strategy '{strategy}' win rate {strategy_win_rate:.1%} below 40% threshold",
            )

        # Approve
        return self._make_decision(
            approver=PORTFOLIO_MANAGER,
            decision=ApprovalDecision.APPROVED,
            reason=f"Position sizing acceptable (pct={position_pct:.2%}, correlated={correlated})",
        )

    async def _senior_trader_review(
        self, trade_request: Dict, tier: ApprovalTier
    ) -> Dict[str, Any]:
        """
        Senior Trader advisory review for extraordinary positions.

        This is the final check — usually approves with conditions.
        """
        position_pct = float(trade_request.get("position_pct", 0.0))
        confidence = float(trade_request.get("confidence", 0.5))

        # Only reject if both confidence is very low AND position is very large
        if confidence < 0.5 and position_pct > 0.08:
            return self._make_decision(
                approver=SENIOR_TRADER,
                decision=ApprovalDecision.REJECTED,
                reason=f"Very low confidence ({confidence:.2f}) + very large position ({position_pct:.2%})",
            )

        # Approve (possibly with size reduction recommendation)
        return self._make_decision(
            approver=SENIOR_TRADER,
            decision=ApprovalDecision.APPROVED,
            reason=f"Approved with advisory: large position {position_pct:.2%} (confidence={confidence:.2f})",
        )

    # ─── Helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _make_decision(
        approver: str,
        decision: ApprovalDecision,
        reason: str,
    ) -> Dict[str, Any]:
        """Create a decision dict."""
        return {
            "approver": approver,
            "decision": decision,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        }

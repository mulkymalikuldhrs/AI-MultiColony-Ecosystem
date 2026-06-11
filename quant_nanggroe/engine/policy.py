"""
Deterministic Policy Layer
============================
From arXiv research on deterministic policies over probabilistic LLM outputs.

LLM outputs are probabilistic — the same prompt can yield different decisions
across runs. This policy layer enforces deterministic, reproducible, and safe
decisions by:

  1. Confidence Gating: Low-confidence LLM outputs → safe default action
  2. Rule Overrides: Hard rules that override LLM suggestions
  3. Fallback Table: Strategy-specific deterministic defaults
  4. Reproducibility: Same inputs always produce same outputs

Decision flow: LLM → Policy Check → Override if needed → Final Decision
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ─── Default Thresholds ─────────────────────────────────────────────────

DEFAULT_CONFIDENCE_THRESHOLD: float = 0.65
DEFAULT_DRAWDOWN_LIMIT: float = 0.15
DEFAULT_POSITION_CAP_PCT: float = 0.50  # Cap position at 50% in crisis


class PolicyDecision(BaseModel):
    """Result of applying the policy layer."""
    original_action: str = "HOLD"
    final_action: str = "HOLD"
    original_confidence: float = 0.0
    final_confidence: float = 0.0
    overridden: bool = False
    override_reasons: List[str] = Field(default_factory=list)
    policy_hash: str = ""
    timestamp: str = ""


class PolicyLayer:
    """
    Deterministic policy layer over probabilistic LLM outputs.

    Ensures reproducible, auditable, and safe decisions by applying
    rule-based overrides and confidence gating on top of LLM outputs.

    Flow: LLM Output → Confidence Gate → Rule Override → Fallback Table → Final Decision

    Design Principles (from arXiv research):
    - Determinism: Same (llm_output, context) → same final decision
    - Safety: Hard rules override LLM when risk limits are breached
    - Auditability: Every override is logged with reasoning
    - Reproducibility: Policy hash enables exact replay
    """

    def __init__(self, config: Optional[Dict] = None) -> None:
        """
        Initialize the policy layer.

        Args:
            config: Optional configuration dict with keys:
                - confidence_threshold: float (default 0.65)
                - drawdown_limit: float (default 0.15)
                - position_cap_in_crisis: float (default 0.50)
                - custom_rules: list of additional rule dicts
        """
        config = config or {}
        self._confidence_threshold = float(
            config.get("confidence_threshold", DEFAULT_CONFIDENCE_THRESHOLD)
        )
        self._drawdown_limit = float(
            config.get("drawdown_limit", DEFAULT_DRAWDOWN_LIMIT)
        )
        self._position_cap_in_crisis = float(
            config.get("position_cap_in_crisis", DEFAULT_POSITION_CAP_PCT)
        )
        self._rules = self._load_default_rules()
        self._fallback_table = self._load_fallback_table()
        self._decision_log: List[PolicyDecision] = []

        # Load custom rules
        for rule in config.get("custom_rules", []):
            self._rules.append(rule)

    # ─── Core API ───────────────────────────────────────────────────────

    def apply(self, llm_output: Dict, context: Dict) -> Dict:
        """
        Apply deterministic policy over LLM output.

        Args:
            llm_output: Dict from LLM with keys:
                - action: str (e.g., 'BUY', 'SELL', 'HOLD')
                - confidence: float (0.0–1.0)
                - position_size_pct: float (0.0–1.0)
                - reasoning: str
                - strategy: str (optional)
            context: Dict with market/risk context:
                - regime: str (e.g., 'TRENDING_UP', 'PANIC', 'NO_TRADE')
                - current_drawdown: float (0.0–1.0)
                - daily_loss_pct: float (0.0–1.0)
                - volatility_level: str (e.g., 'LOW', 'NORMAL', 'HIGH', 'EXTREME')
                - position_count: int
                - correlation_count: int

        Returns:
            Dict with policy-gated decision:
                - action: str (final action)
                - confidence: float (final confidence)
                - overridden: bool
                - override_reasons: list of str
                - original_action: str
                - original_confidence: float
                - policy_hash: str (for audit/replay)
        """
        original_action = str(llm_output.get("action", "HOLD")).upper()
        original_confidence = float(llm_output.get("confidence", 0.0))
        position_size_pct = float(llm_output.get("position_size_pct", 0.0))

        current_action = original_action
        current_confidence = original_confidence
        overridden = False
        override_reasons: List[str] = []

        # Step 1: Confidence gating
        gate_passed = self._check_confidence_gate(llm_output)
        if not gate_passed:
            safe_action = self._get_fallback_action(llm_output, context)
            override_reasons.append(
                f"Confidence gate: {original_confidence:.2f} < {self._confidence_threshold:.2f} "
                f"→ fallback to {safe_action}"
            )
            current_action = safe_action
            current_confidence = self._confidence_threshold
            overridden = True

        # Step 2: Rule overrides (always applied, even after confidence gate)
        rule_override = self._check_rule_overrides(
            {"action": current_action, "confidence": current_confidence, "position_size_pct": position_size_pct},
            context,
        )
        if rule_override is not None:
            current_action = rule_override.get("action", current_action)
            current_confidence = rule_override.get("confidence", current_confidence)
            override_reasons.append(rule_override["reason"])
            overridden = True

        # Step 3: Position size capping
        capped_pct = self._cap_position_size(position_size_pct, context)
        if capped_pct < position_size_pct:
            override_reasons.append(
                f"Position size capped: {position_size_pct:.4f} → {capped_pct:.4f}"
            )
            overridden = True
            position_size_pct = capped_pct

        # Build result
        policy_hash = self._compute_hash(original_action, original_confidence, context)

        decision = PolicyDecision(
            original_action=original_action,
            final_action=current_action,
            original_confidence=original_confidence,
            final_confidence=current_confidence,
            overridden=overridden,
            override_reasons=override_reasons,
            policy_hash=policy_hash,
        )

        self._decision_log.append(decision)

        result = {
            "action": current_action,
            "confidence": current_confidence,
            "position_size_pct": position_size_pct,
            "overridden": overridden,
            "override_reasons": override_reasons,
            "original_action": original_action,
            "original_confidence": original_confidence,
            "policy_hash": policy_hash,
            "strategy": llm_output.get("strategy", "unknown"),
        }

        if overridden:
            logger.info(
                "[POLICY] Overridden: %s/%.2f → %s/%.2f reasons=%s",
                original_action, original_confidence,
                current_action, current_confidence,
                override_reasons,
            )
        else:
            logger.debug(
                "[POLICY] Passed: %s/%.2f (no override)",
                current_action, current_confidence,
            )

        return result

    # ─── Confidence Gate ────────────────────────────────────────────────

    def _check_confidence_gate(self, llm_output: Dict) -> bool:
        """
        If confidence < threshold, fall back to safe default.

        Returns:
            True if confidence is above threshold, False otherwise.
        """
        confidence = float(llm_output.get("confidence", 0.0))
        return confidence >= self._confidence_threshold

    # ─── Rule Overrides ─────────────────────────────────────────────────

    def _check_rule_overrides(
        self, current: Dict, context: Dict
    ) -> Optional[Dict]:
        """
        Apply hard rules that override LLM suggestions.

        Rules are evaluated in order; first matching rule wins.

        Returns:
            Dict with override action and reason, or None if no override.
        """
        action = current.get("action", "HOLD")
        confidence = current.get("confidence", 0.0)
        drawdown = float(context.get("current_drawdown", 0.0))
        daily_loss = float(context.get("daily_loss_pct", 0.0))
        regime = str(context.get("regime", "UNKNOWN")).upper()
        volatility = str(context.get("volatility_level", "NORMAL")).upper()

        # Rule 1: NO_TRADE regime → force HOLD
        if regime == "NO_TRADE":
            return {
                "action": "HOLD",
                "confidence": 0.0,
                "reason": f"Regime is NO_TRADE → force HOLD",
            }

        # Rule 2: PANIC regime → force HOLD
        if regime == "PANIC":
            return {
                "action": "HOLD",
                "confidence": 0.0,
                "reason": f"Regime is PANIC → force HOLD",
            }

        # Rule 3: Drawdown > 15% → force HOLD
        if drawdown > self._drawdown_limit:
            return {
                "action": "HOLD",
                "confidence": 0.0,
                "reason": f"Drawdown {drawdown:.2%} > {self._drawdown_limit:.2%} limit → force HOLD",
            }

        # Rule 4: Daily loss > 1% → force HOLD
        if daily_loss > 0.01:
            return {
                "action": "HOLD",
                "confidence": 0.0,
                "reason": f"Daily loss {daily_loss:.2%} > 1% limit → force HOLD",
            }

        # Rule 5: RISK_OFF regime → only allow HOLD or reduce size
        if regime == "RISK_OFF" and action in ("BUY", "SELL"):
            return {
                "action": "HOLD",
                "confidence": min(confidence, 0.3),
                "reason": f"Regime is RISK_OFF → downgrade active trade to HOLD",
            }

        # Rule 6: EXTREME volatility → cap at HOLD if not already safe
        if volatility == "EXTREME" and action in ("BUY", "SELL"):
            return {
                "action": "HOLD",
                "confidence": min(confidence, 0.3),
                "reason": f"EXTREME volatility → downgrade to HOLD",
            }

        # Rule 7: Position concentration check
        position_count = int(context.get("position_count", 0))
        if position_count >= 10 and action in ("BUY", "SELL"):
            return {
                "action": "HOLD",
                "confidence": min(confidence, 0.4),
                "reason": f"Too many open positions ({position_count} ≥ 10) → force HOLD",
            }

        # No override
        return None

    # ─── Position Size Capping ──────────────────────────────────────────

    def _cap_position_size(self, position_size_pct: float, context: Dict) -> float:
        """
        Cap position size based on market conditions.

        - PANIC / NO_TRADE: zero positions allowed
        - RISK_OFF: reduce to 50% of suggested size
        - VOLATILE: cap at DEFAULT_POSITION_CAP_PCT of portfolio
        """
        regime = str(context.get("regime", "UNKNOWN")).upper()

        if regime in ("PANIC", "NO_TRADE"):
            return 0.0  # No positions allowed

        if regime == "RISK_OFF":
            # Reduce position to half of suggested
            return position_size_pct * 0.5

        # VOLATILE: cap at absolute maximum
        if regime == "VOLATILE":
            return min(position_size_pct, self._position_cap_in_crisis)

        return position_size_pct

    # ─── Fallback Table ─────────────────────────────────────────────────

    def _get_fallback_action(self, llm_output: Dict, context: Dict) -> str:
        """
        Get deterministic fallback action for low-confidence LLM outputs.

        Strategy-specific fallbacks ensure sensible defaults.
        """
        strategy = str(llm_output.get("strategy", "")).lower()
        action = str(llm_output.get("action", "HOLD")).upper()

        # Strategy-specific fallbacks
        if strategy in self._fallback_table:
            return self._fallback_table[strategy]

        # General fallback: if LLM said BUY/SELL but low confidence, default to HOLD
        if action in ("BUY", "SELL"):
            return "HOLD"

        return "HOLD"

    # ─── Loading ────────────────────────────────────────────────────────

    def _load_default_rules(self) -> List[Dict[str, Any]]:
        """Load default deterministic override rules."""
        return [
            {
                "name": "no_trade_regime",
                "condition": lambda ctx: ctx.get("regime", "").upper() == "NO_TRADE",
                "action": "HOLD",
                "reason": "NO_TRADE regime forces HOLD",
            },
            {
                "name": "panic_regime",
                "condition": lambda ctx: ctx.get("regime", "").upper() == "PANIC",
                "action": "HOLD",
                "reason": "PANIC regime forces HOLD",
            },
            {
                "name": "drawdown_limit",
                "condition": lambda ctx: float(ctx.get("current_drawdown", 0)) > self._drawdown_limit,
                "action": "HOLD",
                "reason": "Drawdown exceeds limit",
            },
        ]

    def _load_fallback_table(self) -> Dict[str, str]:
        """
        Load deterministic fallback table per strategy type.

        When LLM confidence is below threshold, these defaults are used
        instead of the LLM's suggested action.
        """
        return {
            "momentum": "HOLD",          # Momentum: no signal → wait
            "mean_reversion": "HOLD",    # Mean reversion: no clear deviation → wait
            "pairs_trading": "HOLD",     # Pairs: no divergence → wait
            "market_making": "HOLD",     # MM: low confidence → stay flat
            "volatility_arbitrage": "HOLD",  # Vol arb: uncertain → wait
            "crypto_momentum": "HOLD",   # Crypto: uncertain → wait
            "statistical_arbitrage": "HOLD",  # Stat arb: no edge → wait
            "regime_based": "HOLD",      # Regime: unclear regime → wait
        }

    # ─── Hashing for Reproducibility ────────────────────────────────────

    @staticmethod
    def _compute_hash(action: str, confidence: float, context: Dict) -> str:
        """
        Compute a deterministic hash of the decision inputs.

        Same inputs → same hash → reproducible audit trail.
        """
        canonical = json.dumps(
            {"action": action, "confidence": round(confidence, 4), "context": context},
            sort_keys=True,
            default=str,
        )
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]

    # ─── Reporting ──────────────────────────────────────────────────────

    def get_decision_log(self, limit: int = 100) -> List[PolicyDecision]:
        """Get recent policy decisions."""
        return self._decision_log[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get policy layer statistics."""
        total = len(self._decision_log)
        if total == 0:
            return {"total": 0, "overridden": 0, "override_rate": 0.0}
        overridden = sum(1 for d in self._decision_log if d.overridden)
        return {
            "total": total,
            "overridden": overridden,
            "override_rate": overridden / total,
            "confidence_threshold": self._confidence_threshold,
            "drawdown_limit": self._drawdown_limit,
        }

    def get_fallback_table(self) -> Dict[str, str]:
        """Get the current fallback table."""
        return dict(self._fallback_table)

    def add_fallback(self, strategy: str, default_action: str) -> None:
        """Add or update a fallback entry for a strategy."""
        self._fallback_table[strategy.lower()] = default_action.upper()

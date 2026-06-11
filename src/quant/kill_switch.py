"""
Kill Switch - Emergency halt system with manual reset after review.
Auto-triggers when risk limits are breached.

Source: HermesQuantOS
"""

from __future__ import annotations

import logging
from datetime import datetime

from pydantic import BaseModel, Field

from src.quant.risk_officer import MAX_DAILY_LOSS, MAX_WEEKLY_LOSS

logger = logging.getLogger("ecosystem.quant.kill_switch")


class KillSwitchState(BaseModel):
    """Kill switch state."""
    is_active: bool = False
    activated_at: str | None = None
    activation_reason: str | None = None
    auto_triggers: int = 0
    manual_triggers: int = 0


class KillSwitchTool:
    """L4 Agent: Kill Switch - Emergency halt system."""

    CONFIRMATION_PHRASE = "CONFIRM_RESET_AFTER_REVIEW"

    def __init__(self) -> None:
        self._state = KillSwitchState()

    @property
    def is_active(self) -> bool:
        return self._state.is_active

    def activate(self, reason: str = "MANUAL") -> dict:
        """Activate kill switch - halts all trading."""
        self._state.is_active = True
        self._state.activated_at = datetime.now().isoformat()
        self._state.activation_reason = reason

        if reason.startswith("AUTO_"):
            self._state.auto_triggers += 1
        else:
            self._state.manual_triggers += 1

        logger.critical("KILL SWITCH ACTIVATED: %s", reason)

        return {
            "status": "ACTIVATED",
            "reason": reason,
            "activated_at": self._state.activated_at,
            "message": "ALL TRADING HALTED. Manual reset required after review.",
            "auto_triggers_total": self._state.auto_triggers,
            "manual_triggers_total": self._state.manual_triggers,
        }

    def reset(self, confirmation: str = "") -> dict:
        """Reset kill switch - requires explicit confirmation."""
        if confirmation != self.CONFIRMATION_PHRASE:
            return {
                "status": "STILL_ACTIVE",
                "message": "Kill switch requires explicit confirmation to reset.",
                "confirmation_required": self.CONFIRMATION_PHRASE,
            }

        self._state.is_active = False
        self._state.activated_at = None
        self._state.activation_reason = None

        logger.info("Kill switch RESET after review")

        return {
            "status": "RESET",
            "message": "Kill switch deactivated. Trading resumed.",
        }

    def check_auto_trigger(self, daily_pnl_pct: float, weekly_pnl_pct: float) -> dict:
        """Auto-check if kill switch should trigger based on risk limits."""
        if abs(min(0, daily_pnl_pct)) >= MAX_DAILY_LOSS:
            return self.activate("AUTO_DAILY_LIMIT")

        if abs(min(0, weekly_pnl_pct)) >= MAX_WEEKLY_LOSS:
            return self.activate("AUTO_WEEKLY_LIMIT")

        return {
            "status": "OK" if not self._state.is_active else "ACTIVE",
            "daily_pnl": f"{daily_pnl_pct:.2%}",
            "weekly_pnl": f"{weekly_pnl_pct:.2%}",
        }

    def status(self) -> dict:
        """Get kill switch status."""
        return {
            "is_active": self._state.is_active,
            "activated_at": self._state.activated_at,
            "activation_reason": self._state.activation_reason,
            "auto_triggers": self._state.auto_triggers,
            "manual_triggers": self._state.manual_triggers,
            "message": "TRADING HALTED" if self._state.is_active else "System operational",
        }

"""Kill Switch — Emergency Halt Mechanism.

Implements the emergency kill switch that automatically activates
when constitutional risk limits are breached. Once activated,
ALL trading is halted and can only be reset after manual review.

Activation triggers:
- AUTO_DAILY_LIMIT: Daily loss limit breached
- AUTO_WEEKLY_LIMIT: Weekly loss limit breached
- AUTO_MAX_DRAWDOWN: Maximum drawdown breached
- MANUAL: Manual activation by human operator

Reset requires explicit confirmation: "CONFIRM_RESET_AFTER_REVIEW"

Persistence:
- Kill switch state is persisted to data/kill_switch_state.json
- On initialization, if persisted state is active, trading is REFUSED
  until manually reset with explicit confirmation
- This ensures that a process restart cannot bypass the kill switch

Extracted from HermesQuantOS's KillSwitchTool.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Confirmation string required for reset (prevents accidental reset)
RESET_CONFIRMATION: str = "CONFIRM_RESET_AFTER_REVIEW"

# Default persistence path
_DEFAULT_STATE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
_DEFAULT_STATE_FILE = _DEFAULT_STATE_DIR / "kill_switch_state.json"


class KillSwitch:
    """Emergency Kill Switch with file-based persistence.

    Once activated, ALL trading is halted. The kill switch can only
    be reset after explicit manual review and confirmation.

    This is the ultimate safety net — no agent or system can
    bypass or override the kill switch.

    Persistence ensures that a process restart does NOT clear
    the kill switch. If it was active before restart, it remains
    active until explicitly reset with confirmation.
    """

    def __init__(
        self,
        state_file: Optional[Path] = None,
    ) -> None:
        self._is_active: bool = False
        self._activated_at: Optional[str] = None
        self._activation_reason: Optional[str] = None
        self._auto_triggers: int = 0
        self._manual_triggers: int = 0
        self._activation_log: list = []

        # Persistence
        self._state_file: Path = state_file or _DEFAULT_STATE_FILE

        # On initialization, check for persisted active state
        self._load_persisted_state()

    @property
    def is_active(self) -> bool:
        """Whether the kill switch is currently active."""
        return self._is_active

    def activate(self, reason: str = "MANUAL") -> Dict[str, any]:
        """Activate kill switch — halts ALL trading.

        Args:
            reason: Activation reason.

        Returns:
            Dict with activation status.
        """
        if self._is_active:
            return {
                "status": "ALREADY_ACTIVE",
                "reason": self._activation_reason,
                "activated_at": self._activated_at,
            }

        self._is_active = True
        self._activated_at = datetime.now().isoformat()
        self._activation_reason = reason

        if reason.startswith("AUTO_"):
            self._auto_triggers += 1
        else:
            self._manual_triggers += 1

        self._activation_log.append({
            "activated_at": self._activated_at,
            "reason": reason,
        })

        # Persist state to disk
        self._persist_state()

        logger.critical("⚠️ KILL SWITCH ACTIVATED: %s", reason)

        return {
            "status": "ACTIVATED",
            "reason": reason,
            "activated_at": self._activated_at,
            "message": "ALL TRADING HALTED. Manual reset required after review.",
            "auto_triggers_total": self._auto_triggers,
            "manual_triggers_total": self._manual_triggers,
        }

    def reset(self, confirmation: str = "") -> Dict[str, any]:
        """Reset kill switch — requires explicit confirmation.

        Args:
            confirmation: Must be exactly "CONFIRM_RESET_AFTER_REVIEW".

        Returns:
            Dict with reset status.
        """
        if not self._is_active:
            return {
                "status": "NOT_ACTIVE",
                "message": "Kill switch is not currently active.",
            }

        if confirmation != RESET_CONFIRMATION:
            return {
                "status": "STILL_ACTIVE",
                "message": "Kill switch requires explicit confirmation to reset.",
                "confirmation_required": RESET_CONFIRMATION,
                "note": "Review all trades and risk status before resetting.",
            }

        self._is_active = False
        self._activated_at = None
        self._activation_reason = None

        # Persist the reset state
        self._persist_state()

        logger.info("Kill switch RESET after review")

        return {
            "status": "RESET",
            "message": "Kill switch deactivated. Trading resumed.",
            "note": "Ensure risk parameters are reviewed before resuming.",
        }

    def status(self) -> Dict[str, any]:
        """Get kill switch status."""
        return {
            "is_active": self._is_active,
            "activated_at": self._activated_at,
            "activation_reason": self._activation_reason,
            "auto_triggers": self._auto_triggers,
            "manual_triggers": self._manual_triggers,
            "total_activations": self._auto_triggers + self._manual_triggers,
            "message": "TRADING HALTED" if self._is_active else "System operational",
            "persisted": self._state_file.exists(),
        }

    def check_auto_trigger(
        self,
        daily_loss_pct: float,
        weekly_loss_pct: float,
        drawdown_pct: float = 0.0,
    ) -> Optional[Dict[str, any]]:
        """Auto-check if kill switch should trigger based on risk limits.

        Uses the KILL_SWITCH thresholds (early warning) from constants.py,
        which trigger BEFORE the hard constitutional limits.

        Args:
            daily_loss_pct: Current daily loss as fraction.
            weekly_loss_pct: Current weekly loss as fraction.
            drawdown_pct: Current drawdown as fraction.

        Returns:
            Activation dict if triggered, None otherwise.
        """
        from quant_nanggroe.engine.risk.constants import (
            MAX_DAILY_LOSS,
            MAX_WEEKLY_LOSS,
            MAX_DRAWDOWN_PCT,
            KILL_SWITCH_DAILY_PNL,
            KILL_SWITCH_WEEKLY_PNL,
        )
        MAX_DRAWDOWN = MAX_DRAWDOWN_PCT

        # Kill switch triggers at the early warning thresholds
        if daily_loss_pct >= abs(KILL_SWITCH_DAILY_PNL):
            return self.activate("AUTO_DAILY_LIMIT")

        # Also check the hard limit (belt and suspenders)
        if daily_loss_pct >= MAX_DAILY_LOSS:
            return self.activate("AUTO_DAILY_LIMIT_HARD")

        if weekly_loss_pct >= abs(KILL_SWITCH_WEEKLY_PNL):
            return self.activate("AUTO_WEEKLY_LIMIT")

        if weekly_loss_pct >= MAX_WEEKLY_LOSS:
            return self.activate("AUTO_WEEKLY_LIMIT_HARD")

        if drawdown_pct >= MAX_DRAWDOWN:
            return self.activate("AUTO_MAX_DRAWDOWN")

        return None

    # ── Persistence Methods ──────────────────────────────────────────────

    def _persist_state(self) -> None:
        """Save kill switch state to disk.

        Ensures the state directory exists and writes the current
        state as JSON. If the kill switch is active, the file serves
        as a lock that prevents trading even after restart.
        """
        try:
            self._state_file.parent.mkdir(parents=True, exist_ok=True)

            state_data = {
                "is_active": self._is_active,
                "activated_at": self._activated_at,
                "activation_reason": self._activation_reason,
                "auto_triggers": self._auto_triggers,
                "manual_triggers": self._manual_triggers,
                "activation_log": self._activation_log[-100:],  # Keep last 100
                "persisted_at": datetime.now().isoformat(),
            }

            # Write atomically via temp file
            temp_file = self._state_file.with_suffix(".tmp")
            with open(temp_file, "w") as f:
                json.dump(state_data, f, indent=2)
            temp_file.replace(self._state_file)

            logger.debug("Kill switch state persisted to %s", self._state_file)

        except Exception as e:
            logger.error("Failed to persist kill switch state: %s", e)
            # Non-fatal: the kill switch still works in-memory

    def _load_persisted_state(self) -> None:
        """Load kill switch state from disk.

        If the persisted state shows the kill switch was active,
        it remains active. This ensures that a process restart
        cannot bypass the kill switch.
        """
        if not self._state_file.exists():
            return

        try:
            with open(self._state_file, "r") as f:
                state_data = json.load(f)

            # Restore counters and log (always, regardless of active state)
            self._auto_triggers = state_data.get("auto_triggers", 0)
            self._manual_triggers = state_data.get("manual_triggers", 0)
            self._activation_log = state_data.get("activation_log", [])

            # If kill switch was active, keep it active!
            if state_data.get("is_active", False):
                self._is_active = True
                self._activated_at = state_data.get("activated_at")
                self._activation_reason = state_data.get("activation_reason")

                logger.critical(
                    "⚠️ KILL SWITCH PERSISTED ACTIVE from previous session! "
                    "Reason: %s | Activated at: %s | "
                    "Trading is REFUSED until manually reset with confirmation.",
                    self._activation_reason,
                    self._activated_at,
                )

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error("Failed to load kill switch state from %s: %s", self._state_file, e)
            # Non-fatal: start with clean in-memory state

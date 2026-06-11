"""
Risk Officer - 9-checkpoint risk validation with hardcoded limits and FULL VETO authority.
Risk Rules HARDCODED: 0.5%/trade, 1%/day, 3%/week - NO OVERRIDE POSSIBLE.

Source: HermesQuantOS
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.quant.risk_officer")

# HARDCODED RISK LIMITS - NO OVERRIDE POSSIBLE
MAX_RISK_PER_TRADE = 0.005    # 0.5% max risk per trade
MAX_DAILY_LOSS = 0.01         # 1% max daily loss
MAX_WEEKLY_LOSS = 0.03        # 3% max weekly loss
MIN_RISK_REWARD = 2.0         # Minimum 1:2 R:R ratio
MAX_CORRELATED_POSITIONS = 3  # Max correlated positions


class RiskCheckResult(BaseModel):
    """Result of a risk check."""
    symbol: str
    direction: str
    lot_size: float
    entry: float
    stop_loss: float
    take_profit: Optional[float] = None
    risk_pct: str = ""
    rr_ratio: str = ""
    verdict: str  # APPROVED or VETOED
    checkpoints: dict = Field(default_factory=dict)
    veto_count_total: int = 0
    approval_count_total: int = 0
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class RiskOfficerTool:
    """L3 Agent: Risk Officer - FULL VETO, hardcoded risk rules."""

    # Correlated symbol groups
    CORRELATED_GROUPS: list[set[str]] = [
        {"EURUSD", "GBPUSD", "AUDUSD", "NZDUSD"},
        {"USDJPY", "USDCHF", "USDCAD"},
        {"XAUUSD", "XAGUSD"},
        {"BTCUSDT", "ETHUSDT", "SHIB", "TRX"},
    ]

    def __init__(self, account_balance: float = 10000.0) -> None:
        self.account_balance = account_balance
        self.daily_pnl = 0.0  # Track as fraction of account balance
        self.weekly_pnl = 0.0  # Track as fraction of account balance
        self.trade_count_today = 0
        self.trade_count_week = 0
        self.active_positions: list[str] = []
        self.veto_count = 0
        self.approval_count = 0
        self.last_reset = datetime.now().date()

    def _reset_daily_if_needed(self) -> None:
        """Reset daily counters if new day."""
        today = datetime.now().date()
        if today > self.last_reset:
            self.daily_pnl = 0.0
            self.trade_count_today = 0
            self.last_reset = today

    def check_trade(
        self,
        symbol: str,
        direction: str,
        lot_size: float,
        entry: float,
        stop_loss: float,
        account_balance: float = 10000.0,
        take_profit: Optional[float] = None,
    ) -> RiskCheckResult:
        """9-checkpoint risk validation. Returns APPROVED or VETOED."""
        self._reset_daily_if_needed()

        checkpoints: dict = {}
        all_passed = True

        # Checkpoint 1: Risk per trade limit
        risk_amount = abs(entry - stop_loss) * lot_size * 100000
        risk_pct = risk_amount / account_balance if account_balance > 0 else 1.0
        checkpoints["1_risk_per_trade"] = {
            "value": f"{risk_pct:.4f}",
            "limit": f"{MAX_RISK_PER_TRADE:.4f}",
            "passed": risk_pct <= MAX_RISK_PER_TRADE,
        }
        if not checkpoints["1_risk_per_trade"]["passed"]:
            all_passed = False

        # Checkpoint 2: Daily loss limit
        daily_loss_pct = abs(min(0, self.daily_pnl)) if self.daily_pnl < 0 else 0
        checkpoints["2_daily_loss"] = {
            "value": f"{daily_loss_pct:.4f}",
            "limit": f"{MAX_DAILY_LOSS:.4f}",
            "passed": daily_loss_pct < MAX_DAILY_LOSS,
        }
        if not checkpoints["2_daily_loss"]["passed"]:
            all_passed = False

        # Checkpoint 3: Weekly loss limit
        weekly_loss_pct = abs(min(0, self.weekly_pnl)) if self.weekly_pnl < 0 else 0
        checkpoints["3_weekly_loss"] = {
            "value": f"{weekly_loss_pct:.4f}",
            "limit": f"{MAX_WEEKLY_LOSS:.4f}",
            "passed": weekly_loss_pct < MAX_WEEKLY_LOSS,
        }
        if not checkpoints["3_weekly_loss"]["passed"]:
            all_passed = False

        # Checkpoint 4: Risk:Reward ratio
        if take_profit and stop_loss:
            rr_ratio = abs(take_profit - entry) / abs(entry - stop_loss) if abs(entry - stop_loss) > 0 else 0
        else:
            rr_ratio = 0
        checkpoints["4_risk_reward"] = {
            "value": f"1:{rr_ratio:.1f}",
            "limit": f"1:{MIN_RISK_REWARD:.1f}",
            "passed": rr_ratio >= MIN_RISK_REWARD,
        }
        if not checkpoints["4_risk_reward"]["passed"]:
            all_passed = False

        # Checkpoint 5: Stop loss exists
        checkpoints["5_stop_loss_exists"] = {
            "value": str(stop_loss is not None and stop_loss > 0),
            "limit": "True",
            "passed": stop_loss is not None and stop_loss > 0,
        }
        if not checkpoints["5_stop_loss_exists"]["passed"]:
            all_passed = False

        # Checkpoint 6: Entry is valid
        checkpoints["6_valid_entry"] = {
            "value": str(entry > 0),
            "limit": "True",
            "passed": entry > 0,
        }
        if not checkpoints["6_valid_entry"]["passed"]:
            all_passed = False

        # Checkpoint 7: Direction is valid
        valid_dirs = {"BUY", "SELL", "LONG", "SHORT"}
        checkpoints["7_valid_direction"] = {
            "value": direction.upper(),
            "limit": "BUY/SELL",
            "passed": direction.upper() in valid_dirs,
        }
        if not checkpoints["7_valid_direction"]["passed"]:
            all_passed = False

        # Checkpoint 8: Not overtrading
        checkpoints["8_not_overtrading"] = {
            "value": str(self.trade_count_today),
            "limit": "5",
            "passed": self.trade_count_today < 5,
        }
        if not checkpoints["8_not_overtrading"]["passed"]:
            all_passed = False

        # Checkpoint 9: Correlated position check
        correlated = sum(1 for p in self.active_positions if self._is_correlated(p, symbol))
        checkpoints["9_correlation_check"] = {
            "value": str(correlated),
            "limit": str(MAX_CORRELATED_POSITIONS),
            "passed": correlated < MAX_CORRELATED_POSITIONS,
        }
        if not checkpoints["9_correlation_check"]["passed"]:
            all_passed = False

        verdict = "APPROVED" if all_passed else "VETOED"
        if verdict == "VETOED":
            self.veto_count += 1
        else:
            self.approval_count += 1

        logger.info("RISK CHECK: %s %s -> %s", symbol, direction, verdict)

        return RiskCheckResult(
            symbol=symbol,
            direction=direction.upper(),
            lot_size=lot_size,
            entry=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_pct=f"{risk_pct:.4f}",
            rr_ratio=f"1:{rr_ratio:.1f}" if rr_ratio > 0 else "N/A",
            verdict=verdict,
            checkpoints=checkpoints,
            veto_count_total=self.veto_count,
            approval_count_total=self.approval_count,
        )

    def _is_correlated(self, position_symbol: str, new_symbol: str) -> bool:
        """Check if two symbols are correlated."""
        for group in self.CORRELATED_GROUPS:
            if position_symbol.upper() in group and new_symbol.upper() in group:
                return True
        return False

    def calculate_lot_size(
        self, account_balance: float, risk_pct: float, stop_loss_pips: float, pip_value: float = 10.0
    ) -> dict:
        """Calculate proper lot size. Risk_pct is capped at MAX_RISK_PER_TRADE regardless of input."""
        effective_risk = min(risk_pct, MAX_RISK_PER_TRADE)
        risk_amount = account_balance * effective_risk
        lot_size = risk_amount / (stop_loss_pips * pip_value) if stop_loss_pips > 0 else 0
        lot_size = max(0.01, round(lot_size * 100) / 100)

        return {
            "account_balance": account_balance,
            "requested_risk_pct": f"{risk_pct:.4f}",
            "effective_risk_pct": f"{effective_risk:.4f}",
            "capped": risk_pct > MAX_RISK_PER_TRADE,
            "risk_amount": round(risk_amount, 2),
            "stop_loss_pips": stop_loss_pips,
            "lot_size": lot_size,
        }

    def update_pnl(self, trade_pnl: float, account_balance: Optional[float] = None) -> None:
        """Update daily and weekly PnL tracking.
        
        Args:
            trade_pnl: Absolute PnL from the trade (e.g., +50.0 or -200.0)
            account_balance: Current account balance. If provided, updates the stored balance
                             and tracks PnL as a fraction for percentage-based comparisons.
        """
        self._reset_daily_if_needed()
        if account_balance is not None:
            self.account_balance = account_balance
        # Convert absolute PnL to fraction of account balance for percentage comparison
        if self.account_balance > 0:
            pnl_fraction = trade_pnl / self.account_balance
        else:
            pnl_fraction = 0.0
        self.daily_pnl += pnl_fraction
        self.weekly_pnl += pnl_fraction
        self.trade_count_today += 1
        self.trade_count_week += 1

    def status(self) -> dict:
        """Get current risk status."""
        self._reset_daily_if_needed()
        daily_status = "OK" if abs(min(0, self.daily_pnl)) < MAX_DAILY_LOSS else "LIMIT_REACHED"
        weekly_status = "OK" if abs(min(0, self.weekly_pnl)) < MAX_WEEKLY_LOSS else "LIMIT_REACHED"
        overall = "TRADING_ALLOWED" if daily_status == "OK" and weekly_status == "OK" else "KILL_SWITCH_ACTIVE"

        return {
            "overall_status": overall,
            "daily_pnl": f"{self.daily_pnl:.2%}",
            "weekly_pnl": f"{self.weekly_pnl:.2%}",
            "daily_limit": f"{MAX_DAILY_LOSS:.2%}",
            "weekly_limit": f"{MAX_WEEKLY_LOSS:.2%}",
            "daily_status": daily_status,
            "weekly_status": weekly_status,
            "trades_today": self.trade_count_today,
            "trades_week": self.trade_count_week,
            "veto_count": self.veto_count,
            "approval_count": self.approval_count,
            "active_positions": len(self.active_positions),
            "hardcoded_limits": {
                "max_risk_per_trade": f"{MAX_RISK_PER_TRADE:.2%}",
                "max_daily_loss": f"{MAX_DAILY_LOSS:.2%}",
                "max_weekly_loss": f"{MAX_WEEKLY_LOSS:.2%}",
                "min_rr_ratio": f"1:{MIN_RISK_REWARD}",
                "override_possible": False,
            },
        }

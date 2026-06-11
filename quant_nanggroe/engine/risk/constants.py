"""Constitutional Risk Limits for Quant Nanggroe AI.

These values are HARDCODED and CANNOT be overridden at runtime.
They represent the absolute maximum risk tolerances for the system.

All risk modules MUST import constants from this file to avoid circular imports.
These values are the single source of truth — they must match agents/state.py.

The constants are implemented using a metaclass that makes them read-only
after class creation. Any attempt to modify them at runtime raises
AttributeError.
"""


class _ConstantsMeta(type):
    """Metaclass that makes all class attributes read-only after creation.

    Once the class body has executed and the attributes are defined,
    any attempt to set or delete them raises AttributeError. This
    prevents runtime mutation of constitutional risk limits like
    ``constants.MAX_LEVERAGE = 999``.
    """

    def __setattr__(cls, name: str, value: object) -> None:
        raise AttributeError(
            f"Cannot modify constitutional constant '{name}' on {cls.__name__}. "
            f"Constitutional risk limits are immutable at runtime."
        )

    def __delattr__(cls, name: str) -> None:
        raise AttributeError(
            f"Cannot delete constitutional constant '{name}' on {cls.__name__}. "
            f"Constitutional risk limits are immutable at runtime."
        )


class _ConstitutionalConstants(metaclass=_ConstantsMeta):
    """Constitutional risk limits — immutable at runtime.

    These values are the single source of truth for all risk limits.
    They CANNOT be changed at runtime, even via direct attribute
    assignment on the class or module.
    """

    MAX_RISK_PER_TRADE: float = 0.005       # 0.5% max risk per trade
    MAX_DAILY_LOSS: float = 0.01            # 1% max daily loss
    MAX_WEEKLY_LOSS: float = 0.03           # 3% max weekly loss
    MIN_RISK_REWARD: float = 2.0            # Minimum 1:2 R:R ratio
    MAX_CORRELATED_POSITIONS: int = 3       # Max correlated positions
    MAX_POSITION_SIZE_PCT: float = 0.10     # Max 10% of portfolio in single position
    MAX_LEVERAGE: float = 3.0               # Max 3x leverage
    MAX_DRAWDOWN_PCT: float = 0.15          # Max 15% drawdown before kill switch
    MAX_DAILY_TRADES: int = 5               # Max 5 trades per day to prevent overtrading
    CONFIDENCE_THRESHOLD: float = 0.65      # Below this, trigger council debate
    KILL_SWITCH_DAILY_PNL: float = -0.02    # Kill switch at -2% daily PnL
    KILL_SWITCH_WEEKLY_PNL: float = -0.05   # Kill switch at -5% weekly PnL
    MAX_PORTFOLIO_VAR_PCT: float = 0.02      # Max 2% portfolio VaR
    MAX_SECTOR_EXPOSURE_PCT: float = 0.30    # Max 30% exposure to single sector
    NO_NAKED_SHORT: bool = True              # Naked short selling is FORBIDDEN


# ─── Module-level constants (expose class attributes as module constants) ──
# These are the public API that other modules import. They delegate to the
# immutable class so that ``from constants import MAX_LEVERAGE`` works while
# still preventing ``constants.MAX_LEVERAGE = 999``.
MAX_RISK_PER_TRADE: float = _ConstitutionalConstants.MAX_RISK_PER_TRADE
MAX_DAILY_LOSS: float = _ConstitutionalConstants.MAX_DAILY_LOSS
MAX_WEEKLY_LOSS: float = _ConstitutionalConstants.MAX_WEEKLY_LOSS
MIN_RISK_REWARD: float = _ConstitutionalConstants.MIN_RISK_REWARD
MAX_CORRELATED_POSITIONS: int = _ConstitutionalConstants.MAX_CORRELATED_POSITIONS
MAX_POSITION_SIZE_PCT: float = _ConstitutionalConstants.MAX_POSITION_SIZE_PCT
MAX_LEVERAGE: float = _ConstitutionalConstants.MAX_LEVERAGE
MAX_DRAWDOWN_PCT: float = _ConstitutionalConstants.MAX_DRAWDOWN_PCT
MAX_DAILY_TRADES: int = _ConstitutionalConstants.MAX_DAILY_TRADES
CONFIDENCE_THRESHOLD: float = _ConstitutionalConstants.CONFIDENCE_THRESHOLD
KILL_SWITCH_DAILY_PNL: float = _ConstitutionalConstants.KILL_SWITCH_DAILY_PNL
KILL_SWITCH_WEEKLY_PNL: float = _ConstitutionalConstants.KILL_SWITCH_WEEKLY_PNL
MAX_PORTFOLIO_VAR_PCT: float = _ConstitutionalConstants.MAX_PORTFOLIO_VAR_PCT
MAX_SECTOR_EXPOSURE_PCT: float = _ConstitutionalConstants.MAX_SECTOR_EXPOSURE_PCT
NO_NAKED_SHORT: bool = _ConstitutionalConstants.NO_NAKED_SHORT

"""Regime-Aware Strategy Adapter — wraps strategies to make them regime-aware.

Adjusts position sizing, blocks incompatible strategies, and applies
regime-specific parameter overrides based on the current market regime.

Design rationale:
  - BULL:    Increase position size (up to 1.5x), allow all strategies.
  - BEAR:    Reduce position size (0.5x), block momentum strategies.
  - SIDEWAYS: Default position size, favor mean-reversion.
  - CRISIS:  Minimum position size (0.2x), block momentum and breakout.
  - RECOVERY: Moderate increase (1.2x), allow all but with caution.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set

from quant_nanggroe.engine.regime.detector import RegimeDetector
from quant_nanggroe.engine.regime.types import RegimeResult, RegimeType
from quant_nanggroe.engine.strategies.base import (
    SignalDirection,
    Strategy,
    StrategySignal,
)

logger = logging.getLogger(__name__)

# ─── Regime-specific position size multipliers ────────────────────────────────
REGIME_SIZE_MULTIPLIER: Dict[RegimeType, float] = {
    RegimeType.BULL: 1.5,
    RegimeType.RECOVERY: 1.2,
    RegimeType.SIDEWAYS: 1.0,
    RegimeType.BEAR: 0.5,
    RegimeType.CRISIS: 0.2,
}

# ─── Strategies blocked per regime ────────────────────────────────────────────
# Momentum strategies are dangerous in CRISIS/BEAR; breakout strategies fail
# in CRISIS; mean-reversion fails in strong BULL trends (not blocked by default).
BLOCKED_STRATEGIES: Dict[RegimeType, Set[str]] = {
    RegimeType.CRISIS: {"momentum", "breakout", "trend_following"},
    RegimeType.BEAR: {"momentum", "breakout"},
    RegimeType.SIDEWAYS: set(),
    RegimeType.BULL: set(),
    RegimeType.RECOVERY: set(),
}

# ─── Default parameter overrides per regime ───────────────────────────────────
DEFAULT_PARAM_OVERRIDES: Dict[RegimeType, Dict[str, Any]] = {
    RegimeType.CRISIS: {
        "stop_loss_multiplier": 0.5,    # Tighter stops
        "take_profit_multiplier": 0.5,  # Smaller targets
        "max_position_pct": 0.02,       # 2% max position
    },
    RegimeType.BEAR: {
        "stop_loss_multiplier": 0.75,
        "take_profit_multiplier": 0.75,
        "max_position_pct": 0.05,
    },
    RegimeType.SIDEWAYS: {
        "stop_loss_multiplier": 1.0,
        "take_profit_multiplier": 1.0,
        "max_position_pct": 0.10,
    },
    RegimeType.BULL: {
        "stop_loss_multiplier": 1.5,
        "take_profit_multiplier": 2.0,
        "max_position_pct": 0.15,
    },
    RegimeType.RECOVERY: {
        "stop_loss_multiplier": 1.0,
        "take_profit_multiplier": 1.2,
        "max_position_pct": 0.10,
    },
}


class RegimeAwareStrategyAdapter:
    """Wraps a Strategy to make it regime-aware.

    Adjusts position sizing, blocks execution in incompatible regimes,
    and applies regime-specific parameter overrides.

    Args:
        strategy: The underlying strategy to wrap.
        detector: RegimeDetector instance for regime classification.
        param_overrides: Optional custom parameter overrides per regime.
            If None, uses DEFAULT_PARAM_OVERRIDES.
        blocked_strategies: Optional custom blocked strategy names per regime.
            If None, uses BLOCKED_STRATEGIES.
    """

    def __init__(
        self,
        strategy: Strategy,
        detector: RegimeDetector,
        param_overrides: Optional[Dict[RegimeType, Dict[str, Any]]] = None,
        blocked_strategies: Optional[Dict[RegimeType, Set[str]]] = None,
    ) -> None:
        self._strategy = strategy
        self._detector = detector
        self._param_overrides = param_overrides or DEFAULT_PARAM_OVERRIDES
        self._blocked_strategies = blocked_strategies or BLOCKED_STRATEGIES
        self._last_regime_result: Optional[RegimeResult] = None

    # ─── Properties ──────────────────────────────────────────────────────

    @property
    def strategy(self) -> Strategy:
        """Access the wrapped strategy."""
        return self._strategy

    @property
    def last_regime_result(self) -> Optional[RegimeResult]:
        """Most recent regime detection result."""
        return self._last_regime_result

    # ─── Public API ──────────────────────────────────────────────────────

    def generate_signal(
        self,
        data: Any,
        returns: Optional[Any] = None,
        **kwargs,
    ) -> Optional[StrategySignal]:
        """Generate a regime-adjusted trading signal.

        Args:
            data: Market data (typically DataFrame with OHLCV).
            returns: Return series for regime detection. If None,
                attempts to compute from data if it has a 'close' column.
            **kwargs: Additional arguments passed to underlying strategy.

        Returns:
            Adjusted StrategySignal, or None if strategy is blocked
            in the current regime.
        """
        # Detect regime
        regime_result = self._detect_regime_from_data(data, returns)
        self._last_regime_result = regime_result

        # Check if strategy is blocked in current regime
        if self._is_strategy_blocked(regime_result.current_regime):
            logger.info(
                "Strategy '%s' blocked in %s regime",
                self._strategy.name,
                regime_result.current_regime.value,
            )
            return None

        # Apply parameter overrides
        self._apply_param_overrides(regime_result.current_regime)

        # Generate base signal
        signal = self._strategy.generate_signal(data, **kwargs)

        if signal is None:
            return None

        # Adjust position sizing based on regime
        signal = self._adjust_signal(signal, regime_result.current_regime)

        # Add regime metadata
        signal.indicators["regime"] = regime_result.current_regime.value
        signal.indicators["regime_confidence"] = regime_result.confidence

        return signal

    def get_position_size_multiplier(self, regime: RegimeType) -> float:
        """Get position size multiplier for a given regime.

        Args:
            regime: The current market regime.

        Returns:
            Position size multiplier (e.g., 0.2 for CRISIS, 1.5 for BULL).
        """
        return REGIME_SIZE_MULTIPLIER.get(regime, 1.0)

    def is_strategy_allowed(self, regime: RegimeType) -> bool:
        """Check if the wrapped strategy is allowed in the given regime.

        Args:
            regime: The market regime to check.

        Returns:
            True if the strategy is allowed, False if blocked.
        """
        return not self._is_strategy_blocked(regime)

    def get_param_overrides(self, regime: RegimeType) -> Dict[str, Any]:
        """Get parameter overrides for a specific regime.

        Args:
            regime: The market regime.

        Returns:
            Dict of parameter overrides to apply.
        """
        return dict(self._param_overrides.get(regime, {}))

    # ─── Private methods ─────────────────────────────────────────────────

    def _detect_regime_from_data(
        self,
        data: Any,
        returns: Optional[Any] = None,
    ) -> RegimeResult:
        """Run regime detection, computing returns if needed."""
        import pandas as pd

        if returns is not None:
            if isinstance(returns, pd.Series):
                return self._detector.detect_regime(returns)

        # Try to compute returns from data
        if isinstance(data, pd.DataFrame) and "close" in data.columns:
            rets = data["close"].pct_change().dropna()
            return self._detector.detect_regime(rets)

        # Fallback: return sideways with low confidence
        return RegimeResult(
            current_regime=RegimeType.SIDEWAYS,
            confidence=0.0,
            metadata={"method": "fallback", "reason": "no_returns_available"},
        )

    def _is_strategy_blocked(self, regime: RegimeType) -> bool:
        """Check if the strategy is blocked in the given regime."""
        blocked = self._blocked_strategies.get(regime, set())
        return self._strategy.name.lower() in {s.lower() for s in blocked}

    def _apply_param_overrides(self, regime: RegimeType) -> None:
        """Apply regime-specific parameter overrides to the wrapped strategy."""
        overrides = self._param_overrides.get(regime, {})
        for key, value in overrides.items():
            self._strategy.parameters.set(key, value)

    def _adjust_signal(
        self, signal: StrategySignal, regime: RegimeType
    ) -> StrategySignal:
        """Adjust signal based on regime (position sizing, etc.)."""
        multiplier = REGIME_SIZE_MULTIPLIER.get(regime, 1.0)

        # Adjust confidence by regime multiplier
        adjusted_confidence = signal.confidence * multiplier
        signal.confidence = max(0.0, min(1.0, adjusted_confidence))

        # If regime is CRISIS and signal is not EXIT/HOLD, weaken it
        if regime == RegimeType.CRISIS and signal.direction not in (
            SignalDirection.EXIT,
            SignalDirection.HOLD,
        ):
            signal.strength = "weak"  # type: ignore[assignment]
            if signal.stop_loss is not None and signal.entry_price is not None:
                # Tighten stop loss in crisis
                stop_mult = self._param_overrides.get(
                    regime, {}
                ).get("stop_loss_multiplier", 0.5)
                if signal.direction == SignalDirection.BUY:
                    signal.stop_loss = signal.entry_price - (
                        signal.entry_price - signal.stop_loss
                    ) * stop_mult
                elif signal.direction == SignalDirection.SELL:
                    signal.stop_loss = signal.entry_price + (
                        signal.stop_loss - signal.entry_price
                    ) * stop_mult

        return signal


__all__ = [
    "RegimeAwareStrategyAdapter",
    "REGIME_SIZE_MULTIPLIER",
    "BLOCKED_STRATEGIES",
    "DEFAULT_PARAM_OVERRIDES",
]

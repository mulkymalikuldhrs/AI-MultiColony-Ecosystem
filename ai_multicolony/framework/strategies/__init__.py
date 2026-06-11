"""Strategy sub-package for AI-MultiColony.

Imports all concrete strategy implementations and registers them with
the :class:`~ai_multicolony.framework.strategy_base.StrategyRegistry`.

Registered Strategies
---------------------
``smc_trend``
    :class:`SMCTrendStrategy` — Smart Money Concepts trend-following.
``mean_reversion``
    :class:`MeanReversionStrategy` — Bollinger Bands + RSI.
``momentum_breakout``
    :class:`MomentumBreakoutStrategy` — Volume-confirmed momentum breakout.

Usage
-----
>>> from ai_multicolony.framework.strategies import SMCTrendStrategy
>>> from ai_multicolony.framework.strategy_base import StrategyRegistry
>>> StrategyRegistry().list_strategies()
['mean_reversion', 'momentum_breakout', 'smc_trend']
"""

from __future__ import annotations

from ai_multicolony.framework.strategy_base import StrategyRegistry

from .smc_trend import SMCTrendStrategy
from .mean_reversion import MeanReversionStrategy
from .momentum_breakout import MomentumBreakoutStrategy

# ── Register all strategies with the singleton registry ────────────────
_registry = StrategyRegistry()
_registry.register("smc_trend", SMCTrendStrategy)
_registry.register("mean_reversion", MeanReversionStrategy)
_registry.register("momentum_breakout", MomentumBreakoutStrategy)

__all__ = [
    "SMCTrendStrategy",
    "MeanReversionStrategy",
    "MomentumBreakoutStrategy",
]

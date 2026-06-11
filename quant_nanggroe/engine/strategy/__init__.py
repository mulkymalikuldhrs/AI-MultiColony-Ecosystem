"""YAML Strategy System for Quant Nanggroe AI.

Provides a declarative strategy definition system where trading strategies
are defined in YAML files, validated with Pydantic models, and converted
to executable signal generators for the backtest engine.

Also provides production-quality strategy implementations that extend
BaseStrategy and generate real Signal objects.

Components:
- schema: Pydantic models for strategy YAML validation
- parser: YAML strategy parser and code generator
- loader: Strategy loader, registry, and hot-reload
- backtest_adapter: Connect strategies to backtest engine
- strategies: Production strategy implementations
"""

from __future__ import annotations

from quant_nanggroe.engine.strategy.schema import (
    EntryRule,
    ExitRule,
    RiskRules,
    StrategyConfig,
    UniverseDefinition,
)
from quant_nanggroe.engine.strategy.parser import (
    parse_strategy,
    validate_strategy,
    strategy_to_code,
)
from quant_nanggroe.engine.strategy.loader import StrategyLoader, StrategyRegistry
from quant_nanggroe.engine.strategy.backtest_adapter import StrategyBacktestAdapter

# Production strategy implementations
from quant_nanggroe.engine.strategy.strategies import (
    BaseStrategy,
    MeanReversionStrategy,
    MomentumStrategy,
    PairsTradingStrategy,
    VolatilityArbitrageStrategy,
    StatisticalArbitrageStrategy,
    MarketMakingStrategy,
    RegimeBasedStrategy,
    CryptoSpecificStrategy,
    create_strategy,
    list_strategies,
    get_strategy_metadata,
    register_strategy,
)

__all__ = [
    # Schema
    "EntryRule",
    "ExitRule",
    "RiskRules",
    "StrategyConfig",
    "UniverseDefinition",
    # Parser
    "parse_strategy",
    "validate_strategy",
    "strategy_to_code",
    # Loader
    "StrategyLoader",
    "StrategyRegistry",
    # Adapter
    "StrategyBacktestAdapter",
    # Strategy implementations
    "BaseStrategy",
    "MeanReversionStrategy",
    "MomentumStrategy",
    "PairsTradingStrategy",
    "VolatilityArbitrageStrategy",
    "StatisticalArbitrageStrategy",
    "MarketMakingStrategy",
    "RegimeBasedStrategy",
    "CryptoSpecificStrategy",
    # Strategy registry functions
    "create_strategy",
    "list_strategies",
    "get_strategy_metadata",
    "register_strategy",
]

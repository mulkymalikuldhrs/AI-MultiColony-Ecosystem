"""AI-MultiColony Framework — Workflow engine, strategy system, and data pipeline.

This package provides the core framework infrastructure for building
trading strategies, orchestrating multi-step workflows, and ingesting
market data with failover support.

Re-exports
----------
WorkflowEngine, EventTrigger
    From :mod:`workflow_engine` — LangGraph StateGraph-based workflow
    orchestration with event triggers.

StrategyBase, StrategyRegistry, SignalType, Signal, StrategyConfig
    From :mod:`strategy_base` — Abstract strategy base class, signal
    model, and singleton registry.  Includes ``SMCTrendStrategy``,
    ``MeanReversionStrategy``, and ``MomentumBreakoutStrategy``.

DataPipeline, DataSourceConfig, DataUnavailableError
    From :mod:`data_pipeline` — Multi-source data fetcher with
    priority-based failover and deterministic slippage model.
"""

from __future__ import annotations

from .workflow_engine import (
    EventTrigger,
    WorkflowDefinition,
    WorkflowEngine,
    WorkflowState,
    WorkflowStep,
)

from .strategy_base import (
    MeanReversionStrategy,
    MomentumBreakoutStrategy,
    Signal,
    SignalType,
    SMCTrendStrategy,
    StrategyBase,
    StrategyConfig,
    StrategyRegistry,
    get_strategy_class,
    register_strategy,
)

from .data_pipeline import (
    DataPipeline,
    DataSourceConfig,
    DataUnavailableError,
    calculate_slippage,
)

__all__ = [
    # Workflow Engine
    "WorkflowEngine",
    "EventTrigger",
    "WorkflowState",
    "WorkflowStep",
    "WorkflowDefinition",
    # Strategy
    "SignalType",
    "Signal",
    "StrategyConfig",
    "StrategyBase",
    "StrategyRegistry",
    "SMCTrendStrategy",
    "MeanReversionStrategy",
    "MomentumBreakoutStrategy",
    "register_strategy",
    "get_strategy_class",
    # Data Pipeline
    "DataPipeline",
    "DataSourceConfig",
    "DataUnavailableError",
    "calculate_slippage",
]

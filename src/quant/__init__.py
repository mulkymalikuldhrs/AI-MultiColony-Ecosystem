"""
HermesQuantOS Quant Trading Tools - Integrated into AI-MultiColony-Ecosystem.

Modules:
    math_engine: Pure deterministic indicator calculations (SMA, EMA, RSI, MACD, Bollinger, ATR, etc.)
    backtest_engine: Realistic backtesting with execution reality (spread, slippage, latency, partial fill)
    risk_officer: 9-checkpoint risk validation with hardcoded limits and full veto authority
    kill_switch: Emergency halt system with manual reset after review
    smc_agent: Smart Money Concepts agent (ICT methodology: BOS, CHoCH, OB, FVG, Liquidity, OTE)
    news_sentinel: News event classification with logarithmic time decay impact scoring
    macro_sentiment: Macro/fundamental regime detection (risk-on/risk-off)
    decision_engine: Deterministic decision table synthesizing pressure + regime -> trade decision
    pressure_engine: Pressure normalization (all sensor outputs -> BUY/SELL pressure 0-1)
    market_state: Regime detection (TRENDING|RANGE|MEAN_REVERT|RISK_OFF|PANIC|NO_TRADE)
    autoswitch: LLM provider health-monitored failover with exponential backoff
    audit_logger: Trade audit trail with timestamped entries
    auditor_research_tool: Multi-source research aggregation for trade auditing
    chart_vision_tool: Chart image analysis and pattern recognition
    execution_tool: Trade execution with broker abstraction
    journal_tool: Trading journal with performance tracking
    market_data_tool: Market data fetching with caching
    portfolio_tool: Portfolio management and position tracking
    shared_state: Shared state management across quant tools
    strategy_lifecycle: Strategy lifecycle management (create, deploy, monitor, retire)
    strategy_tool: Strategy configuration and backtesting interface
    technical_analysis_tool: Comprehensive technical analysis indicators
    hermes_quant: Main HermesQuantOS orchestrator class
    watchdog: System health monitoring and alerting
    keeper: Process management and auto-restart daemon
    system_prompt: System prompt configuration for quant agents
"""

from src.quant.math_engine import MathEngine
from src.quant.backtest_engine import BacktestEngine, Trade, BacktestResult
from src.quant.risk_officer import RiskOfficerTool
from src.quant.kill_switch import KillSwitchTool
from src.quant.smc_agent import SMCAgentEnhanced
from src.quant.news_sentinel import NewsSentinelTool
from src.quant.macro_sentiment import MacroSentimentTool
from src.quant.decision_engine import DecisionSynthesisEngine
from src.quant.pressure_engine import PressureNormalizationEngine
from src.quant.market_state import MarketStateEngine
from src.quant.autoswitch import AutoSwitchEngine, ProviderHealth
from src.quant.audit_logger import AuditLogger
from src.quant.auditor_research_tool import AuditorResearchTool
from src.quant.chart_vision_tool import ChartVisionTool
from src.quant.execution_tool import ExecutionTool
from src.quant.journal_tool import JournalTool
from src.quant.market_data_tool import MarketDataTool
from src.quant.portfolio_tool import PortfolioTool
from src.quant.shared_state import SharedState, get_shared_state
from src.quant.strategy_lifecycle import StrategyLifecycleManager
from src.quant.strategy_tool import StrategyTool
from src.quant.technical_analysis_tool import TechnicalAnalysisTool

__all__ = [
    "MathEngine",
    "BacktestEngine",
    "Trade",
    "BacktestResult",
    "RiskOfficerTool",
    "KillSwitchTool",
    "SMCAgentEnhanced",
    "NewsSentinelTool",
    "MacroSentimentTool",
    "DecisionSynthesisEngine",
    "PressureNormalizationEngine",
    "MarketStateEngine",
    "AutoSwitchEngine",
    "ProviderHealth",
    "AuditLogger",
    "AuditorResearchTool",
    "ChartVisionTool",
    "ExecutionTool",
    "JournalTool",
    "MarketDataTool",
    "PortfolioTool",
    "SharedState",
    "get_shared_state",
    "StrategyLifecycleManager",
    "StrategyTool",
    "TechnicalAnalysisTool",
]

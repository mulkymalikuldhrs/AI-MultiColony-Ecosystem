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
]

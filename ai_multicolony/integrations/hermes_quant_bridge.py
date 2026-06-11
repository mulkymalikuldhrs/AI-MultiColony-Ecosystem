"""HermesQuantOS Bridge — Full 21-tool integration for AI-MultiColony.

Provides a unified bridge to all HermesQuantOS trading tools, wrapping each
with graceful degradation, deterministic slippage, and audit-trail metadata.

Tools exposed
-------------
1.  Market Data Tool       — OHLCV, economic calendar
2.  Chart Vision Tool      — LLM-based chart analysis
3.  Technical Analysis Tool — indicators (RSI, EMA, ATR, MACD, SMC)
4.  Macro Sentiment Tool   — economic sentiment / regime
5.  SMC Agent Enhanced     — ICT/Smart Money Concepts (BOS, CHoCH, OB, FVG)
6.  News Sentinel          — news monitoring with logarithmic decay
7.  Market State Engine    — regime detection (TRENDING, RANGE, …)
8.  Strategy Tool          — strategy management, 3-scenario generation
9.  Risk Officer Tool      — risk assessment, 9-checkpoint veto
10. Portfolio Tool         — portfolio management, allocation
11. Decision Engine        — decision synthesis, pressure → trade
12. Pressure Engine        — pressure normalization (buy/sell vectors)
13. Strategy Lifecycle     — Darwinian strategy evolution
14. Execution Tool         — order execution with risk gate
15. Kill Switch Tool       — emergency halt
16. Autoswitch Engine      — LLM provider failover
17. Journal Tool           — trade journaling
18. Auditor Research Tool  — research audit, edge-decay detection
19. Audit Logger           — audit trail across decision layers
20. Backtest Engine        — backtesting with execution reality
21. Math Engine            — statistical calculations (RSI, MACD, BB, …)
"""

from __future__ import annotations

import hashlib
import importlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class HermesQuantBridgeError(Exception):
    """Base exception for HermesQuant bridge failures."""


class DataUnavailableError(HermesQuantBridgeError):
    """Raised when a data source fails to return data."""


class ToolNotFoundError(HermesQuantBridgeError):
    """Raised when a requested tool name is not registered."""


class ToolImportError(HermesQuantBridgeError):
    """Raised when a tool module cannot be imported."""


class ToolExecutionError(HermesQuantBridgeError):
    """Raised when a tool execution fails."""

# ---------------------------------------------------------------------------
# Deterministic slippage model (seeded RNG)
# ---------------------------------------------------------------------------


class DeterministicSlippageModel:
    """Slippage model that uses a seeded hash for reproducibility.

    No use of ``random`` — fully deterministic given the same inputs.
    """

    BASE_SPREAD = 0.0002  # 2 pips
    COMMISSION_PCT = 0.001  # 0.1% per side

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed

    def compute_slippage(
        self,
        symbol: str,
        price: float,
        direction: str,
        volatility: str = "NORMAL",
    ) -> Dict[str, Any]:
        """Compute deterministic slippage for an order.

        Parameters
        ----------
        symbol : str
            Trading symbol.
        price : float
            Intended entry/exit price.
        direction : str
            ``BUY`` or ``SELL``.
        volatility : str
            ``LOW``, ``NORMAL``, or ``HIGH``.

        Returns
        -------
        dict
            Keys: ``slippage``, ``spread``, ``commission``, ``fill_price``,
            ``data_source``.
        """
        vol_multiplier = {"HIGH": 3.0, "NORMAL": 1.0, "LOW": 0.5}.get(
            volatility, 1.0
        )

        # Deterministic slippage from hash of inputs + seed
        raw = f"{self.seed}:{symbol}:{price}:{direction}:{volatility}".encode()
        digest = hashlib.sha256(raw).hexdigest()
        fraction = int(digest[:8], 16) / 0xFFFFFFFF  # 0.0 – 1.0

        spread = self.BASE_SPREAD * vol_multiplier
        max_slip = (self.BASE_SPREAD / 2) * vol_multiplier
        slippage = fraction * max_slip

        if direction.upper() == "BUY":
            fill_price = price + slippage
        else:
            fill_price = price - slippage

        commission = fill_price * self.COMMISSION_PCT * 2  # round-trip

        return {
            "slippage": round(slippage, 6),
            "spread": round(spread, 6),
            "commission": round(commission, 6),
            "fill_price": round(fill_price, 5),
            "data_source": "hermes_quant_slippage_model",
        }

# ---------------------------------------------------------------------------
# Tool registry
# ---------------------------------------------------------------------------

# Mapping: canonical name → (module_path, class_name)
_TOOL_REGISTRY: Dict[str, tuple[str, str]] = {
    "market_data":         ("tools.market_data_tool",         "MarketDataTool"),
    "chart_vision":        ("tools.chart_vision_tool",        "ChartVisionTool"),
    "technical_analysis":  ("tools.technical_analysis_tool",  "TechnicalAnalysisTool"),
    "macro_sentiment":     ("tools.macro_sentiment_tool",     "MacroSentimentTool"),
    "smc_agent_enhanced":  ("tools.smc_agent_enhanced",       "SMCAgentEnhanced"),
    "news_sentinel":       ("tools.news_sentinel",            "NewsSentinelTool"),
    "market_state_engine": ("tools.market_state_engine",      "MarketStateEngine"),
    "strategy":            ("tools.strategy_tool",            "StrategyTool"),
    "risk_officer":        ("tools.risk_officer_tool",        "RiskOfficerTool"),
    "portfolio":           ("tools.portfolio_tool",           "PortfolioTool"),
    "decision_engine":     ("tools.decision_engine",          "DecisionSynthesisEngine"),
    "pressure_engine":     ("tools.pressure_engine",          "PressureNormalizationEngine"),
    "strategy_lifecycle":  ("tools.strategy_lifecycle",       "StrategyLifecycleManager"),
    "execution":           ("tools.execution_tool",           "ExecutionTool"),
    "kill_switch":         ("tools.kill_switch_tool",         "KillSwitchTool"),
    "autoswitch":          ("tools.autoswitch_engine",        "AutoSwitchEngine"),
    "journal":             ("tools.journal_tool",             "JournalTool"),
    "auditor_research":    ("tools.auditor_research_tool",    "AuditorResearchTool"),
    "audit_logger":        ("tools.audit_logger",             "AuditLogger"),
    "backtest_engine":     ("tools.backtest_engine",          "BacktestEngine"),
    "math_engine":         ("tools.math_engine",              "MathEngine"),
}

# ---------------------------------------------------------------------------
# Bridge class
# ---------------------------------------------------------------------------


class HermesQuantBridge:
    """Full 21-tool bridge to HermesQuantOS.

    Parameters
    ----------
    config : dict
        Configuration dictionary.  Recognized keys:

        - ``hermes_quant_path`` (str): Absolute path to the
          ``HermesQuantOS/src`` directory.  Defaults to
          ``/home/z/my-project/HermesQuantOS/src``.
        - ``slippage_seed`` (int): Seed for the deterministic slippage
          model.  Defaults to ``42``.
    """

    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._hermes_path = Path(
            self.config.get(
                "hermes_quant_path",
                "/home/z/my-project/HermesQuantOS/src",
            )
        )
        self._slippage = DeterministicSlippageModel(
            seed=self.config.get("slippage_seed", 42)
        )
        self._tool_cache: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}

        # Ensure the Hermes path is on sys.path so relative imports work
        hermes_src = str(self._hermes_path)
        if hermes_src not in sys.path:
            sys.path.insert(0, hermes_src)

        logger.info(
            "hermes_bridge_initialised",
            hermes_path=str(self._hermes_path),
            tool_count=len(_TOOL_REGISTRY),
        )

    # ------------------------------------------------------------------
    # Tool management
    # ------------------------------------------------------------------

    def list_tools(self) -> List[str]:
        """Return the canonical names of all 21 HermesQuantOS tools."""
        return list(_TOOL_REGISTRY.keys())

    def get_tool(self, name: str) -> Callable[..., Any]:
        """Return a callable wrapper for a specific HermesQuantOS tool.

        The returned callable invokes ``execute_tool`` under the hood,
        guaranteeing audit-trail metadata and graceful error handling.

        Raises
        ------
        ToolNotFoundError
            If *name* is not in the tool registry.
        """
        if name not in _TOOL_REGISTRY:
            raise ToolNotFoundError(f"Tool '{name}' not found in HermesQuant registry")

        def _wrapped(**kwargs: Any) -> Dict[str, Any]:
            return self.execute_tool(name, **kwargs)

        _wrapped.__name__ = f"hermes_{name}"
        _wrapped.__doc__ = f"HermesQuant bridge wrapper for {name}"
        return _wrapped

    def _instantiate_tool(self, name: str) -> Any:
        """Lazily import and instantiate a HermesQuantOS tool.

        Returns
        -------
        object
            An instance of the tool class.

        Raises
        ------
        ToolImportError
            If the module cannot be imported.
        """
        if name in self._tool_cache:
            return self._tool_cache[name]

        if name in self._import_errors:
            raise ToolImportError(self._import_errors[name])

        module_path, class_name = _TOOL_REGISTRY[name]

        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)

            # Some tools accept optional constructor arguments
            if name == "audit_logger":
                instance = cls(max_entries=1000)
            elif name == "backtest_engine":
                instance = cls(initial_balance=self.config.get("initial_balance", 10000.0))
            elif name == "execution":
                instance = cls(mode=self.config.get("execution_mode", "paper"))
            else:
                instance = cls()

            self._tool_cache[name] = instance
            logger.debug("hermes_tool_instantiated", tool=name)
            return instance

        except Exception as exc:
            self._import_errors[name] = str(exc)
            logger.warning(
                "hermes_tool_import_failed",
                tool=name,
                module=module_path,
                error=str(exc),
            )
            raise ToolImportError(
                f"Cannot import HermesQuant tool '{name}' "
                f"(module={module_path}, class={class_name}): {exc}"
            ) from exc

    def execute_tool(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a HermesQuantOS tool by name.

        All results include a ``data_source`` field for audit traceability.

        Parameters
        ----------
        name : str
            Canonical tool name from ``list_tools()``.
        **kwargs
            Arguments forwarded to the tool method.

        Returns
        -------
        dict
            Result dictionary with at minimum ``data_source`` and
            ``timestamp`` keys.

        Raises
        ------
        ToolNotFoundError
            If *name* is not registered.
        DataUnavailableError
            If the tool returns an error indicating unavailable data.
        """
        if name not in _TOOL_REGISTRY:
            raise ToolNotFoundError(f"Tool '{name}' not found in HermesQuant registry")

        timestamp = datetime.now().isoformat()

        try:
            tool = self._instantiate_tool(name)
        except ToolImportError as exc:
            return {
                "error": str(exc),
                "data_source": "hermes_quant_bridge",
                "tool": name,
                "status": "import_failed",
                "timestamp": timestamp,
            }

        # Determine which method to call — most tools have a primary method
        method_name = self._resolve_method(name, kwargs)
        method = getattr(tool, method_name, None)

        if method is None:
            return {
                "error": f"Method '{method_name}' not found on tool '{name}'",
                "data_source": "hermes_quant_bridge",
                "tool": name,
                "status": "method_not_found",
                "timestamp": timestamp,
            }

        try:
            result = method(**kwargs)

            # Many HermesQuantOS tools return JSON strings
            if isinstance(result, str):
                try:
                    parsed = json.loads(result)
                except (json.JSONDecodeError, TypeError):
                    parsed = {"raw": result}
            elif isinstance(result, dict):
                parsed = result
            else:
                parsed = {"raw": str(result)}

            # Check for data-unavailability signals
            if isinstance(parsed, dict) and "error" in parsed:
                error_msg = parsed["error"]
                if any(
                    kw in str(error_msg).lower()
                    for kw in ("no data", "not installed", "unavailable", "not_configured")
                ):
                    raise DataUnavailableError(
                        f"Data unavailable for tool '{name}': {error_msg}"
                    )

            # Inject audit-trail metadata
            parsed.setdefault("data_source", f"hermes_quant_{name}")
            parsed.setdefault("timestamp", timestamp)

            return parsed

        except DataUnavailableError:
            return {
                "error": f"Data unavailable for tool '{name}'",
                "data_source": "hermes_quant_bridge",
                "tool": name,
                "status": "data_unavailable",
                "timestamp": timestamp,
            }
        except Exception as exc:
            logger.warning(
                "hermes_tool_execution_failed",
                tool=name,
                method=method_name,
                error=str(exc),
            )
            return {
                "error": str(exc),
                "data_source": "hermes_quant_bridge",
                "tool": name,
                "status": "execution_failed",
                "timestamp": timestamp,
            }

    # ------------------------------------------------------------------
    # Deterministic slippage access
    # ------------------------------------------------------------------

    def compute_slippage(
        self,
        symbol: str,
        price: float,
        direction: str,
        volatility: str = "NORMAL",
    ) -> Dict[str, Any]:
        """Compute deterministic slippage for an order.

        Delegates to :class:`DeterministicSlippageModel`.
        """
        return self._slippage.compute_slippage(symbol, price, direction, volatility)

    # ------------------------------------------------------------------
    # Bulk operations
    # ------------------------------------------------------------------

    def execute_all(self, **common_kwargs: Any) -> Dict[str, Dict[str, Any]]:
        """Execute every registered tool and collect results.

        Tools that fail are included with ``status: "failed"`` rather
        than raising.
        """
        results: Dict[str, Dict[str, Any]] = {}
        for name in self.list_tools():
            try:
                results[name] = self.execute_tool(name, **common_kwargs)
            except Exception as exc:
                results[name] = {
                    "error": str(exc),
                    "data_source": "hermes_quant_bridge",
                    "tool": name,
                    "status": "failed",
                    "timestamp": datetime.now().isoformat(),
                }
        return results

    def health_check(self) -> Dict[str, Any]:
        """Check which tools can be instantiated successfully.

        Returns
        -------
        dict
            Keys: ``available`` (list[str]), ``unavailable`` (list[str]),
            ``total`` (int), ``data_source``.
        """
        available: List[str] = []
        unavailable: List[str] = []

        for name in self.list_tools():
            try:
                self._instantiate_tool(name)
                available.append(name)
            except ToolImportError:
                unavailable.append(name)

        return {
            "available": available,
            "unavailable": unavailable,
            "total": len(self.list_tools()),
            "available_count": len(available),
            "data_source": "hermes_quant_bridge",
            "timestamp": datetime.now().isoformat(),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_method(name: str, kwargs: Dict[str, Any]) -> str:
        """Resolve the primary method name for a given tool.

        Most HermesQuantOS tools use a single entry-point method.  This
        mapping encodes those conventions based on the actual source code.
        """
        _METHOD_MAP: Dict[str, str] = {
            "market_data":         "get_ohlcv",
            "chart_vision":        "analyze_chart",
            "technical_analysis":  "analyze",
            "macro_sentiment":     "get_regime",
            "smc_agent_enhanced":  "analyze",
            "news_sentinel":       "score_impact",
            "market_state_engine": "auto_detect",
            "strategy":            "generate_scenarios",
            "risk_officer":        "check_trade",
            "portfolio":           "assess",
            "decision_engine":     "synthesize",
            "pressure_engine":     "normalize",
            "strategy_lifecycle":  "get_strategy_report",
            "execution":           "paper_trade",
            "kill_switch":         "status",
            "autoswitch":          "get_status",
            "journal":             "get_stats",
            "auditor_research":    "audit_recent",
            "audit_logger":        "get_summary",
            "backtest_engine":     "run",
            "math_engine":         "analyze_sequence",
        }
        return _METHOD_MAP.get(name, "status")

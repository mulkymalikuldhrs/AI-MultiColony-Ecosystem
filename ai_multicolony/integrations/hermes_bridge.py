"""
HermesQuant Bridge — Integrates the Hermes Quant trading engine into the ecosystem.

Wraps key HermesQuant tools as ai_multicolony-compatible tools, providing
market analysis, risk management, and trading signals to the agent system.

All external tool calls are protected by a :class:`CircuitBreaker`.
When the circuit is OPEN, unavailable/fallback responses are returned.
"""

from __future__ import annotations

import importlib
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy import helper — HermesQuant lives in packages/hermes-quant/
# ---------------------------------------------------------------------------

_HERMES_SRC = Path(__file__).resolve().parents[3] / "packages" / "hermes-quant" / "src"


def _ensure_hermes_on_path() -> None:
    """Add HermesQuant src to sys.path if not already present."""
    hermes_str = str(_HERMES_SRC)
    if hermes_str not in sys.path and _HERMES_SRC.exists():
        sys.path.insert(0, hermes_str)


def _import_hermes_module(module_name: str):
    """Lazy-import a module from the HermesQuant package."""
    _ensure_hermes_on_path()
    return importlib.import_module(module_name)


# ---------------------------------------------------------------------------
# Fallback response helpers
# ---------------------------------------------------------------------------

def _unavailable_result(symbol: str = "", **extra: Any) -> Dict[str, Any]:
    """Return a standardised unavailable/fallback result dict."""
    result: Dict[str, Any] = {"error": "HermesQuant unavailable (circuit breaker open)"}
    if symbol:
        result["symbol"] = symbol
    result.update(extra)
    return result


# ---------------------------------------------------------------------------
# Bridge class
# ---------------------------------------------------------------------------

class HermesQuantBridge:
    """Bridge to the HermesQuant trading engine.

    Provides high-level methods that wrap the individual tools from
    packages/hermes-quant/src/tools/ and return structured results.

    All tool calls are guarded by a :class:`CircuitBreaker`.  When the
    circuit is OPEN, each method returns an unavailable/fallback response
    instead of attempting the call.

    Usage::

        bridge = HermesQuantBridge()
        analysis = await bridge.analyze_market("XAUUSD")
        risk = await bridge.check_risk("XAUUSD")
    """

    def __init__(
        self,
        circuit_breaker_failure_threshold: int = 5,
        circuit_breaker_timeout_seconds: float = 60.0,
    ) -> None:
        self._market_data = None
        self._technical_analysis = None
        self._risk_officer = None
        self._decision_engine = None
        self._strategy_tool = None
        self._portfolio_tool = None
        self._kill_switch = None
        self._shared_state = None

        # Circuit breaker guarding all HermesQuant tool calls
        self._circuit_breaker = CircuitBreaker(
            name="hermes",
            failure_threshold=circuit_breaker_failure_threshold,
            timeout_seconds=circuit_breaker_timeout_seconds,
        )

    @property
    def circuit_breaker(self) -> CircuitBreaker:
        """Expose the circuit breaker for introspection or manual reset."""
        return self._circuit_breaker

    def _get_shared_state(self):
        if self._shared_state is None:
            try:
                mod = _import_hermes_module("tools.shared_state")
                self._shared_state = mod.SharedState()
            except Exception as exc:
                logger.warning("Could not import HermesQuant SharedState: %s", exc)
        return self._shared_state

    def _get_tool(self, tool_name: str):
        """Get a tool instance from HermesQuant shared state."""
        state = self._get_shared_state()
        if state is None:
            return None
        return getattr(state, tool_name, None)

    # -----------------------------------------------------------------------
    # Internal: circuit-breaker protected execution
    # -----------------------------------------------------------------------

    def _check_circuit(self) -> bool:
        """Return True if the circuit allows execution; log warning otherwise."""
        if not self._circuit_breaker.can_execute():
            logger.warning(
                "CircuitBreaker[hermes]: circuit OPEN — returning fallback"
            )
            return False
        return True

    # -----------------------------------------------------------------------
    # Market Analysis
    # -----------------------------------------------------------------------

    async def analyze_market(self, symbol: str = "XAUUSD") -> Dict[str, Any]:
        """Run technical analysis on a symbol.

        Returns an unavailable dict when the circuit breaker is open.

        Returns:
            Dict with keys: symbol, regime, signals, smc_analysis, summary
        """
        if not self._check_circuit():
            return _unavailable_result(symbol=symbol)

        result: Dict[str, Any] = {"symbol": symbol, "error": None}

        try:
            # Market data
            market_data = self._get_tool("market_data")
            if market_data:
                ohlcv = market_data.get_ohlcv(symbol)
                result["ohlcv"] = ohlcv

            # Technical analysis
            ta = self._get_tool("technical_analysis")
            if ta and market_data:
                data = market_data.get_ohlcv(symbol) if hasattr(market_data, 'get_ohlcv') else []
                if data:
                    analysis = ta.analyze(data)
                    result["signals"] = analysis

            # Market state / regime
            mse = self._get_tool("market_state_engine")
            if mse:
                regime = mse.detect_regime(symbol=symbol)
                result["regime"] = regime

            # SMC analysis
            smc = self._get_tool("smc_agent_enhanced")
            if smc and market_data:
                data = market_data.get_ohlcv(symbol) if hasattr(market_data, 'get_ohlcv') else []
                if data:
                    smc_result = smc.analyze(data)
                    result["smc_analysis"] = smc_result

            self._circuit_breaker.record_success()

        except Exception as exc:
            logger.error("HermesQuant analyze_market error: %s", exc)
            result["error"] = str(exc)
            self._circuit_breaker.record_failure()

        return result

    # -----------------------------------------------------------------------
    # Risk Management
    # -----------------------------------------------------------------------

    async def check_risk(self, symbol: str = "XAUUSD") -> Dict[str, Any]:
        """Check risk status for a symbol.

        Returns an unavailable dict when the circuit breaker is open.

        Returns:
            Dict with keys: symbol, risk_status, kill_switch_active, checks
        """
        if not self._check_circuit():
            return _unavailable_result(symbol=symbol)

        result: Dict[str, Any] = {"symbol": symbol, "error": None}

        try:
            risk = self._get_tool("risk_officer")
            if risk:
                status = risk.status()
                result["risk_status"] = status

            kill = self._get_tool("kill_switch")
            if kill:
                ks_status = kill.check_auto_trigger()
                result["kill_switch_active"] = ks_status

            self._circuit_breaker.record_success()

        except Exception as exc:
            logger.error("HermesQuant check_risk error: %s", exc)
            result["error"] = str(exc)
            self._circuit_breaker.record_failure()

        return result

    # -----------------------------------------------------------------------
    # Strategy
    # -----------------------------------------------------------------------

    async def get_strategy(self, symbol: str = "XAUUSD") -> Dict[str, Any]:
        """Get 3-scenario strategy analysis.

        Returns an unavailable dict when the circuit breaker is open.

        Returns:
            Dict with keys: symbol, scenarios, confluence, recommendation
        """
        if not self._check_circuit():
            return _unavailable_result(symbol=symbol)

        result: Dict[str, Any] = {"symbol": symbol, "error": None}

        try:
            strategy = self._get_tool("strategy_tool")
            if strategy:
                scenarios = strategy.generate_scenarios(symbol)
                result["scenarios"] = scenarios

            decision = self._get_tool("decision_engine")
            if decision:
                eval_result = decision.evaluate(symbol)
                result["evaluation"] = eval_result

            self._circuit_breaker.record_success()

        except Exception as exc:
            logger.error("HermesQuant get_strategy error: %s", exc)
            result["error"] = str(exc)
            self._circuit_breaker.record_failure()

        return result

    # -----------------------------------------------------------------------
    # Portfolio
    # -----------------------------------------------------------------------

    async def get_portfolio_status(self) -> Dict[str, Any]:
        """Get portfolio status and allocation.

        Returns an unavailable dict when the circuit breaker is open.

        Returns:
            Dict with keys: pnl, positions, allocation, journal_stats
        """
        if not self._check_circuit():
            return _unavailable_result()

        result: Dict[str, Any] = {"error": None}

        try:
            portfolio = self._get_tool("portfolio_tool")
            if portfolio:
                result["allocation"] = portfolio.assess()

            journal = self._get_tool("journal_tool")
            if journal:
                result["journal_stats"] = journal.get_stats()

            # PnL from shared state
            state = self._get_shared_state()
            if state:
                result["pnl"] = state.get_pnl_state()

            self._circuit_breaker.record_success()

        except Exception as exc:
            logger.error("HermesQuant get_portfolio_status error: %s", exc)
            result["error"] = str(exc)
            self._circuit_breaker.record_failure()

        return result

    # -----------------------------------------------------------------------
    # Health check
    # -----------------------------------------------------------------------

    async def is_available(self) -> bool:
        """Check if HermesQuant engine is available.

        Returns False when the circuit breaker is open.
        """
        if self._circuit_breaker.is_open:
            logger.warning("CircuitBreaker[hermes]: circuit OPEN — reporting unavailable")
            return False
        try:
            state = self._get_shared_state()
            return state is not None
        except Exception:
            logger.exception("HermesQuant availability check failed")
            return False

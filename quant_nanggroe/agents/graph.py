"""
Main Trading Graph for Quant Nanggroe AI Trading Framework.

Implements the LangGraph StateGraph that orchestrates the full trading
pipeline from market analysis through execution and reflection.

Graph Flow:
1. market_analysis → Researcher + Macro + Crypto + Forex agents
2. signal_generation → Strategist agent
3. risk_assessment → Risk agent (9-checkpoint gate)
4. portfolio_optimization → Portfolio agent
5. execution_decision → Trader agent
6. order_execution → Execution agent
7. reflection → Council debate (post-trade analysis)

Conditional edges:
- If risk_assessment fails → halt (no trade)
- If confidence < threshold → council debate
- If kill_switch active → emergency exit
"""

from __future__ import annotations

import logging
import structlog
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from langchain_core.language_models import BaseChatModel
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from quant_nanggroe.agents.base import create_llm
from quant_nanggroe.agents.council.debate import CouncilDebate
from quant_nanggroe.agents.council.voting import CouncilVoting
from quant_nanggroe.agents.registry import AgentFactory
from quant_nanggroe.agents.state import (
    AgentState,
    CONFIDENCE_THRESHOLD,
    RiskVerdict,
    TradeAction,
    create_initial_state,
)
from quant_nanggroe.engine.correlation_context import CorrelationContext
from quant_nanggroe.engine.synthesis.pressure_synthesis import (
    PressureSynthesizer,
    PressureSynthesisConfig,
    AgentSignal,
    RegimeState as SynthesisRegimeState,
    FactorSnapshot as SynthesisFactorSnapshot,
    RiskState as SynthesisRiskState,
    extract_agent_signals,
)
from quant_nanggroe.types.engine import MarketRegime
from quant_nanggroe.engine.regime.regime_detector import RegimeDetector
from quant_nanggroe.engine.factors.factor_pipeline_bridge import FactorPipelineBridge


logger = structlog.get_logger(__name__)


class TradingGraph:
    """
    Main trading graph orchestrating the full trading pipeline.

    Uses LangGraph StateGraph to define the agent workflow with
    conditional edges for risk gates, council debates, and
    emergency exits.
    """

    def __init__(
        self,
        llm_provider: str = "openai",
        deep_think_model: str = "gpt-4o",
        quick_think_model: str = "gpt-4o-mini",
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        max_debate_rounds: int = 2,
        max_risk_rounds: int = 2,
        confidence_threshold: float = CONFIDENCE_THRESHOLD,
    ) -> None:
        """
        Initialize the trading graph.

        Args:
            llm_provider: LLM provider name
            deep_think_model: Model for deep analysis tasks
            quick_think_model: Model for quick response tasks
            base_url: Optional API base URL
            api_key: Optional API key
            max_debate_rounds: Maximum debate rounds
            max_risk_rounds: Maximum risk debate rounds
            confidence_threshold: Confidence threshold for council debate
        """
        self._llm_provider = llm_provider
        self._deep_think_model = deep_think_model
        self._quick_think_model = quick_think_model
        self._base_url = base_url
        self._api_key = api_key
        self._max_debate_rounds = max_debate_rounds
        self._max_risk_rounds = max_risk_rounds
        self._confidence_threshold = confidence_threshold

        # Create LLMs
        self._deep_llm = create_llm(
            provider=llm_provider,
            model=deep_think_model,
            base_url=base_url,
            api_key=api_key,
            temperature=0.0,
        )
        self._quick_llm = create_llm(
            provider=llm_provider,
            model=quick_think_model,
            base_url=base_url,
            api_key=api_key,
            temperature=0.0,
        )

        # Create agent factory
        self._factory = AgentFactory(
            llm_provider=llm_provider,
            deep_think_model=deep_think_model,
            quick_think_model=quick_think_model,
            base_url=base_url,
            api_key=api_key,
        )

        # Create council components
        self._council_debate = CouncilDebate(
            llm=self._deep_llm,
            max_debate_rounds=max_debate_rounds,
            max_risk_rounds=max_risk_rounds,
        )
        self._council_voting = CouncilVoting(
            llm=self._deep_llm,
            consensus_threshold=confidence_threshold,
        )

        # Create pressure synthesizer
        self._pressure_synthesizer = PressureSynthesizer(
            config=PressureSynthesisConfig()
        )

        # Create factor pipeline bridge and regime detector
        self._factor_bridge = FactorPipelineBridge(top_n=20)
        self._regime_detector = RegimeDetector()

        # Flag indicating whether synthetic/fabricated data is being used
        # downstream agents must check this flag before making trading decisions
        self.using_synthetic_data = False

        # Build and compile the graph
        self._graph = self._build_graph()

    @property
    def graph(self) -> StateGraph:
        """Get the compiled LangGraph graph."""
        return self._graph

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph trading graph.

        Returns:
            Compiled StateGraph
        """
        # Create the workflow
        workflow = StateGraph(AgentState)

        # Add agent nodes
        workflow.add_node("market_analysis", self._market_analysis_node)
        workflow.add_node("signal_generation", self._signal_generation_node)
        workflow.add_node("risk_assessment", self._risk_assessment_node)
        workflow.add_node("portfolio_optimization", self._portfolio_optimization_node)
        workflow.add_node("execution_decision", self._execution_decision_node)
        workflow.add_node("order_execution", self._order_execution_node)
        workflow.add_node("reflection", self._reflection_node)
        workflow.add_node("council_debate", self._council_debate_node)
        workflow.add_node("pressure_synthesis", self._pressure_synthesis_node)
        workflow.add_node("emergency_exit", self._emergency_exit_node)

        # Add factor/regime detection node (runs after market analysis, before signal generation)
        workflow.add_node("factor_regime_detection", self._factor_regime_detection_node)

        # Define the main flow
        workflow.add_edge(START, "market_analysis")
        workflow.add_edge("market_analysis", "factor_regime_detection")
        workflow.add_edge("factor_regime_detection", "signal_generation")
        workflow.add_edge("signal_generation", "risk_assessment")

        # Conditional edge after risk assessment
        workflow.add_conditional_edges(
            "risk_assessment",
            self._risk_conditional,
            {
                "continue": "portfolio_optimization",
                "halt": END,
                "council_debate": "council_debate",
                "emergency_exit": "emergency_exit",
            },
        )

        workflow.add_edge("portfolio_optimization", "execution_decision")
        workflow.add_edge("execution_decision", "order_execution")
        workflow.add_edge("order_execution", "reflection")
        workflow.add_edge("reflection", END)
        workflow.add_edge("council_debate", "pressure_synthesis")
        workflow.add_edge("pressure_synthesis", "execution_decision")
        workflow.add_edge("emergency_exit", END)

        # Compile
        return workflow.compile()

    def _risk_conditional(self, state: AgentState) -> str:
        """
        Determine the next step after risk assessment.

        Args:
            state: Current agent state

        Returns:
            Next node name
        """
        # Kill switch active → emergency exit
        if state.get("kill_switch_active", False):
            logger.warning("Kill switch active - routing to emergency exit")
            return "emergency_exit"

        # Risk vetoed → halt
        risk_verdict = state.get("risk_verdict", "VETOED")
        if risk_verdict == RiskVerdict.VETOED.value:
            logger.info("Risk assessment vetoed - halting pipeline")
            return "halt"

        if risk_verdict == RiskVerdict.KILL_SWITCH.value:
            logger.critical("Risk assessment triggered kill switch - emergency exit")
            return "emergency_exit"

        # Low confidence → council debate
        confidence = state.get("confidence", 0.0)
        if confidence < self._confidence_threshold:
            logger.info(
                f"Low confidence ({confidence:.2f} < {self._confidence_threshold}) "
                f"- routing to council debate"
            )
            return "council_debate"

        # Continue to portfolio optimization
        return "continue"

    def _market_analysis_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Market analysis node: runs researcher, macro, crypto, and forex agents.

        Args:
            state: Current agent state

        Returns:
            State updates with analysis outputs
        """
        logger.info("=== Market Analysis Phase ===")

        updates: Dict[str, Any] = {
            "iteration": state.get("iteration", 0) + 1,
        }

        # Run researcher agent
        try:
            researcher = self._factory.create_agent("researcher")
            result = researcher(state)
            updates["research_output"] = result.get("research_output", "")
            updates["agent_outputs"] = {
                **state.get("agent_outputs", {}),
                **result.get("agent_outputs", {}),
            }
        except Exception as e:
            logger.error(f"Researcher agent failed: {e}")
            updates["research_output"] = f"Research failed: {e}"

        # Run macro agent
        try:
            macro = self._factory.create_agent("macro")
            result = macro(state)
            updates["macro_output"] = result.get("macro_output", "")
            updates["agent_outputs"] = {
                **updates.get("agent_outputs", state.get("agent_outputs", {})),
                **result.get("agent_outputs", {}),
            }
        except Exception as e:
            logger.error(f"Macro agent failed: {e}")
            updates["macro_output"] = f"Macro analysis failed: {e}"

        # Run crypto agent
        try:
            crypto = self._factory.create_agent("crypto")
            result = crypto(state)
            updates["crypto_output"] = result.get("crypto_output", "")
            updates["agent_outputs"] = {
                **updates.get("agent_outputs", state.get("agent_outputs", {})),
                **result.get("agent_outputs", {}),
            }
        except Exception as e:
            logger.error(f"Crypto agent failed: {e}")
            updates["crypto_output"] = f"Crypto analysis failed: {e}"

        # Run forex agent
        try:
            forex = self._factory.create_agent("forex")
            result = forex(state)
            updates["forex_output"] = result.get("forex_output", "")
            updates["agent_outputs"] = {
                **updates.get("agent_outputs", state.get("agent_outputs", {})),
                **result.get("agent_outputs", {}),
            }
        except Exception as e:
            logger.error(f"Forex agent failed: {e}")
            updates["forex_output"] = f"Forex analysis failed: {e}"

        updates["sender"] = "market_analysis"
        return updates

    def _factor_regime_detection_node(self, state: AgentState) -> Dict[str, Any]:
        """Factor computation and regime detection node.

        Runs after market analysis to compute alpha factors from the 446
        available factors (Alpha101, GTJA191, Qlib158, etc.) and detect
        the current market regime. This bridges the gap where factors
        were previously computed but never used in the decision pipeline.

        Outputs:
        - factor_snapshot: FactorSnapshot data (bullish/bearish factors, composite score)
        - regime_state: RegimeState data (current regime, risk multiplier, probabilities)
        - Updated metadata with factor/regime info for downstream nodes

        Args:
            state: Current agent state

        Returns:
            State updates with factor snapshot and regime state.
        """
        logger.info("=== Factor & Regime Detection Phase ===")

        updates: Dict[str, Any] = {}

        try:
            # Compute factor snapshot from market data if available
            market_data = state.get("market_data", {})
            if market_data:
                # Convert market data to panel format for factor computation
                # Use the first available symbol's data
                symbols = state.get("symbols", [])
                if symbols:
                    symbol = symbols[0]
                    symbol_data = market_data.get(symbol, {})

                    # Build a simple OHLCV DataFrame from market data
                    if isinstance(symbol_data, dict) and "close" in symbol_data:
                        import pandas as pd
                        import numpy as np

                        # Create synthetic panel from current market data
                        close_price = float(symbol_data.get("close", 100.0))
                        open_price = float(symbol_data.get("open", close_price))
                        high_price = float(symbol_data.get("high", close_price * 1.01))
                        low_price = float(symbol_data.get("low", close_price * 0.99))
                        volume = float(symbol_data.get("volume", 1_000_000))

                        # CRITICAL: Generating synthetic lookback data from random noise.
                        # This is NOT real market data. Any trading decisions based on
                        # this are unreliable and should be suppressed or flagged.
                        self.using_synthetic_data = True
                        logger.critical(
                            "USING_SYNTHETIC_DATA",
                            msg="Synthetic OHLCV data generated because real historical data is unavailable. "
                                "All downstream trading decisions are UNRELIABLE and must be flagged.",
                            symbol=symbol,
                            n_bars=100,
                        )
                        np.random.seed(42)
                        n_bars = 100
                        dates = pd.date_range(end=pd.Timestamp.now(), periods=n_bars, freq="D")
                        returns = np.random.normal(0.0001, 0.02, n_bars)
                        close_series = close_price * np.cumprod(1 + returns)

                        panel = {
                            "close": pd.DataFrame({"SYMBOL": close_series}, index=dates),
                            "open": pd.DataFrame({"SYMBOL": close_series * (1 + np.random.normal(0, 0.005, n_bars))}, index=dates),
                            "high": pd.DataFrame({"SYMBOL": close_series * (1 + np.abs(np.random.normal(0, 0.01, n_bars)))}, index=dates),
                            "low": pd.DataFrame({"SYMBOL": close_series * (1 - np.abs(np.random.normal(0, 0.01, n_bars)))}, index=dates),
                            "volume": pd.DataFrame({"SYMBOL": np.random.lognormal(14, 1, n_bars)}, index=dates),
                        }

                        # Compute factor snapshot
                        factor_snapshot = self._factor_bridge.compute_snapshot(panel)
                        updates["factor_snapshot"] = factor_snapshot.model_dump()

                        # Compute returns for regime detection
                        returns_series = pd.Series(returns, index=dates)
                        volatility_series = returns_series.rolling(20, min_periods=5).std()

                        # Detect regime
                        regime_state = self._regime_detector.detect(
                            factor_snapshot=factor_snapshot,
                            returns=returns_series,
                            volatility=volatility_series,
                        )
                        updates["regime_state"] = regime_state.model_dump()

                        logger.info(
                            "factor_regime_detected",
                            factor_regime=factor_snapshot.regime_signal,
                            factor_confidence=round(factor_snapshot.factor_confidence, 3),
                            market_regime=regime_state.current_regime,
                            risk_multiplier=regime_state.risk_multiplier,
                        )

                        # Update metadata for pressure synthesis compatibility
                        updates["metadata"] = {
                            **state.get("metadata", {}),
                            "regime": regime_state.current_regime.upper(),
                            "regime_confidence": regime_state.confidence,
                            "risk_multiplier": regime_state.risk_multiplier,
                            "factor_composite": factor_snapshot.composite_score,
                            "momentum_score": float(np.clip(factor_snapshot.composite_score, -1.0, 1.0)),
                            "n_bullish_factors": len(factor_snapshot.top_bullish_factors),
                            "n_bearish_factors": len(factor_snapshot.top_bearish_factors),
                        }
                    else:
                        # No close data — use defaults
                        updates["factor_snapshot"] = {}
                        updates["regime_state"] = {
                            "current_regime": "sideways",
                            "regime_probability": {"bull": 0.25, "bear": 0.25, "sideways": 0.25, "crisis": 0.25},
                            "risk_multiplier": 1.0,
                        }
                else:
                    updates["factor_snapshot"] = {}
                    updates["regime_state"] = {
                        "current_regime": "sideways",
                        "regime_probability": {"bull": 0.25, "bear": 0.25, "sideways": 0.25, "crisis": 0.25},
                        "risk_multiplier": 1.0,
                    }
            else:
                updates["factor_snapshot"] = {}
                updates["regime_state"] = {
                    "current_regime": "sideways",
                    "regime_probability": {"bull": 0.25, "bear": 0.25, "sideways": 0.25, "crisis": 0.25},
                    "risk_multiplier": 1.0,
                }

        except Exception as e:
            logger.error(f"Factor/regime detection failed: {e}")
            updates["factor_snapshot"] = {"error": str(e)}
            updates["regime_state"] = {
                "current_regime": "sideways",
                "regime_probability": {"bull": 0.25, "bear": 0.25, "sideways": 0.25, "crisis": 0.25},
                "risk_multiplier": 1.0,
                "error": str(e),
            }

        updates["sender"] = "factor_regime_detection"
        return updates

    def _signal_generation_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Signal generation node: runs the strategist agent.

        Args:
            state: Current agent state

        Returns:
            State updates with generated signals
        """
        logger.info("=== Signal Generation Phase ===")

        try:
            strategist = self._factory.create_agent("strategist", use_deep_llm=True)
            result = strategist(state)
            return {
                "signals": result.get("signals", []),
                "strategist_output": result.get("strategist_output", ""),
                "confidence": result.get("confidence", 0.0),
                "agent_outputs": {
                    **state.get("agent_outputs", {}),
                    **result.get("agent_outputs", {}),
                },
                "sender": "signal_generation",
            }
        except Exception as e:
            logger.error(f"Strategist agent failed: {e}")
            return {
                "signals": [],
                "strategist_output": f"Strategy generation failed: {e}",
                "confidence": 0.0,
                "sender": "signal_generation",
            }

    def _risk_assessment_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Risk assessment node: runs the 9-checkpoint risk gate.

        Args:
            state: Current agent state

        Returns:
            State updates with risk assessment
        """
        logger.info("=== Risk Assessment Phase ===")

        try:
            risk = self._factory.create_agent("risk", use_deep_llm=True)
            result = risk(state)
            return {
                "risk_assessment": result.get("risk_assessment", {}),
                "risk_verdict": result.get("risk_verdict", RiskVerdict.VETOED.value),
                "kill_switch_active": result.get("kill_switch_active", False),
                "should_halt": result.get("should_halt", True),
                "agent_outputs": {
                    **state.get("agent_outputs", {}),
                    **result.get("agent_outputs", {}),
                },
                "sender": "risk_assessment",
            }
        except Exception as e:
            logger.error(f"Risk agent failed: {e}")
            return {
                "risk_assessment": {"error": str(e)},
                "risk_verdict": RiskVerdict.VETOED.value,
                "kill_switch_active": False,
                "should_halt": True,
                "sender": "risk_assessment",
            }

    def _portfolio_optimization_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Portfolio optimization node.

        Args:
            state: Current agent state

        Returns:
            State updates with portfolio optimization
        """
        logger.info("=== Portfolio Optimization Phase ===")

        try:
            portfolio = self._factory.create_agent("portfolio")
            result = portfolio(state)
            return {
                "portfolio_output": result.get("portfolio_output", ""),
                "agent_outputs": {
                    **state.get("agent_outputs", {}),
                    **result.get("agent_outputs", {}),
                },
                "sender": "portfolio_optimization",
            }
        except Exception as e:
            logger.error(f"Portfolio agent failed: {e}")
            return {
                "portfolio_output": f"Portfolio optimization failed: {e}",
                "sender": "portfolio_optimization",
            }

    def _execution_decision_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Execution decision node: runs the trader agent.

        Args:
            state: Current agent state

        Returns:
            State updates with trading decisions
        """
        logger.info("=== Execution Decision Phase ===")

        # Warn if trading decisions are based on synthetic data
        if self.using_synthetic_data:
            logger.critical(
                "EXECUTION_ON_SYNTHETIC_DATA",
                msg="Trading decisions are being made on SYNTHETIC/FABRICATED data. "
                    "All decisions are UNRELIABLE. Consider suppressing or flagging.",
            )

        try:
            trader = self._factory.create_agent("trader")
            result = trader(state)

            # Flag decisions as unreliable if synthetic data was used
            decisions = result.get("decisions", [])
            if self.using_synthetic_data and decisions:
                for decision in decisions:
                    decision["using_synthetic_data"] = True
                    decision["reliability_warning"] = (
                        "Decision based on synthetic/fabricated market data — not reliable"
                    )

            return {
                "decisions": decisions,
                "trader_output": result.get("trader_output", ""),
                "confidence": result.get("confidence", state.get("confidence", 0.0)),
                "agent_outputs": {
                    **state.get("agent_outputs", {}),
                    **result.get("agent_outputs", {}),
                },
                "sender": "execution_decision",
            }
        except Exception as e:
            logger.error(f"Trader agent failed: {e}")
            return {
                "decisions": [],
                "trader_output": f"Trade decision failed: {e}",
                "sender": "execution_decision",
            }

    def _order_execution_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Order execution node: runs the execution agent.

        Args:
            state: Current agent state

        Returns:
            State updates with executed orders
        """
        logger.info("=== Order Execution Phase ===")

        try:
            execution = self._factory.create_agent("execution")
            result = execution(state)
            return {
                "execution_output": result.get("execution_output", ""),
                "orders_placed": result.get("orders_placed", []),
                "agent_outputs": {
                    **state.get("agent_outputs", {}),
                    **result.get("agent_outputs", {}),
                },
                "sender": "order_execution",
            }
        except Exception as e:
            logger.error(f"Execution agent failed: {e}")
            return {
                "execution_output": f"Order execution failed: {e}",
                "orders_placed": [],
                "sender": "order_execution",
            }

    def _reflection_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Reflection node: post-trade analysis and learning.

        Args:
            state: Current agent state

        Returns:
            State updates with reflection results
        """
        logger.info("=== Reflection Phase ===")

        # Run a brief council debate for reflection
        try:
            debate_results = self._council_debate.run_full_debate(state)
            return {
                "debate_state": debate_results.get("debate_state", {}),
                "sender": "reflection",
            }
        except Exception as e:
            logger.error(f"Reflection failed: {e}")
            return {
                "debate_state": {"error": str(e)},
                "sender": "reflection",
            }

    def _council_debate_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Council debate node: runs when confidence is below threshold.

        CRITICAL: If the risk agent has issued a VETO or KILL_SWITCH,
        the council CANNOT override it. The council's final_decision
        will be forced to HOLD (VETO) or EMERGENCY_EXIT (KILL_SWITCH)
        by the CouncilVoting.run_council_vote() method.

        Args:
            state: Current agent state

        Returns:
            State updates with council debate results
        """
        logger.info("=== Council Debate Phase ===")

        # Constitutional guard: If risk verdict was VETOED or KILL_SWITCH,
        # council debate cannot override it. Force halt/emergency exit.
        risk_verdict = state.get("risk_verdict", "")
        if risk_verdict == RiskVerdict.VETOED.value:
            logger.warning(
                "Council debate bypassed: risk VETO is constitutional and cannot be overridden"
            )
            return {
                "debate_state": {"veto_override": True, "reason": "Risk VETO is constitutional"},
                "council_result": {"final_decision": TradeAction.HOLD.value, "veto_enforced": True},
                "should_halt": True,
                "sender": "council_debate",
            }
        if risk_verdict == RiskVerdict.KILL_SWITCH.value:
            logger.critical(
                "Council debate bypassed: KILL_SWITCH is constitutional and cannot be overridden"
            )
            return {
                "debate_state": {"veto_override": True, "reason": "KILL_SWITCH is constitutional"},
                "council_result": {"final_decision": TradeAction.EMERGENCY_EXIT.value, "kill_switch_enforced": True},
                "kill_switch_active": True,
                "should_halt": True,
                "sender": "council_debate",
            }

        try:
            # Run the council debate
            debate_results = self._council_debate.run_full_debate(state)

            # Run the council vote
            council_result = self._council_voting.run_council_vote(state)

            # Override the trader decision with council result if needed
            if council_result.final_decision in (TradeAction.BUY, TradeAction.SELL):
                # Update decisions based on council vote
                symbols = state.get("symbols", [])
                updated_decisions = []
                for symbol in symbols:
                    updated_decisions.append({
                        "symbol": symbol,
                        "action": council_result.final_decision.value,
                        "confidence": council_result.consensus_level,
                        "reasoning": "Council debate decision with weighted voting",
                    })

                return {
                    "debate_state": debate_results.get("debate_state", {}),
                    "council_result": council_result.model_dump(),
                    "decisions": updated_decisions,
                    "confidence": council_result.consensus_level,
                    "agent_outputs": {
                        **state.get("agent_outputs", {}),
                        "council": council_result.model_dump(),
                    },
                    "sender": "council_debate",
                }

            return {
                "debate_state": debate_results.get("debate_state", {}),
                "council_result": council_result.model_dump(),
                "sender": "council_debate",
            }
        except Exception as e:
            logger.error(f"Council debate failed: {e}")
            return {
                "debate_state": {"error": str(e)},
                "sender": "council_debate",
            }

    def _pressure_synthesis_node(self, state: AgentState) -> Dict[str, Any]:
        """Pressure synthesis node: synthesises multi-agent signals into a unified PressureVector.

        Runs after council debate/voting and before the execution decision.
        Takes all agent outputs, regime state, factor snapshot, and risk
        state and produces a unified PressureVector that the execution
        decision node can use.

        Args:
            state: Current agent state

        Returns:
            State updates with the pressure_vector and metadata
        """
        logger.info("=== Pressure Synthesis Phase ===")

        try:
            # Extract agent signals from the accumulated agent outputs
            agent_outputs = state.get("agent_outputs", {})
            agent_signals = extract_agent_signals(agent_outputs)

            # Build regime state from metadata or risk assessment
            risk_assessment = state.get("risk_assessment", {})
            metadata = state.get("metadata", {})
            regime_str = metadata.get("regime", "UNKNOWN")
            try:
                regime = MarketRegime(regime_str)
            except ValueError:
                regime = MarketRegime.UNKNOWN

            regime_state = SynthesisRegimeState(
                regime=regime,
                regime_confidence=metadata.get("regime_confidence", 0.5),
                volatility_level=metadata.get("volatility_level", 0.3),
            )

            # Build factor snapshot from metadata, enriched by factor pipeline bridge data
            factor_snapshot_data = state.get("factor_snapshot", {})
            momentum_score = metadata.get("momentum_score", 0.0)
            if factor_snapshot_data and "composite_score" in factor_snapshot_data:
                # Use the actual factor composite score from the bridge
                momentum_score = float(np.clip(factor_snapshot_data.get("composite_score", 0.0), -1.0, 1.0))

            factor_snapshot = SynthesisFactorSnapshot(
                momentum_score=momentum_score,
                value_score=metadata.get("value_score", 0.0),
                sentiment_score=metadata.get("sentiment_score", 0.0),
                flow_score=metadata.get("flow_score", 0.0),
            )

            # Build risk state from risk assessment
            risk_state = SynthesisRiskState(
                risk_budget_used=risk_assessment.get("risk_budget_used", 0.0),
                kill_switch_active=state.get("kill_switch_active", False),
                daily_loss_pct=risk_assessment.get("daily_pnl_pct", 0.0),
                weekly_loss_pct=risk_assessment.get("weekly_pnl_pct", 0.0),
            )

            # Synthesize
            pressure_vector = self._pressure_synthesizer.synthesize(
                agent_signals=agent_signals,
                regime_state=regime_state,
                factor_snapshot=factor_snapshot,
                risk_state=risk_state,
            )

            # Update confidence based on pressure vector
            updated_confidence = pressure_vector.confidence
            if pressure_vector.consensus_level in ("strong_majority", "majority"):
                updated_confidence = max(updated_confidence, state.get("confidence", 0.0))

            return {
                "pressure_vector": pressure_vector.model_dump(),
                "confidence": updated_confidence,
                "metadata": {
                    **state.get("metadata", {}),
                    "pressure_direction": pressure_vector.direction,
                    "pressure_magnitude": pressure_vector.magnitude,
                    "pressure_consensus": pressure_vector.consensus_level,
                    "regime_adjusted_direction": pressure_vector.regime_adjusted_direction,
                },
                "sender": "pressure_synthesis",
            }
        except Exception as e:
            logger.error(f"Pressure synthesis failed: {e}")
            return {
                "pressure_vector": {
                    "direction": 0.0,
                    "magnitude": 0.0,
                    "confidence": 0.0,
                    "consensus_level": "no_consensus",
                },
                "sender": "pressure_synthesis",
            }

    def _emergency_exit_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Emergency exit node: closes all positions immediately.

        Args:
            state: Current agent state

        Returns:
            State updates with emergency exit actions
        """
        logger.critical("=== EMERGENCY EXIT ACTIVATED ===")

        symbols = state.get("symbols", [])
        decisions = []
        for symbol in symbols:
            decisions.append({
                "symbol": symbol,
                "action": TradeAction.EMERGENCY_EXIT.value,
                "quantity": 0,
                "reasoning": "Kill switch activated - emergency exit",
                "confidence": 1.0,
            })

        return {
            "decisions": decisions,
            "should_halt": True,
            "kill_switch_active": True,
            "sender": "emergency_exit",
        }

    def run(
        self,
        symbols: List[str],
        trade_date: Optional[str] = None,
        market_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run the complete trading pipeline.

        Args:
            symbols: List of trading symbols to analyze
            trade_date: Trading date string (YYYY-MM-DD)
            market_data: Optional pre-loaded market data
            metadata: Optional additional metadata

        Returns:
            Final agent state after pipeline completion
        """
        trade_date = trade_date or datetime.now().strftime("%Y-%m-%d")

        # Start a new correlation context for this trading cycle
        # This ensures all downstream decisions are traceable
        primary_symbol = symbols[0] if symbols else None
        cycle_metadata = {
            "trade_date": trade_date,
            "symbols": symbols,
            **(metadata or {}),
        }
        correlation_id = CorrelationContext.new_cycle(
            symbol=primary_symbol,
            metadata=cycle_metadata,
        )
        logger.info(
            f"Starting trading pipeline for {symbols} on {trade_date} "
            f"[correlation_id={correlation_id}]"
        )

        # Create initial state
        initial_state = create_initial_state(symbols, trade_date)

        # Inject correlation ID into state metadata
        initial_state["metadata"]["correlation_id"] = correlation_id

        # Add optional data
        if market_data:
            initial_state["market_data"] = market_data
        if metadata:
            initial_state["metadata"].update(metadata)
            # Re-set correlation_id in case metadata overwrote it
            initial_state["metadata"]["correlation_id"] = correlation_id

        # Run the graph
        try:
            final_state = self._graph.invoke(initial_state)
            logger.info(
                "Trading pipeline completed successfully",
                extra={"correlation_id": correlation_id}
            )
            return final_state
        except Exception as e:
            logger.error(
                f"Trading pipeline failed: {e}",
                extra={"correlation_id": correlation_id}
            )
            return {
                **initial_state,
                "error": str(e),
                "should_halt": True,
            }
        finally:
            CorrelationContext.clear()

    def run_stream(self, symbols: List[str], trade_date: Optional[str] = None, **kwargs: Any):
        """
        Run the trading pipeline with streaming output.

        Args:
            symbols: List of trading symbols
            trade_date: Trading date string
            **kwargs: Additional arguments passed to run()

        Yields:
            State updates as they occur
        """
        trade_date = trade_date or datetime.now().strftime("%Y-%m-%d")
        initial_state = create_initial_state(symbols, trade_date)

        # Start correlation context for streaming pipeline
        primary_symbol = symbols[0] if symbols else None
        correlation_id = CorrelationContext.new_cycle(
            symbol=primary_symbol,
            metadata={"trade_date": trade_date, "symbols": symbols},
        )
        initial_state["metadata"]["correlation_id"] = correlation_id

        try:
            for chunk in self._graph.stream(initial_state):
                yield chunk
        finally:
            CorrelationContext.clear()

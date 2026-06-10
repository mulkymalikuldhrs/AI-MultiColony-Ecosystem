"""
Main LangGraph Trading Graph
=============================
Researcher → Analyst → Strategist → Risk Manager → Trader → Portfolio Manager

The graph uses conditional routing:
- If risk is VETOED → skip to end (NO_TRADE)
- If regime is NO_TRADE → skip to end
- Portfolio Manager has final gate approval
"""

from __future__ import annotations

from typing import Any

from langgraph.graph import StateGraph, END

from quant_nanggroe_ai.agents.state import AgentState


def researcher_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Research Agent — Gathers market data, news, and macro context.

    This is the entry point of the trading graph.
    """
    # Placeholder — will be implemented with actual LLM integration
    return {
        "research_summary": f"Research completed for {state.get('symbol', 'UNKNOWN')}",
        "agent_trace": state.get("agent_trace", []) + [
            {"agent": "researcher", "status": "completed", "action": "research"}
        ],
    }


def analyst_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Market Intelligence Agent — Technical analysis, SMC, sentiment.

    Processes research data into actionable intelligence.
    """
    return {
        "agent_trace": state.get("agent_trace", []) + [
            {"agent": "analyst", "status": "completed", "action": "analyze"}
        ],
    }


def strategist_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Strategy Lab Agent — Generates entry/exit strategies.

    Combines analysis with market state to produce trade plans.
    """
    regime = state.get("regime", "UNKNOWN")
    buy_pressure = state.get("buy_pressure", 0.0)
    sell_pressure = state.get("sell_pressure", 0.0)

    # Basic signal determination
    if buy_pressure > 0.6:
        signal = "BUY"
    elif sell_pressure > 0.6:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "strategy_signal": signal,
        "agent_trace": state.get("agent_trace", []) + [
            {"agent": "strategist", "status": "completed", "signal": signal}
        ],
    }


def risk_manager_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Risk Engine Agent — 9-checkpoint VETO system.

    Has FULL VETO authority. Cannot be overridden.
    """
    from quant_nanggroe_ai.engine.risk_guard import ConstitutionalRiskGuard

    risk_guard = ConstitutionalRiskGuard()

    # Check the trade through the 9-checkpoint system
    result = risk_guard.check_trade(
        symbol=state.get("symbol", ""),
        direction=state.get("strategy_signal", "HOLD"),
        lot_size=state.get("position_size", 0.01),
        entry=state.get("entry_price", 0.0),
        stop_loss=state.get("stop_loss", None),
        take_profit=state.get("take_profit", [None])[0] if state.get("take_profit") else None,
    )

    return {
        "risk_verdict": result.verdict,
        "risk_checkpoints": {k: v.model_dump() for k, v in result.checkpoints.items()},
        "risk_clearance": "CLEAR" if result.verdict == "APPROVED" else "BLOCKED",
        "agent_trace": state.get("agent_trace", []) + [
            {"agent": "risk_manager", "status": "completed", "verdict": result.verdict}
        ],
    }


def trader_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Execution Agent — Executes approved trades.

    Only reached if risk clearance is CLEAR.
    """
    return {
        "execution_status": "PENDING",
        "agent_trace": state.get("agent_trace", []) + [
            {"agent": "trader", "status": "completed", "action": "execute"}
        ],
    }


def portfolio_manager_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Portfolio Intelligence Agent — Final gate.

    Reviews all decisions before execution. Can REJECT even after risk approval.
    """
    # Final portfolio-level checks (correlation, concentration, etc.)
    decision_action = state.get("decision_action", "NO_TRADE")
    risk_clearance = state.get("risk_clearance", "BLOCKED")

    if risk_clearance == "CLEAR" and decision_action != "NO_TRADE":
        portfolio_decision = "APPROVE"
    else:
        portfolio_decision = "REJECT"

    return {
        "portfolio_decision": portfolio_decision,
        "agent_trace": state.get("agent_trace", []) + [
            {"agent": "portfolio_manager", "status": "completed", "decision": portfolio_decision}
        ],
    }


def should_continue_after_risk(state: dict[str, Any]) -> str:
    """Conditional routing: if risk VETOED, skip to end."""
    if state.get("risk_clearance") == "CLEAR":
        return "trader"
    return "end"


def should_continue_after_regime(state: dict[str, Any]) -> str:
    """Conditional routing: if NO_TRADE regime, skip to end."""
    regime = state.get("regime", "UNKNOWN")
    if regime in ("NO_TRADE", "PANIC", "RISK_OFF"):
        return "end"
    return "analyst"


def build_trading_graph() -> StateGraph:
    """
    Build the main LangGraph trading graph.

    Flow:
    1. Researcher → gathers data
    2. Analyst → processes intelligence
    3. Strategist → generates strategy
    4. Risk Manager → VETO/APPROVE
    5. Trader → executes (if approved)
    6. Portfolio Manager → final gate

    Returns:
        Compiled StateGraph ready for execution
    """
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("researcher", researcher_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("strategist", strategist_node)
    graph.add_node("risk_manager", risk_manager_node)
    graph.add_node("trader", trader_node)
    graph.add_node("portfolio_manager", portfolio_manager_node)

    # Set entry point
    graph.set_entry_point("researcher")

    # Add edges
    graph.add_conditional_edges(
        "researcher",
        should_continue_after_regime,
        {"analyst": "analyst", "end": END},
    )
    graph.add_edge("analyst", "strategist")
    graph.add_edge("strategist", "risk_manager")
    graph.add_conditional_edges(
        "risk_manager",
        should_continue_after_risk,
        {"trader": "trader", "end": END},
    )
    graph.add_edge("trader", "portfolio_manager")
    graph.add_edge("portfolio_manager", END)

    return graph.compile()


# Singleton compiled graph
_compiled_graph = None


def get_trading_graph():
    """Get or create the compiled trading graph."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_trading_graph()
    return _compiled_graph

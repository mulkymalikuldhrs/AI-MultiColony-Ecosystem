"""
Portfolio Intelligence Agent — Final gate approval.
"""

from __future__ import annotations

from typing import Any


async def portfolio_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Portfolio Intelligence Agent node.

    Final gate: reviews all decisions before execution.
    Can REJECT even after risk approval.
    """
    return {
        "portfolio_decision": "REJECT",
        "agent_trace": state.get("agent_trace", []) + [
            {"agent": "portfolio_manager", "status": "completed"}
        ],
    }

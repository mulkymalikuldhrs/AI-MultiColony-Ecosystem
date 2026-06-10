"""Trade execution tool for agents."""

from __future__ import annotations

from typing import Any


async def execute_trade(
    symbol: str,
    direction: str,
    quantity: float,
    order_type: str = "MARKET",
    price: float | None = None,
) -> dict[str, Any]:
    """Execute a trade through the broker."""
    # TODO: Integrate with execution layer
    return {"status": "pending", "message": "Execution engine not yet integrated"}

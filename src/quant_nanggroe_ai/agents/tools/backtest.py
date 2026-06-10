"""Backtest runner tool for agents."""

from __future__ import annotations

from typing import Any


async def run_backtest(
    symbol: str,
    strategy_name: str,
    start_date: str,
    end_date: str,
    initial_capital: float = 10000.0,
) -> dict[str, Any]:
    """Run a backtest for a strategy."""
    # TODO: Integrate with backtest engine
    return {"status": "pending", "message": "Backtest engine not yet integrated"}

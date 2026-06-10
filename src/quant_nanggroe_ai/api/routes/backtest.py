"""Backtest routes."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.post("/run")
async def run_backtest(symbol: str, strategy: str, start_date: str, end_date: str):
    """Run a backtest."""
    return {"status": "pending", "symbol": symbol, "strategy": strategy}


@router.get("/results/{backtest_id}")
async def get_backtest_results(backtest_id: str):
    """Get backtest results."""
    return {"backtest_id": backtest_id, "status": "pending"}

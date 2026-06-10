"""Portfolio routes."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/summary")
async def get_portfolio_summary():
    """Get portfolio summary."""
    return {"total_value": 0.0, "positions": [], "pnl": 0.0}


@router.get("/risk")
async def get_portfolio_risk():
    """Get portfolio risk metrics."""
    return {"var": 0.0, "cvar": 0.0, "max_drawdown": 0.0}

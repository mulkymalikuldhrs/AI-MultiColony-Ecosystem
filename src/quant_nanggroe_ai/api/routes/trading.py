"""Trading routes."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.post("/order")
async def place_order(symbol: str, direction: str, quantity: float):
    """Place a trade order."""
    return {"status": "pending", "symbol": symbol, "direction": direction, "quantity": quantity}


@router.get("/positions")
async def get_positions():
    """Get all open positions."""
    return {"positions": []}


@router.get("/history")
async def get_trade_history(limit: int = 50):
    """Get trade history."""
    return {"trades": []}


@router.post("/risk-check")
async def risk_check(symbol: str, direction: str, entry: float, stop_loss: float, lot_size: float = 0.01):
    """Run a risk check for a proposed trade."""
    from quant_nanggroe_ai.engine.risk_guard import ConstitutionalRiskGuard
    guard = ConstitutionalRiskGuard()
    result = guard.check_trade(symbol=symbol, direction=direction, lot_size=lot_size, entry=entry, stop_loss=stop_loss)
    return result.model_dump()

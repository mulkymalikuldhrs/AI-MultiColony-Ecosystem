"""Market data routes."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/ohlcv/{symbol}")
async def get_ohlcv(symbol: str, timeframe: str = "1d", limit: int = 100):
    """Get OHLCV data for a symbol."""
    return {"symbol": symbol, "timeframe": timeframe, "data": []}


@router.get("/price/{symbol}")
async def get_latest_price(symbol: str):
    """Get the latest price for a symbol."""
    return {"symbol": symbol, "price": None}


@router.get("/regime/{symbol}")
async def get_market_regime(symbol: str):
    """Get current market regime for a symbol."""
    from quant_nanggroe_ai.engine.market_state import MarketStateEngine
    engine = MarketStateEngine()
    result = engine.detect_regime(symbol=symbol)
    return result.model_dump()

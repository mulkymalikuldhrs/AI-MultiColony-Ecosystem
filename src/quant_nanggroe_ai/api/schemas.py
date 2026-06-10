"""
Pydantic Request/Response Schemas
===================================
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


# ── Market Data ───────────────────────────────────────────────────────

class OHLCVRequest(BaseModel):
    symbol: str
    timeframe: str = "1d"
    limit: int = Field(default=100, ge=1, le=1000)


class PriceResponse(BaseModel):
    symbol: str
    price: float | None
    timestamp: datetime = Field(default_factory=datetime.now)


# ── Trading ───────────────────────────────────────────────────────────

class OrderRequest(BaseModel):
    symbol: str
    direction: str  # BUY / SELL
    quantity: float = Field(gt=0)
    order_type: str = "MARKET"
    price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None


class OrderResponse(BaseModel):
    order_id: str
    status: str
    symbol: str
    direction: str
    quantity: float
    filled_price: float | None = None
    timestamp: datetime = Field(default_factory=datetime.now)


# ── Risk ──────────────────────────────────────────────────────────────

class RiskCheckRequest(BaseModel):
    symbol: str
    direction: str
    entry: float = Field(gt=0)
    stop_loss: float | None = None
    take_profit: float | None = None
    lot_size: float = Field(default=0.01, gt=0)
    account_balance: float = Field(default=10000.0, gt=0)


# ── Backtest ──────────────────────────────────────────────────────────

class BacktestRequest(BaseModel):
    symbol: str
    strategy: str
    start_date: str
    end_date: str
    initial_capital: float = Field(default=10000.0, gt=0)


# ── Agent ─────────────────────────────────────────────────────────────

class AgentRunRequest(BaseModel):
    symbol: str
    query: str = ""
    timeframe: str = "1d"


# ── Common ────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
    error_type: str = "unknown"

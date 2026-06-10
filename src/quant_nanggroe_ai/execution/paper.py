"""
Paper Trading Broker — Simulated execution for testing
=======================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class PaperOrder(BaseModel):
    """Paper trading order."""

    id: str = ""
    symbol: str
    direction: str  # BUY / SELL
    quantity: float
    order_type: str = "MARKET"  # MARKET / LIMIT
    price: float | None = None
    status: str = "PENDING"  # PENDING / FILLED / CANCELLED
    filled_price: float | None = None
    filled_at: datetime | None = None
    commission: float = 0.0
    slippage: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)


class PaperBroker:
    """
    Simulated broker for paper trading.

    Features:
    - Market and limit order simulation
    - Configurable commission and slippage
    - Full order history
    """

    def __init__(self, commission: float = 0.001, slippage: float = 0.0005) -> None:
        self.commission = commission
        self.slippage = slippage
        self.orders: list[PaperOrder] = []
        self._order_counter = 0

    async def submit_order(
        self,
        symbol: str,
        direction: str,
        quantity: float,
        order_type: str = "MARKET",
        price: float | None = None,
        current_market_price: float | None = None,
    ) -> PaperOrder:
        """Submit an order for paper execution."""
        self._order_counter += 1
        order = PaperOrder(
            id=f"PAPER-{self._order_counter:06d}",
            symbol=symbol,
            direction=direction,
            quantity=quantity,
            order_type=order_type,
            price=price,
        )

        # Simulate fill
        fill_price = price or current_market_price or 0.0
        if fill_price > 0:
            slip = fill_price * self.slippage
            if direction == "BUY":
                fill_price += slip
            else:
                fill_price -= slip

            order.status = "FILLED"
            order.filled_price = fill_price
            order.filled_at = datetime.now()
            order.commission = fill_price * quantity * self.commission
            order.slippage = abs(slip)

        self.orders.append(order)
        return order

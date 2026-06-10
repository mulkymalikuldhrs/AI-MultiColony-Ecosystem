"""Alpaca live broker connector (stub — requires API key)."""

from __future__ import annotations

from typing import Any


class AlpacaBroker:
    """Alpaca live broker — stocks and crypto execution."""

    async def submit_order(self, symbol: str, direction: str, quantity: float, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError("Alpaca broker requires API key configuration")

    async def get_positions(self) -> list[dict[str, Any]]:
        raise NotImplementedError("Alpaca broker requires API key configuration")

    async def cancel_order(self, order_id: str) -> dict[str, Any]:
        raise NotImplementedError("Alpaca broker requires API key configuration")

"""Polymarket execution connector (stub — from polymarket-cli)."""

from __future__ import annotations

from typing import Any


class PolymarketExecutor:
    """Polymarket execution — from polymarket-cli."""

    async def place_bet(self, market_id: str, outcome: str, amount: float) -> dict[str, Any]:
        raise NotImplementedError("Polymarket connector requires API key configuration")

    async def get_markets(self) -> list[dict[str, Any]]:
        raise NotImplementedError("Polymarket connector requires API key configuration")

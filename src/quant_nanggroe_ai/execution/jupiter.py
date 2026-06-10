"""Jupiter V6 Solana swap connector (stub — from SolSniperX)."""

from __future__ import annotations

from typing import Any


class JupiterSwap:
    """Jupiter V6 Solana DEX aggregator — from SolSniperX."""

    async def get_quote(self, input_mint: str, output_mint: str, amount: int) -> dict[str, Any]:
        raise NotImplementedError("Jupiter connector requires Solana wallet configuration")

    async def execute_swap(self, quote: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Jupiter connector requires Solana wallet configuration")

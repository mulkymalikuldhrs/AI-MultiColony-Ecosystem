"""Technical analysis tool for agents — runs MathEngine indicators."""

from __future__ import annotations

from typing import Any

from quant_nanggroe_ai.engine.math_lib import MathEngine


async def run_technical_analysis(
    closes: list[float],
    highs: list[float] | None = None,
    lows: list[float] | None = None,
    volumes: list[float] | None = None,
) -> dict[str, Any]:
    """Run full technical analysis on price data."""
    return MathEngine.analyze_sequence(closes, highs, lows, volumes)

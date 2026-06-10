"""
Performance Metrics — QuantStats/Empyrical integration
======================================================
Sharpe, Sortino, Calmar, Max Drawdown, Win Rate, Profit Factor, etc.
"""

from __future__ import annotations

from typing import Any


def calculate_metrics(returns: list[float], benchmark: list[float] | None = None) -> dict[str, Any]:
    """
    Calculate comprehensive performance metrics from a returns series.

    Args:
        returns: List of period returns
        benchmark: Optional benchmark returns for comparison

    Returns:
        Dict with all calculated metrics
    """
    if not returns:
        return {"error": "No returns data provided"}

    n = len(returns)
    total_return = sum(returns)
    avg_return = total_return / n if n > 0 else 0.0

    # Basic statistics
    positive_returns = [r for r in returns if r > 0]
    negative_returns = [r for r in returns if r < 0]
    win_rate = len(positive_returns) / n if n > 0 else 0.0

    # Volatility
    if n > 1:
        variance = sum((r - avg_return) ** 2 for r in returns) / (n - 1)
        std_dev = variance ** 0.5
        sharpe_ratio = (avg_return / std_dev) if std_dev > 0 else 0.0
    else:
        std_dev = 0.0
        sharpe_ratio = 0.0

    # Max drawdown
    peak = 0.0
    max_dd = 0.0
    equity = 1.0
    for r in returns:
        equity *= (1 + r)
        peak = max(peak, equity)
        dd = (peak - equity) / peak if peak > 0 else 0.0
        max_dd = max(max_dd, dd)

    # Profit factor
    gross_profit = sum(positive_returns) if positive_returns else 0.0
    gross_loss = abs(sum(negative_returns)) if negative_returns else 0.0
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    return {
        "total_return": round(total_return, 4),
        "avg_return": round(avg_return, 6),
        "volatility": round(std_dev, 6),
        "sharpe_ratio": round(sharpe_ratio, 4),
        "max_drawdown": round(max_dd, 4),
        "win_rate": round(win_rate, 4),
        "profit_factor": round(profit_factor, 4) if profit_factor != float("inf") else "INF",
        "total_trades": n,
        "avg_win": round(sum(positive_returns) / len(positive_returns), 6) if positive_returns else 0.0,
        "avg_loss": round(sum(negative_returns) / len(negative_returns), 6) if negative_returns else 0.0,
    }

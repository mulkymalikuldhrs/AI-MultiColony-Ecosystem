"""Professional Backtest Report Generation.

Generates comprehensive backtest reports with:
- Summary statistics table
- Monthly returns table
- Yearly returns table
- Drawdown analysis table
- Trade analysis table
- Rolling metrics (rolling Sharpe, rolling Sortino, etc.)
- Factor exposure report
- Monte Carlo confidence intervals
- Walk-forward out-of-sample results

Supports JSON and text output formats.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from quant_nanggroe.engine.backtest.portfolio import TradeRecord

logger = logging.getLogger(__name__)


class BacktestReport:
    """Generates comprehensive backtest reports.

    Supports:
    - JSON report for programmatic consumption
    - Text summary for console output
    - Monthly and yearly returns tables
    - Drawdown analysis
    - Trade-by-trade analysis
    - Rolling metrics analysis
    - Factor exposure report
    - Monte Carlo confidence intervals
    - Walk-forward out-of-sample results
    """

    @staticmethod
    def generate(
        metrics: Dict[str, Any],
        equity_curve: pd.Series,
        trades: List[TradeRecord],
        config: Optional[Dict[str, Any]] = None,
        format: str = "json",
        factor_report: Optional[Dict[str, Any]] = None,
        mc_report: Optional[Dict[str, Any]] = None,
        wf_report: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a backtest report.

        Args:
            metrics: Performance metrics dict.
            equity_curve: Equity curve series.
            trades: List of trade records.
            config: Backtest configuration dict.
            format: Output format ('json' or 'text').
            factor_report: Optional factor exposure report.
            mc_report: Optional Monte Carlo report.
            wf_report: Optional walk-forward report.

        Returns:
            Formatted report string.
        """
        if format == "json":
            return BacktestReport._generate_json(
                metrics, equity_curve, trades, config,
                factor_report, mc_report, wf_report,
            )
        elif format == "text":
            return BacktestReport._generate_text(
                metrics, equity_curve, trades, config,
                factor_report, mc_report, wf_report,
            )
        else:
            raise ValueError(f"Unknown report format: {format}")

    @staticmethod
    def generate_monthly_returns(equity_curve: pd.Series) -> pd.DataFrame:
        """Generate monthly returns table.

        Args:
            equity_curve: Equity curve with DatetimeIndex.

        Returns:
            DataFrame with monthly returns (rows=year, columns=month).
        """
        if not isinstance(equity_curve.index, pd.DatetimeIndex):
            return pd.DataFrame()

        monthly = equity_curve.resample("ME").last()
        monthly_returns = monthly.pct_change().dropna()

        if len(monthly_returns) == 0:
            return pd.DataFrame()

        # Pivot to year x month
        df = pd.DataFrame({
            "year": monthly_returns.index.year,
            "month": monthly_returns.index.month,
            "return": monthly_returns.values,
        })

        pivot = df.pivot(index="year", columns="month", values="return")
        pivot.columns = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ][:len(pivot.columns)]

        # Add annual return
        annual = equity_curve.resample("YE").last().pct_change().dropna()
        if len(annual) > 0:
            pivot["Year"] = annual.values[:len(pivot)]

        return pivot

    @staticmethod
    def generate_yearly_returns(equity_curve: pd.Series) -> pd.DataFrame:
        """Generate yearly returns table.

        Args:
            equity_curve: Equity curve with DatetimeIndex.

        Returns:
            DataFrame with yearly returns.
        """
        if not isinstance(equity_curve.index, pd.DatetimeIndex):
            return pd.DataFrame()

        yearly = equity_curve.resample("YE").last()
        yearly_returns = yearly.pct_change().dropna()

        if len(yearly_returns) == 0:
            return pd.DataFrame()

        return pd.DataFrame({
            "year": yearly_returns.index.year,
            "return": yearly_returns.values,
            "cumulative": (1 + yearly_returns).cumprod().values,
        })

    @staticmethod
    def generate_drawdown_analysis(equity_curve: pd.Series, top_n: int = 10) -> pd.DataFrame:
        """Generate drawdown analysis table.

        Args:
            equity_curve: Equity curve.
            top_n: Number of top drawdowns to report.

        Returns:
            DataFrame with drawdown details.
        """
        peak = equity_curve.cummax()
        drawdown = (equity_curve - peak) / peak.replace(0, 1)

        # Find drawdown periods
        in_dd = drawdown < 0
        dd_starts: List[int] = []
        dd_ends: List[int] = []
        dd_depths: List[float] = []

        i = 0
        while i < len(drawdown):
            if in_dd.iloc[i]:
                start = i
                max_dd = 0.0
                while i < len(drawdown) and in_dd.iloc[i]:
                    if drawdown.iloc[i] < max_dd:
                        max_dd = drawdown.iloc[i]
                    i += 1
                dd_starts.append(start)
                dd_ends.append(min(i, len(drawdown) - 1))
                dd_depths.append(max_dd)
            else:
                i += 1

        if not dd_starts:
            return pd.DataFrame()

        # Sort by depth
        sorted_idx = np.argsort(dd_depths)
        top_drawdowns = sorted_idx[:top_n]

        rows = []
        for idx in top_drawdowns:
            start_ts = equity_curve.index[dd_starts[idx]]
            end_ts = equity_curve.index[dd_ends[idx]]
            duration = dd_ends[idx] - dd_starts[idx]

            rows.append({
                "start": start_ts,
                "end": end_ts,
                "depth": round(dd_depths[idx], 4),
                "duration_bars": duration,
                "peak_equity": round(float(peak.iloc[dd_starts[idx]]), 2),
                "trough_equity": round(float(equity_curve.iloc[dd_starts[idx]:dd_ends[idx]+1].min()), 2),
            })

        return pd.DataFrame(rows)

    @staticmethod
    def generate_trade_analysis(trades: List[TradeRecord], top_n: int = 20) -> pd.DataFrame:
        """Generate trade analysis table.

        Args:
            trades: List of trade records.
            top_n: Number of top/worst trades to report.

        Returns:
            DataFrame with trade details.
        """
        if not trades:
            return pd.DataFrame()

        rows = []
        for t in trades:
            rows.append({
                "symbol": t.symbol,
                "direction": "LONG" if t.direction == 1 else "SHORT",
                "entry_price": round(t.entry_price, 4),
                "exit_price": round(t.exit_price, 4),
                "pnl": round(t.pnl, 4),
                "pnl_pct": round(t.pnl_pct, 2),
                "exit_reason": t.exit_reason,
                "holding_bars": t.holding_bars,
                "entry_time": str(t.entry_time),
                "exit_time": str(t.exit_time),
            })

        df = pd.DataFrame(rows)
        return df

    @staticmethod
    def calculate_rolling_metrics(
        equity_curve: pd.Series,
        window: int = 63,
        bars_per_year: int = 252,
        risk_free_rate: float = 0.02,
    ) -> pd.DataFrame:
        """Calculate rolling metrics (rolling Sharpe, rolling Sortino, etc.).

        Args:
            equity_curve: Equity curve.
            window: Rolling window in bars.
            bars_per_year: Bars per year.
            risk_free_rate: Annual risk-free rate.

        Returns:
            DataFrame with rolling metrics.
        """
        returns = equity_curve.pct_change().dropna()
        rf_per_bar = risk_free_rate / bars_per_year

        # Rolling Sharpe
        rolling_mean = returns.rolling(window).mean()
        rolling_std = returns.rolling(window).std()
        rolling_sharpe = (rolling_mean - rf_per_bar) / rolling_std * np.sqrt(bars_per_year)
        rolling_sharpe = rolling_sharpe.replace([np.inf, -np.inf], 0.0)

        # Rolling Sortino
        def rolling_sortino(ret_window: np.ndarray) -> float:
            excess = ret_window - rf_per_bar
            downside = excess[excess < 0]
            if len(downside) == 0:
                return 0.0
            dd = np.sqrt(np.mean(downside ** 2)) * np.sqrt(bars_per_year)
            return float(np.mean(excess) * bars_per_year / dd) if dd > 1e-10 else 0.0

        rolling_sortino_values = returns.rolling(window).apply(
            rolling_sortino, raw=True
        )

        # Rolling Max Drawdown
        def rolling_max_dd(eq_window: np.ndarray) -> float:
            peak = np.maximum.accumulate(eq_window)
            dd = (eq_window - peak) / np.where(peak > 0, peak, 1)
            return float(np.min(dd))

        rolling_max_dd = equity_curve.rolling(window).apply(
            rolling_max_dd, raw=True
        )

        # Rolling Volatility
        rolling_vol = returns.rolling(window).std() * np.sqrt(bars_per_year)

        return pd.DataFrame({
            "rolling_sharpe": rolling_sharpe,
            "rolling_sortino": rolling_sortino_values,
            "rolling_max_dd": rolling_max_dd,
            "rolling_volatility": rolling_vol,
        })

    # ══════════════════════════════════════════════════════════════════
    # JSON Report
    # ══════════════════════════════════════════════════════════════════

    @staticmethod
    def _generate_json(
        metrics: Dict[str, Any],
        equity_curve: pd.Series,
        trades: List[TradeRecord],
        config: Optional[Dict[str, Any]],
        factor_report: Optional[Dict[str, Any]] = None,
        mc_report: Optional[Dict[str, Any]] = None,
        wf_report: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate comprehensive JSON report."""
        report: Dict[str, Any] = {
            "generated_at": datetime.now().isoformat(),
            "summary": {k: v for k, v in metrics.items() if not isinstance(v, dict)},
            "config": config or {},
            "trade_count": len(trades),
        }

        # Monthly returns
        monthly = BacktestReport.generate_monthly_returns(equity_curve)
        if not monthly.empty:
            report["monthly_returns"] = monthly.to_dict()

        # Yearly returns
        yearly = BacktestReport.generate_yearly_returns(equity_curve)
        if not yearly.empty:
            report["yearly_returns"] = yearly.to_dict()

        # Drawdown analysis
        dd_analysis = BacktestReport.generate_drawdown_analysis(equity_curve)
        if not dd_analysis.empty:
            report["drawdown_analysis"] = dd_analysis.to_dict()

        # Trade analysis
        trade_analysis = BacktestReport.generate_trade_analysis(trades)
        if not trade_analysis.empty:
            report["trades"] = trade_analysis.to_dict()

        # Rolling metrics
        rolling = BacktestReport.calculate_rolling_metrics(equity_curve)
        if not rolling.empty:
            report["rolling_metrics_last"] = rolling.iloc[-1].to_dict() if len(rolling) > 0 else {}

        # Factor exposure
        if factor_report:
            report["factor_exposure"] = factor_report

        # Monte Carlo
        if mc_report:
            report["monte_carlo"] = mc_report

        # Walk-forward
        if wf_report:
            report["walk_forward"] = wf_report

        return json.dumps(report, indent=2, default=str)

    # ══════════════════════════════════════════════════════════════════
    # Text Report
    # ══════════════════════════════════════════════════════════════════

    @staticmethod
    def _generate_text(
        metrics: Dict[str, Any],
        equity_curve: pd.Series,
        trades: List[TradeRecord],
        config: Optional[Dict[str, Any]],
        factor_report: Optional[Dict[str, Any]] = None,
        mc_report: Optional[Dict[str, Any]] = None,
        wf_report: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate comprehensive text summary report."""
        lines = [
            "=" * 70,
            "  QUANT-NANGGROE-AI BACKTEST REPORT",
            "=" * 70,
            "",
            "PERFORMANCE SUMMARY",
            "-" * 50,
            f"  Final Equity:        {metrics.get('final_equity', 0):>14,.2f}",
            f"  Total Return:        {metrics.get('total_return', 0):>13.2%}",
            f"  Annual Return:       {metrics.get('annual_return', 0):>13.2%}",
            f"  CAGR:                {metrics.get('cagr', 0):>13.2%}",
            "",
            "RISK-ADJUSTED RATIOS",
            "-" * 50,
            f"  Sharpe Ratio:        {metrics.get('sharpe_ratio', 0):>13.4f}",
            f"  Sortino Ratio:       {metrics.get('sortino_ratio', 0):>13.4f}",
            f"  Calmar Ratio:        {metrics.get('calmar_ratio', 0):>13.4f}",
            f"  Omega Ratio:         {metrics.get('omega_ratio', 0):>13.4f}",
            f"  Kappa Ratio (3):     {metrics.get('kappa_ratio', 0):>13.4f}",
            f"  Sterling Ratio:      {metrics.get('sterling_ratio', 0):>13.4f}",
            f"  Burke Ratio:         {metrics.get('burke_ratio', 0):>13.4f}",
            f"  Martin Ratio:        {metrics.get('martin_ratio', 0):>13.4f}",
            f"  Tail Ratio:          {metrics.get('tail_ratio', 0):>13.4f}",
            f"  Common Sense Ratio:  {metrics.get('common_sense_ratio', 0):>13.4f}",
            "",
            "DRAWDOWN METRICS",
            "-" * 50,
            f"  Max Drawdown:        {metrics.get('max_drawdown', 0):>13.2%}",
            f"  Max DD Duration:     {metrics.get('max_drawdown_duration', 0):>10} bars",
            f"  Avg DD Duration:     {metrics.get('avg_drawdown_duration', 0):>10.1f} bars",
            f"  Ulcer Index:         {metrics.get('ulcer_index', 0):>13.6f}",
            f"  CDaR:                {metrics.get('cdar', 0):>13.4%}",
            "",
            "RISK METRICS",
            "-" * 50,
            f"  Volatility:          {metrics.get('volatility', 0):>13.4%}",
            f"  Downside Dev:        {metrics.get('downside_deviation', 0):>13.4%}",
            f"  VaR (95%):           {metrics.get('var_95', 0):>13.4%}",
            f"  CVaR (95%):          {metrics.get('cvar_95', 0):>13.4%}",
            f"  EVaR:                {metrics.get('evar', 0):>13.4%}",
            f"  CF-VaR (95%):        {metrics.get('cornish_fisher_var_95', 0):>13.4%}",
            f"  Skewness:            {metrics.get('skewness', 0):>13.4f}",
            f"  Kurtosis:            {metrics.get('kurtosis', 0):>13.4f}",
            "",
            "TRADE STATISTICS",
            "-" * 50,
            f"  Total Trades:        {metrics.get('total_trades', 0):>10}",
            f"  Winning Trades:      {metrics.get('winning_trades', 0):>10}",
            f"  Losing Trades:       {metrics.get('losing_trades', 0):>10}",
            f"  Win Rate:            {metrics.get('win_rate', 0):>13.2%}",
            f"  Profit Factor:       {metrics.get('profit_factor', 0):>13.4f}",
            f"  Payoff Ratio:        {metrics.get('payoff_ratio', 0):>13.4f}",
            f"  Recovery Factor:     {metrics.get('recovery_factor', 0):>13.4f}",
            f"  Expectancy:          {metrics.get('expectancy', 0):>13.4f}",
            f"  Avg Win:             {metrics.get('avg_win', 0):>13.4f}",
            f"  Avg Loss:            {metrics.get('avg_loss', 0):>13.4f}",
            f"  Max Consec Wins:     {metrics.get('max_consecutive_wins', 0):>10}",
            f"  Max Consec Losses:   {metrics.get('max_consecutive_losses', 0):>10}",
            f"  Avg Holding Bars:    {metrics.get('avg_holding_bars', 0):>10.1f}",
            "",
        ]

        # Benchmark comparison
        if "benchmark_return" in metrics:
            lines.extend([
                "BENCHMARK COMPARISON",
                "-" * 50,
                f"  Benchmark Return:    {metrics.get('benchmark_return', 0):>13.2%}",
                f"  Excess Return:       {metrics.get('excess_return', 0):>13.2%}",
                f"  Alpha:               {metrics.get('alpha', 0):>13.4f}",
                f"  Beta:                {metrics.get('beta', 0):>13.4f}",
                f"  Information Ratio:   {metrics.get('information_ratio', 0):>13.4f}",
                f"  Tracking Error:      {metrics.get('tracking_error', 0):>13.4f}",
                "",
            ])

        # Overfitting detection
        if "deflated_sharpe_ratio" in metrics:
            lines.extend([
                "OVERFITTING DETECTION",
                "-" * 50,
                f"  Deflated Sharpe:     {metrics.get('deflated_sharpe_ratio', 0):>13.4f}",
                f"  MC p-value:          {metrics.get('monte_carlo_pvalue', 0):>13.4f}",
                "",
            ])

        # Factor exposure
        if factor_report:
            lines.extend([
                "FACTOR EXPOSURE",
                "-" * 50,
            ])
            exposures = factor_report.get("exposures", [])
            for exp in exposures:
                if isinstance(exp, dict):
                    lines.append(f"  {exp.get('factor_name', ''):20s} β={exp.get('beta', 0):.4f}  t={exp.get('t_stat', 0):.2f}")
            lines.append(f"  R²:                  {factor_report.get('r_squared', 0):>13.4f}")
            lines.append(f"  Adj R²:              {factor_report.get('adj_r_squared', 0):>13.4f}")
            lines.append("")

        # Monte Carlo
        if mc_report:
            lines.extend([
                "MONTE CARLO CONFIDENCE INTERVALS",
                "-" * 50,
            ])
            for metric_name, mc_data in mc_report.items():
                if isinstance(mc_data, dict) and "confidence_95" in mc_data:
                    ci = mc_data["confidence_95"]
                    lines.append(f"  {metric_name:20s} 95% CI: [{ci[0]:.4f}, {ci[1]:.4f}]")
            lines.append("")

        # Walk-forward
        if wf_report:
            aggregate = wf_report.get("aggregate", {})
            degradation = wf_report.get("degradation_stats", {})
            overfitting = wf_report.get("overfitting_detection", {})
            lines.extend([
                "WALK-FORWARD ANALYSIS",
                "-" * 50,
                f"  Num Windows:         {aggregate.get('num_windows', 0):>10}",
                f"  Avg OOS Return:      {aggregate.get('avg_oos_return', 0):>13.4f}",
                f"  Avg OOS Sharpe:      {aggregate.get('avg_oos_sharpe', 0):>13.4f}",
                f"  OOS Win Rate:        {aggregate.get('win_rate', 0):>13.2%}",
                f"  Avg Degradation:     {degradation.get('avg_degradation', 0):>13.4f}",
                f"  Pass Rate:           {degradation.get('pass_rate', 0):>13.2%}",
                f"  Is Overfit:          {overfitting.get('is_overfit', False):>10}",
                f"  Overfit Severity:    {overfitting.get('overfit_severity', 'N/A'):>10}",
                "",
            ])

        lines.append("=" * 70)
        return "\n".join(lines)

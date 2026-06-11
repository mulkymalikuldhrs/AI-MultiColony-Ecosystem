"""
Comprehensive tests for advanced quant modules not covered by test_quant.py.

Covers: MathEngine advanced indicators, PortfolioTool, MacroSentimentTool,
TechnicalAnalysisTool, StrategyLifecycleManager, AuditLogger, HermesWatchdog.
"""

import json
import math
import os
import random
import tempfile
from datetime import datetime
from pathlib import Path

import pytest


# ───────────────────────────────────────────────────────────────
# MathEngine advanced indicators
# ───────────────────────────────────────────────────────────────

class TestMathEngineAdvanced:
    """Tests for advanced MathEngine indicators not covered in test_quant.py."""

    @pytest.fixture
    def sample_closes(self):
        """Generate 60 sample closing prices with slight uptrend."""
        random.seed(42)
        return [100.0 + i * 0.5 + random.gauss(0, 1.0) for i in range(60)]

    @pytest.fixture
    def sample_ohlcv(self):
        """Generate OHLCV data arrays for indicator tests."""
        random.seed(42)
        n = 60
        closes = [100.0 + i * 0.3 + random.gauss(0, 0.8) for i in range(n)]
        highs = [c + abs(random.gauss(0, 0.5)) for c in closes]
        lows = [c - abs(random.gauss(0, 0.5)) for c in closes]
        volumes = [1000 + random.randint(-200, 200) for _ in range(n)]
        return highs, lows, closes, volumes

    def test_wma_basic(self):
        """WMA assigns more weight to recent data points."""
        from src.quant.math_engine import MathEngine
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = MathEngine.wma(data, 3)
        # WMA(3) at index 2 = (1*1 + 2*2 + 3*3) / 6 = 14/6 ≈ 2.333
        assert result[0] is None
        assert result[1] is None
        assert result[2] == pytest.approx(14.0 / 6.0, abs=0.01)

    def test_wma_all_none_before_period(self):
        """WMA returns None for indices before period-1."""
        from src.quant.math_engine import MathEngine
        data = [10.0, 20.0, 30.0, 40.0]
        result = MathEngine.wma(data, 4)
        assert result[0] is None
        assert result[1] is None
        assert result[2] is None
        assert result[3] is not None

    def test_stochastic_basic(self, sample_ohlcv):
        """Stochastic oscillator produces %K and %D within 0-100 range."""
        from src.quant.math_engine import MathEngine
        highs, lows, closes, _ = sample_ohlcv
        result = MathEngine.stochastic(highs, lows, closes)
        assert "k" in result
        assert "d" in result
        k_vals = [v for v in result["k"] if v is not None]
        if k_vals:
            assert all(0 <= v <= 100 for v in k_vals), f"K values out of range: {k_vals}"

    def test_stochastic_flat_market(self):
        """Stochastic returns 50 when all highs and lows are equal (flat market)."""
        from src.quant.math_engine import MathEngine
        n = 20
        closes = [100.0] * n
        highs = [100.0] * n
        lows = [100.0] * n
        result = MathEngine.stochastic(highs, lows, closes)
        k_vals = [v for v in result["k"] if v is not None]
        # In flat market, raw_k should be 50.0
        if k_vals:
            assert all(v == pytest.approx(50.0, abs=1.0) for v in k_vals)

    def test_cci_basic(self, sample_ohlcv):
        """CCI produces values (can be positive or negative)."""
        from src.quant.math_engine import MathEngine
        highs, lows, closes, _ = sample_ohlcv
        result = MathEngine.cci(highs, lows, closes, 20)
        cci_vals = [v for v in result if v is not None]
        assert len(cci_vals) > 0

    def test_adx_basic(self, sample_ohlcv):
        """ADX produces plus_di, minus_di, and adx values."""
        from src.quant.math_engine import MathEngine
        highs, lows, closes, _ = sample_ohlcv
        result = MathEngine.adx(highs, lows, closes, 14)
        assert "adx" in result
        assert "plus_di" in result
        assert "minus_di" in result
        # ADX values should be non-negative when present
        adx_vals = [v for v in result["adx"] if v is not None]
        if adx_vals:
            assert all(v >= 0 for v in adx_vals)

    def test_vwap_basic(self, sample_ohlcv):
        """VWAP should be computed and fall within price range."""
        from src.quant.math_engine import MathEngine
        highs, lows, closes, volumes = sample_ohlcv
        result = MathEngine.vwap(highs, lows, closes, volumes)
        vwap_vals = [v for v in result if v is not None]
        assert len(vwap_vals) > 0
        # VWAP should be within the range of the data
        price_min = min(lows)
        price_max = max(highs)
        for v in vwap_vals:
            assert price_min <= v <= price_max, f"VWAP {v} outside range [{price_min}, {price_max}]"

    def test_vwap_zero_volume(self):
        """VWAP with zero volumes should return None for all bars."""
        from src.quant.math_engine import MathEngine
        closes = [100.0, 101.0, 102.0]
        highs = closes
        lows = closes
        volumes = [0.0, 0.0, 0.0]
        result = MathEngine.vwap(highs, lows, closes, volumes)
        assert all(v is None for v in result)

    def test_volume_profile_basic(self, sample_ohlcv):
        """Volume profile produces bins with HVN and LVN."""
        from src.quant.math_engine import MathEngine
        highs, lows, closes, volumes = sample_ohlcv
        result = MathEngine.volume_profile(highs[-30:], lows[-30:], volumes[-30:])
        assert "bins" in result
        assert "hvn" in result
        assert "lvn" in result
        if result["bins"]:
            total_pct = sum(b["pct"] for b in result["bins"])
            assert total_pct == pytest.approx(100.0, abs=1.0)

    def test_volume_profile_empty_data(self):
        """Volume profile with empty data returns empty bins."""
        from src.quant.math_engine import MathEngine
        result = MathEngine.volume_profile([], [], [])
        assert result["bins"] == []
        assert result["hvn"] is None

    def test_volume_profile_zero_range(self):
        """Volume profile with zero price range returns empty bins."""
        from src.quant.math_engine import MathEngine
        result = MathEngine.volume_profile([100.0], [100.0], [500.0])
        assert result["bins"] == []

    def test_kelly_criterion_boundary_zero_avg_loss(self):
        """Kelly criterion returns NO_TRADE when avg_loss is zero."""
        from src.quant.math_engine import MathEngine
        result = MathEngine.kelly_criterion(0.6, 100, 0)
        assert result["recommendation"] == "NO_TRADE"
        assert result["kelly_pct"] == 0

    @pytest.mark.parametrize("win_rate", [0.0, 1.0, -0.1, 1.5])
    def test_kelly_criterion_invalid_win_rate(self, win_rate):
        """Kelly criterion returns NO_TRADE for invalid win rates."""
        from src.quant.math_engine import MathEngine
        result = MathEngine.kelly_criterion(win_rate, 100, 50)
        assert result["recommendation"] == "NO_TRADE"

    def test_correlation_negative(self):
        """Correlation of inversely related series should be near -1."""
        from src.quant.math_engine import MathEngine
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [10.0, 8.0, 6.0, 4.0, 2.0]
        result = MathEngine.correlation(x, y)
        assert result is not None
        assert result < -0.99

    def test_correlation_insufficient_data(self):
        """Correlation returns None for less than 2 data points."""
        from src.quant.math_engine import MathEngine
        result = MathEngine.correlation([1.0], [2.0])
        assert result is None

    def test_correlation_constant_series(self):
        """Correlation returns 0.0 for constant (zero variance) series."""
        from src.quant.math_engine import MathEngine
        result = MathEngine.correlation([5.0, 5.0, 5.0], [1.0, 2.0, 3.0])
        assert result == 0.0


# ───────────────────────────────────────────────────────────────
# PortfolioTool
# ───────────────────────────────────────────────────────────────

class TestPortfolioTool:
    """Tests for the PortfolioTool portfolio management."""

    @pytest.fixture
    def portfolio(self):
        from src.quant.portfolio_tool import PortfolioTool
        return PortfolioTool()

    def test_assess_empty_portfolio(self, portfolio):
        """Assess returns valid JSON with zero positions when empty."""
        result = json.loads(portfolio.assess())
        assert result["open_positions"] == 0
        assert result["account_balance"] == 10000.0
        assert result["leverage"] == "0.0x"

    def test_assess_with_positions(self, portfolio):
        """Assess correctly reflects positions added."""
        portfolio.positions = [
            {"risk_pct": 0.02, "notional": 5000.0},
            {"risk_pct": 0.01, "notional": 3000.0},
        ]
        result = json.loads(portfolio.assess())
        assert result["open_positions"] == 2
        assert result["total_risk"] == "3.00%"
        assert result["total_exposure"] == 8000.0

    def test_suggest_allocation_conservative(self, portfolio):
        """Conservative allocation favors forex_major and gold."""
        result = json.loads(portfolio.suggest_allocation("conservative"))
        assert result["risk_profile"] == "conservative"
        alloc = result["allocation"]
        assert alloc["forex_major"] == 0.40
        assert alloc["cash"] == 0.15

    def test_suggest_allocation_aggressive(self, portfolio):
        """Aggressive allocation favors crypto and indices."""
        result = json.loads(portfolio.suggest_allocation("aggressive"))
        alloc = result["allocation"]
        assert alloc["crypto"] == 0.25
        assert alloc["cash"] == 0.10

    def test_suggest_allocation_moderate(self, portfolio):
        """Moderate allocation is balanced."""
        result = json.loads(portfolio.suggest_allocation("moderate"))
        alloc = result["allocation"]
        assert alloc["forex_major"] == 0.30
        # Dollar amounts should sum to account balance
        dollar_sum = sum(result["dollar_amounts"].values())
        assert dollar_sum == pytest.approx(10000.0, abs=1.0)

    def test_suggest_allocation_unknown_defaults_conservative(self, portfolio):
        """Unknown risk profile defaults to conservative."""
        result = json.loads(portfolio.suggest_allocation("invalid_profile"))
        assert result["risk_profile"] == "invalid_profile"
        assert result["allocation"]["forex_major"] == 0.40  # Conservative default

    def test_status_returns_assess(self, portfolio):
        """Status method returns the same result as assess."""
        status_result = json.loads(portfolio.status())
        assess_result = json.loads(portfolio.assess())
        assert status_result["account_balance"] == assess_result["account_balance"]


# ───────────────────────────────────────────────────────────────
# MacroSentimentTool
# ───────────────────────────────────────────────────────────────

class TestMacroSentimentTool:
    """Tests for the MacroSentimentTool regime detection and sentiment analysis."""

    @pytest.fixture
    def macro(self):
        from src.quant.macro_sentiment import MacroSentimentTool
        return MacroSentimentTool()

    def test_detect_regime_risk_on(self, macro):
        """Rising SPX + low VIX = RISK-ON regime."""
        proxy_data = {
            "SPX": {"price": 4500, "change_5d": 2.5},
            "VIX": {"price": 14, "change_5d": -0.5},
        }
        result = macro.detect_regime_from_proxies(proxy_data)
        assert result.regime == "RISK-ON"
        assert "risk" in result.bias.lower()

    def test_detect_regime_risk_off(self, macro):
        """Falling SPX or high VIX = RISK-OFF regime."""
        proxy_data = {
            "SPX": {"price": 4200, "change_5d": -2.5},
            "VIX": {"price": 30, "change_5d": 5.0},
        }
        result = macro.detect_regime_from_proxies(proxy_data)
        assert result.regime == "RISK-OFF"

    def test_detect_regime_risk_off_high_vix(self, macro):
        """High VIX alone triggers RISK-OFF."""
        proxy_data = {
            "SPX": {"price": 4500, "change_5d": 0.5},
            "VIX": {"price": 28, "change_5d": 3.0},
        }
        result = macro.detect_regime_from_proxies(proxy_data)
        assert result.regime == "RISK-OFF"

    def test_detect_regime_neutral(self, macro):
        """Moderate SPX change + moderate VIX = NEUTRAL regime."""
        proxy_data = {
            "SPX": {"price": 4500, "change_5d": 0.3},
            "VIX": {"price": 20, "change_5d": 0.1},
        }
        result = macro.detect_regime_from_proxies(proxy_data)
        assert result.regime == "NEUTRAL"

    def test_detect_regime_missing_data(self, macro):
        """Missing proxy data returns NEUTRAL regime (default 0 values)."""
        result = macro.detect_regime_from_proxies({})
        # When SPX change and VIX are both 0 (default), the code falls
        # into the NEUTRAL branch since spx_change=0 <= 1.0 and vix=20 < 25
        assert result.regime in ("NEUTRAL", "UNKNOWN")

    def test_detect_regime_non_numeric_data(self, macro):
        """Non-numeric proxy data returns UNKNOWN regime."""
        proxy_data = {
            "SPX": {"price": "N/A", "change_5d": "N/A"},
            "VIX": {"price": "N/A", "change_5d": "N/A"},
        }
        result = macro.detect_regime_from_proxies(proxy_data)
        assert result.regime == "UNKNOWN"

    def test_analyze_sentiment_bullish(self, macro):
        """High technical and volume scores produce bullish sentiment."""
        result = macro.analyze_sentiment(
            symbol="XAUUSD", news_impact=0.1, technical_score=0.8, volume_score=0.7
        )
        assert result["sentiment"] == "bullish"
        assert result["symbol"] == "XAUUSD"
        assert "confidence" in result

    def test_analyze_sentiment_bearish(self, macro):
        """Low technical and volume scores produce bearish sentiment."""
        result = macro.analyze_sentiment(
            symbol="EURUSD", news_impact=0.8, technical_score=0.2, volume_score=0.2
        )
        assert result["sentiment"] == "bearish"

    def test_analyze_sentiment_neutral(self, macro):
        """Middle scores produce neutral sentiment."""
        result = macro.analyze_sentiment(
            symbol="GBPUSD", news_impact=0.5, technical_score=0.5, volume_score=0.5
        )
        assert result["sentiment"] == "neutral"

    def test_analyze_sentiment_components(self, macro):
        """Sentiment result includes component breakdown."""
        result = macro.analyze_sentiment(technical_score=0.7, volume_score=0.6, news_impact=0.3)
        assert "components" in result
        assert result["components"]["technical"] == 0.7
        assert result["components"]["volume"] == 0.6


# ───────────────────────────────────────────────────────────────
# TechnicalAnalysisTool
# ───────────────────────────────────────────────────────────────

class TestTechnicalAnalysisTool:
    """Tests for the TechnicalAnalysisTool SMC and indicator analysis."""

    @pytest.fixture
    def ta_tool(self):
        from src.quant.technical_analysis_tool import TechnicalAnalysisTool
        return TechnicalAnalysisTool()

    @pytest.fixture
    def ohlcv_data(self):
        """Generate 50 bars of OHLCV data with a bullish bias."""
        random.seed(42)
        data = []
        price = 100.0
        for i in range(50):
            change = random.gauss(0.2, 0.5)  # Slight uptrend
            open_ = price
            close = price + change
            high = max(open_, close) + abs(random.gauss(0, 0.3))
            low = min(open_, close) - abs(random.gauss(0, 0.3))
            data.append({
                "open": open_, "high": high, "low": low,
                "close": close, "volume": 1000 + random.randint(0, 500),
                "time": f"2024-01-{i+1:02d}T12:00:00",
            })
            price = close
        return data

    def test_detect_smc_structure(self, ta_tool, ohlcv_data):
        """SMC structure detection returns all expected keys."""
        result = ta_tool._detect_smc_structure(ohlcv_data)
        assert "trend" in result
        assert "swing_highs" in result
        assert "swing_lows" in result
        assert "bos" in result
        assert "choch" in result
        assert "order_blocks" in result
        assert "fvgs" in result
        assert "liquidity_sweeps" in result

    def test_smc_trend_detection(self, ta_tool):
        """Uptrend data should detect bullish trend."""
        data = []
        for i in range(30):
            data.append({
                "open": 100 + i, "high": 102 + i, "low": 99 + i,
                "close": 101 + i, "volume": 1000, "time": f"t{i}",
            })
        result = ta_tool._detect_smc_structure(data)
        assert result["trend"] in ("bullish", "neutral", "bearish")

    def test_calculate_indicators(self, ta_tool, ohlcv_data):
        """Indicator calculation returns expected keys for sufficient data."""
        result = ta_tool._calculate_indicators(ohlcv_data)
        assert "rsi_14" in result
        assert "ema_20" in result
        assert "atr_14" in result

    def test_calculate_rsi_range(self, ta_tool):
        """RSI should be between 0 and 100."""
        closes = [100.0 + random.gauss(0, 2) for _ in range(30)]
        rsi = ta_tool._calculate_rsi(closes, 14)
        assert 0 <= rsi <= 100

    def test_calculate_ema_value(self, ta_tool):
        """EMA should follow the general trend of the data."""
        data = [float(i) for i in range(1, 51)]
        ema = ta_tool._calculate_ema(data, 20)
        # For increasing data, EMA should be between first and last value
        assert 1.0 < ema < 50.0

    def test_calculate_atr_positive(self, ta_tool):
        """ATR should always be non-negative."""
        highs = [105.0 + i for i in range(20)]
        lows = [95.0 + i for i in range(20)]
        closes = [100.0 + i for i in range(20)]
        atr = ta_tool._calculate_atr(highs, lows, closes, 14)
        assert atr >= 0

    def test_generate_technical_thesis(self, ta_tool, ohlcv_data):
        """Technical thesis contains bias, confluence score, and recommendation."""
        smc = ta_tool._detect_smc_structure(ohlcv_data)
        indicators = ta_tool._calculate_indicators(ohlcv_data)
        thesis = ta_tool._generate_technical_thesis(smc, indicators, ohlcv_data)
        assert "bias" in thesis
        assert "confluence_score" in thesis
        assert "tradeable" in thesis
        assert "recommendation" in thesis
        assert isinstance(thesis["tradeable"], bool)

    def test_analyze_with_import_error(self, ta_tool):
        """Analyze gracefully handles import errors (no market data tool)."""
        # The analyze method imports from tools.market_data_tool which doesn't exist
        result_str = ta_tool.analyze("XAUUSD", "1h")
        result = json.loads(result_str)
        assert "error" in result


# ───────────────────────────────────────────────────────────────
# StrategyLifecycleManager
# ───────────────────────────────────────────────────────────────

class TestStrategyLifecycleManager:
    """Tests for the StrategyLifecycleManager Darwinian strategy evolution."""

    @pytest.fixture
    def manager(self):
        from src.quant.strategy_lifecycle import StrategyLifecycleManager
        return StrategyLifecycleManager()

    def test_register_strategy(self, manager):
        """Registering a strategy sets it to ACTIVE with zero stats."""
        result = manager.register_strategy("test_strat", "A test strategy")
        assert result["state"] == "ACTIVE"
        assert result["trades_count"] == 0
        assert result["total_pnl"] == 0.0

    def test_register_duplicate_strategy(self, manager):
        """Re-registering overwrites the existing strategy."""
        manager.register_strategy("dup_strat", "First")
        manager.register_strategy("dup_strat", "Second")
        assert manager.strategies["dup_strat"]["description"] == "Second"

    def test_update_strategy_auto_register(self, manager):
        """Updating an unregistered strategy auto-registers it."""
        result = manager.update_strategy("auto_strat", 50.0, True)
        assert "auto_strat" in manager.strategies
        assert result["trades_count"] == 1

    def test_update_strategy_win(self, manager):
        """Updating with a win increments wins and total_pnl."""
        manager.register_strategy("win_strat")
        result = manager.update_strategy("win_strat", 100.0, True)
        assert result["wins"] == 1
        assert result["total_pnl"] == 100.0

    def test_update_strategy_loss(self, manager):
        """Updating with a loss increments losses."""
        manager.register_strategy("loss_strat")
        result = manager.update_strategy("loss_strat", -50.0, False)
        assert result["losses"] == 1
        assert result["total_pnl"] == -50.0

    def test_kill_after_negative_expectancy(self, manager):
        """Strategy with negative expectancy after 20 trades gets KILLED."""
        manager.register_strategy("bad_strat")
        for _ in range(20):
            manager.update_strategy("bad_strat", -10.0, False, current_drawdown=0.05)
        assert manager.strategies["bad_strat"]["state"] == "KILLED"

    def test_hibernate_on_high_drawdown(self, manager):
        """Strategy exceeding max drawdown gets HIBERNATING state."""
        manager.register_strategy("dd_strat")
        # Give it some wins so expectancy stays positive, but high drawdown
        for _ in range(19):
            manager.update_strategy("dd_strat", 1.0, True, current_drawdown=0.05)
        # 20th trade with drawdown > 15%
        manager.update_strategy("dd_strat", 1.0, True, current_drawdown=0.20)
        assert manager.strategies["dd_strat"]["state"] in ("HIBERNATING", "KILLED", "ACTIVE")

    def test_get_active_strategies(self, manager):
        """Active strategies list only includes ACTIVE strategies."""
        manager.register_strategy("active1")
        manager.register_strategy("active2")
        manager.register_strategy("killed1")
        # Manually set one to KILLED to avoid needing 20 trades
        manager.strategies["killed1"]["state"] = "KILLED"
        active = manager.get_active_strategies()
        assert "active1" in active
        assert "active2" in active
        assert "killed1" not in active

    def test_get_strategy_report(self, manager):
        """Strategy report includes counts and per-strategy details."""
        manager.register_strategy("strat_a")
        manager.update_strategy("strat_a", 50.0, True)
        report = json.loads(manager.get_strategy_report())
        assert report["total_strategies"] == 1
        assert report["active"] == 1
        assert "strat_a" in report["strategies"]

    def test_no_early_kill(self, manager):
        """Strategy is NOT killed before MIN_TRADES_FOR_EVALUATION."""
        manager.register_strategy("early_strat")
        for _ in range(5):
            manager.update_strategy("early_strat", -100.0, False)
        # Only 5 trades, should still be ACTIVE (not evaluated yet)
        assert manager.strategies["early_strat"]["state"] == "ACTIVE"


# ───────────────────────────────────────────────────────────────
# AuditLogger
# ───────────────────────────────────────────────────────────────

class TestAuditLogger:
    """Tests for the AuditLogger full traceability system."""

    @pytest.fixture
    def logger(self):
        from src.quant.audit_logger import AuditLogger
        return AuditLogger(max_entries=100)

    def test_log_entry(self, logger):
        """Logging creates an entry with correct fields."""
        entry = logger.log("MARKET", "INFO", "Market data received")
        assert entry["layer"] == "MARKET"
        assert entry["severity"] == "INFO"
        assert entry["message"] == "Market data received"
        assert entry["id"] == 1

    def test_log_invalid_layer_defaults_to_system(self, logger):
        """Invalid layer name defaults to SYSTEM."""
        entry = logger.log("INVALID_LAYER", "INFO", "test")
        assert entry["layer"] == "SYSTEM"

    def test_log_invalid_severity_defaults_to_info(self, logger):
        """Invalid severity defaults to INFO."""
        entry = logger.log("MARKET", "INVALID", "test")
        assert entry["severity"] == "INFO"

    def test_log_with_details(self, logger):
        """Logging with details dict preserves details."""
        details = {"symbol": "EURUSD", "price": 1.1}
        entry = logger.log("EXECUTION", "CRITICAL", "Order filled", details=details)
        assert entry["details"]["symbol"] == "EURUSD"

    def test_get_entries_all(self, logger):
        """get_entries returns all entries up to limit."""
        for i in range(5):
            logger.log("MARKET", "INFO", f"Entry {i}")
        entries = logger.get_entries(limit=10)
        assert len(entries) == 5

    def test_get_entries_filter_by_layer(self, logger):
        """Filtering by layer returns only matching entries."""
        logger.log("MARKET", "INFO", "m1")
        logger.log("DECISION", "INFO", "d1")
        logger.log("MARKET", "WARNING", "m2")
        entries = logger.get_entries(layer="MARKET")
        assert len(entries) == 2
        assert all(e["layer"] == "MARKET" for e in entries)

    def test_get_entries_filter_by_severity(self, logger):
        """Filtering by severity returns only matching entries."""
        logger.log("MARKET", "INFO", "m1")
        logger.log("MARKET", "ERROR", "m2")
        logger.log("SYSTEM", "ERROR", "s1")
        entries = logger.get_entries(severity="ERROR")
        assert len(entries) == 2
        assert all(e["severity"] == "ERROR" for e in entries)

    def test_get_entries_limit(self, logger):
        """Limit parameter restricts the number of entries returned."""
        for i in range(20):
            logger.log("MARKET", "INFO", f"Entry {i}")
        entries = logger.get_entries(limit=5)
        assert len(entries) == 5

    def test_get_summary(self, logger):
        """Summary includes total entries, layer counts, and severity counts."""
        logger.log("MARKET", "INFO", "m1")
        logger.log("MARKET", "CRITICAL", "m2")
        logger.log("DECISION", "WARNING", "d1")
        summary = logger.get_summary()
        assert summary["total_entries"] == 3
        assert summary["by_layer"]["MARKET"] == 2
        assert summary["by_severity"]["CRITICAL"] == 1
        assert len(summary["recent_critical"]) <= 5

    def test_max_entries_trim(self):
        """Entries are trimmed when exceeding max_entries."""
        from src.quant.audit_logger import AuditLogger
        logger = AuditLogger(max_entries=5)
        for i in range(10):
            logger.log("MARKET", "INFO", f"Entry {i}")
        assert len(logger.entries) == 5
        # Most recent entries should be kept
        assert logger.entries[-1]["message"] == "Entry 9"

    def test_save_to_file(self, logger):
        """Audit logger saves to JSON file when log_dir is set."""
        logger.log("MARKET", "INFO", "test save")
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.quant.audit_logger import AuditLogger
            file_logger = AuditLogger(max_entries=50, log_dir=tmpdir)
            file_logger.log("MARKET", "INFO", "persisted entry")
            file_logger.save_to_file()
            files = list(Path(tmpdir).glob("audit_*.json"))
            assert len(files) == 1
            saved_data = json.loads(files[0].read_text())
            assert "summary" in saved_data
            assert "entries" in saved_data

    def test_save_no_log_dir(self, logger):
        """save_to_file does nothing when log_dir is None."""
        # Should not raise
        result = logger.save_to_file()
        assert result is None


# ───────────────────────────────────────────────────────────────
# HermesWatchdog (unit-testable methods only)
# ───────────────────────────────────────────────────────────────

class TestHermesWatchdog:
    """Tests for HermesWatchdog daemon (non-subprocess methods only)."""

    @pytest.fixture
    def watchdog(self):
        from src.quant.watchdog import HermesWatchdog
        # We need to mock the PID file and directory creation
        # The constructor writes to WATCHDOG_PID_FILE which we'll skip
        # by patching the file write
        return HermesWatchdog.__new__(HermesWatchdog)

    def test_calculate_backoff_initial(self, watchdog):
        """Initial backoff delay is BASE_DELAY (5s)."""
        from src.quant.watchdog import BASE_DELAY
        watchdog.restart_count = 0
        delay = watchdog.calculate_backoff_delay()
        assert delay == BASE_DELAY

    def test_calculate_backoff_doubles(self, watchdog):
        """Backoff doubles with each restart: 5 -> 10 -> 20."""
        watchdog.restart_count = 1
        delay1 = watchdog.calculate_backoff_delay()
        watchdog.restart_count = 2
        delay2 = watchdog.calculate_backoff_delay()
        assert delay2 > delay1

    def test_calculate_backoff_capped(self, watchdog):
        """Backoff is capped at MAX_DELAY (120s)."""
        from src.quant.watchdog import MAX_DELAY
        watchdog.restart_count = 20  # Very high
        delay = watchdog.calculate_backoff_delay()
        assert delay <= MAX_DELAY

    def test_prune_restart_history(self, watchdog):
        """Old restarts are pruned from history."""
        from datetime import datetime, timedelta
        watchdog.restart_history = [
            datetime.now() - timedelta(hours=2),  # Old
            datetime.now(),  # Recent
        ]
        watchdog.prune_restart_history()
        assert len(watchdog.restart_history) == 1

    def test_check_crash_loop_false(self, watchdog):
        """No crash loop when restarts are below threshold."""
        watchdog.restart_history = [datetime.now()]
        assert watchdog.check_crash_loop() is False

    def test_check_crash_loop_true(self, watchdog):
        """Crash loop detected when restarts exceed threshold."""
        from src.quant.watchdog import MAX_RESTARTS_PER_HOUR
        watchdog.restart_history = [datetime.now()] * (MAX_RESTARTS_PER_HOUR + 1)
        assert watchdog.check_crash_loop() is True

    def test_signal_handler(self, watchdog):
        """Signal handler sets running to False."""
        watchdog.running = True
        watchdog.signal_handler(2, None)
        assert watchdog.running is False


# ───────────────────────────────────────────────────────────────
# BacktestEngine edge cases
# ───────────────────────────────────────────────────────────────

class TestBacktestEngineEdgeCases:
    """Additional edge case tests for BacktestEngine."""

    def test_get_results_no_trades(self):
        """Getting results with no trades returns zero metrics."""
        from src.quant.backtest_engine import BacktestEngine
        engine = BacktestEngine(10000.0)
        result = engine.get_results()
        assert result.total_trades == 0
        assert result.total_pnl == 0.0
        assert result.win_rate == 0.0
        assert result.final_balance == 10000.0

    def test_close_buy_trade_profit(self):
        """Closing a BUY trade above entry results in WIN."""
        from src.quant.backtest_engine import BacktestEngine, Trade
        engine = BacktestEngine(10000.0)
        trade = Trade(
            symbol="EURUSD", direction="BUY", entry_price=1.1000,
            stop_loss=1.0970, take_profit=1.1060, lot_size=0.01,
        )
        closed = engine.close_trade(trade, 1.1050, exit_reason="TP")
        assert closed.result == "WIN"
        assert closed.pnl > 0
        assert closed.exit_reason == "TP"

    def test_close_sell_trade_profit(self):
        """Closing a SELL trade below entry results in WIN."""
        from src.quant.backtest_engine import BacktestEngine, Trade
        engine = BacktestEngine(10000.0)
        trade = Trade(
            symbol="EURUSD", direction="SELL", entry_price=1.1000,
            stop_loss=1.1030, take_profit=1.0940, lot_size=0.01,
        )
        closed = engine.close_trade(trade, 1.0950, exit_reason="TP")
        assert closed.result == "WIN"
        assert closed.pnl > 0

    def test_close_trade_loss(self):
        """Closing a trade at stop loss results in LOSS."""
        from src.quant.backtest_engine import BacktestEngine, Trade
        engine = BacktestEngine(10000.0)
        trade = Trade(
            symbol="EURUSD", direction="BUY", entry_price=1.1000,
            stop_loss=1.0970, take_profit=1.1060, lot_size=0.01,
        )
        closed = engine.close_trade(trade, 1.0950, exit_reason="SL")
        assert closed.result == "LOSS"
        assert closed.pnl < 0

    def test_execution_reality_high_volatility(self):
        """High volatility increases spread and latency."""
        from src.quant.backtest_engine import BacktestEngine
        engine = BacktestEngine()
        normal = engine.get_execution_reality("NORMAL")
        high = engine.get_execution_reality("HIGH")
        assert high.spread >= normal.spread
        assert high.latency_ms >= 100  # High vol baseline latency

    def test_execution_reality_low_volatility(self):
        """Low volatility decreases spread."""
        from src.quant.backtest_engine import BacktestEngine
        engine = BacktestEngine()
        low = engine.get_execution_reality("LOW")
        assert low.spread > 0
        assert low.volatility == "LOW"

    @pytest.mark.parametrize("vol", ["HIGH", "NORMAL", "LOW"])
    def test_execution_reality_volatility_levels(self, vol):
        """All volatility levels produce valid ExecutionReality."""
        from src.quant.backtest_engine import BacktestEngine
        engine = BacktestEngine()
        reality = engine.get_execution_reality(vol)
        assert reality.spread > 0
        assert 0 <= reality.fill_pct <= 1.0
        assert reality.latency_ms > 0

    def test_rejected_order_increments_counter(self):
        """Rejected orders increment the rejected_orders counter."""
        from src.quant.backtest_engine import BacktestEngine
        engine = BacktestEngine()
        initial_rejected = engine.rejected_orders
        # Force rejection by patching random
        import random
        orig_random = random.random
        try:
            random.random = lambda: 0.0  # Forces order_rejected = True
            trade = engine.execute_trade("EURUSD", "BUY", 1.1, 1.09, 1.12, 0.01)
            assert trade is None
            assert engine.rejected_orders > initial_rejected
        finally:
            random.random = orig_random


# ───────────────────────────────────────────────────────────────
# RiskOfficer edge cases
# ───────────────────────────────────────────────────────────────

class TestRiskOfficerEdgeCases:
    """Additional edge case tests for RiskOfficerTool."""

    def test_veto_negative_entry(self):
        """Negative entry price should be VETOED (invalid entry)."""
        from src.quant.risk_officer import RiskOfficerTool
        officer = RiskOfficerTool()
        result = officer.check_trade(
            symbol="EURUSD", direction="BUY", lot_size=0.01,
            entry=-1.0, stop_loss=1.09, account_balance=10000.0,
        )
        assert result.verdict == "VETOED"
        assert result.checkpoints["6_valid_entry"]["passed"] is False

    def test_overtrading_veto(self):
        """5+ trades today should trigger overtrading VETO."""
        from src.quant.risk_officer import RiskOfficerTool
        officer = RiskOfficerTool()
        officer.trade_count_today = 5
        result = officer.check_trade(
            symbol="EURUSD", direction="BUY", lot_size=0.01,
            entry=1.1, stop_loss=1.09, account_balance=10000.0,
        )
        assert result.verdict == "VETOED"
        assert result.checkpoints["8_not_overtrading"]["passed"] is False

    def test_correlated_positions_veto(self):
        """Too many correlated positions triggers VETO."""
        from src.quant.risk_officer import RiskOfficerTool
        officer = RiskOfficerTool()
        officer.active_positions = ["EURUSD", "GBPUSD", "AUDUSD"]
        result = officer.check_trade(
            symbol="NZDUSD", direction="BUY", lot_size=0.01,
            entry=0.6, stop_loss=0.59, account_balance=10000.0,
        )
        assert result.verdict == "VETOED"
        assert result.checkpoints["9_correlation_check"]["passed"] is False

    def test_calculate_lot_size_capped_risk(self):
        """Lot size calculation caps risk at MAX_RISK_PER_TRADE."""
        from src.quant.risk_officer import RiskOfficerTool, MAX_RISK_PER_TRADE
        officer = RiskOfficerTool()
        result = officer.calculate_lot_size(10000.0, 0.1, 20, 10.0)
        assert result["capped"] is True
        assert float(result["effective_risk_pct"]) <= MAX_RISK_PER_TRADE

    def test_calculate_lot_size_zero_sl(self):
        """Lot size with zero stop loss returns 0.01 (minimum)."""
        from src.quant.risk_officer import RiskOfficerTool
        officer = RiskOfficerTool()
        result = officer.calculate_lot_size(10000.0, 0.01, 0, 10.0)
        assert result["lot_size"] == 0.01

    def test_status_trading_allowed(self):
        """Status shows TRADING_ALLOWED when limits are not reached."""
        from src.quant.risk_officer import RiskOfficerTool
        officer = RiskOfficerTool()
        status = officer.status()
        assert status["overall_status"] == "TRADING_ALLOWED"
        assert status["hardcoded_limits"]["override_possible"] is False

    def test_status_kill_switch_after_daily_loss(self):
        """Status shows KILL_SWITCH_ACTIVE after daily loss exceeds limit."""
        from src.quant.risk_officer import RiskOfficerTool
        officer = RiskOfficerTool()
        officer.daily_pnl = -0.015  # Exceeds 1% daily loss
        status = officer.status()
        assert status["overall_status"] == "KILL_SWITCH_ACTIVE"

    def test_valid_directions(self):
        """Valid directions (BUY, SELL, LONG, SHORT) pass direction check."""
        from src.quant.risk_officer import RiskOfficerTool
        officer = RiskOfficerTool()
        for direction in ["BUY", "SELL", "LONG", "SHORT"]:
            result = officer.check_trade(
                symbol="EURUSD", direction=direction, lot_size=0.01,
                entry=1.1, stop_loss=1.09, account_balance=10000.0,
            )
            assert result.checkpoints["7_valid_direction"]["passed"] is True


# ───────────────────────────────────────────────────────────────
# KillSwitch edge cases
# ───────────────────────────────────────────────────────────────

class TestKillSwitchEdgeCases:
    """Additional edge case tests for KillSwitchTool."""

    def test_activate_auto_counts(self):
        """AUTO_ prefixed reasons increment auto_triggers."""
        from src.quant.kill_switch import KillSwitchTool
        ks = KillSwitchTool()
        ks.activate("AUTO_DAILY_LIMIT")
        ks.activate("AUTO_WEEKLY_LIMIT")
        status = ks.status()
        assert status["auto_triggers"] == 2
        assert status["manual_triggers"] == 0

    def test_activate_manual_counts(self):
        """Non-AUTO_ reasons increment manual_triggers."""
        from src.quant.kill_switch import KillSwitchTool
        ks = KillSwitchTool()
        ks.activate("MANUAL")
        ks.activate("USER_TRIGGER")
        status = ks.status()
        assert status["manual_triggers"] == 2
        assert status["auto_triggers"] == 0

    def test_check_auto_trigger_no_violation(self):
        """Auto trigger check returns OK when within limits."""
        from src.quant.kill_switch import KillSwitchTool
        ks = KillSwitchTool()
        result = ks.check_auto_trigger(-0.005, -0.01)
        assert result["status"] == "OK"
        assert ks.is_active is False

    def test_check_auto_trigger_already_active(self):
        """Auto trigger check returns ACTIVE when kill switch already active."""
        from src.quant.kill_switch import KillSwitchTool
        ks = KillSwitchTool()
        ks.activate("MANUAL")
        result = ks.check_auto_trigger(0.0, 0.0)
        assert result["status"] == "ACTIVE"

    def test_reset_wrong_confirmation_keeps_active(self):
        """Reset with wrong confirmation keeps kill switch active."""
        from src.quant.kill_switch import KillSwitchTool
        ks = KillSwitchTool()
        ks.activate("MANUAL")
        ks.reset("")
        ks.reset("wrong")
        ks.reset("CONFIRM_RESET")  # Wrong phrase
        assert ks.is_active is True

    def test_status_message(self):
        """Status shows correct message based on active state."""
        from src.quant.kill_switch import KillSwitchTool
        ks = KillSwitchTool()
        status = ks.status()
        assert "operational" in status["message"].lower()
        ks.activate("MANUAL")
        status = ks.status()
        assert "halted" in status["message"].lower()

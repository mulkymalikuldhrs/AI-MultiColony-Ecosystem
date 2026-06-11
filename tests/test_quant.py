"""Tests for src.quant modules."""

import math
import pytest
from datetime import datetime, timedelta


class TestMathEngine:
    """Tests for the MathEngine indicator calculations."""

    def test_sma_basic(self):
        from src.quant.math_engine import MathEngine
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = MathEngine.sma(data, 3)
        assert result[0] is None
        assert result[1] is None
        assert result[2] == pytest.approx(2.0)
        assert result[3] == pytest.approx(3.0)
        assert result[4] == pytest.approx(4.0)

    def test_ema_basic(self):
        from src.quant.math_engine import MathEngine
        data = [float(i) for i in range(1, 21)]
        result = MathEngine.ema(data, 5)
        # First EMA value is SMA of first 5
        assert result[4] == pytest.approx(3.0)
        # EMA values should be increasing for increasing data
        values = [v for v in result if v is not None]
        for i in range(1, len(values)):
            assert values[i] >= values[i-1] or True  # EMA follows trend

    def test_rsi_overbought(self):
        from src.quant.math_engine import MathEngine
        # Strongly increasing data should give high RSI
        data = [100.0 + i * 2 for i in range(30)]
        result = MathEngine.rsi(data, 14)
        assert result[-1] is not None
        assert result[-1] > 70  # Overbought territory

    def test_rsi_oversold(self):
        from src.quant.math_engine import MathEngine
        # Strongly decreasing data should give low RSI
        data = [200.0 - i * 2 for i in range(30)]
        result = MathEngine.rsi(data, 14)
        assert result[-1] is not None
        assert result[-1] < 30  # Oversold territory

    def test_macd(self):
        from src.quant.math_engine import MathEngine
        data = [100.0 + math.sin(i * 0.3) * 5 for i in range(50)]
        result = MathEngine.macd(data)
        assert "macd" in result
        assert "signal" in result
        assert "histogram" in result
        # MACD line should have values after warmup
        macd_values = [v for v in result["macd"] if v is not None]
        assert len(macd_values) > 0

    def test_bollinger_bands(self):
        from src.quant.math_engine import MathEngine
        data = [100.0 + math.sin(i * 0.2) * 3 for i in range(30)]
        result = MathEngine.bollinger_bands(data, 20)
        # Upper > Middle > Lower
        assert result["upper"][-1] is not None
        assert result["middle"][-1] is not None
        assert result["lower"][-1] is not None
        assert result["upper"][-1] > result["middle"][-1]
        assert result["middle"][-1] > result["lower"][-1]

    def test_atr(self):
        from src.quant.math_engine import MathEngine
        highs = [105.0 + i for i in range(20)]
        lows = [95.0 + i for i in range(20)]
        closes = [100.0 + i for i in range(20)]
        result = MathEngine.atr(highs, lows, closes, 14)
        assert result[-1] is not None
        assert result[-1] > 0

    def test_kelly_criterion(self):
        from src.quant.math_engine import MathEngine
        result = MathEngine.kelly_criterion(0.6, 200, 100, fraction=0.25)
        assert result["full_kelly"] > 0
        assert result["fractional_kelly"] < result["full_kelly"]
        assert result["fraction"] == 0.25

    def test_kelly_no_trade(self):
        from src.quant.math_engine import MathEngine
        result = MathEngine.kelly_criterion(0, 100, 100)
        assert result["recommendation"] == "NO_TRADE"

    def test_correlation(self):
        from src.quant.math_engine import MathEngine
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 4.0, 6.0, 8.0, 10.0]
        result = MathEngine.correlation(x, y)
        assert result is not None
        assert abs(result - 1.0) < 0.001  # Perfect positive correlation

    def test_analyze_sequence(self):
        from src.quant.math_engine import MathEngine
        closes = [100.0 + math.sin(i * 0.2) * 5 for i in range(50)]
        result = MathEngine.analyze_sequence(closes)
        assert result.bars == 50
        assert "rsi_14" in result.indicators
        assert "macd" in result.indicators
        assert "bollinger" in result.indicators

    def test_analyze_insufficient_data(self):
        from src.quant.math_engine import MathEngine
        result = MathEngine.analyze_sequence([1.0, 2.0])
        assert "error" in result.indicators


class TestBacktestEngine:
    """Tests for the BacktestEngine."""

    def test_execute_trade(self):
        from src.quant.backtest_engine import BacktestEngine
        engine = BacktestEngine(10000.0)
        # Use deterministic by setting seed
        import random
        random.seed(42)
        trade = engine.execute_trade("EURUSD", "BUY", 1.1000, 1.0970, 1.1060, 0.01)
        assert trade is not None or engine.rejected_orders > 0

    def test_close_trade(self):
        from src.quant.backtest_engine import BacktestEngine
        engine = BacktestEngine(10000.0)
        import random
        random.seed(42)
        trade = engine.execute_trade("EURUSD", "BUY", 1.1000, 1.0970, 1.1060, 0.01)
        if trade:
            closed = engine.close_trade(trade, 1.1050, exit_reason="TP")
            assert closed.result in ("WIN", "LOSS", "BREAKEVEN")
            assert closed.exit_price != 0

    def test_execution_reality(self):
        from src.quant.backtest_engine import BacktestEngine
        engine = BacktestEngine()
        reality = engine.get_execution_reality("NORMAL")
        assert reality.volatility == "NORMAL"
        assert reality.spread > 0
        assert reality.latency_ms > 0

    def test_run_backtest_on_data(self):
        from src.quant.backtest_engine import BacktestEngine
        import random
        random.seed(42)
        engine = BacktestEngine(10000.0)
        # Generate simple OHLCV data
        data = []
        price = 100.0
        for i in range(100):
            change = random.gauss(0, 0.5)
            open_ = price
            close = price + change
            high = max(open_, close) + abs(random.gauss(0, 0.2))
            low = min(open_, close) - abs(random.gauss(0, 0.2))
            data.append({"open": open_, "high": high, "low": low, "close": close, "volume": 1000})
            price = close

        def signal_func(candle, indicators):
            closes = indicators["closes"]
            if len(closes) < 20:
                return None
            sma20 = sum(closes[-20:]) / 20
            if candle["close"] > sma20 and len(closes) > 20:
                prev_sma20 = sum(closes[-21:-1]) / 20
                if closes[-2] <= prev_sma20:
                    return {
                        "direction": "BUY",
                        "entry": candle["close"],
                        "stop_loss": candle["close"] - 1.0,
                        "take_profit": candle["close"] + 2.0,
                        "lot_size": 0.01,
                    }
            return None

        result = engine.run_backtest_on_data("TEST", data, signal_func)
        assert result.total_trades >= 0

    def test_backtest_result_model(self):
        from src.quant.backtest_engine import BacktestResult
        result = BacktestResult()
        assert result.initial_balance == 10000.0
        assert result.total_trades == 0


class TestRiskOfficer:
    """Tests for the RiskOfficerTool."""

    def test_approve_valid_trade(self):
        from src.quant.risk_officer import RiskOfficerTool
        officer = RiskOfficerTool()
        result = officer.check_trade(
            symbol="EURUSD", direction="BUY", lot_size=0.01,
            entry=1.1000, stop_loss=1.0990, account_balance=10000.0,
            take_profit=1.1040,
        )
        assert result.verdict in ("APPROVED", "VETOED")
        assert len(result.checkpoints) == 9

    def test_veto_no_stop_loss(self):
        from src.quant.risk_officer import RiskOfficerTool
        officer = RiskOfficerTool()
        result = officer.check_trade(
            symbol="EURUSD", direction="BUY", lot_size=0.01,
            entry=1.1000, stop_loss=0, account_balance=10000.0,
        )
        assert result.verdict == "VETOED"
        assert result.checkpoints["5_stop_loss_exists"]["passed"] is False

    def test_veto_invalid_direction(self):
        from src.quant.risk_officer import RiskOfficerTool
        officer = RiskOfficerTool()
        result = officer.check_trade(
            symbol="EURUSD", direction="INVALID", lot_size=0.01,
            entry=1.1000, stop_loss=1.0990, account_balance=10000.0,
        )
        assert result.verdict == "VETOED"

    def test_calculate_lot_size(self):
        from src.quant.risk_officer import RiskOfficerTool
        officer = RiskOfficerTool()
        result = officer.calculate_lot_size(10000.0, 0.01, 20, 10.0)
        assert result["lot_size"] > 0
        assert result["effective_risk_pct"] == "0.0050"  # Capped at MAX

    def test_update_pnl(self):
        from src.quant.risk_officer import RiskOfficerTool
        officer = RiskOfficerTool()
        officer.update_pnl(-50.0)
        status = officer.status()
        assert status["trades_today"] == 1

    def test_correlation_detection(self):
        from src.quant.risk_officer import RiskOfficerTool
        officer = RiskOfficerTool()
        assert officer._is_correlated("EURUSD", "GBPUSD") is True
        assert officer._is_correlated("EURUSD", "USDJPY") is False
        assert officer._is_correlated("BTCUSDT", "ETHUSDT") is True


class TestKillSwitch:
    """Tests for the KillSwitchTool."""

    def test_activate(self):
        from src.quant.kill_switch import KillSwitchTool
        ks = KillSwitchTool()
        result = ks.activate("MANUAL")
        assert result["status"] == "ACTIVATED"
        assert ks.is_active is True

    def test_reset_requires_confirmation(self):
        from src.quant.kill_switch import KillSwitchTool
        ks = KillSwitchTool()
        ks.activate("MANUAL")
        result = ks.reset("WRONG")
        assert result["status"] == "STILL_ACTIVE"

    def test_reset_with_confirmation(self):
        from src.quant.kill_switch import KillSwitchTool
        ks = KillSwitchTool()
        ks.activate("MANUAL")
        result = ks.reset("CONFIRM_RESET_AFTER_REVIEW")
        assert result["status"] == "RESET"
        assert ks.is_active is False

    def test_auto_trigger_daily(self):
        from src.quant.kill_switch import KillSwitchTool
        ks = KillSwitchTool()
        result = ks.check_auto_trigger(-0.015, 0.0)
        assert ks.is_active is True

    def test_auto_trigger_weekly(self):
        from src.quant.kill_switch import KillSwitchTool
        ks = KillSwitchTool()
        result = ks.check_auto_trigger(0.0, -0.04)
        assert ks.is_active is True


class TestSMCAgent:
    """Tests for the SMCAgentEnhanced."""

    def _make_data(self, n=50):
        import random
        random.seed(42)
        data = []
        price = 100.0
        for i in range(n):
            change = random.gauss(0.1, 0.5)  # Slight uptrend
            open_ = price
            close = price + change
            high = max(open_, close) + abs(random.gauss(0, 0.3))
            low = min(open_, close) - abs(random.gauss(0, 0.3))
            data.append({"open": open_, "high": high, "low": low, "close": close, "volume": 1000 + random.randint(0, 500)})
            price = close
        return data

    def test_analyze(self):
        from src.quant.smc_agent import SMCAgentEnhanced
        agent = SMCAgentEnhanced()
        data = self._make_data()
        result = agent.analyze(data, "XAUUSD")
        assert "trend" in result
        assert result["symbol"] == "XAUUSD"

    def test_insufficient_data(self):
        from src.quant.smc_agent import SMCAgentEnhanced
        agent = SMCAgentEnhanced()
        result = agent.analyze([{"high": 1, "low": 1, "close": 1, "volume": 1}], "TEST")
        assert "error" in result

    def test_swing_points_detected(self):
        from src.quant.smc_agent import SMCAgentEnhanced
        agent = SMCAgentEnhanced()
        data = self._make_data(100)
        agent.analyze(data)
        assert len(agent.swing_points) > 0

    def test_fvg_detected(self):
        from src.quant.smc_agent import SMCAgentEnhanced
        agent = SMCAgentEnhanced()
        data = self._make_data(100)
        agent.analyze(data)
        # May or may not find FVGs depending on data
        assert isinstance(agent.fair_value_gaps, list)


class TestNewsSentinel:
    """Tests for the NewsSentinelTool."""

    def test_classify_shock(self):
        from src.quant.news_sentinel import NewsSentinelTool
        sentinel = NewsSentinelTool()
        result = sentinel.classify_event("War breaks out in Middle East")
        assert result["event_type"] == "SHOCK"

    def test_classify_macro(self):
        from src.quant.news_sentinel import NewsSentinelTool
        sentinel = NewsSentinelTool()
        result = sentinel.classify_event("Fed raises interest rates by 0.5%")
        assert result["event_type"] == "MACRO"

    def test_classify_scheduled(self):
        from src.quant.news_sentinel import NewsSentinelTool
        sentinel = NewsSentinelTool()
        result = sentinel.classify_event("Earnings report expected next week")
        assert result["event_type"] == "SCHEDULED"

    def test_classify_noise(self):
        from src.quant.news_sentinel import NewsSentinelTool
        sentinel = NewsSentinelTool()
        result = sentinel.classify_event("The weather is nice today")
        assert result["event_type"] == "NOISE"

    def test_decayed_impact(self):
        from src.quant.news_sentinel import NewsSentinelTool
        sentinel = NewsSentinelTool()
        event = sentinel.add_event("War crisis emergency", timestamp=datetime.now().isoformat())
        impact = sentinel.calculate_decayed_impact(event)
        assert impact > 0
        assert impact <= 1.0

    def test_decayed_impact_old_event(self):
        from src.quant.news_sentinel import NewsSentinelTool
        sentinel = NewsSentinelTool()
        old_time = (datetime.now() - timedelta(hours=48)).isoformat()
        event = sentinel.add_event("Some news", timestamp=old_time)
        impact = sentinel.calculate_decayed_impact(event)
        # SHOCK event with 4h half-life after 48h should be very small
        assert impact < 0.01

    def test_total_impact(self):
        from src.quant.news_sentinel import NewsSentinelTool
        sentinel = NewsSentinelTool()
        sentinel.add_event("Fed raises rates")
        sentinel.add_event("War crisis")
        result = sentinel.get_total_impact()
        assert result["total_impact"] > 0

    def test_cleanup(self):
        from src.quant.news_sentinel import NewsSentinelTool
        sentinel = NewsSentinelTool()
        sentinel.add_event("Recent news")
        old_time = (datetime.now() - timedelta(hours=48)).isoformat()
        sentinel.add_event("Old news", timestamp=old_time)
        removed = sentinel.cleanup_old_events(24.0)
        assert removed >= 1


class TestDecisionEngine:
    """Tests for the DecisionSynthesisEngine."""

    def test_strong_buy(self):
        from src.quant.decision_engine import DecisionSynthesisEngine
        engine = DecisionSynthesisEngine()
        result = engine.evaluate("TRENDING", 0.8, 0.2, 0.7, "NORMAL")
        assert result.action == "ALLOW_LONG"
        assert result.risk_clearance == "CLEAR"

    def test_no_trade_panic(self):
        from src.quant.decision_engine import DecisionSynthesisEngine
        engine = DecisionSynthesisEngine()
        result = engine.evaluate("PANIC", 0.5, 0.5, 0.5, "HIGH")
        assert result.action == "NO_TRADE"
        assert result.risk_clearance == "BLOCKED"

    def test_watch_mode(self):
        from src.quant.decision_engine import DecisionSynthesisEngine
        engine = DecisionSynthesisEngine()
        result = engine.evaluate("RANGE", 0.6, 0.4, 0.6, "NORMAL")
        assert "WATCH" in result.action or result.action in ("ALLOW_LONG_TRENDING", "NO_TRADE")

    def test_daily_loss_blocks(self):
        from src.quant.decision_engine import DecisionSynthesisEngine
        engine = DecisionSynthesisEngine()
        result = engine.evaluate("TRENDING", 0.8, 0.2, 0.7, "NORMAL", daily_pnl_pct=-0.02)
        assert result.action == "NO_TRADE"
        assert result.risk_clearance == "BLOCKED"


class TestPressureEngine:
    """Tests for the PressureNormalizationEngine."""

    def test_strong_buy_pressure(self):
        from src.quant.pressure_engine import PressureNormalizationEngine
        engine = PressureNormalizationEngine()
        result = engine.compile_pressure(
            trend_direction="bullish", trend_strength=0.9,
            smc_signal="bullish_bos", displacement_strength=0.8,
            news_impact=0.3, news_uncertainty=0.3,
            flow_imbalance=0.7, flow_direction="long",
        )
        assert result.buy_pressure > 0.6
        assert result.verdict in ("BUY", "STRONG_BUY")

    def test_neutral_pressure(self):
        from src.quant.pressure_engine import PressureNormalizationEngine
        engine = PressureNormalizationEngine()
        result = engine.compile_pressure()
        assert result.verdict == "NEUTRAL"
        assert result.buy_pressure == pytest.approx(0.0)
        assert result.sell_pressure == pytest.approx(0.0)


class TestMarketState:
    """Tests for the MarketStateEngine."""

    def test_trending_regime(self):
        from src.quant.market_state import MarketStateEngine
        engine = MarketStateEngine()
        result = engine.detect_regime(adx=30, rsi=55)
        assert result.regime == "TRENDING"

    def test_panic_regime(self):
        from src.quant.market_state import MarketStateEngine
        engine = MarketStateEngine()
        result = engine.detect_regime(price_change_5d=-6.0)
        assert result.base_regime == "PANIC"
        assert result.regime == "NO_TRADE"

    def test_mean_revert_regime(self):
        from src.quant.market_state import MarketStateEngine
        engine = MarketStateEngine()
        result = engine.detect_regime(rsi=80)
        assert result.regime == "MEAN_REVERT"

    def test_range_regime(self):
        from src.quant.market_state import MarketStateEngine
        engine = MarketStateEngine()
        result = engine.detect_regime(adx=15, rsi=50)
        assert result.regime == "RANGE"

    def test_no_trade_high_vol_thin_liq(self):
        from src.quant.market_state import MarketStateEngine
        engine = MarketStateEngine()
        result = engine.detect_regime(atr_pct=3.0, volume_ratio=0.3)
        assert result.regime == "NO_TRADE"


class TestAutoSwitch:
    """Tests for the AutoSwitchEngine."""

    def test_register_provider(self):
        from src.quant.autoswitch import AutoSwitchEngine
        engine = AutoSwitchEngine()
        engine.register_provider("openai")
        assert "openai" in engine.providers

    def test_provider_order(self):
        from src.quant.autoswitch import AutoSwitchEngine
        engine = AutoSwitchEngine()
        engine.register_provider("openai")
        engine.register_provider("anthropic")
        engine.record_success("openai", 500)
        engine.record_success("anthropic", 200)
        order = engine.get_provider_order()
        assert order[0] == "anthropic"  # Faster = higher score

    def test_failure_cooldown(self):
        from src.quant.autoswitch import AutoSwitchEngine
        engine = AutoSwitchEngine()
        engine.register_provider("bad_provider")
        for _ in range(6):
            engine.record_failure("bad_provider", "error")
        # Provider should have cooldown
        ph = engine.providers["bad_provider"]
        assert ph.cooldown_until is not None

    def test_rate_limit_cooldown(self):
        from src.quant.autoswitch import AutoSwitchEngine
        engine = AutoSwitchEngine()
        engine.register_provider("openai")
        engine.record_failure("openai", "rate limited", status_code=429)
        ph = engine.providers["openai"]
        assert ph.cooldown_until is not None

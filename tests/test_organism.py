"""Tests for src.organism modules."""

import asyncio
import pytest
import tempfile
from pathlib import Path


class TestScheduler:
    """Tests for the OrganismScheduler."""

    def test_initial_state(self):
        from src.organism.scheduler import OrganismScheduler, CycleType
        scheduler = OrganismScheduler()
        for ct in CycleType:
            assert scheduler.should_run(ct) is True

    def test_run_cycle(self):
        from src.organism.scheduler import OrganismScheduler, CycleType
        scheduler = OrganismScheduler()
        executed = []

        async def callback():
            executed.append("ran")

        result = asyncio.run(scheduler.run_cycle(CycleType.HOURLY, callback))
        assert result is True
        assert "ran" in executed

    def test_cycle_not_ready(self):
        from src.organism.scheduler import OrganismScheduler, CycleType
        scheduler = OrganismScheduler()
        # Run once
        asyncio.run(scheduler.run_cycle(CycleType.HOURLY, lambda: None))
        # Immediately running again should be blocked by interval
        result = asyncio.run(scheduler.run_cycle(CycleType.HOURLY, lambda: None))
        assert result is False

    def test_force_run(self):
        from src.organism.scheduler import OrganismScheduler, CycleType
        scheduler = OrganismScheduler()
        asyncio.run(scheduler.run_cycle(CycleType.HOURLY, lambda: None))
        scheduler.force_run(CycleType.HOURLY)
        assert scheduler.should_run(CycleType.HOURLY) is True

    def test_run_all(self):
        from src.organism.scheduler import OrganismScheduler, CycleType
        scheduler = OrganismScheduler()
        callbacks = {CycleType.HOURLY: lambda: None}
        results = asyncio.run(scheduler.run_all(callbacks))
        assert CycleType.HOURLY in results
        assert results[CycleType.HOURLY] is True

    def test_status(self):
        from src.organism.scheduler import OrganismScheduler
        scheduler = OrganismScheduler()
        status = scheduler.get_status()
        assert "cycles" in status


class TestSenseEngine:
    """Tests for the SenseEngine."""

    def test_add_problems(self):
        from src.organism.sense import SenseEngine
        engine = SenseEngine()
        problems = [
            {"text": "Need better automation tools", "source": "reddit", "comments": 50},
            {"text": "App keeps crashing on startup", "source": "kaskus", "comments": 30},
        ]
        added = engine.add_problems(problems)
        assert len(added) == 2

    def test_deduplication(self):
        from src.organism.sense import SenseEngine
        engine = SenseEngine()
        problems = [
            {"text": "Need better tools", "source": "reddit"},
            {"text": "Need better tools", "source": "reddit"},  # Duplicate
        ]
        added = engine.add_problems(problems)
        assert len(added) == 1

    def test_sentiment_negative(self):
        from src.organism.sense import SenseEngine
        engine = SenseEngine()
        sentiment = engine.analyze_sentiment("The app is broken and expensive")
        assert sentiment == "negative"

    def test_sentiment_positive(self):
        from src.organism.sense import SenseEngine
        engine = SenseEngine()
        sentiment = engine.analyze_sentiment("This is great and awesome")
        assert sentiment == "positive"

    def test_get_negative_problems(self):
        from src.organism.sense import SenseEngine
        engine = SenseEngine()
        engine.add_problems([
            {"text": "System is broken and fails", "source": "reddit", "comments": 50},
            {"text": "I love this easy tool", "source": "twitter", "comments": 10},
        ])
        neg = engine.get_negative_problems()
        assert len(neg) >= 1

    def test_status(self):
        from src.organism.sense import SenseEngine
        engine = SenseEngine()
        engine.add_problems([{"text": "Test problem", "source": "test"}])
        status = engine.get_status()
        assert status["total_problems"] == 1


class TestImmuneSystem:
    """Tests for the ImmuneSystem."""

    def test_can_continue_within_limit(self):
        from src.organism.immune import ImmuneSystem
        immune = ImmuneSystem()
        for _ in range(9):
            assert immune.can_continue("task1") is True

    def test_exceeds_iteration_limit(self):
        from src.organism.immune import ImmuneSystem
        immune = ImmuneSystem()
        for _ in range(10):
            immune.can_continue("task1")
        assert immune.can_continue("task1") is False

    def test_error_tracking(self):
        from src.organism.immune import ImmuneSystem
        immune = ImmuneSystem()
        for _ in range(5):
            result = immune.record_error("task1")
        assert result is False  # Exceeded max

    def test_success_resets_errors(self):
        from src.organism.immune import ImmuneSystem
        immune = ImmuneSystem()
        immune.record_error("task1")
        immune.record_error("task1")
        immune.record_success("task1")
        counters = immune._get_counters("task1")
        assert counters.errors == 0

    def test_loop_detection(self):
        from src.organism.immune import ImmuneSystem
        immune = ImmuneSystem()
        for _ in range(101):
            result = immune.detect_loop("task1", "same_state")
        assert result is False

    def test_kill_task(self):
        from src.organism.immune import ImmuneSystem
        immune = ImmuneSystem()
        immune.can_continue("task1")
        result = immune.kill("task1", "too many errors")
        assert result.killed is True
        assert "task1" not in immune.counters

    def test_health_check(self):
        from src.organism.immune import ImmuneSystem
        immune = ImmuneSystem()
        result = immune.health_check()
        assert result.healthy is True

    def test_health_check_with_warnings(self):
        from src.organism.immune import ImmuneSystem
        immune = ImmuneSystem()
        for _ in range(3):
            immune.record_error("bad_task")
        result = immune.health_check()
        assert "bad_task" in result.warning_tasks


class TestDecisionCore:
    """Tests for the DecisionCore."""

    def test_calculate_score(self):
        from src.organism.decision import DecisionCore
        core = DecisionCore()
        result = core.calculate_score({
            "text": "Need auto posting tool for business",
            "comments": 150,
        })
        assert result.scores.total > 0
        assert 0 <= result.scores.automation <= 1
        assert 0 <= result.scores.money <= 1

    def test_rank_problems(self):
        from src.organism.decision import DecisionCore
        core = DecisionCore()
        problems = [
            {"text": "Minor issue", "comments": 5},
            {"text": "Major broken system fails", "comments": 200},
            {"text": "Nice to have feature", "comments": 50},
        ]
        ranked = core.rank_problems(problems)
        assert len(ranked) == 3
        assert ranked[0].scores.total >= ranked[1].scores.total

    def test_select_best(self):
        from src.organism.decision import DecisionCore
        core = DecisionCore()
        problems = [
            {"text": "Low value free request", "comments": 10},
            {"text": "Expensive business automation tool needed", "comments": 200},
        ]
        best = core.select_best(problems)
        assert best is not None
        assert best.scores.total > 0

    def test_select_best_empty(self):
        from src.organism.decision import DecisionCore
        core = DecisionCore()
        result = core.select_best([])
        assert result is None

    def test_sentiment_analysis(self):
        from src.organism.decision import DecisionCore
        core = DecisionCore()
        assert core.analyze_sentiment("System is broken and fails") == "negative"
        assert core.analyze_sentiment("This is great and perfect") == "positive"
        assert core.analyze_sentiment("The weather today") == "neutral"


class TestSaasFactory:
    """Tests for the SaasFactory."""

    def test_build(self):
        from src.organism.factory import SaasFactory
        with tempfile.TemporaryDirectory() as tmpdir:
            factory = SaasFactory(output_dir=tmpdir)
            result = factory.build("Need auto posting Instagram tool")
            assert result.status == "READY"
            assert len(result.files) > 0

    def test_project_name_generation(self):
        from src.organism.factory import SaasFactory
        factory = SaasFactory()
        name = factory.generate_project_name("Need Auto Posting Tool")
        assert "need" in name or "auto" in name

    def test_status(self):
        from src.organism.factory import SaasFactory
        with tempfile.TemporaryDirectory() as tmpdir:
            factory = SaasFactory(output_dir=tmpdir)
            status = factory.get_status()
            assert "output_dir" in status


class TestMemoryEngine:
    """Tests for the MemoryEngine."""

    def test_log_and_retrieve(self):
        from src.organism.memory import MemoryEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = MemoryEngine(storage_path=str(Path(tmpdir) / "test.json"))
            entry = engine.log("PRODUCT", "AutoPost", "SUCCESS", "High demand")
            assert entry.entry_type == "PRODUCT"
            assert entry.result == "SUCCESS"
            assert len(engine.logs) == 1

    def test_analyze_failures(self):
        from src.organism.memory import MemoryEngine
        engine = MemoryEngine()
        engine.log("PRODUCT", "A", "FAILED", "No demand")
        engine.log("PRODUCT", "B", "FAILED", "No demand")
        engine.log("AGENT", "C", "FAILED", "Cost too high")
        patterns = engine.analyze_failures()
        assert len(patterns) > 0
        assert patterns[0].reason == "No demand"
        assert patterns[0].count == 2

    def test_analyze_success(self):
        from src.organism.memory import MemoryEngine
        engine = MemoryEngine()
        engine.log("PRODUCT", "A", "SUCCESS", "High demand")
        engine.log("AGENT", "B", "SUCCESS", "Efficient")
        result = engine.analyze_success()
        assert "PRODUCT" in result
        assert "AGENT" in result

    def test_weekly_review(self):
        from src.organism.memory import MemoryEngine
        engine = MemoryEngine()
        engine.log("PRODUCT", "A", "FAILED", "No demand")
        engine.log("PRODUCT", "B", "SUCCESS", "High demand")
        review = engine.weekly_review()
        assert review["total_entries"] == 2
        assert len(review["recommendations"]) > 0

    def test_persistence(self):
        from src.organism.memory import MemoryEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            path = str(Path(tmpdir) / "test.json")
            engine = MemoryEngine(storage_path=path)
            engine.log("PRODUCT", "Test", "SUCCESS", "Works")

            # Create new engine with same path
            engine2 = MemoryEngine(storage_path=path)
            assert len(engine2.logs) == 1

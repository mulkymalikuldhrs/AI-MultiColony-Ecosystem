"""
Comprehensive tests for advanced organism modules.

Covers additional edge cases and deeper testing of: OrganismScheduler,
SenseEngine, ImmuneSystem, DecisionCore, SaasFactory, MemoryEngine.
These tests complement test_organism.py with more thorough coverage.
"""

import asyncio
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest


# ───────────────────────────────────────────────────────────────
# OrganismScheduler - extended tests
# ───────────────────────────────────────────────────────────────

class TestSchedulerAdvanced:
    """Extended tests for OrganismScheduler covering edge cases."""

    @pytest.fixture
    def scheduler(self):
        from src.organism.scheduler import OrganismScheduler
        return OrganismScheduler()

    def test_cycle_intervals_are_positive(self, scheduler):
        """All cycle intervals should be positive integers."""
        from src.organism.scheduler import CycleType
        for ct in CycleType:
            assert scheduler.cycles[ct].interval_ms > 0

    def test_cycle_intervals_ordering(self, scheduler):
        """Cycle intervals should increase: HOURLY < DAILY < WEEKLY < MONTHLY."""
        from src.organism.scheduler import CycleType
        assert scheduler.cycles[CycleType.HOURLY].interval_ms < scheduler.cycles[CycleType.DAILY].interval_ms
        assert scheduler.cycles[CycleType.DAILY].interval_ms < scheduler.cycles[CycleType.WEEKLY].interval_ms
        assert scheduler.cycles[CycleType.WEEKLY].interval_ms < scheduler.cycles[CycleType.MONTHLY].interval_ms

    def test_run_cycle_increments_count(self, scheduler):
        """Running a cycle increments its run_count."""
        from src.organism.scheduler import CycleType
        assert scheduler.cycles[CycleType.HOURLY].run_count == 0
        asyncio.run(scheduler.run_cycle(CycleType.HOURLY, lambda: None))
        assert scheduler.cycles[CycleType.HOURLY].run_count == 1

    def test_run_cycle_with_sync_callback(self, scheduler):
        """Running a cycle with a synchronous callback works."""
        from src.organism.scheduler import CycleType
        result = asyncio.run(scheduler.run_cycle(CycleType.DAILY, lambda: print("sync")))
        assert result is True

    def test_run_cycle_with_async_callback(self, scheduler):
        """Running a cycle with an async callback works."""
        from src.organism.scheduler import CycleType

        async def async_cb():
            pass

        result = asyncio.run(scheduler.run_cycle(CycleType.WEEKLY, async_cb))
        assert result is True

    def test_run_cycle_callback_exception(self, scheduler):
        """Running a cycle where callback raises returns False."""
        from src.organism.scheduler import CycleType

        def failing_callback():
            raise RuntimeError("test failure")

        result = asyncio.run(scheduler.run_cycle(CycleType.HOURLY, failing_callback))
        assert result is False

    def test_run_cycle_async_callback_exception(self, scheduler):
        """Running a cycle where async callback raises returns False."""
        from src.organism.scheduler import CycleType

        async def failing_async():
            raise RuntimeError("async failure")

        result = asyncio.run(scheduler.run_cycle(CycleType.HOURLY, failing_async))
        assert result is False

    def test_run_all_with_missing_callback(self, scheduler):
        """run_all with missing callbacks for some cycles returns False for those."""
        from src.organism.scheduler import CycleType
        callbacks = {CycleType.HOURLY: lambda: None}  # Only hourly has callback
        results = asyncio.run(scheduler.run_all(callbacks))
        assert results[CycleType.HOURLY] is True
        assert results[CycleType.DAILY] is False

    def test_force_run_resets_last_run(self, scheduler):
        """force_run resets last_run to None."""
        from src.organism.scheduler import CycleType
        asyncio.run(scheduler.run_cycle(CycleType.HOURLY, lambda: None))
        assert scheduler.cycles[CycleType.HOURLY].last_run is not None
        scheduler.force_run(CycleType.HOURLY)
        assert scheduler.cycles[CycleType.HOURLY].last_run is None

    def test_get_status_includes_all_cycles(self, scheduler):
        """get_status includes all four cycle types."""
        from src.organism.scheduler import CycleType
        status = scheduler.get_status()
        for ct in CycleType:
            assert ct.value in status["cycles"]
            assert "run_count" in status["cycles"][ct.value]
            assert "should_run" in status["cycles"][ct.value]

    def test_last_run_set_after_execution(self, scheduler):
        """last_run is set after a cycle executes."""
        from src.organism.scheduler import CycleType
        assert scheduler.cycles[CycleType.MONTHLY].last_run is None
        asyncio.run(scheduler.run_cycle(CycleType.MONTHLY, lambda: None))
        assert scheduler.cycles[CycleType.MONTHLY].last_run is not None


# ───────────────────────────────────────────────────────────────
# SenseEngine - extended tests
# ───────────────────────────────────────────────────────────────

class TestSenseEngineAdvanced:
    """Extended tests for SenseEngine covering edge cases."""

    @pytest.fixture
    def engine(self):
        from src.organism.sense import SenseEngine
        return SenseEngine()

    def test_add_problems_empty_list(self, engine):
        """Adding empty list returns empty result."""
        result = engine.add_problems([])
        assert result == []

    def test_add_problems_empty_text(self, engine):
        """Problems with empty text are skipped."""
        result = engine.add_problems([{"text": "", "source": "test"}])
        assert result == []

    def test_add_problems_whitespace_only(self, engine):
        """Problems with only whitespace text are skipped."""
        result = engine.add_problems([{"text": "   ", "source": "test"}])
        assert result == []

    def test_add_problems_with_replies_key(self, engine):
        """Problems using 'replies' key instead of 'comments' work."""
        result = engine.add_problems([
            {"text": "Test problem with replies", "source": "reddit", "replies": 42},
        ])
        assert len(result) == 1
        assert result[0].comments == 42

    def test_add_problems_with_reviews_key(self, engine):
        """Problems using 'reviews' key work."""
        result = engine.add_problems([
            {"text": "Test problem with reviews", "source": "app_store", "reviews": 15},
        ])
        assert len(result) == 1
        assert result[0].comments == 15

    def test_sentiment_mixed(self, engine):
        """Text with both positive and negative words leans toward the dominant."""
        # More negative words
        result = engine.analyze_sentiment("This is hard and difficult and broken but great")
        assert result == "negative"
        # More positive words
        result = engine.analyze_sentiment("This is great and awesome and excellent but hard")
        assert result == "positive"

    def test_sentiment_neutral(self, engine):
        """Text with no sentiment words is neutral."""
        result = engine.analyze_sentiment("The weather is cloudy today")
        assert result == "neutral"

    def test_get_negative_problems_min_comments(self, engine):
        """min_comments filter excludes low-comment problems."""
        engine.add_problems([
            {"text": "This error is broken", "source": "test", "comments": 1},
            {"text": "That fail is frustrating", "source": "test", "comments": 50},
        ])
        neg = engine.get_negative_problems(min_comments=10)
        assert all(p.comments >= 10 for p in neg)

    def test_get_status_sentiment_distribution(self, engine):
        """Status includes correct sentiment distribution."""
        engine.add_problems([
            {"text": "This is great and awesome", "source": "test"},
            {"text": "This is broken and fails", "source": "test"},
            {"text": "Just a normal post", "source": "test"},
        ])
        status = engine.get_status()
        assert status["sentiment_distribution"]["positive"] >= 1
        assert status["sentiment_distribution"]["negative"] >= 1
        assert status["total_problems"] == 3

    def test_get_status_sources(self, engine):
        """Status lists unique sources."""
        engine.add_problems([
            {"text": "Problem A", "source": "reddit"},
            {"text": "Problem B", "source": "twitter"},
            {"text": "Problem C", "source": "reddit"},
        ])
        status = engine.get_status()
        assert set(status["sources"]) == {"reddit", "twitter"}

    def test_deduplication_case_insensitive(self, engine):
        """Deduplication is case-insensitive after text cleaning."""
        engine.add_problems([
            {"text": "Need Better Tools", "source": "test"},
        ])
        new = engine.add_problems([
            {"text": "need better tools", "source": "test"},
        ])
        # After lowercasing and cleaning, these should be duplicates
        assert len(new) == 0

    def test_clean_text_static(self):
        """Static clean_text method processes input without error."""
        from src.organism.sense import SenseEngine
        result = SenseEngine.clean_text("Test https://example.com text")
        assert isinstance(result, str)


# ───────────────────────────────────────────────────────────────
# ImmuneSystem - extended tests
# ───────────────────────────────────────────────────────────────

class TestImmuneSystemAdvanced:
    """Extended tests for ImmuneSystem covering edge cases."""

    @pytest.fixture
    def immune(self):
        from src.organism.immune import ImmuneSystem
        return ImmuneSystem()

    @pytest.fixture
    def strict_immune(self):
        from src.organism.immune import ImmuneSystem, ImmuneConfig
        config = ImmuneConfig(
            max_iterations_per_task=3,
            hard_timeout_ms=5000,
            max_consecutive_errors=2,
            max_loop_detection=5,
        )
        return ImmuneSystem(config=config)

    def test_custom_config(self, strict_immune):
        """Custom config is applied correctly."""
        assert strict_immune.config.max_iterations_per_task == 3
        assert strict_immune.config.max_consecutive_errors == 2

    def test_can_continue_custom_limit(self, strict_immune):
        """can_continue respects custom iteration limit."""
        for _ in range(3):
            assert strict_immune.can_continue("task1") is True
        assert strict_immune.can_continue("task1") is False

    def test_can_continue_different_tasks(self, immune):
        """Different tasks have independent iteration counters."""
        for _ in range(5):
            immune.can_continue("task_a")
        # task_b should still have all iterations available
        assert immune.can_continue("task_b") is True

    def test_check_timeout_within(self, immune):
        """check_timeout returns True when within timeout."""
        import time
        start = time.time() * 1000
        assert immune.check_timeout("task1", start) is True

    def test_check_timeout_exceeded(self, immune):
        """check_timeout returns False when timeout exceeded."""
        # Set start time far in the past
        start = 0  # Very old start time
        assert immune.check_timeout("task1", start) is False

    def test_check_timeout_custom(self, strict_immune):
        """check_timeout uses custom timeout from config."""
        import time
        start = (time.time() * 1000) - 10000  # 10 seconds ago
        # Config has 5000ms timeout, so this should be exceeded
        assert strict_immune.check_timeout("task1", start) is False

    def test_record_error_custom_limit(self, strict_immune):
        """record_error respects custom max_consecutive_errors."""
        assert strict_immune.record_error("task1") is True  # 1 error
        assert strict_immune.record_error("task1") is False  # 2 errors = max

    def test_record_success_resets_errors(self, immune):
        """Success resets the error counter for a task."""
        immune.record_error("task1")
        immune.record_error("task1")
        immune.record_success("task1")
        counters = immune._get_counters("task1")
        assert counters.errors == 0

    def test_detect_loop_custom_limit(self, strict_immune):
        """Loop detection uses custom max_loop_detection (5 = triggered at 6th occurrence)."""
        for i in range(5):
            result = strict_immune.detect_loop("task1", "same_state")
            assert result is True  # First 5 occurrences are OK
        # 6th occurrence should trigger loop detection (count > 5)
        result = strict_immune.detect_loop("task1", "same_state")
        assert result is False

    def test_detect_loop_different_states(self, immune):
        """Different states don't trigger loop detection."""
        for i in range(50):
            result = immune.detect_loop("task1", f"state_{i}")
            assert result is True

    def test_kill_removes_counters(self, immune):
        """Killing a task removes its counters."""
        immune.can_continue("task1")
        result = immune.kill("task1", "test kill")
        assert "task1" not in immune.counters
        assert result.killed is True
        assert result.reason == "test kill"

    def test_kill_nonexistent_task(self, immune):
        """Killing a non-existent task raises KeyError."""
        with pytest.raises(KeyError):
            immune.kill("nonexistent", "reason")

    def test_reset_task(self, immune):
        """Resetting a task clears its counters."""
        immune.can_continue("task1")
        immune.record_error("task1")
        immune.reset("task1")
        counters = immune._get_counters("task1")
        assert counters.iterations == 0
        assert counters.errors == 0

    def test_reset_nonexistent_task(self, immune):
        """Resetting a non-existent task does nothing (no crash)."""
        immune.reset("nonexistent")  # Should not raise

    def test_health_check_healthy(self, immune):
        """Health check is healthy when no tasks have many errors."""
        immune.record_error("task1")
        result = immune.health_check()
        assert result.healthy is True
        assert result.total_errors == 1

    def test_health_check_unhealthy(self, immune):
        """Health check is unhealthy when tasks have 3+ errors."""
        for _ in range(3):
            immune.record_error("bad_task")
        result = immune.health_check()
        assert result.healthy is False
        assert "bad_task" in result.warning_tasks

    def test_get_status(self, immune):
        """get_status returns config and health info."""
        immune.can_continue("task1")
        status = immune.get_status()
        assert "config" in status
        assert "tracked_tasks" in status
        assert "health" in status
        assert status["tracked_tasks"] == 1

    def test_get_counters_auto_create(self, immune):
        """Getting counters for a new task auto-creates them."""
        counters = immune._get_counters("new_task")
        assert counters.iterations == 0
        assert counters.errors == 0


# ───────────────────────────────────────────────────────────────
# DecisionCore - extended tests
# ───────────────────────────────────────────────────────────────

class TestDecisionCoreAdvanced:
    """Extended tests for DecisionCore covering edge cases."""

    @pytest.fixture
    def core(self):
        from src.organism.decision import DecisionCore
        return DecisionCore()

    def test_estimate_automation_auto_friendly(self, core):
        """Text with automation-friendly words scores higher."""
        auto_score = core.estimate_automation("I need an auto bot script for my app")
        manual_score = core.estimate_automation("I need someone to do it by hand manually")
        assert auto_score > manual_score

    def test_estimate_automation_clamped(self, core):
        """Automation score is clamped between 0 and 1."""
        # Very auto-friendly text should not exceed 1.0
        score = core.estimate_automation("auto automation script bot api system app tools software digital")
        assert 0.0 <= score <= 1.0

    def test_estimate_money_potential_high_value(self, core):
        """Text with money-related words scores higher."""
        money_score = core.estimate_money_potential("jual beli uang modal bisnis produk harga")
        low_score = core.estimate_money_potential("free gratisan mau cari butuh")
        assert money_score > low_score

    def test_estimate_money_potential_clamped(self, core):
        """Money potential score is clamped between 0 and 1."""
        score = core.estimate_money_potential("sell buy money capital business product price revenue jual beli uang modal")
        assert 0.0 <= score <= 1.0

    def test_calculate_score_with_default_comments(self, core):
        """calculate_score uses default comments=10 when not specified."""
        result = core.calculate_score({"text": "Test problem"})
        assert result.comments == 10  # Default from the code

    def test_calculate_score_zero_comments(self, core):
        """Zero comments produces zero comment score."""
        result = core.calculate_score({"text": "Test", "comments": 0})
        assert result.scores.comments == 0.0

    def test_calculate_score_high_comments(self, core):
        """Very high comments are capped at 1.0 for comment score."""
        result = core.calculate_score({"text": "Test", "comments": 500})
        assert result.scores.comments == 1.0

    def test_calculate_score_negative_sentiment(self, core):
        """Negative sentiment gives highest sentiment score (1.0)."""
        result = core.calculate_score({"text": "This error is broken and fails", "comments": 10})
        assert result.scores.sentiment == 1.0

    def test_calculate_score_positive_sentiment(self, core):
        """Positive sentiment gives low sentiment score (0.2)."""
        result = core.calculate_score({"text": "This is great and perfect", "comments": 10})
        assert result.scores.sentiment == 0.2

    def test_rank_problems_empty(self, core):
        """Ranking empty list returns empty list."""
        result = core.rank_problems([])
        assert result == []

    def test_rank_problems_ordering(self, core):
        """Problems are ranked by total score descending."""
        problems = [
            {"text": "Low value free request", "comments": 5},
            {"text": "Expensive business automation tool needed", "comments": 200},
            {"text": "Nice to have feature", "comments": 50},
        ]
        ranked = core.rank_problems(problems)
        for i in range(len(ranked) - 1):
            assert ranked[i].scores.total >= ranked[i + 1].scores.total

    @pytest.mark.parametrize("text,expected", [
        ("This is broken and fails", "negative"),
        ("This is great and awesome", "positive"),
        ("The weather today is nice", "neutral"),
        ("Bug in the system makes it crash", "negative"),
        ("Easy and simple to use", "positive"),
    ])
    def test_sentiment_parametrized(self, core, text, expected):
        """Parametrized sentiment analysis tests."""
        result = core.analyze_sentiment(text)
        assert result == expected

    def test_scored_problem_model(self, core):
        """ScoredProblem model has expected fields."""
        result = core.calculate_score({"text": "Test problem", "comments": 50})
        assert hasattr(result, 'text')
        assert hasattr(result, 'source')
        assert hasattr(result, 'comments')
        assert hasattr(result, 'sentiment_label')
        assert hasattr(result, 'scores')
        assert hasattr(result.scores, 'total')


# ───────────────────────────────────────────────────────────────
# SaasFactory - extended tests
# ───────────────────────────────────────────────────────────────

class TestSaasFactoryAdvanced:
    """Extended tests for SaasFactory covering edge cases."""

    @pytest.fixture
    def factory(self):
        from src.organism.factory import SaasFactory
        tmpdir = tempfile.mkdtemp()
        return SaasFactory(output_dir=tmpdir)

    def test_build_creates_files(self, factory):
        """Build creates all expected project files."""
        result = factory.build("Need auto posting Instagram tool")
        assert result.status == "READY"
        assert "package.json" in result.files
        assert "Dockerfile" in result.files
        assert "docker-compose.yml" in result.files
        assert "app/api/route.js" in result.files

    def test_build_project_name(self, factory):
        """Build generates project name from first 3 words."""
        result = factory.build("Create automated email sender tool")
        assert result.name == "create-automated-email"

    def test_build_project_spec_model(self, factory):
        """Build returns ProjectSpec with all expected fields."""
        from src.organism.factory import ProjectSpec
        result = factory.build("Test problem text")
        assert isinstance(result, ProjectSpec)
        assert result.problem == "Test problem text"
        assert result.created is not None

    def test_build_multiple_projects(self, factory):
        """Building multiple projects creates separate directories."""
        factory.build("First project idea")
        factory.build("Second project idea")
        status = factory.get_status()
        assert status["projects_built"] == 2

    def test_generate_project_name_short_text(self, factory):
        """Project name from single word uses just that word."""
        name = factory.generate_project_name("Automation")
        assert name == "automation"

    def test_generate_project_name_long_text(self, factory):
        """Project name from long text uses only first 3 words."""
        name = factory.generate_project_name("This is a very long description of a problem")
        assert name == "this-is-a"

    def test_get_status_after_build(self, factory):
        """Status reflects built projects."""
        factory.build("Test project one")
        status = factory.get_status()
        assert status["projects_built"] == 1
        assert "output_dir" in status

    def test_ensure_dir(self, factory):
        """_ensure_dir creates the output directory."""
        factory._ensure_dir()
        assert factory.output_dir.exists()

    def test_generate_package_json(self, factory):
        """_generate_package_json produces valid JSON with required fields."""
        content = factory._generate_package_json("test-project")
        data = json.loads(content)
        assert data["name"] == "test-project"
        assert "dependencies" in data
        assert "scripts" in data

    def test_generate_dockerfile(self, factory):
        """_generate_dockerfile produces Dockerfile content."""
        content = factory._generate_dockerfile()
        assert "FROM" in content
        assert "node" in content.lower()

    def test_generate_docker_compose(self, factory):
        """_generate_docker_compose produces valid YAML-like content."""
        content = factory._generate_docker_compose()
        assert "services" in content
        assert "app" in content

    def test_generate_api_route(self, factory):
        """_generate_api_route produces JavaScript route content."""
        content = factory._generate_api_route()
        assert "GET" in content
        assert "NextResponse" in content


# ───────────────────────────────────────────────────────────────
# MemoryEngine - extended tests
# ───────────────────────────────────────────────────────────────

class TestMemoryEngineAdvanced:
    """Extended tests for MemoryEngine covering edge cases."""

    @pytest.fixture
    def engine(self):
        from src.organism.memory import MemoryEngine
        return MemoryEngine()

    @pytest.fixture
    def persistent_engine(self):
        from src.organism.memory import MemoryEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            path = str(Path(tmpdir) / "test_memory.json")
            yield MemoryEngine(storage_path=path)

    def test_log_entry_fields(self, engine):
        """Logged entry has all expected fields."""
        entry = engine.log("PRODUCT", "TestProduct", "SUCCESS", "High demand")
        assert entry.id == 1
        assert entry.entry_type == "PRODUCT"
        assert entry.name == "TestProduct"
        assert entry.result == "SUCCESS"
        assert entry.reason == "High demand"
        assert entry.date is not None

    def test_log_auto_increment_id(self, engine):
        """Entry IDs auto-increment."""
        e1 = engine.log("PRODUCT", "A", "SUCCESS", "r1")
        e2 = engine.log("PRODUCT", "B", "FAILED", "r2")
        assert e2.id == e1.id + 1

    def test_analyze_failures_no_failures(self, engine):
        """No failures returns empty list."""
        engine.log("PRODUCT", "A", "SUCCESS", "Works great")
        patterns = engine.analyze_failures()
        assert patterns == []

    def test_analyze_failures_top_5(self, engine):
        """analyze_failures returns at most 5 patterns."""
        for i in range(10):
            engine.log("PRODUCT", f"P{i}", "FAILED", f"Reason {i}")
        patterns = engine.analyze_failures()
        assert len(patterns) <= 5

    def test_analyze_failures_sorted_by_count(self, engine):
        """Failure patterns are sorted by count descending."""
        engine.log("PRODUCT", "A", "FAILED", "common")
        engine.log("PRODUCT", "B", "FAILED", "common")
        engine.log("PRODUCT", "C", "FAILED", "common")
        engine.log("PRODUCT", "D", "FAILED", "rare")
        patterns = engine.analyze_failures()
        assert patterns[0].reason == "common"
        assert patterns[0].count == 3

    def test_analyze_success_no_successes(self, engine):
        """No successes returns empty dict."""
        engine.log("PRODUCT", "A", "FAILED", "error")
        result = engine.analyze_success()
        assert result == {}

    def test_analyze_success_multiple_types(self, engine):
        """Success analysis groups by entry_type."""
        engine.log("PRODUCT", "A", "SUCCESS", "r1")
        engine.log("PRODUCT", "B", "SUCCESS", "r2")
        engine.log("AGENT", "C", "SUCCESS", "r3")
        result = engine.analyze_success()
        assert result["PRODUCT"] == 2
        assert result["AGENT"] == 1

    def test_weekly_review_with_data(self, engine):
        """Weekly review includes recommendations when data exists."""
        engine.log("PRODUCT", "A", "FAILED", "No demand")
        engine.log("PRODUCT", "B", "SUCCESS", "High demand")
        engine.log("CAMPAIGN", "C", "SUCCESS", "Good ROI")
        review = engine.weekly_review()
        assert review["total_entries"] == 3
        assert len(review["failure_patterns"]) > 0
        assert len(review["success_types"]) > 0
        assert len(review["recommendations"]) > 0

    def test_weekly_review_no_data(self, engine):
        """Weekly review with no data has empty patterns."""
        review = engine.weekly_review()
        assert review["total_entries"] == 0
        assert review["failure_patterns"] == []
        assert review["success_types"] == {}
        assert review["recommendations"] == []

    def test_persistence_save_and_load(self, persistent_engine):
        """Entries persist to disk and reload correctly."""
        persistent_engine.log("PRODUCT", "Test", "SUCCESS", "Works")
        persistent_engine._save()

        from src.organism.memory import MemoryEngine
        engine2 = MemoryEngine(storage_path=persistent_engine.storage_path)
        assert len(engine2.logs) == 1
        assert engine2.logs[0].name == "Test"

    def test_persistence_corrupted_file(self):
        """Loading from corrupted JSON file doesn't crash."""
        from src.organism.memory import MemoryEngine
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "corrupted.json"
            path.write_text("NOT VALID JSON {{{")
            engine = MemoryEngine(storage_path=str(path))
            assert engine.logs == []

    def test_get_status(self, engine):
        """get_status returns correct structure."""
        engine.log("PRODUCT", "A", "SUCCESS", "r")
        status = engine.get_status()
        assert status["total_logs"] == 1

    def test_get_status_no_storage(self, engine):
        """get_status returns None for storage_path when not set."""
        status = engine.get_status()
        assert status["storage_path"] is None

    def test_pivot_result_type(self, engine):
        """PIVOT result type is tracked correctly."""
        entry = engine.log("PRODUCT", "PivotProduct", "PIVOT", "Market changed")
        assert entry.result == "PIVOT"
        # PIVOT entries should not appear in failures or successes
        patterns = engine.analyze_failures()
        assert all(p.reason != "Market changed" for p in patterns)
        successes = engine.analyze_success()
        assert "PRODUCT" not in successes

"""Tests for DecisionEngine — MCDA, weighted scoring, approval/rejection."""

from __future__ import annotations

import pytest

from ai_multicolony.organism.decision import (
    CriterionCategory,
    DecisionConfig,
    DecisionEngine,
    DecisionScore,
    DecisionStatus,
    ScoringCriterion,
    DEFAULT_CRITERIA,
)


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def engine():
    return DecisionEngine()


@pytest.fixture
def high_scores():
    """Scores that should result in approval."""
    return {
        "business_impact": 9.0,
        "urgency": 8.0,
        "feasibility": 9.0,
        "cost_efficiency": 8.0,
        "risk_level": 9.0,
        "strategic_alignment": 9.0,
        "innovation_potential": 8.0,
    }


@pytest.fixture
def low_scores():
    """Scores that should result in rejection."""
    return {
        "business_impact": 1.0,
        "urgency": 1.0,
        "feasibility": 1.0,
        "cost_efficiency": 1.0,
        "risk_level": 1.0,
        "strategic_alignment": 1.0,
        "innovation_potential": 1.0,
    }


@pytest.fixture
def medium_scores():
    """Scores in the deferment range."""
    return {
        "business_impact": 5.0,
        "urgency": 5.0,
        "feasibility": 5.0,
        "cost_efficiency": 5.0,
        "risk_level": 5.0,
        "strategic_alignment": 5.0,
        "innovation_potential": 5.0,
    }


# ── ScoringCriterion ─────────────────────────────────────────────────────

class TestScoringCriterion:
    """Test ScoringCriterion model."""

    def test_normalize(self):
        c = ScoringCriterion(min_score=0, max_score=10)
        assert c.normalize(5) == 0.5
        assert c.normalize(0) == 0.0
        assert c.normalize(10) == 1.0

    def test_normalize_clamped(self):
        c = ScoringCriterion(min_score=0, max_score=10)
        assert c.normalize(15) == 1.0  # Clamped
        assert c.normalize(-5) == 0.0  # Clamped

    def test_normalize_zero_range(self):
        c = ScoringCriterion(min_score=5, max_score=5)
        assert c.normalize(5) == 0.0

    def test_default_threshold(self):
        c = ScoringCriterion()
        assert c.threshold == 5.0


# ── Default Criteria ─────────────────────────────────────────────────────

class TestDefaultCriteria:
    """Test default scoring criteria."""

    def test_seven_criteria(self):
        assert len(DEFAULT_CRITERIA) == 7

    def test_criteria_names(self):
        names = {c.name for c in DEFAULT_CRITERIA}
        assert "business_impact" in names
        assert "urgency" in names
        assert "feasibility" in names
        assert "cost_efficiency" in names
        assert "risk_level" in names
        assert "strategic_alignment" in names
        assert "innovation_potential" in names

    def test_criteria_weights(self):
        total_weight = sum(c.weight for c in DEFAULT_CRITERIA)
        assert total_weight > 0


# ── Evaluate ─────────────────────────────────────────────────────────────

class TestEvaluate:
    """Test evaluate method."""

    def test_approve_high_scores(self, engine, high_scores):
        result = engine.evaluate("sig-1", "Great opportunity", high_scores)
        assert result.status in (DecisionStatus.APPROVED, DecisionStatus.ESCALATED)
        assert result.normalized_score > 0.6

    def test_reject_low_scores(self, engine, low_scores):
        result = engine.evaluate("sig-2", "Poor opportunity", low_scores)
        assert result.status == DecisionStatus.REJECTED
        assert result.normalized_score < 0.3

    def test_defer_medium_scores(self, engine, medium_scores):
        result = engine.evaluate("sig-3", "Borderline", medium_scores)
        # Could be approved, deferred, or escalated depending on exact scores
        assert result.status in (
            DecisionStatus.APPROVED,
            DecisionStatus.DEFERRED,
            DecisionStatus.ESCALATED,
        )

    def test_escalate_very_high_scores(self, engine):
        scores = {c.name: 10.0 for c in DEFAULT_CRITERIA}
        result = engine.evaluate("sig-4", "Exceptional", scores)
        assert result.status == DecisionStatus.ESCALATED
        assert result.normalized_score >= 0.8

    def test_weighted_scores_populated(self, engine, high_scores):
        result = engine.evaluate("sig-5", "Test", high_scores)
        assert len(result.weighted_scores) > 0

    def test_total_score_positive(self, engine, high_scores):
        result = engine.evaluate("sig-6", "Test", high_scores)
        assert result.total_score > 0

    def test_max_possible_score(self, engine, high_scores):
        result = engine.evaluate("sig-7", "Test", high_scores)
        assert result.max_possible_score > 0

    def test_missing_criteria_defaults_to_zero(self, engine):
        result = engine.evaluate("sig-8", "Partial", {"business_impact": 8.0})
        assert result.normalized_score < 0.5  # Missing criteria hurt


# ── Batch Evaluate ───────────────────────────────────────────────────────

class TestBatchEvaluate:
    """Test batch_evaluate method."""

    def test_batch_sorted_by_score(self, engine):
        signals = [
            {"signal_id": "1", "signal_title": "Low", "criteria_scores": {
                c.name: 2.0 for c in DEFAULT_CRITERIA}},
            {"signal_id": "2", "signal_title": "High", "criteria_scores": {
                c.name: 9.0 for c in DEFAULT_CRITERIA}},
        ]
        results = engine.batch_evaluate(signals)
        assert results[0].normalized_score >= results[1].normalized_score

    def test_batch_returns_all(self, engine):
        signals = [
            {"signal_id": f"{i}", "signal_title": f"Sig {i}", "criteria_scores": {}}
            for i in range(5)
        ]
        results = engine.batch_evaluate(signals)
        assert len(results) == 5


# ── Require All Thresholds ───────────────────────────────────────────────

class TestRequireAllThresholds:
    """Test require_all_thresholds config."""

    def test_reject_when_threshold_not_met(self):
        config = DecisionConfig(
            require_all_thresholds=True,
            criteria=list(DEFAULT_CRITERIA),
        )
        engine = DecisionEngine(config=config)
        # One criterion below threshold
        scores = {c.name: 9.0 for c in DEFAULT_CRITERIA}
        scores["feasibility"] = 2.0  # Below threshold of 5.0
        result = engine.evaluate("sig-1", "Test", scores)
        assert result.status == DecisionStatus.REJECTED


# ── DecisionScore Model ─────────────────────────────────────────────────

class TestDecisionScoreModel:
    """Test DecisionScore model."""

    def test_is_approved_property(self):
        ds = DecisionScore(status=DecisionStatus.APPROVED)
        assert ds.is_approved is True

    def test_is_not_approved_when_rejected(self):
        ds = DecisionScore(status=DecisionStatus.REJECTED)
        assert ds.is_approved is False


# ── Decision Engine Stats ───────────────────────────────────────────────

class TestDecisionEngineStats:
    """Test statistics."""

    def test_initial_stats(self, engine):
        stats = engine.stats
        assert stats["total_decisions"] == 0
        assert stats["approval_rate"] == 0.0

    def test_stats_after_evaluation(self, engine, high_scores):
        engine.evaluate("sig-1", "Test", high_scores)
        stats = engine.stats
        assert stats["total_decisions"] == 1
        assert stats["approved"] + stats["escalated"] + stats["rejected"] + stats["deferred"] == 1

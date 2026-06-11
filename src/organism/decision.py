"""
Decision Core - Multi-factor weighted scoring engine for problem selection.
Port of autonomous-organism/decision/index.js to Python with Pydantic v2.

Scoring Formula:
    score = (comments * 0.4) + (emotion * 0.2) + (automation * 0.2) + (money * 0.2)
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.organism.decision")


class ProblemScore(BaseModel):
    """Score breakdown for a problem."""
    comments: float = 0.0
    sentiment: float = 0.0
    automation: float = 0.0
    money: float = 0.0
    total: float = 0.0


class ScoredProblem(BaseModel):
    """A problem with its scoring breakdown."""
    text: str
    source: str = "unknown"
    comments: int = 0
    sentiment_label: str = "neutral"
    scores: ProblemScore = Field(default_factory=ProblemScore)


class DecisionCore:
    """Decision scoring engine for selecting best problems to solve.

    Uses a weighted multi-factor scoring formula:
    score = comment_score * 0.4 + sentiment_score * 0.2 +
            automation_score * 0.2 + money_score * 0.2
    """

    NEGATIVE_WORDS: set[str] = {
        "susah", "ribet", "gagal", "error", "bug", "mati", "rugi",
        "bikin cape", "mahal", "rumit", "hard", "difficult", "expensive",
        "broken", "fail", "crash", "slow", "annoying", "frustrating",
    }

    POSITIVE_WORDS: set[str] = {
        "mantap", "bagus", "senang", "suka", "easy", "simple",
        "great", "awesome", "excellent", "love", "perfect", "fast",
    }

    AUTO_FRIENDLY_WORDS: set[str] = {
        "auto", "otomatis", "system", "app", "tools", "software", "digital",
        "automation", "script", "bot", "api",
    }

    MANUAL_WORDS: set[str] = {
        "orang", "manual", "kerjain sendiri", "pake orang",
        "person", "hand", "physical",
    }

    HIGH_VALUE_WORDS: set[str] = {
        "jual", "beli", "uang", "modal", "bisnis", "jualan", "produk", "harga",
        "sell", "buy", "money", "capital", "business", "product", "price", "revenue",
    }

    LOW_VALUE_WORDS: set[str] = {
        "cari", "butuh", "mau", "free", "gratisan",
        "find", "need", "want", "cheap",
    }

    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text."""
        lower = text.lower()
        neg_count = sum(1 for w in self.NEGATIVE_WORDS if w in lower)
        pos_count = sum(1 for w in self.POSITIVE_WORDS if w in lower)

        if neg_count > pos_count:
            return "negative"
        elif pos_count > neg_count:
            return "positive"
        return "neutral"

    def estimate_automation(self, text: str) -> float:
        """Estimate ease of automation (0-1)."""
        lower = text.lower()
        score = 0.5
        for w in self.AUTO_FRIENDLY_WORDS:
            if w in lower:
                score += 0.15
        for w in self.MANUAL_WORDS:
            if w in lower:
                score -= 0.15
        return max(0.0, min(1.0, score))

    def estimate_money_potential(self, text: str) -> float:
        """Estimate money-making potential (0-1)."""
        lower = text.lower()
        score = 0.5
        for w in self.HIGH_VALUE_WORDS:
            if w in lower:
                score += 0.15
        for w in self.LOW_VALUE_WORDS:
            if w in lower:
                score -= 0.15
        return max(0.0, min(1.0, score))

    def calculate_score(self, problem: dict) -> ScoredProblem:
        """Calculate multi-factor score for a problem.

        Args:
            problem: Dict with keys: text, comments (or replies/reviews), source (optional)
        """
        text = problem.get("text", "")
        comments = problem.get("comments", problem.get("replies", problem.get("reviews", 10)))

        # Comment score: normalize to 0-1
        comment_score = min(comments / 200, 1.0) if isinstance(comments, (int, float)) else 0.5

        # Sentiment score: negative problems are more interesting
        sentiment = self.analyze_sentiment(text)
        sentiment_score = {"negative": 1.0, "neutral": 0.5, "positive": 0.2}.get(sentiment, 0.5)

        # Automation and money scores
        auto_score = self.estimate_automation(text)
        money_score = self.estimate_money_potential(text)

        total = (
            comment_score * 0.4
            + sentiment_score * 0.2
            + auto_score * 0.2
            + money_score * 0.2
        )

        return ScoredProblem(
            text=text,
            source=problem.get("source", "unknown"),
            comments=comments if isinstance(comments, int) else 0,
            sentiment_label=sentiment,
            scores=ProblemScore(
                comments=round(comment_score, 4),
                sentiment=round(sentiment_score, 4),
                automation=round(auto_score, 4),
                money=round(money_score, 4),
                total=round(total, 4),
            ),
        )

    def rank_problems(self, problems: list[dict]) -> list[ScoredProblem]:
        """Score and rank a list of problems by total score (descending).

        Args:
            problems: List of problem dicts with 'text' and optional 'comments'.

        Returns:
            List of ScoredProblem sorted by total score descending.
        """
        scored = [self.calculate_score(p) for p in problems]
        scored.sort(key=lambda x: x.scores.total, reverse=True)
        return scored

    def select_best(self, problems: list[dict]) -> Optional[ScoredProblem]:
        """Select the best problem from a list.

        Returns:
            The highest-scoring ScoredProblem, or None if empty.
        """
        if not problems:
            return None
        ranked = self.rank_problems(problems)
        return ranked[0]

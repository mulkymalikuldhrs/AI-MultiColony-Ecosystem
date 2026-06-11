"""
Sense Engine - Problem/opportunity sensing and data collection.
Port of autonomous-organism/sense/index.js to Python with Pydantic v2.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.organism.sense")


class SensedProblem(BaseModel):
    """A sensed problem/opportunity from data sources."""
    source: str
    text: str
    text_clean: str = ""
    comments: int = 0
    sentiment: str = "neutral"  # positive, negative, neutral
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class SenseEngine:
    """Collects and processes problems/opportunities from various sources.

    Supports text cleaning, deduplication, and basic sentiment analysis.
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

    def __init__(self) -> None:
        self.problems: list[SensedProblem] = []

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text for deduplication."""
        return (
            text.lower()
            .replace(re.compile(r"https?://\S+").sub("", text), "")
            .strip()
        )

    def _clean_text_simple(self, text: str) -> str:
        """Simple text cleaning without regex compilation."""
        cleaned = text.lower()
        cleaned = re.sub(r"https?://\S+", "", cleaned)
        cleaned = re.sub(r"@\w+", "", cleaned)
        cleaned = re.sub(r"[^\w\s]", "", cleaned)
        return cleaned.strip()

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

    def add_problems(self, problems: list[dict]) -> list[SensedProblem]:
        """Add a batch of sensed problems with cleaning and dedup.

        Args:
            problems: List of dicts with keys: source, text, comments (optional)

        Returns:
            List of newly added SensedProblem instances.
        """
        new_problems: list[SensedProblem] = []
        existing_clean = {p.text_clean for p in self.problems}

        for p in problems:
            text = p.get("text", "")
            text_clean = self._clean_text_simple(text)
            if not text_clean or text_clean in existing_clean:
                continue

            sentiment = self.analyze_sentiment(text)
            problem = SensedProblem(
                source=p.get("source", "unknown"),
                text=text,
                text_clean=text_clean,
                comments=p.get("comments", p.get("replies", p.get("reviews", 0))),
                sentiment=sentiment,
            )
            self.problems.append(problem)
            existing_clean.add(text_clean)
            new_problems.append(problem)

        logger.info("Sense: Added %d new problems (total: %d)", len(new_problems), len(self.problems))
        return new_problems

    def get_negative_problems(self, min_comments: int = 0) -> list[SensedProblem]:
        """Get problems with negative sentiment above comment threshold."""
        return [
            p for p in self.problems
            if p.sentiment == "negative" and p.comments >= min_comments
        ]

    def get_status(self) -> dict:
        """Get sense engine status."""
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for p in self.problems:
            sentiment_counts[p.sentiment] = sentiment_counts.get(p.sentiment, 0) + 1

        return {
            "total_problems": len(self.problems),
            "sentiment_distribution": sentiment_counts,
            "sources": list(set(p.source for p in self.problems)),
        }

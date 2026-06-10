"""
Research Memory — Stores and retrieves research findings.
From openhuman — persistent knowledge accumulation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ResearchItem(BaseModel):
    """A single research item."""

    id: str
    category: str  # macro, sector, company, crypto, forex
    title: str
    content: str
    source: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    tags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ResearchMemory:
    """
    Persistent research memory for knowledge accumulation.

    Features:
    - Category-based organization
    - Confidence scoring
    - Tag-based retrieval
    - Time-based decay
    """

    def __init__(self) -> None:
        self.items: dict[str, ResearchItem] = {}

    def add(self, item: ResearchItem) -> None:
        """Add a research item."""
        self.items[item.id] = item

    def get(self, item_id: str) -> ResearchItem | None:
        """Get a research item by ID."""
        return self.items.get(item_id)

    def search_by_category(self, category: str) -> list[ResearchItem]:
        """Search research items by category."""
        return [item for item in self.items.values() if item.category == category]

    def search_by_tag(self, tag: str) -> list[ResearchItem]:
        """Search research items by tag."""
        return [item for item in self.items.values() if tag in item.tags]

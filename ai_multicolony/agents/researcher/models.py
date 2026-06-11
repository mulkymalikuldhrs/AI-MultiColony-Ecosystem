"""Research models for the Researcher agent."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List


class ResearchDocument:
    """Represents a research document or search result."""

    def __init__(
        self,
        doc_id: str = "",
        title: str = "",
        source: str = "",
        content: str = "",
        url: str = "",
        relevance_score: float = 0.0,
    ):
        self.doc_id = doc_id or f"doc-{uuid.uuid4().hex[:8]}"
        self.title = title
        self.source = source
        self.content = content
        self.url = url
        self.relevance_score = relevance_score
        self.retrieved_at = datetime.now(timezone.utc)
        self.metadata: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "source": self.source,
            "url": self.url,
            "relevance_score": self.relevance_score,
            "content_length": len(self.content),
            "retrieved_at": self.retrieved_at.isoformat(),
        }


class ResearchReport:
    """Structured research report."""

    def __init__(self, report_id: str = "", topic: str = ""):
        self.report_id = report_id or f"rpt-{uuid.uuid4().hex[:8]}"
        self.topic = topic
        self.summary: str = ""
        self.findings: List[Dict[str, Any]] = []
        self.sources: List[Dict[str, Any]] = []
        self.recommendations: List[str] = []
        self.confidence: float = 0.0
        self.created_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "topic": self.topic,
            "summary": self.summary,
            "findings_count": len(self.findings),
            "sources_count": len(self.sources),
            "recommendations": self.recommendations,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }

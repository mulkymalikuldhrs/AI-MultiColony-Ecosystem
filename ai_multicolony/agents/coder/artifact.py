"""Code artifact model for the Coder agent."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List


class CodeArtifact:
    """Represents a generated or reviewed code artifact."""

    def __init__(
        self,
        artifact_id: str = "",
        language: str = "python",
        code: str = "",
        tests: str = "",
        file_path: str = "",
        review_status: str = "pending",
    ):
        self.artifact_id = artifact_id or f"art-{uuid.uuid4().hex[:8]}"
        self.language = language
        self.code = code
        self.tests = tests
        self.file_path = file_path
        self.review_status = review_status
        self.issues: List[Dict[str, Any]] = []
        self.security_findings: List[Dict[str, Any]] = []
        self.suggestions: List[str] = []
        self.created_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "language": self.language,
            "code": self.code[:8192],
            "tests": self.tests[:4096],
            "file_path": self.file_path,
            "review_status": self.review_status,
        }

"""Voice session model for the Voice agent."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List


class VoiceSession:
    """Tracks a single voice interaction session."""

    def __init__(self, session_id: str = "", language: str = "en-US"):
        self.session_id = session_id or f"vs-{uuid.uuid4().hex[:8]}"
        self.language = language
        self.transcriptions: List[Dict[str, Any]] = []
        self.syntheses: List[Dict[str, Any]] = []
        self.created_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "language": self.language,
            "transcription_count": len(self.transcriptions),
            "synthesis_count": len(self.syntheses),
            "created_at": self.created_at.isoformat(),
        }

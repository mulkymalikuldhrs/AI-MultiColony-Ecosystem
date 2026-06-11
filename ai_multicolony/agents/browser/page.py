"""Browser page model for the Browser agent."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional


class BrowserPage:
    """Represents a browser page with its state."""

    def __init__(self, url: str = "about:blank", title: str = ""):
        self.url = url
        self.title = title
        self.status_code: int = 200
        self.content: str = ""
        self.screenshot: Optional[bytes] = None
        self.loaded_at: datetime = datetime.utcnow()
        self.cookies: List[Dict[str, Any]] = []
        self.headers: Dict[str, str] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "status_code": self.status_code,
            "content_length": len(self.content),
            "has_screenshot": self.screenshot is not None,
            "loaded_at": self.loaded_at.isoformat(),
            "cookie_count": len(self.cookies),
        }

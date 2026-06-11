"""
Persistence Engine - Deer-flow style persistence layer.
Provides thread metadata management and data storage abstractions.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger("ecosystem.backend.persistence")


class ThreadMeta(BaseModel):
    """Metadata for a conversation thread."""
    thread_id: str
    title: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    message_count: int = 0
    user_id: str | None = None
    metadata: dict = Field(default_factory=dict)


class PersistenceEngine:
    """Simple JSON-file-based persistence engine.

    Inspired by deer-flow's persistence layer with:
    - Thread metadata management
    - JSON file storage
    - CRUD operations for thread data
    """

    def __init__(self, data_dir: str | Path | None = None) -> None:
        self.data_dir = Path(data_dir) if data_dir else Path.cwd() / "data"
        self._threads: dict[str, ThreadMeta] = {}

    def _ensure_dir(self) -> None:
        """Ensure data directory exists."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def create_thread(self, thread_id: str, title: str = "", user_id: str | None = None) -> ThreadMeta:
        """Create a new thread with metadata."""
        thread = ThreadMeta(
            thread_id=thread_id,
            title=title,
            user_id=user_id,
        )
        self._threads[thread_id] = thread
        logger.info("Created thread: %s", thread_id)
        return thread

    def get_thread(self, thread_id: str) -> Optional[ThreadMeta]:
        """Get thread metadata."""
        return self._threads.get(thread_id)

    def update_thread(self, thread_id: str, **kwargs) -> Optional[ThreadMeta]:
        """Update thread metadata fields."""
        thread = self._threads.get(thread_id)
        if not thread:
            return None

        for key, value in kwargs.items():
            if hasattr(thread, key):
                setattr(thread, key, value)
        thread.updated_at = datetime.now().isoformat()
        return thread

    def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread."""
        if thread_id in self._threads:
            del self._threads[thread_id]
            return True
        return False

    def list_threads(self, user_id: str | None = None) -> list[ThreadMeta]:
        """List threads, optionally filtered by user."""
        threads = list(self._threads.values())
        if user_id:
            threads = [t for t in threads if t.user_id == user_id]
        return sorted(threads, key=lambda t: t.updated_at, reverse=True)

    def save_to_disk(self) -> None:
        """Persist all thread metadata to disk."""
        self._ensure_dir()
        data = {tid: t.model_dump() for tid, t in self._threads.items()}
        path = self.data_dir / "threads.json"
        path.write_text(json.dumps(data, indent=2))
        logger.info("Saved %d threads to disk", len(self._threads))

    def load_from_disk(self) -> None:
        """Load thread metadata from disk."""
        path = self.data_dir / "threads.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                self._threads = {
                    tid: ThreadMeta(**meta) for tid, meta in data.items()
                }
                logger.info("Loaded %d threads from disk", len(self._threads))
            except (json.JSONDecodeError, Exception) as e:
                logger.error("Failed to load threads: %s", e)
                self._threads = {}

    def get_status(self) -> dict:
        """Get persistence engine status."""
        return {
            "data_dir": str(self.data_dir),
            "thread_count": len(self._threads),
            "disk_path": str(self.data_dir / "threads.json"),
        }

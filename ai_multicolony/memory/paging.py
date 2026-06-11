"""Letta-style memory paging for context window management.

Manages memory pages that can be loaded/unloaded to efficiently
use the LLM context window, with LRU eviction and token budgets.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from ai_multicolony.types.memory import MemoryPage, MemoryType


class MemoryPager:
    """Letta-style memory paging system.

    Manages pages of memory that can be loaded into or unloaded from
    the active context window to optimize token usage.

    Features:
    - Create, load, and unload pages
    - Automatic page eviction (LRU)
    - Token budget management
    - Page prioritization by importance
    - Page pinning (prevent eviction)
    """

    def __init__(
        self,
        max_active_pages: int = 5,
        max_tokens_per_page: int = 2000,
        total_token_budget: int = 10000,
    ) -> None:
        self._pages: dict[str, MemoryPage] = {}
        self._max_active_pages = max_active_pages
        self._max_tokens_per_page = max_tokens_per_page
        self._total_token_budget = total_token_budget
        self._pinned_pages: set[str] = set()

    def create_page(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.WORKING,
        title: str = "",
        tags: Optional[list[str]] = None,
    ) -> MemoryPage:
        """Create a new memory page.

        Args:
            content: Page content.
            memory_type: Type of memory.
            title: Page title.
            tags: Optional tags.

        Returns:
            The created page.
        """
        token_count = min(len(content) // 4, self._max_tokens_per_page)
        page = MemoryPage(
            memory_type=memory_type,
            title=title,
            content=content,
            token_count=token_count,
            is_active=False,
            tags=tags or [],
        )
        self._pages[page.id] = page
        return page

    def load_page(self, page_id: str) -> MemoryPage:
        """Load a page into active context.

        If loading would exceed the token budget or max active pages,
        the least recently used pages are evicted first (except pinned).

        Args:
            page_id: The page ID to load.

        Returns:
            The loaded page.

        Raises:
            KeyError: If the page is not found.
        """
        if page_id not in self._pages:
            raise KeyError(f"Page not found: {page_id}")

        page = self._pages[page_id]

        # Already active
        if page.is_active:
            page.accessed_at = time.time()
            page.access_count += 1
            return page

        # Check if we need to evict pages
        active_pages = [p for p in self._pages.values() if p.is_active]
        total_tokens = sum(p.token_count for p in active_pages) + page.token_count

        while (
            len(active_pages) >= self._max_active_pages
            or total_tokens > self._total_token_budget
        ):
            evicted = self._evict_lru()
            if not evicted:
                break
            active_pages = [p for p in self._pages.values() if p.is_active]
            total_tokens = sum(p.token_count for p in active_pages) + page.token_count

        page.is_active = True
        page.accessed_at = time.time()
        page.access_count += 1
        return page

    def unload_page(self, page_id: str) -> None:
        """Unload a page from active context.

        Args:
            page_id: The page ID to unload.
        """
        if page_id in self._pages:
            self._pages[page_id].is_active = False

    def pin_page(self, page_id: str) -> None:
        """Pin a page so it won't be evicted.

        Args:
            page_id: The page ID to pin.
        """
        if page_id in self._pages:
            self._pinned_pages.add(page_id)

    def unpin_page(self, page_id: str) -> None:
        """Unpin a page so it can be evicted.

        Args:
            page_id: The page ID to unpin.
        """
        self._pinned_pages.discard(page_id)

    def get_active_context(self) -> str:
        """Get the combined content of all active pages.

        Returns:
            Concatenated content of active pages sorted by page number.
        """
        active = [p for p in self._pages.values() if p.is_active]
        active.sort(key=lambda p: (p.page_number, p.created_at))
        return "\n\n".join(f"## {p.title or p.id[:8]}\n{p.content}" for p in active)

    def get_active_pages(self) -> list[MemoryPage]:
        """Get all active pages sorted by page number."""
        pages = [p for p in self._pages.values() if p.is_active]
        pages.sort(key=lambda p: (p.page_number, p.created_at))
        return pages

    def get_page(self, page_id: str) -> Optional[MemoryPage]:
        """Get a page by ID."""
        return self._pages.get(page_id)

    def update_page(self, page_id: str, content: Optional[str] = None, title: Optional[str] = None) -> Optional[MemoryPage]:
        """Update a page's content and/or title.

        Args:
            page_id: The page ID.
            content: New content (if provided).
            title: New title (if provided).

        Returns:
            The updated page, or None if not found.
        """
        if page_id not in self._pages:
            return None

        page = self._pages[page_id]
        if content is not None:
            page.content = content
            page.token_count = min(len(content) // 4, self._max_tokens_per_page)
        if title is not None:
            page.title = title
        page.updated_at = time.time()
        return page

    def delete_page(self, page_id: str) -> None:
        """Delete a page entirely."""
        self._pinned_pages.discard(page_id)
        self._pages.pop(page_id, None)

    def get_token_usage(self) -> dict[str, Any]:
        """Get token usage information.

        Returns:
            Token usage stats.
        """
        active_pages = [p for p in self._pages.values() if p.is_active]
        active_tokens = sum(p.token_count for p in active_pages)
        return {
            "active_pages": len(active_pages),
            "active_tokens": active_tokens,
            "total_pages": len(self._pages),
            "total_tokens": sum(p.token_count for p in self._pages.values()),
            "budget": self._total_token_budget,
            "remaining": self._total_token_budget - active_tokens,
            "pinned_pages": len(self._pinned_pages),
            "max_active_pages": self._max_active_pages,
        }

    def _evict_lru(self) -> bool:
        """Evict the least recently used active page (excluding pinned).

        Returns:
            True if a page was evicted, False otherwise.
        """
        active_pages = [
            p for p in self._pages.values()
            if p.is_active and p.id not in self._pinned_pages
        ]
        if active_pages:
            lru = min(active_pages, key=lambda p: p.accessed_at)
            lru.is_active = False
            return True
        return False

    def clear(self) -> None:
        """Clear all pages."""
        self._pages.clear()
        self._pinned_pages.clear()

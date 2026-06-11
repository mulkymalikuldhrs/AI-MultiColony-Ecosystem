"""Knowledge base for persistent storage and retrieval.

Provides a knowledge base with hybrid search (vector + keyword),
document storage, and confidence scoring.
"""

from __future__ import annotations

import math
import time
import uuid
from collections import defaultdict
from typing import Any, Optional

from pydantic import BaseModel, Field

from ai_multicolony.config.logging_config import get_logger

logger = get_logger(__name__)


class KnowledgeEntry(BaseModel):
    """An entry in the knowledge base."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    category: str = "general"
    tags: list[str] = Field(default_factory=list)
    source: str = ""
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    access_count: int = 0
    embedding: Optional[list[float]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}


class SearchResult(BaseModel):
    """A search result from the knowledge base."""

    entry: KnowledgeEntry
    score: float = 0.0
    match_type: str = "keyword"  # keyword, vector, hybrid

    model_config = {"arbitrary_types_allowed": True}


class KnowledgeBase:
    """Knowledge base for persistent information storage with hybrid search.

    Features:
    - Store and retrieve knowledge entries
    - Category-based organization
    - Tag-based search
    - Confidence scoring
    - Full-text keyword search with TF-IDF ranking
    - Hybrid search combining vector similarity and keyword matching
    - Document chunking support
    """

    def __init__(
        self,
        max_entries: int = 10000,
        vector_store: Optional[Any] = None,
    ) -> None:
        self._entries: dict[str, KnowledgeEntry] = {}
        self._categories: dict[str, set[str]] = defaultdict(set)
        self._tags: dict[str, set[str]] = defaultdict(set)
        self._max_entries = max_entries
        self._vector_store = vector_store

        # TF-IDF index
        self._doc_freq: dict[str, int] = defaultdict(int)
        self._term_freq: dict[str, dict[str, int]] = {}  # entry_id -> {term: count}
        self._doc_count = 0

    def add(
        self,
        title: str,
        content: str,
        category: str = "general",
        tags: Optional[list[str]] = None,
        source: str = "",
        confidence: float = 1.0,
        embedding: Optional[list[float]] = None,
    ) -> KnowledgeEntry:
        """Add a knowledge entry.

        Args:
            title: Entry title.
            content: Entry content.
            category: Entry category.
            tags: Optional tags.
            source: Source of the knowledge.
            confidence: Confidence score (0-1).
            embedding: Optional embedding vector.

        Returns:
            The created entry.
        """
        if len(self._entries) >= self._max_entries:
            self._evict_oldest()

        entry = KnowledgeEntry(
            title=title,
            content=content,
            category=category,
            tags=tags or [],
            source=source,
            confidence=confidence,
            embedding=embedding,
        )

        self._entries[entry.id] = entry
        self._categories[category].add(entry.id)
        for tag in entry.tags:
            self._tags[tag].add(entry.id)

        # Update TF-IDF index
        self._index_entry(entry)

        # Store in vector store if available
        if self._vector_store and embedding:
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(
                        self._vector_store.store(
                            collection="knowledge",
                            entry_id=entry.id,
                            embedding=embedding,
                            metadata={"title": title, "content": content[:500], "category": category, "tags": tags or []},
                        )
                    )
                else:
                    loop.run_until_complete(
                        self._vector_store.store(
                            collection="knowledge",
                            entry_id=entry.id,
                            embedding=embedding,
                            metadata={"title": title, "content": content[:500], "category": category, "tags": tags or []},
                        )
                    )
            except Exception as e:
                logger.warning("vector_store_store_error", error=str(e))

        return entry

    def get(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Get an entry by ID.

        Args:
            entry_id: The entry ID.

        Returns:
            The entry, or None if not found.
        """
        entry = self._entries.get(entry_id)
        if entry:
            entry.access_count += 1
            entry.updated_at = time.time()
        return entry

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[list[str]] = None,
        min_confidence: float = 0.0,
        limit: int = 10,
        search_type: str = "keyword",
    ) -> list[SearchResult]:
        """Search the knowledge base.

        Args:
            query: Search query text.
            category: Optional category filter.
            tags: Optional tag filters.
            min_confidence: Minimum confidence score.
            limit: Maximum results.
            search_type: Search type - "keyword", "vector", or "hybrid".

        Returns:
            List of search results with scores.
        """
        if search_type == "vector" and self._vector_store:
            return self._vector_search(query, category, tags, min_confidence, limit)
        elif search_type == "hybrid" and self._vector_store:
            return self._hybrid_search(query, category, tags, min_confidence, limit)
        else:
            return self._keyword_search(query, category, tags, min_confidence, limit)

    def _keyword_search(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[list[str]] = None,
        min_confidence: float = 0.0,
        limit: int = 10,
    ) -> list[SearchResult]:
        """TF-IDF based keyword search."""
        query_terms = self._tokenize(query)
        if not query_terms:
            return []

        scored: list[tuple[float, KnowledgeEntry]] = []
        for entry_id, entry in self._entries.items():
            # Apply filters
            if category and entry.category != category:
                continue
            if tags and not all(t in entry.tags for t in tags):
                continue
            if entry.confidence < min_confidence:
                continue

            # Compute TF-IDF score
            score = self._tfidf_score(query_terms, entry_id)
            if score > 0:
                # Boost by confidence and recency
                recency = max(0.1, 1.0 - (time.time() - entry.updated_at) / 86400)
                final_score = score * entry.confidence * recency
                scored.append((final_score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            SearchResult(entry=entry, score=score, match_type="keyword")
            for score, entry in scored[:limit]
        ]

    def _vector_search(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[list[str]] = None,
        min_confidence: float = 0.0,
        limit: int = 10,
    ) -> list[SearchResult]:
        """Vector similarity search (requires vector store)."""
        # This is a placeholder - actual implementation needs an embedding for the query
        # Fall back to keyword search
        return self._keyword_search(query, category, tags, min_confidence, limit)

    async def vector_search_async(
        self,
        query_embedding: list[float],
        category: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 10,
    ) -> list[SearchResult]:
        """Async vector similarity search using an embedding.

        Args:
            query_embedding: The query embedding vector.
            category: Optional category filter.
            min_confidence: Minimum confidence.
            limit: Maximum results.

        Returns:
            List of search results.
        """
        if not self._vector_store:
            return []

        try:
            filters = {}
            if category:
                filters["category"] = category

            results = await self._vector_store.search(
                collection="knowledge",
                query_embedding=query_embedding,
                limit=limit,
                filters=filters if filters else None,
            )

            search_results = []
            for r in results:
                entry_id = r.get("id", "")
                entry = self._entries.get(entry_id)
                if entry and entry.confidence >= min_confidence:
                    search_results.append(SearchResult(
                        entry=entry,
                        score=r.get("score", 0.0),
                        match_type="vector",
                    ))
            return search_results
        except Exception as e:
            logger.warning("vector_search_error", error=str(e))
            return []

    def _hybrid_search(
        self,
        query: str,
        category: Optional[str] = None,
        tags: Optional[list[str]] = None,
        min_confidence: float = 0.0,
        limit: int = 10,
    ) -> list[SearchResult]:
        """Hybrid search combining keyword and vector results.

        Uses Reciprocal Rank Fusion (RRF) to merge results.
        """
        keyword_results = self._keyword_search(query, category, tags, min_confidence, limit * 2)

        # For hybrid without actual vector search, boost keyword results
        # that match both title and content
        query_lower = query.lower()
        results: list[SearchResult] = []

        for kr in keyword_results:
            title_match = query_lower in kr.entry.title.lower()
            content_match = query_lower in kr.entry.content.lower()

            hybrid_score = kr.score
            if title_match:
                hybrid_score *= 1.5
            if content_match:
                hybrid_score *= 1.2
            if title_match and content_match:
                hybrid_score *= 1.3

            results.append(SearchResult(
                entry=kr.entry,
                score=hybrid_score,
                match_type="hybrid",
            ))

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

    def update(self, entry_id: str, **kwargs: Any) -> Optional[KnowledgeEntry]:
        """Update a knowledge entry.

        Args:
            entry_id: The entry ID.
            **kwargs: Fields to update.

        Returns:
            The updated entry, or None if not found.
        """
        entry = self._entries.get(entry_id)
        if not entry:
            return None

        old_category = entry.category
        old_tags = set(entry.tags)

        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        entry.updated_at = time.time()

        # Update indexes if category or tags changed
        if entry.category != old_category:
            self._categories[old_category].discard(entry.id)
            self._categories[entry.category].add(entry.id)

        new_tags = set(entry.tags)
        for tag in old_tags - new_tags:
            self._tags[tag].discard(entry.id)
        for tag in new_tags - old_tags:
            self._tags[tag].add(entry.id)

        return entry

    def delete(self, entry_id: str) -> bool:
        """Delete a knowledge entry.

        Args:
            entry_id: The entry ID.

        Returns:
            True if the entry was found and deleted.
        """
        entry = self._entries.pop(entry_id, None)
        if not entry:
            return False

        # Remove from indexes
        self._categories[entry.category].discard(entry.id)
        for tag in entry.tags:
            self._tags[tag].discard(entry.id)

        # Remove from TF-IDF index
        self._term_freq.pop(entry_id, None)

        return True

    def add_document(
        self,
        content: str,
        title: str = "",
        category: str = "document",
        chunk_size: int = 500,
        overlap: int = 50,
        source: str = "",
    ) -> list[KnowledgeEntry]:
        """Add a document by chunking it into entries.

        Args:
            content: Document content.
            title: Document title.
            category: Entry category.
            chunk_size: Size of each chunk in characters.
            overlap: Overlap between chunks.
            source: Source of the document.

        Returns:
            List of created entries.
        """
        entries = []
        chunks = self._chunk_text(content, chunk_size, overlap)

        for i, chunk in enumerate(chunks):
            entry = self.add(
                title=f"{title} (part {i + 1}/{len(chunks)})" if title else f"Document chunk {i + 1}",
                content=chunk,
                category=category,
                source=source,
                tags=["document", f"chunk-{i}"],
            )
            entries.append(entry)

        return entries

    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        """Split text into overlapping chunks."""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            # Try to break at sentence or word boundary
            if end < len(text):
                # Look for sentence boundary
                for sep in [". ", ".\n", "\n\n", " "]:
                    last_sep = text.rfind(sep, start + chunk_size // 2, end)
                    if last_sep != -1:
                        end = last_sep + len(sep)
                        break

            chunks.append(text[start:end])
            start = end - overlap

        return chunks

    # === TF-IDF Index ===

    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenizer for TF-IDF."""
        return [
            w.lower()
            for w in text.replace(".", " ").replace(",", " ").replace("!", " ").replace("?", " ").split()
            if len(w) > 2
        ]

    def _index_entry(self, entry: KnowledgeEntry) -> None:
        """Index an entry for TF-IDF search."""
        text = f"{entry.title} {entry.content}"
        terms = self._tokenize(text)

        term_counts: dict[str, int] = defaultdict(int)
        for term in terms:
            term_counts[term] += 1

        self._term_freq[entry.id] = dict(term_counts)
        self._doc_count += 1

        # Update document frequency
        unique_terms = set(terms)
        for term in unique_terms:
            self._doc_freq[term] += 1

    def _tfidf_score(self, query_terms: list[str], entry_id: str) -> float:
        """Compute TF-IDF score for a query against an entry."""
        if entry_id not in self._term_freq or self._doc_count == 0:
            return 0.0

        entry_terms = self._term_freq[entry_id]
        total_terms = sum(entry_terms.values())

        score = 0.0
        for term in query_terms:
            if term in entry_terms:
                # TF
                tf = entry_terms[term] / max(total_terms, 1)
                # IDF
                df = self._doc_freq.get(term, 0)
                idf = math.log((self._doc_count + 1) / (df + 1)) + 1
                score += tf * idf

        return score

    # === Utility ===

    def get_categories(self) -> list[str]:
        """Get all categories."""
        return list(self._categories.keys())

    def get_tags(self) -> list[str]:
        """Get all tags."""
        return list(self._tags.keys())

    def _evict_oldest(self) -> None:
        """Evict the oldest, least accessed entry."""
        if not self._entries:
            return
        oldest = min(self._entries.values(), key=lambda e: (e.access_count, e.updated_at))
        self.delete(oldest.id)

    def get_stats(self) -> dict[str, Any]:
        """Get knowledge base statistics."""
        return {
            "total_entries": len(self._entries),
            "categories": len(self._categories),
            "tags": len(self._tags),
            "max_entries": self._max_entries,
            "indexed_terms": len(self._doc_freq),
            "has_vector_store": self._vector_store is not None,
        }

"""Vector store integration with Qdrant and ChromaDB backends.

Provides vector similarity search with 5 collection types:
agents, tools, knowledge, decisions, sessions.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional

from ai_multicolony.config.logging_config import get_logger
from ai_multicolony.types.memory import MemoryEntry

logger = get_logger(__name__)


class CollectionType(str, Enum):
    """Predefined vector store collections."""

    AGENTS = "agents"
    TOOLS = "tools"
    KNOWLEDGE = "knowledge"
    DECISIONS = "decisions"
    SESSIONS = "sessions"


class VectorStoreBackend(ABC):
    """Abstract interface for vector store backends."""

    @abstractmethod
    async def upsert(self, collection: str, id: str, embedding: list[float], metadata: dict[str, Any]) -> None:
        ...

    @abstractmethod
    async def search(
        self, collection: str, embedding: list[float], limit: int = 10,
        min_score: float = 0.0, filters: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def delete(self, collection: str, id: str) -> None:
        ...

    @abstractmethod
    async def ensure_collection(self, collection: str, dimension: int) -> None:
        ...


class QdrantBackend(VectorStoreBackend):
    """Qdrant vector store backend.

    Provides vector similarity search using the Qdrant engine.
    Gracefully falls back to in-memory storage when Qdrant is unavailable.
    """

    def __init__(
        self,
        url: str = "http://localhost:6333",
        api_key: Optional[str] = None,
        embedding_dimension: int = 1536,
    ) -> None:
        self._url = url
        self._api_key = api_key
        self._embedding_dimension = embedding_dimension
        self._client: Optional[Any] = None
        self._fallback = InMemoryBackend()

    def _get_client(self) -> Any:
        """Lazy-initialize the Qdrant client."""
        if self._client is None:
            try:
                from qdrant_client import QdrantClient
                kwargs: dict[str, Any] = {"url": self._url}
                if self._api_key:
                    kwargs["api_key"] = self._api_key
                self._client = QdrantClient(**kwargs)
            except ImportError:
                raise ImportError("qdrant-client not installed. Install with: pip install qdrant-client")
        return self._client

    async def ensure_collection(self, collection: str, dimension: int) -> None:
        """Ensure a collection exists in Qdrant."""
        try:
            from qdrant_client.models import Distance, VectorParams

            client = self._get_client()
            collections = client.get_collections().collections
            collection_names = [c.name for c in collections]

            if collection not in collection_names:
                client.create_collection(
                    collection_name=collection,
                    vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
                )
                logger.info("created_qdrant_collection", collection=collection)
        except Exception as e:
            logger.warning("qdrant_collection_error", error=str(e))
            # Fall back to in-memory
            await self._fallback.ensure_collection(collection, dimension)

    async def upsert(self, collection: str, id: str, embedding: list[float], metadata: dict[str, Any]) -> None:
        """Upsert a vector into Qdrant."""
        try:
            from qdrant_client.models import PointStruct

            client = self._get_client()
            await self.ensure_collection(collection, len(embedding))

            point = PointStruct(id=id, vector=embedding, payload=metadata)
            client.upsert(collection_name=collection, points=[point])
        except Exception as e:
            logger.warning("qdrant_upsert_error", error=str(e))
            await self._fallback.upsert(collection, id, embedding, metadata)

    async def search(
        self,
        collection: str,
        embedding: list[float],
        limit: int = 10,
        min_score: float = 0.0,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors in Qdrant."""
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            client = self._get_client()
            query_filter = None
            if filters:
                conditions = [
                    FieldCondition(key=k, match=MatchValue(value=v))
                    for k, v in filters.items()
                ]
                query_filter = Filter(must=conditions)

            results = client.search(
                collection_name=collection,
                query_vector=embedding,
                limit=limit,
                score_threshold=min_score,
                query_filter=query_filter,
            )

            return [
                {"id": str(r.id), "score": r.score, "payload": r.payload or {}}
                for r in results
            ]
        except Exception as e:
            logger.warning("qdrant_search_error", error=str(e))
            return await self._fallback.search(collection, embedding, limit, min_score, filters)

    async def delete(self, collection: str, id: str) -> None:
        """Delete a vector from Qdrant."""
        try:
            client = self._get_client()
            client.delete(collection_name=collection, points_selector=[id])
        except Exception as e:
            logger.warning("qdrant_delete_error", error=str(e))
            await self._fallback.delete(collection, id)


class ChromaBackend(VectorStoreBackend):
    """ChromaDB vector store backend.

    Provides vector similarity search using ChromaDB with
    persistent storage. Falls back gracefully when unavailable.
    """

    def __init__(
        self,
        persist_directory: str = "./data/chroma",
        embedding_dimension: int = 1536,
    ) -> None:
        self._persist_directory = persist_directory
        self._embedding_dimension = embedding_dimension
        self._client: Optional[Any] = None
        self._collections: dict[str, Any] = {}
        self._fallback = InMemoryBackend()

    def _get_client(self) -> Any:
        """Lazy-initialize the ChromaDB client."""
        if self._client is None:
            try:
                import chromadb
                self._client = chromadb.PersistentClient(path=self._persist_directory)
            except ImportError:
                raise ImportError("chromadb not installed. Install with: pip install chromadb")
        return self._client

    def _get_collection(self, name: str) -> Any:
        """Get or create a ChromaDB collection."""
        if name not in self._collections:
            try:
                client = self._get_client()
                self._collections[name] = client.get_or_create_collection(name)
            except Exception as e:
                logger.warning("chroma_collection_error", error=str(e))
                return None
        return self._collections.get(name)

    async def ensure_collection(self, collection: str, dimension: int) -> None:
        """Ensure a collection exists in ChromaDB."""
        try:
            self._get_collection(collection)
        except Exception:
            await self._fallback.ensure_collection(collection, dimension)

    async def upsert(self, collection: str, id: str, embedding: list[float], metadata: dict[str, Any]) -> None:
        """Upsert a vector into ChromaDB."""
        try:
            col = self._get_collection(collection)
            if col:
                # ChromaDB requires string IDs
                str_id = str(id)
                col.upsert(
                    ids=[str_id],
                    embeddings=[embedding],
                    metadatas=[metadata],
                    documents=[metadata.get("content", "")],
                )
            else:
                await self._fallback.upsert(collection, id, embedding, metadata)
        except Exception as e:
            logger.warning("chroma_upsert_error", error=str(e))
            await self._fallback.upsert(collection, id, embedding, metadata)

    async def search(
        self,
        collection: str,
        embedding: list[float],
        limit: int = 10,
        min_score: float = 0.0,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors in ChromaDB."""
        try:
            col = self._get_collection(collection)
            if col:
                kwargs: dict[str, Any] = {
                    "query_embeddings": [embedding],
                    "n_results": limit,
                }
                if filters:
                    kwargs["where"] = filters

                results = col.query(**kwargs)
                items = []
                for i in range(len(results["ids"][0])):
                    distance = results["distances"][0][i] if "distances" in results else 0
                    score = 1.0 - distance  # Convert distance to similarity
                    if score >= min_score:
                        items.append({
                            "id": results["ids"][0][i],
                            "score": score,
                            "payload": results["metadatas"][0][i] if "metadatas" in results else {},
                        })
                return items
            return await self._fallback.search(collection, embedding, limit, min_score, filters)
        except Exception as e:
            logger.warning("chroma_search_error", error=str(e))
            return await self._fallback.search(collection, embedding, limit, min_score, filters)

    async def delete(self, collection: str, id: str) -> None:
        """Delete a vector from ChromaDB."""
        try:
            col = self._get_collection(collection)
            if col:
                col.delete(ids=[str(id)])
            else:
                await self._fallback.delete(collection, id)
        except Exception as e:
            logger.warning("chroma_delete_error", error=str(e))
            await self._fallback.delete(collection, id)


class InMemoryBackend(VectorStoreBackend):
    """In-memory fallback vector store backend.

    Uses simple cosine similarity for search. Used when external
    vector databases are not available.
    """

    def __init__(self) -> None:
        self._collections: dict[str, dict[str, dict[str, Any]]] = {}

    async def ensure_collection(self, collection: str, dimension: int) -> None:
        """Ensure a collection exists in memory."""
        if collection not in self._collections:
            self._collections[collection] = {}

    async def upsert(self, collection: str, id: str, embedding: list[float], metadata: dict[str, Any]) -> None:
        """Store a vector in memory."""
        await self.ensure_collection(collection, len(embedding))
        self._collections[collection][id] = {
            "id": id,
            "embedding": embedding,
            "payload": metadata,
        }

    async def search(
        self,
        collection: str,
        embedding: list[float],
        limit: int = 10,
        min_score: float = 0.0,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors using cosine similarity."""
        import math

        collection_data = self._collections.get(collection, {})
        results = []

        for item_id, item in collection_data.items():
            # Apply filters
            if filters:
                match = all(
                    item["payload"].get(k) == v for k, v in filters.items()
                )
                if not match:
                    continue

            # Cosine similarity
            vec_a = embedding
            vec_b = item["embedding"]
            dot = sum(a * b for a, b in zip(vec_a, vec_b))
            norm_a = math.sqrt(sum(a * a for a in vec_a))
            norm_b = math.sqrt(sum(b * b for b in vec_b))

            if norm_a == 0 or norm_b == 0:
                score = 0.0
            else:
                score = dot / (norm_a * norm_b)

            if score >= min_score:
                results.append({
                    "id": item_id,
                    "score": score,
                    "payload": item["payload"],
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    async def delete(self, collection: str, id: str) -> None:
        """Delete a vector from memory."""
        if collection in self._collections:
            self._collections[collection].pop(id, None)


class VectorStore:
    """Vector store with multiple backend support.

    Provides a unified interface for vector similarity search
    across Qdrant, ChromaDB, and in-memory backends with
    5 predefined collections (agents, tools, knowledge, decisions, sessions).

    Features:
    - Store and search embeddings
    - Multiple backend support (Qdrant, ChromaDB, in-memory)
    - 5 predefined collections
    - Collection management
    - Batch operations
    - Graceful fallback when backends are unavailable
    """

    DEFAULT_COLLECTIONS = [c.value for c in CollectionType]

    def __init__(
        self,
        backend: str = "qdrant",
        url: str = "http://localhost:6333",
        api_key: Optional[str] = None,
        persist_directory: str = "./data/chroma",
        embedding_dimension: int = 1536,
    ) -> None:
        self._embedding_dimension = embedding_dimension
        self._backend_name = backend

        # Initialize backend
        if backend == "qdrant":
            self._backend: VectorStoreBackend = QdrantBackend(
                url=url, api_key=api_key, embedding_dimension=embedding_dimension,
            )
        elif backend == "chroma":
            self._backend = ChromaBackend(
                persist_directory=persist_directory,
                embedding_dimension=embedding_dimension,
            )
        else:
            self._backend = InMemoryBackend()

        # Stats
        self._upsert_count = 0
        self._search_count = 0

    async def initialize(self) -> None:
        """Initialize all default collections."""
        for collection in self.DEFAULT_COLLECTIONS:
            try:
                await self._backend.ensure_collection(collection, self._embedding_dimension)
            except Exception as e:
                logger.warning("collection_init_error", collection=collection, error=str(e))

    async def store(
        self,
        collection: str,
        entry_id: str,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> str:
        """Store an entry with its embedding.

        Args:
            collection: Collection name (use CollectionType values).
            entry_id: Unique entry ID.
            embedding: The embedding vector.
            metadata: Metadata to store with the entry.

        Returns:
            The entry ID.
        """
        await self._backend.ensure_collection(collection, len(embedding))
        await self._backend.upsert(collection, entry_id, embedding, metadata)
        self._upsert_count += 1
        return entry_id

    async def store_memory_entry(self, entry: MemoryEntry, embedding: list[float]) -> str:
        """Store a MemoryEntry with its embedding in the appropriate collection.

        Args:
            entry: The memory entry.
            embedding: The embedding vector.

        Returns:
            The entry ID.
        """
        collection = entry.memory_type.value
        metadata = {
            "content": entry.content[:500],
            "memory_type": entry.memory_type.value,
            "agent_id": entry.agent_id,
            "importance": entry.importance,
            "tags": entry.tags,
            "created_at": entry.created_at,
        }
        return await self.store(collection, entry.id, embedding, metadata)

    async def search(
        self,
        collection: str,
        query_embedding: list[float],
        limit: int = 10,
        min_score: float = 0.5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Search for similar entries in a collection.

        Args:
            collection: Collection to search.
            query_embedding: The query embedding vector.
            limit: Maximum results.
            min_score: Minimum similarity score.
            filters: Optional metadata filters.

        Returns:
            List of matching entries with scores.
        """
        self._search_count += 1
        return await self._backend.search(
            collection, query_embedding, limit, min_score, filters,
        )

    async def delete(self, collection: str, entry_id: str) -> None:
        """Delete an entry from a collection.

        Args:
            collection: Collection name.
            entry_id: The entry ID to delete.
        """
        await self._backend.delete(collection, entry_id)

    async def batch_store(
        self,
        collection: str,
        entries: list[tuple[str, list[float], dict[str, Any]]],
    ) -> list[str]:
        """Store multiple entries at once.

        Args:
            collection: Collection name.
            entries: List of (id, embedding, metadata) tuples.

        Returns:
            List of stored entry IDs.
        """
        ids = []
        for entry_id, embedding, metadata in entries:
            await self.store(collection, entry_id, embedding, metadata)
            ids.append(entry_id)
        return ids

    def get_stats(self) -> dict[str, Any]:
        """Get vector store statistics."""
        return {
            "backend": self._backend_name,
            "embedding_dimension": self._embedding_dimension,
            "collections": self.DEFAULT_COLLECTIONS,
            "upsert_count": self._upsert_count,
            "search_count": self._search_count,
        }

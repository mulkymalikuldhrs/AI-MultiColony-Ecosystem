"""Memory module with condensers, vector store, paging, sessions, and knowledge base."""

from ai_multicolony.memory.condenser import (
    BaseCondenser,
    NoOpCondenser,
    RecentEventsCondenser,
    RecentCondenser,
    ObservationCondenser,
    LLMCondenser,
    AmortizedCondenser,
    BrowserOutputCondenser,
    LLMAttentionCondenser,
    SummaryCondenser,
    EventMaskCondenser,
    LLMLinguaCondenser,
)
from ai_multicolony.memory.vector import VectorStore, CollectionType, InMemoryBackend
from ai_multicolony.memory.paging import MemoryPager
from ai_multicolony.memory.session import SessionManager, Session
from ai_multicolony.memory.knowledge import KnowledgeBase, KnowledgeEntry, SearchResult

# Re-export MemoryManager from core for convenience
from ai_multicolony.core.memory_manager import MemoryManager

__all__ = [
    # Condensers
    "BaseCondenser", "NoOpCondenser", "RecentEventsCondenser", "RecentCondenser",
    "ObservationCondenser", "LLMCondenser", "AmortizedCondenser",
    "BrowserOutputCondenser", "LLMAttentionCondenser", "SummaryCondenser",
    "EventMaskCondenser", "LLMLinguaCondenser",
    # Vector store
    "VectorStore", "CollectionType", "InMemoryBackend",
    # Paging
    "MemoryPager",
    # Session
    "SessionManager", "Session",
    # Knowledge
    "KnowledgeBase", "KnowledgeEntry", "SearchResult",
    # Memory Manager (from core)
    "MemoryManager",
]

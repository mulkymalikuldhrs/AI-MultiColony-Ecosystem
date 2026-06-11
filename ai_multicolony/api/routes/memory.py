"""Memory management API routes."""

from __future__ import annotations

from typing import Any

from ai_multicolony.api.schemas import (
    MemoryStoreRequest,
    MemoryQueryRequest,
    KnowledgeAddRequest,
    KnowledgeSearchRequest,
    SessionCreateRequest,
    MessageResponse,
)


def create_router() -> Any:
    """Create the memory router."""
    from fastapi import APIRouter

    router = APIRouter(prefix="/memory", tags=["memory"])

    # === Memory Entries ===

    @router.post("/store", response_model=MessageResponse)
    async def store_memory(request: MemoryStoreRequest) -> MessageResponse:
        """Store a memory entry."""
        from ai_multicolony.core.memory_manager import MemoryManager
        from ai_multicolony.types.memory import MemoryType

        manager = MemoryManager()
        try:
            memory_type = MemoryType(request.memory_type)
        except ValueError:
            memory_type = MemoryType.EPISODIC

        entry = manager.add_entry(
            agent_id="api",
            content=request.content,
            memory_type=memory_type,
            importance=request.importance,
            tags=request.tags,
        )
        return MessageResponse(message=f"Memory stored: {entry.id}")

    @router.post("/query")
    async def query_memory(request: MemoryQueryRequest) -> dict[str, Any]:
        """Query memories."""
        from ai_multicolony.core.memory_manager import MemoryManager
        from ai_multicolony.types.memory import MemoryType, MemoryQuery

        manager = MemoryManager()
        types = []
        for mt in request.memory_types:
            try:
                types.append(MemoryType(mt))
            except ValueError:
                pass

        query = MemoryQuery(query=request.query, memory_types=types, limit=request.limit)
        result = manager.query(query)
        return {
            "entries": [{"id": e.id, "content": e.content[:200], "type": e.memory_type.value} for e in result.entries],
            "total_count": result.total_count,
        }

    @router.get("/stats")
    async def memory_stats() -> dict[str, Any]:
        """Get memory statistics."""
        from ai_multicolony.core.memory_manager import MemoryManager
        manager = MemoryManager()
        return manager.get_stats()

    # === Sessions ===

    @router.post("/sessions", response_model=MessageResponse)
    async def create_session(request: SessionCreateRequest) -> MessageResponse:
        """Create a memory session."""
        from ai_multicolony.memory.session import SessionManager
        manager = SessionManager()
        session = manager.create_session(
            agent_id=request.agent_id,
            colony_id=request.colony_id,
            metadata=request.metadata,
        )
        return MessageResponse(
            message=f"Session created: {session.id}",
            data={"session_id": session.id},
        )

    @router.get("/sessions")
    async def list_sessions(active_only: bool = False) -> list[dict[str, Any]]:
        """List sessions."""
        from ai_multicolony.memory.session import SessionManager
        manager = SessionManager()
        return manager.list_sessions(active_only=active_only)

    @router.delete("/sessions/{session_id}", response_model=MessageResponse)
    async def delete_session(session_id: str) -> MessageResponse:
        """Delete a session."""
        from ai_multicolony.memory.session import SessionManager
        manager = SessionManager()
        deleted = manager.delete_session(session_id)
        return MessageResponse(
            message=f"Session {session_id} deleted" if deleted else f"Session {session_id} not found",
            success=deleted,
        )

    # === Knowledge ===

    @router.post("/knowledge", response_model=MessageResponse)
    async def add_knowledge(request: KnowledgeAddRequest) -> MessageResponse:
        """Add knowledge entry."""
        from ai_multicolony.memory.knowledge import KnowledgeBase
        kb = KnowledgeBase()
        entry = kb.add(
            title=request.title,
            content=request.content,
            category=request.category,
            tags=request.tags,
            source=request.source,
            confidence=request.confidence,
        )
        return MessageResponse(message=f"Knowledge added: {entry.id}")

    @router.post("/knowledge/search")
    async def search_knowledge(request: KnowledgeSearchRequest) -> dict[str, Any]:
        """Search knowledge base."""
        from ai_multicolony.memory.knowledge import KnowledgeBase
        kb = KnowledgeBase()
        results = kb.search(
            query=request.query,
            category=request.category,
            tags=request.tags or None,
            min_confidence=request.min_confidence,
            limit=request.limit,
            search_type=request.search_type,
        )
        return {
            "results": [
                {"id": r.entry.id, "title": r.entry.title, "score": r.score, "match_type": r.match_type}
                for r in results
            ],
            "total_count": len(results),
        }

    @router.get("/knowledge/stats")
    async def knowledge_stats() -> dict[str, Any]:
        """Get knowledge base statistics."""
        from ai_multicolony.memory.knowledge import KnowledgeBase
        kb = KnowledgeBase()
        return kb.get_stats()

    # === Pages ===

    @router.post("/pages", response_model=MessageResponse)
    async def create_page(
        content: str,
        title: str = "",
        memory_type: str = "working",
    ) -> MessageResponse:
        """Create a memory page."""
        from ai_multicolony.memory.paging import MemoryPager
        from ai_multicolony.types.memory import MemoryType

        pager = MemoryPager()
        try:
            mt = MemoryType(memory_type)
        except ValueError:
            mt = MemoryType.WORKING

        page = pager.create_page(content=content, memory_type=mt, title=title)
        return MessageResponse(
            message=f"Page created: {page.id}",
            data={"page_id": page.id, "token_count": page.token_count},
        )

    @router.get("/pages/usage")
    async def page_usage() -> dict[str, Any]:
        """Get memory page usage."""
        from ai_multicolony.memory.paging import MemoryPager
        pager = MemoryPager()
        return pager.get_token_usage()

    return router

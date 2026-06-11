"""Colony management API routes."""

from __future__ import annotations

from typing import Any

from ai_multicolony.api.schemas import (
    ColonyCreateRequest,
    ColonyConfigureRequest,
    ColonyScaleRequest,
    ColonyResponse,
    MessageResponse,
)


def create_router() -> Any:
    """Create the colony router."""
    from fastapi import APIRouter, HTTPException

    router = APIRouter(prefix="/colony", tags=["colony"])

    @router.get("/", response_model=list[dict[str, Any]])
    async def list_colonies() -> list[dict[str, Any]]:
        """List all colonies."""
        from ai_multicolony.colony.manager import ColonyManager
        manager = ColonyManager()
        return manager.list_colonies()

    @router.post("/", response_model=ColonyResponse)
    async def create_colony(request: ColonyCreateRequest) -> ColonyResponse:
        """Create a new colony."""
        from ai_multicolony.colony.manager import ColonyManager
        manager = ColonyManager()
        config = await manager.create(name=request.name, model=request.model, max_agents=request.max_agents)
        return ColonyResponse(
            colony_id=config.colony_id,
            name=config.name,
            state=config.state.value,
        )

    @router.get("/{colony_id}", response_model=dict[str, Any])
    async def get_colony(colony_id: str) -> dict[str, Any]:
        """Get colony status."""
        from ai_multicolony.colony.manager import ColonyManager
        manager = ColonyManager()
        try:
            return await manager.get_status(colony_id)
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.put("/{colony_id}/configure", response_model=MessageResponse)
    async def configure_colony(colony_id: str, request: ColonyConfigureRequest) -> MessageResponse:
        """Configure a colony."""
        from ai_multicolony.colony.manager import ColonyManager
        manager = ColonyManager()
        try:
            kwargs = {k: v for k, v in request.model_dump().items() if v is not None}
            await manager.configure(colony_id, **kwargs)
            return MessageResponse(message=f"Colony {colony_id} configured")
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.post("/{colony_id}/scale", response_model=MessageResponse)
    async def scale_colony(colony_id: str, request: ColonyScaleRequest) -> MessageResponse:
        """Scale a colony to a target number of agents."""
        from ai_multicolony.colony.manager import ColonyManager
        manager = ColonyManager()
        try:
            result = await manager.scale(colony_id, request.target_agents)
            return MessageResponse(
                message=f"Colony {colony_id} scaled to {request.target_agents} agents",
                data=result,
            )
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))

    @router.post("/{colony_id}/pause", response_model=MessageResponse)
    async def pause_colony(colony_id: str) -> MessageResponse:
        """Pause a colony."""
        from ai_multicolony.colony.manager import ColonyManager
        manager = ColonyManager()
        await manager.pause(colony_id)
        return MessageResponse(message=f"Colony {colony_id} paused")

    @router.post("/{colony_id}/resume", response_model=MessageResponse)
    async def resume_colony(colony_id: str) -> MessageResponse:
        """Resume a paused colony."""
        from ai_multicolony.colony.manager import ColonyManager
        manager = ColonyManager()
        await manager.resume(colony_id)
        return MessageResponse(message=f"Colony {colony_id} resumed")

    @router.delete("/{colony_id}", response_model=MessageResponse)
    async def delete_colony(colony_id: str) -> MessageResponse:
        """Delete a colony."""
        from ai_multicolony.colony.manager import ColonyManager
        manager = ColonyManager()
        await manager.destroy(colony_id)
        return MessageResponse(message=f"Colony {colony_id} destroyed")

    return router

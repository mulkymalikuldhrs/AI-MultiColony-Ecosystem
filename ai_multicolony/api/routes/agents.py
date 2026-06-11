"""Agent management API routes."""

from __future__ import annotations

from typing import Any

from ai_multicolony.api.schemas import (
    AgentCreateRequest,
    AgentRunRequest,
    AgentResponse,
    MessageResponse,
)


def create_router() -> Any:
    """Create the agents router."""
    from fastapi import APIRouter, HTTPException

    router = APIRouter(prefix="/agents", tags=["agents"])

    @router.get("/", response_model=list[dict[str, Any]])
    async def list_agents() -> list[dict[str, Any]]:
        """List available agent types."""
        from ai_multicolony.agents.registry import AgentRegistry
        registry = AgentRegistry()
        return [{"name": k, **v} for k, v in registry.list_all().items()]

    @router.post("/", response_model=AgentResponse)
    async def create_agent(request: AgentCreateRequest) -> AgentResponse:
        """Create a new agent."""
        from ai_multicolony.agents.registry import AgentRegistry
        from ai_multicolony.security.permissions import PermissionEngine, AutonomyLevel

        registry = AgentRegistry()
        try:
            agent = registry.create(
                name=request.agent_type,
                model=request.model,
                tools=request.tools,
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Set autonomy level
        perm_engine = PermissionEngine()
        try:
            autonomy = AutonomyLevel(request.autonomy_level)
        except ValueError:
            autonomy = AutonomyLevel.L2_CONSTRAINED
        perm_engine.set_autonomy(agent.agent_id, autonomy)

        return AgentResponse(
            agent_id=agent.agent_id,
            name=agent.name,
            agent_type=request.agent_type,
            state=agent.state.value,
            autonomy_level=request.autonomy_level,
        )

    @router.get("/{agent_id}", response_model=AgentResponse)
    async def get_agent(agent_id: str) -> AgentResponse:
        """Get agent status."""
        return AgentResponse(
            agent_id=agent_id,
            name="unknown",
            agent_type="unknown",
            state="unknown",
        )

    @router.post("/{agent_id}/run", response_model=MessageResponse)
    async def run_agent(agent_id: str, request: AgentRunRequest) -> MessageResponse:
        """Run an agent with a task."""
        return MessageResponse(
            message=f"Agent {agent_id} task submitted",
            data={"task": request.task},
        )

    @router.delete("/{agent_id}", response_model=MessageResponse)
    async def delete_agent(agent_id: str) -> MessageResponse:
        """Terminate an agent."""
        return MessageResponse(message=f"Agent {agent_id} terminated")

    return router

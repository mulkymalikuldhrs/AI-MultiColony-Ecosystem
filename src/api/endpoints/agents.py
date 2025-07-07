from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel
from typing import Dict, Any
from src.services.agent_service import AgentService, get_agent_service

router = APIRouter()

class AgentRunRequest(BaseModel):
    agent_name: str
    task_description: str
    config_overrides: Dict[str, Any] = {}

@router.post("/run-agent")
async def run_agent(
    request: AgentRunRequest = Body(...),
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Triggers an AI agent to run a specific task.
    
    This endpoint accepts an agent name and a task description,
    and dispatches the task to the agent service for execution.
    """
    result = await agent_service.run_agent_task(
        agent_name=request.agent_name,
        task_description=request.task_description,
        config_overrides=request.config_overrides
    )
    return result
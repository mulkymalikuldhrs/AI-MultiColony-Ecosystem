from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import traceback

# Import from colony instead of src
from colony.core.agent_registry import (
    list_all_agents, 
    get_agent, 
    get_agent_info,
    get_all_agents,
    update_agent_status
)

router = APIRouter(prefix="/api/agents", tags=["agents"])

# Setup logger
logger = logging.getLogger("api.agents")

class AgentRunRequest(BaseModel):
    agent_name: str
    task_description: str
    config_overrides: Dict[str, Any] = {}

# Get all agents
@router.get("/")
async def get_agents():
    """
    Get all registered agents.
    
    Returns:
        List of agents and their metadata
    """
    try:
        agents_info = get_all_agents()
        
        # Format the response
        response = []
        for name, info in agents_info.items():
            response.append({
                "id": name,
                "name": info["metadata"]["name"],
                "description": info["metadata"]["description"],
                "status": info["metadata"]["status"],
                "route": info["metadata"]["route"]
            })
        
        return {
            "status": "success",
            "agents": response
        }
    
    except Exception as e:
        logger.error(f"Error getting agents: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get agents: {str(e)}")

# Get agent status
@router.get("/{name}/status")
async def get_agent_status(name: str):
    """
    Get status of a specific agent.
    
    Args:
        name: Name of the agent
        
    Returns:
        Agent status information
    """
    try:
        agent_info = get_agent_info(name)
        if not agent_info:
            raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")
        
        return {
            "status": "success",
            "agent": {
                "id": name,
                "name": agent_info["metadata"]["name"],
                "status": agent_info["metadata"]["status"],
                "description": agent_info["metadata"]["description"]
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent status: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")

# Run agent
@router.post("/{name}/run")
async def run_agent(name: str, request: AgentRunRequest = Body(...)):
    """
    Start running an agent.
    
    Args:
        name: Name of the agent
        request: Agent run request
        
    Returns:
        Operation status
    """
    try:
        agent_class = get_agent(name)
        if not agent_class:
            raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")
        
        # Update agent status
        update_agent_status(name, "running")
        
        # TODO: Implement actual agent execution
        # This would typically be done asynchronously
        
        return {
            "status": "success",
            "message": f"Agent '{name}' started",
            "task_id": "task_12345",  # Placeholder for task ID
            "task_description": request.task_description
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running agent: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to run agent: {str(e)}")

# Stop agent
@router.post("/{name}/stop")
async def stop_agent(name: str):
    """
    Stop a running agent.
    
    Args:
        name: Name of the agent
        
    Returns:
        Operation status
    """
    try:
        agent_info = get_agent_info(name)
        if not agent_info:
            raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")
        
        # Check if agent is running
        if agent_info["metadata"]["status"] != "running":
            raise HTTPException(status_code=400, detail=f"Agent '{name}' is not running")
        
        # Update agent status
        update_agent_status(name, "idle")
        
        # TODO: Implement actual agent stopping
        
        return {
            "status": "success",
            "message": f"Agent '{name}' stopped"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping agent: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to stop agent: {str(e)}")

# Get agent logs
@router.get("/{name}/logs")
async def get_agent_logs(name: str, limit: int = 10):
    """
    Get logs for a specific agent.
    
    Args:
        name: Name of the agent
        limit: Maximum number of logs to return
        
    Returns:
        Agent logs
    """
    try:
        agent_info = get_agent_info(name)
        if not agent_info:
            raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")
        
        # TODO: Implement actual log retrieval
        
        # Placeholder logs
        logs = [
            {"timestamp": "2025-07-12T12:00:00", "level": "INFO", "message": f"Agent '{name}' initialized"},
            {"timestamp": "2025-07-12T12:01:00", "level": "INFO", "message": f"Agent '{name}' processing task"}
        ]
        
        return {
            "status": "success",
            "agent": name,
            "logs": logs[:limit]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent logs: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get agent logs: {str(e)}")
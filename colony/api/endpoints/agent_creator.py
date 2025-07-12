"""
API Endpoints for Dynamic Agent Creation
Provides REST API for creating new agents dynamically
"""

from fastapi import APIRouter, Body, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
import traceback
import os
from pathlib import Path

from colony.core.agent_registry import reload_registry

router = APIRouter(prefix="/api/agent-creator", tags=["agent-creator"])

# Setup logger
logger = logging.getLogger("api.agent_creator")

class AgentCreateRequest(BaseModel):
    """Request model for creating a new agent."""
    name: str = Field(..., description="Name of the agent (CamelCase)")
    prompt_template: str = Field(..., description="Prompt template for the agent")
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuration for the agent")
    description: Optional[str] = Field(None, description="Description of the agent")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies for the agent")

@router.post("/create")
async def create_agent(request: AgentCreateRequest = Body(...)):
    """
    Create a new agent dynamically.
    
    Args:
        request: Agent creation request
        
    Returns:
        Operation status
    """
    try:
        # Validate agent name (should be CamelCase)
        if not request.name[0].isupper() or not request.name.isalnum():
            raise HTTPException(
                status_code=400, 
                detail="Agent name must be in CamelCase format (e.g., MyAgent)"
            )
        
        # Ensure name ends with "Agent"
        agent_name = request.name if request.name.endswith("Agent") else f"{request.name}Agent"
        
        # Create file path
        agents_dir = Path(__file__).parent.parent.parent / "agents"
        file_path = agents_dir / f"{agent_name.lower()}.py"
        
        # Check if file already exists
        if file_path.exists():
            raise HTTPException(
                status_code=409, 
                detail=f"Agent '{agent_name}' already exists"
            )
        
        # Generate agent code
        agent_code = generate_agent_code(
            agent_name=agent_name,
            prompt_template=request.prompt_template,
            config=request.config,
            description=request.description or f"Dynamically created {agent_name}"
        )
        
        # Write agent code to file
        with open(file_path, "w") as f:
            f.write(agent_code)
        
        # Reload agent registry
        reload_registry()
        
        return {
            "status": "success",
            "message": f"Agent '{agent_name}' created successfully",
            "agent": {
                "name": agent_name,
                "file_path": str(file_path),
                "config": request.config
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")

def generate_agent_code(agent_name: str, prompt_template: str, config: Dict[str, Any], description: str) -> str:
    """
    Generate code for a new agent.
    
    Args:
        agent_name: Name of the agent
        prompt_template: Prompt template for the agent
        config: Configuration for the agent
        description: Description of the agent
        
    Returns:
        Generated agent code
    """
    # Format config as Python dict
    config_str = "{\n"
    for key, value in config.items():
        if isinstance(value, str):
            config_str += f"        \"{key}\": \"{value}\",\n"
        else:
            config_str += f"        \"{key}\": {value},\n"
    config_str += "    }"
    
    # Generate agent code
    code = f'''"""
{description}
Dynamically created agent using the agent creator API
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional

from colony.core.base_agent import BaseAgent

class {agent_name}(BaseAgent):
    """
    {description}
    """
    
    def __init__(self, name=None, config=None, memory=None):
        """Initialize the agent."""
        super().__init__(name or "{agent_name}", config, memory)
        self.prompt_template = """{prompt_template}"""
        self.default_config = {config_str}
    
    async def run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the agent on a task.
        
        Args:
            task: Task to run
            
        Returns:
            Task result
        """
        try:
            self.logger.info(f"Running {self.__class__.__name__} on task: {{task.get('task_id', 'unknown')}}")
            
            # Get task details
            task_description = task.get("request", "")
            context = task.get("context", {})
            
            # Format prompt with task description and context
            prompt = self.prompt_template.format(
                task_description=task_description,
                context=json.dumps(context, indent=2)
            )
            
            # TODO: Implement agent-specific logic here
            # This is a placeholder implementation
            
            # Return result
            return {{
                "status": "success",
                "type": "agent_response",
                "content": f"Processed task: {{task_description}}",
                "metadata": {{
                    "agent": self.__class__.__name__,
                    "task_id": task.get("task_id", "unknown")
                }}
            }}
            
        except Exception as e:
            self.logger.error(f"Error in {self.__class__.__name__}: {{str(e)}}")
            return self.handle_error(e, task)
'''
    
    return code
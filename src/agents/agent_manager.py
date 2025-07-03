"""
Agent Manager for Autonomous Agent Colony
Manages autonomous agents with CAMEL-AI integration
"""

import asyncio
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# CAMEL-AI imports
from camel.agents import ChatAgent, TaskAgent, CriticAgent
from camel.societies import RolePlaying
from camel.workforce import Workforce
from camel.messages import BaseMessage
from camel.types import RoleType

from ..utils.logger import get_logger

logger = get_logger(__name__)

class AutonomousAgent:
    """Individual autonomous agent in the colony"""
    
    def __init__(self, agent_id: str, role: str, model_manager, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.role = role
        self.model_manager = model_manager
        self.config = config
        
        # CAMEL agent
        self.camel_agent = None
        
        # Agent state
        self.status = "initializing"
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.task_count = 0
        self.error_count = 0
        
        # Task queue
        self.task_queue = asyncio.Queue()
        self.current_task = None
        
        # Memory and context
        self.memory = []
        self.context = {}
        
    async def initialize(self):
        """Initialize the agent"""
        try:
            # Get best model for this agent
            model = await self.model_manager.get_best_model(
                task_type=self.config.get("task_type", "general"),
                provider_preference=self.config.get("provider_preference")
            )
            
            # Create CAMEL agent based on role
            if self.role == "developer":
                self.camel_agent = ChatAgent(
                    role_name="Software Developer",
                    model=model,
                    system_message="You are an expert software developer focused on writing clean, efficient code."
                )
            elif self.role == "analyst":
                self.camel_agent = ChatAgent(
                    role_name="Data Analyst",
                    model=model,
                    system_message="You are a data analyst expert at analyzing information and providing insights."
                )
            elif self.role == "researcher":
                self.camel_agent = ChatAgent(
                    role_name="Research Specialist",
                    model=model,
                    system_message="You are a research specialist focused on gathering and analyzing information."
                )
            elif self.role == "critic":
                self.camel_agent = CriticAgent(
                    role_name="Quality Critic",
                    model=model,
                    system_message="You are a critic focused on quality assurance and improvement suggestions."
                )
            else:
                # Default general agent
                self.camel_agent = ChatAgent(
                    role_name="General Assistant",
                    model=model,
                    system_message="You are a helpful AI assistant."
                )
            
            self.status = "ready"
            logger.info(f"✅ Agent {self.agent_id} ({self.role}) initialized")
            
        except Exception as e:
            self.status = "error"
            self.error_count += 1
            logger.error(f"Failed to initialize agent {self.agent_id}: {e}")
            raise
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single task"""
        try:
            self.current_task = task
            self.status = "working"
            self.last_activity = datetime.now()
            
            task_type = task.get("type", "general")
            task_content = task.get("content", "")
            task_context = task.get("context", {})
            
            # Create message for CAMEL agent
            message = BaseMessage(
                role_name=self.role,
                role_type=RoleType.ASSISTANT,
                meta_dict=task_context,
                content=task_content
            )
            
            # Process with CAMEL agent
            response = await self._process_with_camel(message, task_type)
            
            # Store in memory
            self.memory.append({
                "timestamp": datetime.now().isoformat(),
                "task": task,
                "response": response,
                "success": True
            })
            
            self.task_count += 1
            self.status = "ready"
            self.current_task = None
            
            result = {
                "agent_id": self.agent_id,
                "role": self.role,
                "task_id": task.get("id"),
                "success": True,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Agent {self.agent_id} completed task {task.get('id')}")
            return result
            
        except Exception as e:
            self.error_count += 1
            self.status = "error"
            self.current_task = None
            
            # Store error in memory
            self.memory.append({
                "timestamp": datetime.now().isoformat(),
                "task": task,
                "error": str(e),
                "success": False
            })
            
            result = {
                "agent_id": self.agent_id,
                "role": self.role,
                "task_id": task.get("id"),
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.error(f"❌ Agent {self.agent_id} failed task {task.get('id')}: {e}")
            return result
    
    async def _process_with_camel(self, message: BaseMessage, task_type: str) -> str:
        """Process task using CAMEL agent"""
        try:
            if hasattr(self.camel_agent, 'step'):
                # For agents that support step method
                response = self.camel_agent.step(message)
                if hasattr(response, 'content'):
                    return response.content
                else:
                    return str(response)
            else:
                # Fallback to basic processing
                return f"Processed by {self.role}: {message.content[:100]}..."
                
        except Exception as e:
            logger.warning(f"CAMEL processing failed, using fallback: {e}")
            # Fallback to model manager
            return await self.model_manager.generate_response(
                message.content,
                task_type=task_type
            )
    
    async def run_continuously(self):
        """Run agent continuously processing tasks"""
        logger.info(f"Agent {self.agent_id} starting continuous processing")
        
        while self.status != "shutdown":
            try:
                # Wait for task with timeout
                task = await asyncio.wait_for(self.task_queue.get(), timeout=60.0)
                
                # Process the task
                result = await self.process_task(task)
                
                # Mark task as done
                self.task_queue.task_done()
                
            except asyncio.TimeoutError:
                # No tasks available, continue waiting
                continue
            except Exception as e:
                logger.error(f"Error in agent {self.agent_id} continuous processing: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def add_task(self, task: Dict[str, Any]):
        """Add task to agent's queue"""
        await self.task_queue.put(task)
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "task_count": self.task_count,
            "error_count": self.error_count,
            "queue_size": self.task_queue.qsize(),
            "current_task": self.current_task.get("id") if self.current_task else None,
            "memory_size": len(self.memory)
        }
    
    async def shutdown(self):
        """Shutdown agent"""
        self.status = "shutdown"
        logger.info(f"Agent {self.agent_id} shutdown")


class AgentManager:
    """Manages the entire agent colony"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents = {}
        self.agent_tasks = {}
        self.model_manager = None
        
        # Colony configuration
        self.max_agents = config.get("max_agents", 50)
        self.auto_scaling = config.get("auto_scaling", True)
        self.health_check_interval = config.get("health_check_interval", 60)
        
        # CAMEL workforce
        self.workforce = None
        self.role_playing_sessions = {}
        
        # Agent types and their configurations
        self.agent_types = {
            "developer": {
                "task_type": "coding",
                "max_instances": 10,
                "auto_scale": True
            },
            "analyst": {
                "task_type": "analysis", 
                "max_instances": 5,
                "auto_scale": True
            },
            "researcher": {
                "task_type": "general",
                "max_instances": 5,
                "auto_scale": True
            },
            "critic": {
                "task_type": "analysis",
                "max_instances": 3,
                "auto_scale": False
            },
            "coordinator": {
                "task_type": "general",
                "max_instances": 2,
                "auto_scale": False
            }
        }
        
        # Task distribution
        self.task_queue = asyncio.Queue()
        self.completed_tasks = []
        
    async def initialize(self):
        """Initialize agent manager"""
        logger.info("Initializing Agent Manager...")
        
        # Initialize CAMEL workforce
        await self._initialize_workforce()
        
        # Create initial agents
        await self._create_initial_agents()
        
        # Start background tasks
        asyncio.create_task(self._task_distributor())
        asyncio.create_task(self._health_monitor())
        
        logger.info(f"✅ Agent Manager initialized with {len(self.agents)} agents")
    
    async def _initialize_workforce(self):
        """Initialize CAMEL workforce"""
        try:
            # Note: This is a simplified initialization
            # In practice, you'd configure the workforce with specific models and tasks
            self.workforce = Workforce("Autonomous Colony Workforce")
            logger.info("✅ CAMEL Workforce initialized")
            
        except Exception as e:
            logger.warning(f"Failed to initialize CAMEL workforce: {e}")
    
    async def _create_initial_agents(self):
        """Create initial set of agents"""
        initial_agents = [
            ("developer", 2),
            ("analyst", 1),
            ("researcher", 1),
            ("critic", 1)
        ]
        
        for role, count in initial_agents:
            for i in range(count):
                await self.create_agent(role)
    
    async def create_agent(self, role: str, config: Dict[str, Any] = None) -> str:
        """Create a new agent"""
        try:
            if len(self.agents) >= self.max_agents:
                raise Exception(f"Maximum agent limit ({self.max_agents}) reached")
            
            agent_id = f"{role}_{uuid.uuid4().hex[:8]}"
            
            # Merge role config with provided config
            agent_config = self.agent_types.get(role, {}).copy()
            if config:
                agent_config.update(config)
            
            # Create agent
            agent = AutonomousAgent(agent_id, role, self.model_manager, agent_config)
            
            # Initialize agent
            await agent.initialize()
            
            # Store agent
            self.agents[agent_id] = agent
            
            # Start agent's continuous processing
            asyncio.create_task(agent.run_continuously())
            
            logger.info(f"✅ Created agent {agent_id} ({role})")
            return agent_id
            
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            raise
    
    async def remove_agent(self, agent_id: str):
        """Remove an agent"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            await agent.shutdown()
            del self.agents[agent_id]
            logger.info(f"✅ Removed agent {agent_id}")
    
    async def submit_task(self, task: Dict[str, Any]) -> str:
        """Submit a task to the colony"""
        task_id = task.get("id", f"task_{uuid.uuid4().hex[:8]}")
        task["id"] = task_id
        task["submitted_at"] = datetime.now().isoformat()
        
        await self.task_queue.put(task)
        logger.info(f"📝 Task {task_id} submitted to colony")
        
        return task_id
    
    async def _task_distributor(self):
        """Distribute tasks to appropriate agents"""
        logger.info("Starting task distributor")
        
        while True:
            try:
                # Get task from queue
                task = await self.task_queue.get()
                
                # Find best agent for task
                agent = await self._find_best_agent(task)
                
                if agent:
                    # Assign task to agent
                    await agent.add_task(task)
                    logger.info(f"📋 Task {task.get('id')} assigned to agent {agent.agent_id}")
                else:
                    # No suitable agent available
                    if self.auto_scaling:
                        # Try to create a new agent
                        required_role = self._get_required_role_for_task(task)
                        try:
                            agent_id = await self.create_agent(required_role)
                            agent = self.agents[agent_id]
                            await agent.add_task(task)
                            logger.info(f"📋 Created new agent {agent_id} for task {task.get('id')}")
                        except Exception as e:
                            logger.error(f"Failed to auto-scale for task {task.get('id')}: {e}")
                            # Put task back in queue
                            await self.task_queue.put(task)
                    else:
                        # Put task back in queue and wait
                        await self.task_queue.put(task)
                        await asyncio.sleep(5)
                
                self.task_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in task distributor: {e}")
                await asyncio.sleep(5)
    
    async def _find_best_agent(self, task: Dict[str, Any]) -> Optional[AutonomousAgent]:
        """Find the best available agent for a task"""
        task_type = task.get("type", "general")
        preferred_role = task.get("preferred_role")
        
        # Filter agents by availability and suitability
        available_agents = []
        
        for agent in self.agents.values():
            if agent.status == "ready":
                # Check if agent role matches task requirements
                if preferred_role:
                    if agent.role == preferred_role:
                        available_agents.append((agent, 10))  # High priority for exact match
                elif task_type == "coding" and agent.role == "developer":
                    available_agents.append((agent, 8))
                elif task_type == "analysis" and agent.role in ["analyst", "critic"]:
                    available_agents.append((agent, 8))
                elif task_type == "research" and agent.role == "researcher":
                    available_agents.append((agent, 8))
                else:
                    available_agents.append((agent, 5))  # Lower priority for general match
        
        if not available_agents:
            return None
        
        # Sort by priority and select best agent
        available_agents.sort(key=lambda x: x[1], reverse=True)
        return available_agents[0][0]
    
    def _get_required_role_for_task(self, task: Dict[str, Any]) -> str:
        """Determine required role for a task"""
        task_type = task.get("type", "general")
        preferred_role = task.get("preferred_role")
        
        if preferred_role and preferred_role in self.agent_types:
            return preferred_role
        
        role_mapping = {
            "coding": "developer",
            "analysis": "analyst", 
            "research": "researcher",
            "critique": "critic",
            "general": "researcher"
        }
        
        return role_mapping.get(task_type, "researcher")
    
    async def _health_monitor(self):
        """Monitor agent health and perform maintenance"""
        logger.info("Starting health monitor")
        
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                healthy_agents = 0
                error_agents = []
                
                for agent_id, agent in self.agents.items():
                    if agent.status == "ready":
                        healthy_agents += 1
                    elif agent.status == "error":
                        error_agents.append(agent_id)
                
                logger.info(f"Health check: {healthy_agents}/{len(self.agents)} agents healthy")
                
                # Handle error agents
                for agent_id in error_agents:
                    if self.agents[agent_id].error_count > 3:
                        logger.warning(f"Removing problematic agent {agent_id}")
                        await self.remove_agent(agent_id)
                        
                        # Replace with new agent if auto-scaling enabled
                        if self.auto_scaling:
                            role = self.agents[agent_id].role
                            await self.create_agent(role)
                
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
    
    async def health_check(self) -> bool:
        """Check overall health of agent manager"""
        healthy_agents = len([a for a in self.agents.values() if a.status == "ready"])
        total_agents = len(self.agents)
        
        if total_agents == 0:
            return False
        
        health_ratio = healthy_agents / total_agents
        return health_ratio > 0.5  # At least 50% of agents should be healthy
    
    async def shutdown(self):
        """Shutdown all agents"""
        logger.info("Shutting down Agent Manager...")
        
        # Shutdown all agents
        for agent in self.agents.values():
            await agent.shutdown()
        
        self.agents.clear()
        logger.info("✅ Agent Manager shutdown complete")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of agent manager"""
        agent_status = {}
        for agent_id, agent in self.agents.items():
            agent_status[agent_id] = agent.get_status()
        
        return {
            "total_agents": len(self.agents),
            "agent_types": {role: len([a for a in self.agents.values() if a.role == role]) 
                           for role in self.agent_types.keys()},
            "queue_size": self.task_queue.qsize(),
            "completed_tasks": len(self.completed_tasks),
            "agents": agent_status
        }
    
    def set_model_manager(self, model_manager):
        """Set model manager reference"""
        self.model_manager = model_manager
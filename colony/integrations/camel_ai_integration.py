"""
Camel AI Integration v7.3.0
Advanced AI agent system integration using Camel AI framework
Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import os
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

try:
    from camel.agents import ChatAgent
    from camel.messages import BaseMessage
    from camel.models import ModelFactory
    from camel.types import RoleType, ModelType
    CAMEL_AI_AVAILABLE = True
except ImportError as e:
    CAMEL_AI_AVAILABLE = False
    logging.warning(f"Camel AI not available: {e}")

from ..core.base_agent import BaseAgent


class CamelAIAgent(BaseAgent):
    """
    Camel AI powered agent with advanced conversational capabilities.
    Integrates Camel AI framework into the colony ecosystem.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None, memory_manager=None):
        super().__init__(name, config, memory_manager)
        
        self.camel_agent = None
        self.model_type = config.get('model_type', ModelType.GPT_4_TURBO) if config else ModelType.GPT_4_TURBO
        self.role_type = config.get('role_type', RoleType.ASSISTANT) if config else RoleType.ASSISTANT
        self.conversation_history = []
        
        if CAMEL_AI_AVAILABLE:
            self._initialize_camel_agent()
        else:
            self.logger.error("Camel AI not available. Install with: pip install camel-ai")
    
    def _initialize_camel_agent(self):
        """Initialize the Camel AI agent."""
        try:
            # Create model
            model = ModelFactory.create(
                model_platform=self.model_type.value.platform,
                model_type=self.model_type
            )
            
            # Create Camel AI agent
            self.camel_agent = ChatAgent(
                role_name=self.name,
                model=model,
                role_type=self.role_type
            )
            
            self.status = "ready"
            self.logger.info(f"Camel AI agent '{self.name}' initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Camel AI agent: {e}")
            self.status = "failed"
    
    def run(self):
        """Main execution loop for the Camel AI agent."""
        if not CAMEL_AI_AVAILABLE or not self.camel_agent:
            self.logger.error("Camel AI agent not properly initialized")
            return
        
        self.status = "running"
        self.logger.info(f"Camel AI agent '{self.name}' is now running")
        
        # Start processing loop
        asyncio.run(self._process_loop())
    
    async def _process_loop(self):
        """Asynchronous processing loop for handling tasks."""
        while self.status == "running":
            try:
                # Check for new tasks or messages
                await self._process_pending_tasks()
                await asyncio.sleep(1)  # Prevent tight loop
                
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _process_pending_tasks(self):
        """Process any pending tasks or messages."""
        # This would be implemented based on your specific task queue system
        pass
    
    def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Send a message to the Camel AI agent and get a response.
        
        Args:
            message: The input message
            context: Additional context for the conversation
            
        Returns:
            str: The agent's response
        """
        if not CAMEL_AI_AVAILABLE or not self.camel_agent:
            return "Camel AI agent not available"
        
        try:
            # Create a BaseMessage
            user_message = BaseMessage(
                role_name="user",
                role_type=RoleType.USER,
                meta_dict={},
                content=message
            )
            
            # Get response from Camel AI agent
            response = self.camel_agent.step(user_message)
            
            # Store conversation history
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user_message': message,
                'agent_response': response.content,
                'context': context
            })
            
            self.last_activity = datetime.now().timestamp()
            return response.content
            
        except Exception as e:
            self.logger.error(f"Error in chat: {e}")
            return f"Error processing message: {str(e)}"
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
        self.logger.info("Conversation history cleared")
    
    def set_system_prompt(self, prompt: str):
        """Set a system prompt for the agent."""
        if self.camel_agent:
            # Update the agent's system message
            self.camel_agent.system_message = BaseMessage(
                role_name="system",
                role_type=RoleType.CRITIC,
                meta_dict={},
                content=prompt
            )
            self.logger.info("System prompt updated")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get detailed status information about the agent."""
        return {
            'name': self.name,
            'status': self.status,
            'camel_ai_available': CAMEL_AI_AVAILABLE,
            'model_type': str(self.model_type) if hasattr(self, 'model_type') else 'unknown',
            'role_type': str(self.role_type) if hasattr(self, 'role_type') else 'unknown',
            'conversation_count': len(self.conversation_history),
            'last_activity': self.last_activity,
            'uptime': datetime.now().timestamp() - self.start_time
        }


class CamelAIColonyIntegration:
    """
    Integration manager for Camel AI agents within the colony ecosystem.
    Handles multiple Camel AI agents and their coordination.
    """
    
    def __init__(self):
        self.camel_agents = {}
        self.logger = logging.getLogger(__name__)
        self.integration_status = "initialized"
    
    def create_camel_agent(self, name: str, config: Optional[Dict[str, Any]] = None) -> CamelAIAgent:
        """
        Create a new Camel AI agent.
        
        Args:
            name: Unique name for the agent
            config: Configuration for the agent
            
        Returns:
            CamelAIAgent: The created agent
        """
        if name in self.camel_agents:
            raise ValueError(f"Camel AI agent '{name}' already exists")
        
        agent = CamelAIAgent(name, config)
        self.camel_agents[name] = agent
        
        self.logger.info(f"Created Camel AI agent: {name}")
        return agent
    
    def get_agent(self, name: str) -> Optional[CamelAIAgent]:
        """Get a Camel AI agent by name."""
        return self.camel_agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all Camel AI agents."""
        return list(self.camel_agents.keys())
    
    def start_all_agents(self):
        """Start all Camel AI agents."""
        for agent in self.camel_agents.values():
            try:
                agent.run()
            except Exception as e:
                self.logger.error(f"Failed to start agent {agent.name}: {e}")
    
    def stop_all_agents(self):
        """Stop all Camel AI agents."""
        for agent in self.camel_agents.values():
            agent.status = "stopped"
        self.logger.info("All Camel AI agents stopped")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get the status of the Camel AI integration."""
        return {
            'integration_status': self.integration_status,
            'camel_ai_available': CAMEL_AI_AVAILABLE,
            'total_agents': len(self.camel_agents),
            'active_agents': sum(1 for agent in self.camel_agents.values() if agent.status == "running"),
            'agent_list': list(self.camel_agents.keys())
        }


# Global integration instance
camel_integration = CamelAIColonyIntegration()

# Convenience functions
def create_camel_agent(name: str, config: Optional[Dict[str, Any]] = None) -> CamelAIAgent:
    """Create a new Camel AI agent."""
    return camel_integration.create_camel_agent(name, config)

def get_camel_agent(name: str) -> Optional[CamelAIAgent]:
    """Get a Camel AI agent by name."""
    return camel_integration.get_agent(name)

def chat_with_camel_agent(agent_name: str, message: str, context: Optional[Dict[str, Any]] = None) -> str:
    """Chat with a specific Camel AI agent."""
    agent = camel_integration.get_agent(agent_name)
    if agent:
        return agent.chat(message, context)
    return f"Camel AI agent '{agent_name}' not found"
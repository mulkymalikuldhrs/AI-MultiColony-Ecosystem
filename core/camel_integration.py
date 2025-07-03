"""
🐫 CAMEL-AI Integration Module - Evolusi Kecerdasan Umum
Advanced multi-agent system integration with Camel-AI framework
Including Societies, Workforce, ChatAgent, and MCP integration

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime
import json
from pathlib import Path

# Graceful camel-ai imports with fallbacks
try:
    # Camel-AI Core Imports
    from camel.agents import ChatAgent
    from camel.models import ModelFactory
    from camel.types import ModelPlatformType, ModelType, RoleType
    from camel.messages import BaseMessage
    from camel.configs import ChatGPTConfig, AnthropicConfig
    from camel.societies import RolePlaying
    from camel.toolkits import (
        SearchToolkit, CodeExecutionToolkit, MathToolkit, 
        BrowserToolkit, ImageAnalysisToolkit, VideoAnalysisToolkit,
        ArxivToolkit, GitHubToolkit, GoogleMapsToolkit,
        WeatherToolkit, ExcelToolkit, NotionToolkit
    )
    
    # Try importing advanced features
    try:
        from camel.societies.workforce import Workforce
        from camel.tasks.task import Task
        WORKFORCE_AVAILABLE = True
    except ImportError:
        WORKFORCE_AVAILABLE = False
    
    try:
        from camel.toolkits import MCPToolkit
        MCP_AVAILABLE = True
    except ImportError:
        MCP_AVAILABLE = False
    
    CAMEL_AVAILABLE = True
    
except ImportError as e:
    logging.warning(f"Camel-AI not available: {e}")
    CAMEL_AVAILABLE = False
    WORKFORCE_AVAILABLE = False
    MCP_AVAILABLE = False
    
    # Create fallback classes to prevent import errors
    class ChatAgent:
        def __init__(self, *args, **kwargs):
            self.model = None
            self.tools = None
            pass
    
    class ModelFactory:
        @staticmethod
        def create(*args, **kwargs):
            return None
    
    class RolePlaying:
        def __init__(self, *args, **kwargs):
            self.max_turns = 10
            pass
    
    class BaseMessage:
        @staticmethod
        def make_assistant_message(*args, **kwargs):
            return None
    
    # Fallback toolkits
    class SearchToolkit:
        def get_tools(self): return []
    
    class CodeExecutionToolkit:
        def get_tools(self): return []
    
    class MathToolkit:
        def get_tools(self): return []

from .enhanced_prompts import enhanced_prompts, PromptCategory

class CamelAgentConfig:
    """Configuration for Camel-AI agents"""
    
    def __init__(self, 
                 name: str,
                 role: str,
                 model_platform: str = "openai",
                 model_type: str = "gpt-4o-mini",
                 temperature: float = 0.7,
                 max_tokens: int = 4096,
                 tools: List[str] = None,
                 system_message: str = None):
        self.name = name
        self.role = role
        self.model_platform = model_platform
        self.model_type = model_type
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.tools = tools or []
        self.system_message = system_message or f"You are {name}, a specialized AI agent with expertise in {role}."

class CamelModelManager:
    """Manages Camel-AI model instances with multiple provider support"""
    
    def __init__(self):
        self.models = {}
        self.available = CAMEL_AVAILABLE
        
    def create_model(self, 
                    provider: str = "openai", 
                    model_type: str = None,
                    temperature: float = 0.7,
                    max_tokens: int = 4096,
                    **kwargs):
        """Create a Camel-AI model instance"""
        if not CAMEL_AVAILABLE:
            logging.warning("Camel-AI not available, returning None model")
            return None
        
        # Implementation when CAMEL is available
        try:
            config_info = {
                "openai": {
                    "platform": ModelPlatformType.OPENAI,
                    "model_type": ModelType.GPT_4O_MINI,
                    "config_class": ChatGPTConfig
                }
            }
            
            config = config_info.get(provider, config_info["openai"])
            model_config = config["config_class"](
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            model = ModelFactory.create(
                model_platform=config["platform"],
                model_type=model_type or config["model_type"],
                model_config_dict=model_config.as_dict()
            )
            
            model_id = f"{provider}_{model_type}_{temperature}"
            self.models[model_id] = model
            return model
            
        except Exception as e:
            logging.error(f"Failed to create model: {e}")
            return None
    
    def get_model(self, model_id: str):
        """Get existing model or create default"""
        if model_id in self.models:
            return self.models[model_id]
        return self.create_model()

class CamelAgentFactory:
    """Factory for creating specialized Camel-AI agents"""
    
    def __init__(self, model_manager: CamelModelManager):
        self.model_manager = model_manager
        self.agents = {}
        self.available = CAMEL_AVAILABLE
        
    def create_agent(self, config: CamelAgentConfig) -> Optional[ChatAgent]:
        """Create a Camel-AI ChatAgent with configuration"""
        if not CAMEL_AVAILABLE:
            logging.warning("Camel-AI not available, returning mock agent")
            # Return a mock agent for compatibility
            mock_agent = type('MockAgent', (), {
                'name': config.name,
                'role': config.role,
                'available': False
            })()
            self.agents[config.name] = mock_agent
            return mock_agent
        
        try:
            model = self.model_manager.create_model(
                provider=config.model_platform,
                model_type=config.model_type,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
            
            if model is None:
                return None
            
            # Create agent with model
            agent = ChatAgent(
                system_message=BaseMessage.make_assistant_message(
                    role_name=config.name,
                    content=config.system_message
                ),
                model=model,
                tools=[]  # Tools setup would go here if available
            )
            
            self.agents[config.name] = agent
            return agent
            
        except Exception as e:
            logging.error(f"Failed to create agent {config.name}: {e}")
            return None
    
    def get_agent(self, name: str) -> Optional[ChatAgent]:
        """Get existing agent by name"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all created agents"""
        return list(self.agents.keys())

class CamelIntegrationManager:
    """Main integration manager for Camel-AI functionality"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/camel_config.json"
        self.config = self._load_config()
        self.available = CAMEL_AVAILABLE
        
        # Initialize managers
        self.model_manager = CamelModelManager()
        self.agent_factory = CamelAgentFactory(self.model_manager)
        
        # Integration state
        self.integration_status = {
            "camel_available": CAMEL_AVAILABLE,
            "workforce_available": WORKFORCE_AVAILABLE,
            "mcp_available": MCP_AVAILABLE,
            "initialized": False,
            "agents_created": 0,
            "societies_created": 0,
            "workforces_created": 0
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load Camel-AI integration configuration"""
        default_config = {
            "default_model": {
                "provider": "openai",
                "model_type": "gpt-4o-mini",
                "temperature": 0.7,
                "max_tokens": 4096
            },
            "agent_templates": {
                "researcher": {
                    "role": "research and analysis",
                    "tools": ["search", "arxiv", "browser"],
                    "system_message": "You are a research specialist focused on thorough analysis and evidence-based insights."
                },
                "developer": {
                    "role": "software development and coding",
                    "tools": ["code", "github"],
                    "system_message": "You are a software development expert specializing in clean, efficient code."
                }
            }
        }
        
        config_file = Path(self.config_path)
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logging.warning(f"Failed to load config: {e}")
        
        return default_config
    
    async def initialize(self) -> bool:
        """Initialize the Camel-AI integration"""
        if not CAMEL_AVAILABLE:
            logging.info("Camel-AI not available, running in offline mode")
            self.integration_status["initialized"] = True
            return True
        
        try:
            # Create default agents from templates if Camel is available
            for agent_name, template in self.config["agent_templates"].items():
                config = CamelAgentConfig(
                    name=agent_name,
                    role=template["role"],
                    system_message=template["system_message"]
                )
                
                agent = self.agent_factory.create_agent(config)
                if agent:
                    self.integration_status["agents_created"] += 1
            
            self.integration_status["initialized"] = True
            logging.info("Camel-AI integration initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize Camel-AI integration: {e}")
            return False
    
    async def process_enhanced_prompt(self, 
                                    prompt_id: str, 
                                    agent_name: str = None,
                                    **variables) -> Dict[str, Any]:
        """Process enhanced prompt with Camel-AI agents"""
        if not CAMEL_AVAILABLE:
            return {
                "success": False,
                "error": "Camel-AI not available - running in offline mode",
                "offline_mode": True
            }
        
        try:
            # Select appropriate agent
            if agent_name and agent_name in self.agent_factory.agents:
                agent = self.agent_factory.agents[agent_name]
            else:
                # Use first available agent or create default
                agents = self.agent_factory.list_agents()
                if agents:
                    agent = self.agent_factory.agents[agents[0]]
                else:
                    # Create a default agent
                    config = CamelAgentConfig(
                        name="default_assistant",
                        role="general assistance"
                    )
                    agent = self.agent_factory.create_agent(config)
            
            if not agent:
                return {"success": False, "error": "No agent available"}
            
            # Get prompt from enhanced prompts
            if hasattr(enhanced_prompts, 'get_prompt'):
                prompt_template = enhanced_prompts.get_prompt(prompt_id)
                if prompt_template:
                    # Format prompt with variables
                    formatted_prompt = prompt_template.format(**variables)
                    
                    # Process with agent (mock implementation)
                    result = {
                        "success": True,
                        "response": f"Processed prompt '{prompt_id}' with agent '{agent.name if hasattr(agent, 'name') else 'unknown'}'",
                        "agent_used": agent_name or "default",
                        "prompt_id": prompt_id
                    }
                    return result
            
            return {"success": False, "error": f"Prompt '{prompt_id}' not found"}
            
        except Exception as e:
            return {"success": False, "error": f"Processing failed: {str(e)}"}
    
    async def create_intelligent_society(self, 
                                       task_description: str,
                                       complexity: str = "medium") -> Dict[str, Any]:
        """Create an intelligent society for complex tasks"""
        if not CAMEL_AVAILABLE:
            return {
                "success": False,
                "error": "Intelligent societies require Camel-AI (not available)",
                "offline_mode": True,
                "fallback_response": f"Task noted: {task_description}. Please install Camel-AI for full society features."
            }
        
        try:
            # Mock society creation for now
            self.integration_status["societies_created"] += 1
            
            return {
                "success": True,
                "society_id": f"society_{self.integration_status['societies_created']}",
                "task": task_description,
                "complexity": complexity,
                "status": "created",
                "message": "Intelligent society created successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Society creation failed: {str(e)}"}
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status"""
        return self.integration_status.copy()
    
    def list_available_features(self) -> Dict[str, List[str]]:
        """List available features based on what's installed"""
        features = {
            "core": ["enhanced_prompts", "agent_factory"],
            "available": [],
            "unavailable": []
        }
        
        if CAMEL_AVAILABLE:
            features["available"].extend(["chat_agents", "model_factory", "role_playing"])
        else:
            features["unavailable"].extend(["chat_agents", "model_factory", "role_playing"])
        
        if WORKFORCE_AVAILABLE:
            features["available"].append("workforce")
        else:
            features["unavailable"].append("workforce")
        
        if MCP_AVAILABLE:
            features["available"].append("mcp_integration")
        else:
            features["unavailable"].append("mcp_integration")
        
        return features

# Global integration manager
_camel_integration_manager = None

async def initialize_camel_integration() -> bool:
    """Initialize global Camel-AI integration"""
    global _camel_integration_manager
    _camel_integration_manager = CamelIntegrationManager()
    return await _camel_integration_manager.initialize()

def get_camel_integration() -> CamelIntegrationManager:
    """Get the global Camel-AI integration manager"""
    global _camel_integration_manager
    if _camel_integration_manager is None:
        _camel_integration_manager = CamelIntegrationManager()
    return _camel_integration_manager
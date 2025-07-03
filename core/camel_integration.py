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
        self.default_configs = {
            "openai": {
                "platform": ModelPlatformType.OPENAI,
                "model_type": ModelType.GPT_4O_MINI,
                "config_class": ChatGPTConfig
            },
            "anthropic": {
                "platform": ModelPlatformType.ANTHROPIC,
                "model_type": "claude-3-5-sonnet",
                "config_class": AnthropicConfig
            },
            "groq": {
                "platform": ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
                "model_type": "llama-3.1-8b-instant",
                "config_class": ChatGPTConfig
            }
        }
    
    def create_model(self, 
                    provider: str = "openai", 
                    model_type: str = None,
                    temperature: float = 0.7,
                    max_tokens: int = 4096,
                    **kwargs):
        """Create a Camel-AI model instance"""
        if not CAMEL_AVAILABLE:
            raise RuntimeError("Camel-AI not available")
        
        config_info = self.default_configs.get(provider, self.default_configs["openai"])
        
        # Create model configuration
        model_config = config_info["config_class"](
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Determine model type
        if model_type is None:
            model_type = config_info["model_type"]
        
        # Create model
        model = ModelFactory.create(
            model_platform=config_info["platform"],
            model_type=model_type,
            model_config_dict=model_config.as_dict()
        )
        
        model_id = f"{provider}_{model_type}_{temperature}"
        self.models[model_id] = model
        
        return model
    
    def get_model(self, model_id: str):
        """Get existing model or create default"""
        if model_id in self.models:
            return self.models[model_id]
        
        # Create default model
        return self.create_model()

class CamelAgentFactory:
    """Factory for creating specialized Camel-AI agents"""
    
    def __init__(self, model_manager: CamelModelManager):
        self.model_manager = model_manager
        self.agents = {}
        self.toolkit_registry = self._initialize_toolkits()
    
    def _initialize_toolkits(self) -> Dict[str, Any]:
        """Initialize available toolkits"""
        toolkits = {}
        
        if CAMEL_AVAILABLE:
            try:
                toolkits["search"] = SearchToolkit()
                toolkits["code"] = CodeExecutionToolkit()
                toolkits["math"] = MathToolkit()
                toolkits["browser"] = BrowserToolkit()
                toolkits["image"] = ImageAnalysisToolkit()
                toolkits["video"] = VideoAnalysisToolkit()
                toolkits["arxiv"] = ArxivToolkit()
                toolkits["github"] = GitHubToolkit()
                toolkits["maps"] = GoogleMapsToolkit()
                toolkits["weather"] = WeatherToolkit()
                toolkits["excel"] = ExcelToolkit()
                toolkits["notion"] = NotionToolkit()
                
                if MCP_AVAILABLE:
                    toolkits["mcp"] = MCPToolkit()
                    
            except Exception as e:
                logging.warning(f"Some toolkits failed to initialize: {e}")
        
        return toolkits
    
    def create_agent(self, config: CamelAgentConfig) -> ChatAgent:
        """Create a Camel-AI ChatAgent with configuration"""
        if not CAMEL_AVAILABLE:
            raise RuntimeError("Camel-AI not available")
        
        # Create model
        model = self.model_manager.create_model(
            provider=config.model_platform,
            model_type=config.model_type,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
        
        # Prepare tools
        tools = []
        for tool_name in config.tools:
            if tool_name in self.toolkit_registry:
                toolkit = self.toolkit_registry[tool_name]
                tools.extend(toolkit.get_tools())
        
        # Create system message
        system_msg = BaseMessage.make_assistant_message(
            role_name=config.name,
            content=config.system_message
        )
        
        # Create agent
        agent = ChatAgent(
            system_message=system_msg,
            model=model,
            tools=tools if tools else None
        )
        
        # Store agent
        self.agents[config.name] = agent
        
        return agent
    
    def get_agent(self, name: str) -> Optional[ChatAgent]:
        """Get existing agent by name"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all created agents"""
        return list(self.agents.keys())

class CamelSocietyManager:
    """Manages Camel-AI Societies and RolePlaying scenarios"""
    
    def __init__(self, agent_factory: CamelAgentFactory):
        self.agent_factory = agent_factory
        self.societies = {}
        self.active_scenarios = {}
    
    def create_role_playing_society(self, 
                                  scenario_name: str,
                                  task_prompt: str,
                                  user_role_config: CamelAgentConfig,
                                  assistant_role_config: CamelAgentConfig,
                                  max_turns: int = 10) -> 'RolePlaying':
        """Create a RolePlaying society"""
        if not CAMEL_AVAILABLE:
            raise RuntimeError("Camel-AI not available")
        
        # Create agents
        user_agent = self.agent_factory.create_agent(user_role_config)
        assistant_agent = self.agent_factory.create_agent(assistant_role_config)
        
        # Create society
        society = RolePlaying(
            task_prompt=task_prompt,
            user_role_name=user_role_config.name,
            assistant_role_name=assistant_role_config.name,
            user_agent_kwargs={'model': user_agent.model},
            assistant_agent_kwargs={'model': assistant_agent.model},
            with_task_specify=True,
            max_turns=max_turns
        )
        
        self.societies[scenario_name] = society
        return society
    
    async def run_society_conversation(self, 
                                     society: 'RolePlaying', 
                                     scenario_name: str) -> Dict[str, Any]:
        """Run a society conversation and return results"""
        if not CAMEL_AVAILABLE:
            return {"error": "Camel-AI not available"}
        
        results = {
            "scenario_name": scenario_name,
            "start_time": datetime.now().isoformat(),
            "messages": [],
            "success": False,
            "error": None
        }
        
        try:
            # Initialize conversation
            input_msg = society.init_chat()
            results["messages"].append({
                "type": "initialization",
                "content": input_msg.content if hasattr(input_msg, 'content') else str(input_msg),
                "timestamp": datetime.now().isoformat()
            })
            
            # Run conversation loop
            for turn in range(society.max_turns):
                try:
                    assistant_response, user_response = society.step(input_msg)
                    
                    # Record responses
                    results["messages"].extend([
                        {
                            "type": "assistant_response",
                            "turn": turn,
                            "content": assistant_response.msg.content,
                            "terminated": assistant_response.terminated,
                            "timestamp": datetime.now().isoformat()
                        },
                        {
                            "type": "user_response", 
                            "turn": turn,
                            "content": user_response.msg.content,
                            "terminated": user_response.terminated,
                            "timestamp": datetime.now().isoformat()
                        }
                    ])
                    
                    # Check termination
                    if assistant_response.terminated or user_response.terminated:
                        results["termination_reason"] = "Agent terminated"
                        break
                    
                    # Check for task completion
                    if 'CAMEL_TASK_DONE' in user_response.msg.content:
                        results["termination_reason"] = "Task completed"
                        break
                    
                    # Prepare next input
                    input_msg = assistant_response.msg
                    
                except Exception as e:
                    results["error"] = f"Conversation error at turn {turn}: {str(e)}"
                    break
            
            results["success"] = True
            results["total_turns"] = len([m for m in results["messages"] if m["type"] in ["assistant_response", "user_response"]]) // 2
            
        except Exception as e:
            results["error"] = f"Society conversation failed: {str(e)}"
        
        results["end_time"] = datetime.now().isoformat()
        return results

class CamelWorkforceManager:
    """Manages Camel-AI Workforce for complex multi-agent tasks"""
    
    def __init__(self, agent_factory: CamelAgentFactory):
        self.agent_factory = agent_factory
        self.workforces = {}
        self.active_tasks = {}
    
    def create_workforce(self, 
                        name: str,
                        agent_configs: List[CamelAgentConfig]) -> Optional['Workforce']:
        """Create a Workforce with multiple agents"""
        if not WORKFORCE_AVAILABLE:
            logging.warning("Workforce functionality not available")
            return None
        
        try:
            workforce = Workforce(name)
            
            # Add agents to workforce
            for config in agent_configs:
                agent = self.agent_factory.create_agent(config)
                workforce.add_single_agent_worker(config.name, worker=agent)
            
            self.workforces[name] = workforce
            return workforce
            
        except Exception as e:
            logging.error(f"Failed to create workforce: {e}")
            return None
    
    async def execute_workforce_task(self, 
                                   workforce_name: str,
                                   task_description: str,
                                   task_id: str = None) -> Dict[str, Any]:
        """Execute a task using the workforce"""
        if workforce_name not in self.workforces:
            return {"error": f"Workforce '{workforce_name}' not found"}
        
        if not WORKFORCE_AVAILABLE:
            return {"error": "Workforce functionality not available"}
        
        workforce = self.workforces[workforce_name]
        
        # Create task
        task_id = task_id or f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        task = Task(content=task_description, id=task_id)
        
        results = {
            "task_id": task_id,
            "workforce_name": workforce_name,
            "start_time": datetime.now().isoformat(),
            "success": False,
            "error": None
        }
        
        try:
            # Execute task
            self.active_tasks[task_id] = task
            result = workforce.process_task(task)
            
            results.update({
                "success": True,
                "result": result,
                "end_time": datetime.now().isoformat()
            })
            
        except Exception as e:
            results["error"] = f"Workforce execution failed: {str(e)}"
        
        return results

class CamelIntegrationManager:
    """Main integration manager for Camel-AI functionality"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/camel_config.json"
        self.config = self._load_config()
        
        # Initialize managers
        self.model_manager = CamelModelManager()
        self.agent_factory = CamelAgentFactory(self.model_manager)
        self.society_manager = CamelSocietyManager(self.agent_factory)
        
        if WORKFORCE_AVAILABLE:
            self.workforce_manager = CamelWorkforceManager(self.agent_factory)
        else:
            self.workforce_manager = None
        
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
        config_file = Path(self.config_path)
        
        # Default configuration
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
                },
                "analyst": {
                    "role": "data analysis and visualization", 
                    "tools": ["math", "excel"],
                    "system_message": "You are a data analyst expert at extracting insights from complex data."
                },
                "communicator": {
                    "role": "communication and coordination",
                    "tools": ["notion"],
                    "system_message": "You are a communication specialist focused on clear, effective interaction."
                }
            },
            "society_templates": {
                "research_collaboration": {
                    "user_role": "researcher",
                    "assistant_role": "analyst",
                    "max_turns": 15
                },
                "development_pair": {
                    "user_role": "developer",
                    "assistant_role": "researcher", 
                    "max_turns": 20
                }
            }
        }
        
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
            logging.error("Cannot initialize: Camel-AI not available")
            return False
        
        try:
            # Create default agents from templates
            for agent_name, template in self.config["agent_templates"].items():
                config = CamelAgentConfig(
                    name=agent_name,
                    role=template["role"],
                    tools=template["tools"],
                    system_message=template["system_message"],
                    **self.config["default_model"]
                )
                
                agent = self.agent_factory.create_agent(config)
                self.integration_status["agents_created"] += 1
                logging.info(f"Created Camel agent: {agent_name}")
            
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
        """Process an enhanced prompt using Camel-AI agents"""
        try:
            # Get the enhanced prompt
            prompt = enhanced_prompts.get_prompt(prompt_id, **variables)
            
            # Select appropriate agent
            if agent_name is None:
                # Auto-select based on prompt category
                prompt_info = enhanced_prompts.get_prompt_info(prompt_id)
                category = prompt_info["category"]
                
                # Map categories to agents
                category_mapping = {
                    PromptCategory.RESEARCH_ANALYSIS: "researcher",
                    PromptCategory.CODE_GENERATION: "developer", 
                    PromptCategory.SYSTEM_ARCHITECTURE: "developer",
                    PromptCategory.COMMUNICATION: "communicator",
                    PromptCategory.TASK_DECOMPOSITION: "analyst"
                }
                
                agent_name = category_mapping.get(category, "researcher")
            
            # Get agent
            agent = self.agent_factory.get_agent(agent_name)
            if not agent:
                return {"error": f"Agent '{agent_name}' not found"}
            
            # Process prompt
            user_message = BaseMessage.make_user_message(
                role_name="User",
                content=prompt
            )
            
            response = agent.step(user_message)
            
            return {
                "success": True,
                "prompt_id": prompt_id,
                "agent_name": agent_name,
                "response": response.msgs[0].content if response.msgs else "No response",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to process prompt: {str(e)}"}
    
    async def create_intelligent_society(self, 
                                       task_description: str,
                                       complexity: str = "medium") -> Dict[str, Any]:
        """Create and run an intelligent society for a task"""
        try:
            # Analyze task to determine best society configuration
            if "research" in task_description.lower():
                template = "research_collaboration"
            elif "develop" in task_description.lower() or "code" in task_description.lower():
                template = "development_pair"
            else:
                template = "research_collaboration"  # Default
            
            society_template = self.config["society_templates"][template]
            
            # Create role configurations
            user_config = CamelAgentConfig(
                name=f"User_{society_template['user_role']}",
                role=self.config["agent_templates"][society_template["user_role"]]["role"],
                tools=self.config["agent_templates"][society_template["user_role"]]["tools"],
                **self.config["default_model"]
            )
            
            assistant_config = CamelAgentConfig(
                name=f"Assistant_{society_template['assistant_role']}", 
                role=self.config["agent_templates"][society_template["assistant_role"]]["role"],
                tools=self.config["agent_templates"][society_template["assistant_role"]]["tools"],
                **self.config["default_model"]
            )
            
            # Create society
            scenario_name = f"intelligent_society_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            society = self.society_manager.create_role_playing_society(
                scenario_name=scenario_name,
                task_prompt=task_description,
                user_role_config=user_config,
                assistant_role_config=assistant_config,
                max_turns=society_template["max_turns"]
            )
            
            self.integration_status["societies_created"] += 1
            
            # Run society conversation
            results = await self.society_manager.run_society_conversation(society, scenario_name)
            
            return results
            
        except Exception as e:
            return {"error": f"Failed to create intelligent society: {str(e)}"}
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status"""
        return self.integration_status.copy()
    
    def list_available_features(self) -> Dict[str, List[str]]:
        """List all available features"""
        features = {
            "agents": self.agent_factory.list_agents(),
            "toolkits": list(self.agent_factory.toolkit_registry.keys()),
            "societies": list(self.society_manager.societies.keys()),
            "prompt_categories": [cat.value for cat in PromptCategory],
            "agent_templates": list(self.config["agent_templates"].keys()),
            "society_templates": list(self.config["society_templates"].keys())
        }
        
        if self.workforce_manager:
            features["workforces"] = list(self.workforce_manager.workforces.keys())
        
        return features

# Global integration instance
camel_integration = CamelIntegrationManager()

async def initialize_camel_integration() -> bool:
    """Initialize global Camel-AI integration"""
    return await camel_integration.initialize()

def get_camel_integration() -> CamelIntegrationManager:
    """Get the global Camel-AI integration manager"""
    return camel_integration
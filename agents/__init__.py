"""
🤖 Agentic AI System - Agents Module
Centralized agent imports and registry
Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

__version__ = "2.0.0"
__author__ = "Mulky Malikul Dhaher"
__description__ = "Autonomous Multi-Agent Intelligence System"

import importlib

# Global agents registry
AGENTS_REGISTRY = {}

# A list of agent modules to attempt to import
AGENT_MODULES = [
    "cybershell",
    "agent_maker",
    "ui_designer",
    "dev_engine",
    "data_sync",
    "fullstack_dev",
    "meta_agent_creator",
    "system_optimizer",
    "code_executor",
    "ai_research_agent",
    "credential_manager",
    "authentication_agent",
    "llm_provider_manager",
]

def initialize_agents(llm_provider):
    """
    Initializes all agents and populates the AGENTS_REGISTRY.
    This function should be called at startup.
    """
    global AGENTS_REGISTRY
    
    # First, initialize the dev_engine as it's a dependency for others
    try:
        dev_engine_module = importlib.import_module(".dev_engine", package="agents")
        DevEngineAgent = getattr(dev_engine_module, "DevEngineAgent")
        dev_engine_agent = DevEngineAgent(llm_provider=llm_provider)
        AGENTS_REGISTRY['dev_engine'] = dev_engine_agent
        print("✅ Dev Engine Agent initialized.")
    except (ImportError, AttributeError) as e:
        print(f"⚠️ Could not initialize DevEngineAgent: {e}")
        dev_engine_agent = None

    # Initialize other agents
    for module_name in AGENT_MODULES:
        if module_name in AGENTS_REGISTRY: # Skip already initialized
            continue
        try:
            module = importlib.import_module(f".{module_name}", package="agents")
            
            # Heuristic to find the agent class and instance name
            class_name = "".join(word.capitalize() for word in module_name.split('_')) + "Agent"
            instance_name = module_name + "_agent"
            
            if hasattr(module, class_name):
                AgentClass = getattr(module, class_name)
                
                # Check for dependencies
                if module_name == "ui_designer":
                    agent_instance = AgentClass(llm_provider=llm_provider, dev_engine=dev_engine_agent)
                else:
                    # Assuming other agents might need llm_provider
                    try:
                        agent_instance = AgentClass(llm_provider=llm_provider)
                    except TypeError:
                        agent_instance = AgentClass()

                AGENTS_REGISTRY[module_name] = agent_instance
            elif hasattr(module, instance_name):
                 # For modules that still expose a global instance
                 AGENTS_REGISTRY[module_name] = getattr(module, instance_name)

        except ImportError as e:
            print(f"ℹ️ Agent module not found: {module_name} ({e})")
        except AttributeError as e:
            print(f"⚠️ Agent class not found in module: {module_name} ({e})")
        except Exception as e:
            print(f"🔥 Failed to load agent {module_name}: {e}")

    print(f"✅ Agents module loaded - {len(AGENTS_REGISTRY)} agents available")

# Agent metadata for UI
AGENTS_METADATA = {
    'cybershell': {
        'name': 'CyberShell Agent',
        'emoji': '🖥️',
        'description': 'Advanced shell execution and system management',
        'category': 'system'
    },
    'agent_maker': {
        'name': 'Agent Maker',
        'emoji': '🤖',
        'description': 'Creates new agents from prompts and specifications',
        'category': 'development'
    },
    'ui_designer': {
        'name': 'UI Designer',
        'emoji': '🎨',
        'description': 'React/Tailwind component generation and UI design',
        'category': 'development'
    },
    'dev_engine': {
        'name': 'Dev Engine',
        'emoji': '⚙️',
        'description': 'Project setup, scaffolding, and development automation',
        'category': 'development'
    },
    'data_sync': {
        'name': 'Data Sync',
        'emoji': '🔄',
        'description': 'Multi-database synchronization and data management',
        'category': 'data'
    },
    'fullstack_dev': {
        'name': 'Full Stack Developer',
        'emoji': '🚀',
        'description': 'Complete application development and deployment',
        'category': 'development'
    },
    'meta_agent_creator': {
        'name': 'Meta Agent Creator',
        'emoji': '🎭',
        'description': 'AI that creates other specialized AI agents dynamically',
        'category': 'ai'
    },
    'system_optimizer': {
        'name': 'System Optimizer',
        'emoji': '⚡',
        'description': 'Autonomous system optimization and performance enhancement',
        'category': 'system'
    },
    'code_executor': {
        'name': 'Code Executor',
        'emoji': '💻',
        'description': 'Multi-language code execution environment like Replit',
        'category': 'development'
    },
    'ai_research_agent': {
        'name': 'AI Research Agent',
        'emoji': '🔬',
        'description': 'Research and analyze cutting-edge AI technologies',
        'category': 'ai'
    },
    'credential_manager': {
        'name': 'Credential Manager',
        'emoji': '🔐',
        'description': 'Secure storage and management of credentials with enterprise encryption',
        'category': 'security'
    },
    'authentication_agent': {
        'name': 'Authentication Agent',
        'emoji': '🔑',
        'description': 'Automatic login and registration across multiple platforms',
        'category': 'security'
    },
    'llm_provider_manager': {
        'name': 'LLM Provider Manager',
        'emoji': '🧠',
        'description': 'Multi-provider AI gateway with automatic failover and cost optimization',
        'category': 'ai'
    }
}

def get_agent_by_id(agent_id: str):
    """Get agent instance by ID"""
    return AGENTS_REGISTRY.get(agent_id)

def get_all_agents():
    """Get all agent instances"""
    return AGENTS_REGISTRY

def get_agents_list():
    """Get agents list with metadata for API"""
    agents_list = []
    
    for agent_id, agent in AGENTS_REGISTRY.items():
        metadata = AGENTS_METADATA.get(agent_id, {})
        
        agent_info = {
            'id': agent_id,
            'name': metadata.get('name', agent_id.replace('_', ' ').title()),
            'emoji': metadata.get('emoji', '🤖'),
            'description': metadata.get('description', 'AI Agent'),
            'category': metadata.get('category', 'general'),
            'status': getattr(agent, 'status', 'ready'),
            'capabilities': getattr(agent, 'capabilities', [])
        }
        
        # Get performance metrics if available
        if hasattr(agent, 'get_performance_metrics'):
            try:
                metrics = agent.get_performance_metrics()
                agent_info['metrics'] = metrics
            except:
                pass
        
        agents_list.append(agent_info)
    
    return agents_list

# Legacy imports for compatibility
__all__ = [
    'initialize_agents',
    'AGENTS_REGISTRY',
    'AGENTS_METADATA', 
    'get_agent_by_id',
    'get_all_agents',
    'get_agents_list'
]

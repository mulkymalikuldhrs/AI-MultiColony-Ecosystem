"""
🤖 Agentic AI System - Agents Module
Centralized agent imports and registry
Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

__version__ = "2.0.0"
__author__ = "Mulky Malikul Dhaher"
__description__ = "Autonomous Multi-Agent Intelligence System"

# Import all agents
try:
    from .cybershell import cybershell_agent
except ImportError:
    cybershell_agent = None

try:
    from .agent_maker import agent_maker
except ImportError:
    agent_maker = None

try:
    from .ui_designer import ui_designer_agent
except ImportError:
    ui_designer_agent = None

try:
    from .dev_engine import dev_engine_agent
except ImportError:
    dev_engine_agent = None

try:
    from .data_sync import data_sync_agent
except ImportError:
    data_sync_agent = None

try:
    from .fullstack_dev import fullstack_dev_agent
except ImportError:
    fullstack_dev_agent = None

try:
    from .meta_agent_creator import meta_agent_creator
except ImportError:
    meta_agent_creator = None

try:
    from .system_optimizer import system_optimizer
except ImportError:
    system_optimizer = None

try:
    from .code_executor import code_executor
except ImportError:
    code_executor = None

try:
    from .ai_research_agent import ai_research_agent
except ImportError:
    ai_research_agent = None

try:
    from .credential_manager import credential_manager
except ImportError:
    credential_manager = None

try:
    from .authentication_agent import authentication_agent
except ImportError:
    authentication_agent = None

try:
    from .llm_provider_manager import llm_provider_manager
except ImportError:
    llm_provider_manager = None

try:
    from .bug_hunter import bug_hunter_agent
except ImportError:
    bug_hunter_agent = None

try:
    from .colony_agents import colony_agent_factory, agent_general_factory
except ImportError:
    colony_agent_factory = None
    agent_general_factory = None

# Global agents registry
AGENTS_REGISTRY = {}

# Add agents that were successfully imported
if cybershell_agent:
    AGENTS_REGISTRY['cybershell'] = cybershell_agent
if agent_maker:
    AGENTS_REGISTRY['agent_maker'] = agent_maker
if ui_designer_agent:
    AGENTS_REGISTRY['ui_designer'] = ui_designer_agent
if dev_engine_agent:
    AGENTS_REGISTRY['dev_engine'] = dev_engine_agent
if data_sync_agent:
    AGENTS_REGISTRY['data_sync'] = data_sync_agent
if fullstack_dev_agent:
    AGENTS_REGISTRY['fullstack_dev'] = fullstack_dev_agent
if meta_agent_creator:
    AGENTS_REGISTRY['meta_agent_creator'] = meta_agent_creator
if system_optimizer:
    AGENTS_REGISTRY['system_optimizer'] = system_optimizer
if code_executor:
    AGENTS_REGISTRY['code_executor'] = code_executor
if ai_research_agent:
    AGENTS_REGISTRY['ai_research_agent'] = ai_research_agent
if credential_manager:
    AGENTS_REGISTRY['credential_manager'] = credential_manager
if authentication_agent:
    AGENTS_REGISTRY['authentication_agent'] = authentication_agent
if llm_provider_manager:
    AGENTS_REGISTRY['llm_provider_manager'] = llm_provider_manager
if bug_hunter_agent:
    AGENTS_REGISTRY['bug_hunter'] = bug_hunter_agent
if colony_agent_factory:
    AGENTS_REGISTRY['colony'] = colony_agent_factory
if agent_general_factory:
    AGENTS_REGISTRY['general'] = agent_general_factory

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
    },
    'bug_hunter': {
        'name': 'Bug Hunter Bot',
        'emoji': '🐞',
        'description': 'Autonomous ethical-hacking agent that discovers vulnerabilities & emails site owners',
        'category': 'security'
    },
    'colony': {
        'name': 'Colony Agent',
        'emoji': '🌍',
        'description': 'Self-governing AI colony node with its own Mayor & elites',
        'category': 'ai'
    },
    'general': {
        'name': 'Agent General',
        'emoji': '🎖️',
        'description': 'High-level strategist supervising multiple colonies',
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

print(f"✅ Agents module loaded - {len(AGENTS_REGISTRY)} agents available")

# Legacy imports for compatibility
__all__ = [
    'AGENTS_REGISTRY',
    'AGENTS_METADATA', 
    'get_agent_by_id',
    'get_all_agents',
    'get_agents_list'
]

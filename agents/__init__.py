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

# New agents from cursor/fix branch integration
try:
    from .agi_colony_connector import agi_colony_connector
except ImportError:
    agi_colony_connector = None

try:
    from .backup_colony_system import backup_colony_system
except ImportError:
    backup_colony_system = None

try:
    from .bug_hunter_bot import bug_hunter_bot
except ImportError:
    bug_hunter_bot = None

try:
    from .commander_agi import commander_agi
except ImportError:
    commander_agi = None

try:
    from .deployment_specialist import deployment_specialist
except ImportError:
    deployment_specialist = None

try:
    from .knowledge_management_agent import knowledge_management_agent
except ImportError:
    knowledge_management_agent = None

try:
    from .marketing_agent import marketing_agent
except ImportError:
    marketing_agent = None

try:
    from .money_making_agent import money_making_agent
except ImportError:
    money_making_agent = None

try:
    from .quality_control_specialist import quality_control_specialist
except ImportError:
    quality_control_specialist = None

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
# New agents from cursor/fix integration
if agi_colony_connector:
    AGENTS_REGISTRY['agi_colony_connector'] = agi_colony_connector
if backup_colony_system:
    AGENTS_REGISTRY['backup_colony_system'] = backup_colony_system
if bug_hunter_bot:
    AGENTS_REGISTRY['bug_hunter_bot'] = bug_hunter_bot
if commander_agi:
    AGENTS_REGISTRY['commander_agi'] = commander_agi
if deployment_specialist:
    AGENTS_REGISTRY['deployment_specialist'] = deployment_specialist
if knowledge_management_agent:
    AGENTS_REGISTRY['knowledge_management_agent'] = knowledge_management_agent
if marketing_agent:
    AGENTS_REGISTRY['marketing_agent'] = marketing_agent
if money_making_agent:
    AGENTS_REGISTRY['money_making_agent'] = money_making_agent
if quality_control_specialist:
    AGENTS_REGISTRY['quality_control_specialist'] = quality_control_specialist

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
    # New agents from cursor/fix integration
    'agi_colony_connector': {
        'name': 'AGI Colony Connector',
        'emoji': '🌐',
        'description': 'Inter-colony communication and secure networking',
        'category': 'networking'
    },
    'backup_colony_system': {
        'name': 'Backup Colony System',
        'emoji': '🔄',
        'description': 'Distributed backup management and system redundancy',
        'category': 'infrastructure'
    },
    'bug_hunter_bot': {
        'name': 'Bug Hunter Bot',
        'emoji': '🕷️',
        'description': 'Ethical hacking and vulnerability discovery',
        'category': 'security'
    },
    'commander_agi': {
        'name': 'Commander AGI',
        'emoji': '🛡️',
        'description': 'Security monitoring and robotics coordination',
        'category': 'security'
    },
    'deployment_specialist': {
        'name': 'Deployment Specialist',
        'emoji': '🚀',
        'description': 'Autonomous colony deployment and expansion',
        'category': 'infrastructure'
    },
    'knowledge_management_agent': {
        'name': 'Knowledge Management Agent',
        'emoji': '🧠',
        'description': 'Advanced memory and intelligent data organization',
        'category': 'ai'
    },
    'marketing_agent': {
        'name': 'Marketing Agent',
        'emoji': '📈',
        'description': 'Automated promotion and outreach system',
        'category': 'business'
    },
    'money_making_agent': {
        'name': 'Money Making Agent',
        'emoji': '💰',
        'description': 'Autonomous revenue generation and financial optimization',
        'category': 'business'
    },
    'quality_control_specialist': {
        'name': 'Quality Control Specialist',
        'emoji': '🔍',
        'description': 'Visual and analytical assessment and quality validation',
        'category': 'quality'
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

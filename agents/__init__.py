"""
🤖 Agentic AI System - Agents Module
Centralized agent imports and registry
Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

__version__ = "2.0.0"
__author__ = "Mulky Malikul Dhaher"
__description__ = "Autonomous Multi-Agent Intelligence System"

# Import all agents with error handling
agents_imported = []
import_errors = []

# Core agents
try:
    from .cybershell import cybershell_agent
    agents_imported.append('cybershell')
except ImportError as e:
    cybershell_agent = None
    import_errors.append(f'cybershell: {e}')

try:
    from .agent_maker import agent_maker
    agents_imported.append('agent_maker')
except ImportError as e:
    agent_maker = None
    import_errors.append(f'agent_maker: {e}')

try:
    from .ui_designer import ui_designer_agent
    agents_imported.append('ui_designer')
except ImportError as e:
    ui_designer_agent = None
    import_errors.append(f'ui_designer: {e}')

try:
    from .dev_engine import dev_engine_agent
    agents_imported.append('dev_engine')
except ImportError as e:
    dev_engine_agent = None
    import_errors.append(f'dev_engine: {e}')

try:
    from .data_sync import data_sync_agent
    agents_imported.append('data_sync')
except ImportError as e:
    data_sync_agent = None
    import_errors.append(f'data_sync: {e}')

try:
    from .fullstack_dev import fullstack_dev_agent
    agents_imported.append('fullstack_dev')
except ImportError as e:
    fullstack_dev_agent = None
    import_errors.append(f'fullstack_dev: {e}')

try:
    from .commander_agi import commander_agi
    agents_imported.append('commander_agi')
except ImportError as e:
    commander_agi = None
    import_errors.append(f'commander_agi: {e}')

try:
    from .authentication_agent import authentication_agent
    agents_imported.append('authentication')
except ImportError as e:
    authentication_agent = None
    import_errors.append(f'authentication: {e}')

try:
    from .knowledge_management_agent import knowledge_management_agent
    agents_imported.append('knowledge_manager')
except ImportError as e:
    knowledge_management_agent = None
    import_errors.append(f'knowledge_manager: {e}')

try:
    from .backup_colony_system import backup_colony_system
    agents_imported.append('backup_colony')
except ImportError as e:
    backup_colony_system = None
    import_errors.append(f'backup_colony: {e}')

try:
    from .marketing_agent import marketing_agent
    agents_imported.append('marketing')
except ImportError as e:
    marketing_agent = None
    import_errors.append(f'marketing: {e}')

try:
    from .quality_control_specialist import quality_control_specialist
    agents_imported.append('quality_control')
except ImportError as e:
    quality_control_specialist = None
    import_errors.append(f'quality_control: {e}')

try:
    from .bug_hunter_bot import bug_hunter_bot
    agents_imported.append('bug_hunter')
except ImportError as e:
    bug_hunter_bot = None
    import_errors.append(f'bug_hunter: {e}')

try:
    from .money_making_agent import money_making_agent
    agents_imported.append('money_maker')
except ImportError as e:
    money_making_agent = None
    import_errors.append(f'money_maker: {e}')

# Additional agents
try:
    from .meta_agent_creator import meta_agent_creator
    agents_imported.append('meta_agent_creator')
except ImportError as e:
    meta_agent_creator = None
    import_errors.append(f'meta_agent_creator: {e}')

try:
    from .system_optimizer import system_optimizer
    agents_imported.append('system_optimizer')
except ImportError as e:
    system_optimizer = None
    import_errors.append(f'system_optimizer: {e}')

try:
    from .code_executor import code_executor
    agents_imported.append('code_executor')
except ImportError as e:
    code_executor = None
    import_errors.append(f'code_executor: {e}')

try:
    from .ai_research_agent import ai_research_agent
    agents_imported.append('ai_research_agent')
except ImportError as e:
    ai_research_agent = None
    import_errors.append(f'ai_research_agent: {e}')

try:
    from .credential_manager import credential_manager
    agents_imported.append('credential_manager')
except ImportError as e:
    credential_manager = None
    import_errors.append(f'credential_manager: {e}')

try:
    from .llm_provider_manager import llm_provider_manager
    agents_imported.append('llm_provider_manager')
except ImportError as e:
    llm_provider_manager = None
    import_errors.append(f'llm_provider_manager: {e}')

try:
    from .prompt_generator import prompt_generator
    agents_imported.append('prompt_generator')
except ImportError as e:
    prompt_generator = None
    import_errors.append(f'prompt_generator: {e}')

try:
    from .deploy_manager import deploy_manager
    agents_imported.append('deploy_manager')
except ImportError as e:
    deploy_manager = None
    import_errors.append(f'deploy_manager: {e}')

# Global agents registry
AGENTS_REGISTRY = {}

# Add agents that were successfully imported
for agent_name in agents_imported:
    agent_var = globals().get(f"{agent_name}_agent") or globals().get(agent_name)
    if agent_var:
        AGENTS_REGISTRY[agent_name] = agent_var

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
    'commander_agi': {
        'name': 'Commander AGI',
        'emoji': '🛡️',
        'description': 'Security monitoring and agent coordination',
        'category': 'security'
    },
    'authentication': {
        'name': 'Authentication Agent',
        'emoji': '🔑',
        'description': 'Automatic login and registration across platforms',
        'category': 'security'
    },
    'knowledge_manager': {
        'name': 'Knowledge Manager',
        'emoji': '�',
        'description': 'Knowledge base management and retrieval',
        'category': 'data'
    },
    'backup_colony': {
        'name': 'Backup Colony',
        'emoji': '�',
        'description': 'Distributed backup and data recovery system',
        'category': 'system'
    },
    'marketing': {
        'name': 'Marketing Agent',
        'emoji': '�',
        'description': 'Digital marketing and content creation',
        'category': 'business'
    },
    'quality_control': {
        'name': 'Quality Control',
        'emoji': '🔍',
        'description': 'Code quality analysis and testing',
        'category': 'development'
    },
    'bug_hunter': {
        'name': 'Bug Hunter',
        'emoji': '�',
        'description': 'Automated bug detection and resolution',
        'category': 'development'
    },
    'money_maker': {
        'name': 'Money Maker',
        'emoji': '💰',
        'description': 'Revenue generation and monetization strategies',
        'category': 'business'
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

# Print import status
print(f"✅ Agents module loaded - {len(AGENTS_REGISTRY)} agents available:")
for agent_name in agents_imported:
    print(f"  ✓ {agent_name}")

if import_errors:
    print(f"⚠️  {len(import_errors)} agents failed to import:")
    for error in import_errors:
        print(f"  ✗ {error}")

# Legacy imports for compatibility
__all__ = [
    'AGENTS_REGISTRY',
    'AGENTS_METADATA', 
    'get_agent_by_id',
    'get_all_agents',
    'get_agents_list'
]

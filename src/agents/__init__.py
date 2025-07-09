"""Agent implementations and initialization for the Agentic AI System"""

from typing import Dict, Any, Optional

# Import agent classes
from .agent_base import AgentBase
from .agent_02_meta_spawner import Agent02MetaSpawner
from .agent_03_planner import Agent03Planner
from .agent_04_executor import Agent04Executor
from .agent_05_designer import Agent05Designer
from .agent_06_specialist import Agent06Specialist
from .dynamic_agent_factory import DynamicAgentFactory
from .deployment_agent import DeploymentAgent
from .output_handler import OutputHandler
from .web_automation_agent import WebAutomationAgent

# Agent registry
AGENTS_REGISTRY: Dict[str, Any] = {}

def initialize_agents(llm_provider: Optional[Any] = None):
    """Initializes and registers all core agents."""
    print("Initializing core agents...")

    # Instantiate core agents
    # Assuming agents access llm_gateway globally or via other means
    # If agents need llm_provider directly, their constructors need modification
    try:
        agent_base = AgentBase()
        AGENTS_REGISTRY[agent_base.agent_id] = agent_base
        print(f"  ✅ Initialized {agent_base.name} ({agent_base.agent_id})")

        agent_meta_spawner = Agent02MetaSpawner()
        AGENTS_REGISTRY[agent_meta_spawner.agent_id] = agent_meta_spawner
        print(f"  ✅ Initialized {agent_meta_spawner.name} ({agent_meta_spawner.agent_id})")

        agent_planner = Agent03Planner()
        AGENTS_REGISTRY[agent_planner.agent_id] = agent_planner
        print(f"  ✅ Initialized {agent_planner.name} ({agent_planner.agent_id})")

        agent_executor = Agent04Executor()
        AGENTS_REGISTRY[agent_executor.agent_id] = agent_executor
        print(f"  ✅ Initialized {agent_executor.name} ({agent_executor.agent_id})")

        agent_designer = Agent05Designer()
        AGENTS_REGISTRY[agent_designer.agent_id] = agent_designer
        print(f"  ✅ Initialized {agent_designer.name} ({agent_designer.agent_id})")

        agent_specialist = Agent06Specialist()
        AGENTS_REGISTRY[agent_specialist.agent_id] = agent_specialist
        print(f"  ✅ Initialized {agent_specialist.name} ({agent_specialist.agent_id})")

        agent_factory = DynamicAgentFactory()
        AGENTS_REGISTRY[agent_factory.agent_id] = agent_factory
        print(f"  ✅ Initialized {agent_factory.name} ({agent_factory.agent_id})")

        agent_deployment = DeploymentAgent()
        AGENTS_REGISTRY[agent_deployment.agent_id] = agent_deployment
        print(f"  ✅ Initialized {agent_deployment.name} ({agent_deployment.agent_id})")

        output_handler = OutputHandler()
        AGENTS_REGISTRY[output_handler.agent_id] = output_handler
        print(f"  ✅ Initialized {output_handler.name} ({output_handler.agent_id})")

        web_automation_agent = WebAutomationAgent()
        AGENTS_REGISTRY[web_automation_agent.agent_id] = web_automation_agent
        print(f"  ✅ Initialized {web_automation_agent.name} ({web_automation_agent.agent_id})")

        print(f"✅ All {len(AGENTS_REGISTRY)} core agents initialized and registered.")

    except Exception as e:
        print(f"❌ Error initializing agents: {e}")
        import traceback
        traceback.print_exc()

# Note: DynamicAIAgent is intended for dynamic creation, not initial loading.
# LauncherAgent might be part of the launcher itself, not a standard agent in the registry.

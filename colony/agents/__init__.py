"""
🤖 Agentic AI System - Agents Module
Multi-Agent Intelligence Registry and Initialization

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

import importlib
import os
import sys
from pathlib import Path
from typing import Any, Dict

# Agent registry to store all active agents
AGENTS_REGISTRY: Dict[str, Any] = {}


def initialize_agents(llm_provider=None):
    """
    Initialize all agents and register them in the global registry
    Enhanced with Camel AI integration
    """
    print("🤖 Initializing Ultimate AGI Force agents...")

    # Define agents to initialize with their modules
    agents_config = {
        "cybershell": ("cybershell", "CyberShellAgent"),
        "agent_maker": ("agent_maker", "AgentMakerAgent"),
        "ui_designer": ("ui_designer", "UIDesignerAgent"),
        "dev_engine": ("dev_engine", "DevEngineAgent"),
        "data_sync": ("data_sync", "DataSyncAgent"),
        "fullstack_dev": ("fullstack_dev", "FullStackDevAgent"),
        "deploy_manager": ("deploy_manager", "DeployManagerAgent"),
        "prompt_generator": ("prompt_generator", "PromptGeneratorAgent"),
        "marketing_agent": ("marketing_agent", "MarketingAgent"),
        "money_making_agent": ("money_making_agent", "MoneyMakingAgent"),
        "meta_agent_creator": ("meta_agent_creator", "MetaAgentCreatorAgent"),
        "quality_control_specialist": (
            "quality_control_specialist",
            "QualityControlSpecialistAgent",
        ),
        "system_optimizer": ("system_optimizer", "SystemOptimizerAgent"),
        "deployment_specialist": ("deployment_specialist", "DeploymentSpecialistAgent"),
        "knowledge_management_agent": (
            "knowledge_management_agent",
            "KnowledgeManagementAgent",
        ),
        "llm_provider_manager": ("llm_provider_manager", "LLMProviderManagerAgent"),
        "backup_colony_system": ("backup_colony_system", "BackupColonySystemAgent"),
        "bug_hunter_bot": ("bug_hunter_bot", "BugHunterBotAgent"),
        "code_executor": ("code_executor", "CodeExecutorAgent"),
        "commander_agi": ("commander_agi", "CommanderAGIAgent"),
        "credential_manager": ("credential_manager", "CredentialManagerAgent"),
        "agi_colony_connector": ("agi_colony_connector", "AGIColonyConnectorAgent"),
        "ai_research_agent": ("ai_research_agent", "AIResearchAgent"),
        "authentication_agent": ("authentication_agent", "AuthenticationAgent"),
    }

    # Initialize each agent
    for agent_id, (module_name, class_name) in agents_config.items():
        try:
            # Import the module
            module = importlib.import_module(f"agents.{module_name}")

            # Get the agent class
            agent_class = getattr(module, class_name)

            # Initialize the agent
            if llm_provider:
                # Try to pass llm_provider to agents that support it
                try:
                    agent_instance = agent_class(llm_provider=llm_provider)
                except TypeError:
                    # Fallback to no parameters if agent doesn't accept llm_provider
                    agent_instance = agent_class()
            else:
                agent_instance = agent_class()

            # Ensure agent has required attributes
            if not hasattr(agent_instance, "agent_id"):
                agent_instance.agent_id = agent_id
            if not hasattr(agent_instance, "name"):
                agent_instance.name = class_name
            if not hasattr(agent_instance, "status"):
                agent_instance.status = "ready"

            # Register the agent
            AGENTS_REGISTRY[agent_id] = agent_instance
            print(f"  ✅ {agent_id}: {class_name} ready")

        except ImportError as e:
            print(f"  ⚠️ {agent_id}: Module import failed - {e}")
        except AttributeError as e:
            print(f"  ⚠️ {agent_id}: Class not found - {e}")
        except Exception as e:
            print(f"  ❌ {agent_id}: Initialization failed - {e}")

    # Initialize Camel AI Agent with special handling
    try:
        from agents.camel_agent_integration import camel_agent

        # Register camel agent
        AGENTS_REGISTRY["camel_agent"] = camel_agent
        print(f"  🐪 camel_agent: Camel AI Collaborative Agent ready")

        # Add camel integration to existing agents
        _integrate_camel_capabilities()

    except ImportError as e:
        print(f"  ⚠️ camel_agent: Import failed - {e}")
    except Exception as e:
        print(f"  ❌ camel_agent: Initialization failed - {e}")

    print(f"🎉 Agent initialization complete! {len(AGENTS_REGISTRY)} agents active")
    print(f"👑 All agents loyal to: Mulky Malikul Dhaher (1108151509970001)")

    return AGENTS_REGISTRY


def _integrate_camel_capabilities():
    """Integrate Camel AI capabilities into existing agents"""
    print("🐪 Integrating Camel AI capabilities into agents...")

    camel_agent = AGENTS_REGISTRY.get("camel_agent")
    if not camel_agent:
        return

    # Add collaborative methods to agents that can benefit
    collaborative_agents = [
        "dev_engine",
        "fullstack_dev",
        "ui_designer",
        "system_optimizer",
        "quality_control_specialist",
        "meta_agent_creator",
        "deployment_specialist",
    ]

    for agent_id in collaborative_agents:
        agent = AGENTS_REGISTRY.get(agent_id)
        if agent and not hasattr(agent, "start_collaboration"):
            # Add collaboration method
            def create_collaboration_method(agent_instance):
                async def start_collaboration(topic, complexity="medium"):
                    """Start collaboration with Camel AI"""
                    task_data = {
                        "content": f"Collaborate on: {topic} (from {agent_instance.name})",
                        "complexity": complexity,
                        "initiating_agent": agent_instance.agent_id,
                    }
                    return await camel_agent.process_task(task_data)

                return start_collaboration

            agent.start_collaboration = create_collaboration_method(agent)

            # Mark as camel-integrated
            if not hasattr(agent, "capabilities"):
                agent.capabilities = []
            if "camel_collaboration" not in agent.capabilities:
                agent.capabilities.append("camel_collaboration")

    print(
        f"  � {len(collaborative_agents)} agents enhanced with Camel AI collaboration"
    )


def get_agent(agent_id: str):
    """Get an agent by ID"""
    return AGENTS_REGISTRY.get(agent_id)


def get_all_agents():
    """Get all registered agents"""
    return AGENTS_REGISTRY.copy()


def get_agents_by_capability(capability: str):
    """Get agents that have a specific capability"""
    return {
        agent_id: agent
        for agent_id, agent in AGENTS_REGISTRY.items()
        if hasattr(agent, "capabilities") and capability in agent.capabilities
    }


def get_camel_integrated_agents():
    """Get all agents that support Camel AI collaboration"""
    return get_agents_by_capability("camel_collaboration")


def list_agent_capabilities():
    """List all unique capabilities across all agents"""
    capabilities = set()
    for agent in AGENTS_REGISTRY.values():
        if hasattr(agent, "capabilities"):
            capabilities.update(agent.capabilities)
    return sorted(list(capabilities))


def get_system_stats():
    """Get system statistics"""
    active_agents = len(
        [
            a
            for a in AGENTS_REGISTRY.values()
            if hasattr(a, "status") and a.status == "ready"
        ]
    )
    camel_integrated = len(get_camel_integrated_agents())

    return {
        "total_agents": len(AGENTS_REGISTRY),
        "active_agents": active_agents,
        "camel_integrated_agents": camel_integrated,
        "unique_capabilities": len(list_agent_capabilities()),
        "agent_list": list(AGENTS_REGISTRY.keys()),
    }


# Create simplified agent classes for missing modules
class SimpleAgent:
    """Base simple agent for fallback"""

    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.status = "ready"
        self.capabilities = ["basic_processing"]
        self.owner_identity = "1108151509970001"
        self.owner_name = "Mulky Malikul Dhaher"

    def process_task(self, task_data):
        """Basic task processing"""
        return {
            "success": True,
            "message": f"Task processed by {self.name}",
            "agent": self.agent_id,
        }


# Export main registry
__all__ = [
    "AGENTS_REGISTRY",
    "initialize_agents",
    "get_agent",
    "get_all_agents",
    "get_agents_by_capability",
    "get_camel_integrated_agents",
    "list_agent_capabilities",
    "get_system_stats",
    "SimpleAgent",
]

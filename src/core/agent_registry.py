"""
Centralized Agent Registry
"""

# Import all agent instances
from agents.agent_maker import agent_maker
from agents.ai_research_agent import ai_research_agent
from agents.authentication_agent import authentication_agent
from agents.auto_deployment_system import auto_deployment_system
from agents.autonomous_maintainer import autonomous_maintainer
from agents.code_executor import code_executor
from agents.credential_manager import credential_manager
from agents.cybershell import cybershell_agent
from agents.data_sync import data_sync_agent
from agents.deploy_manager import deploy_manager
from agents.dev_engine import dev_engine_agent
from agents.fullstack_dev import fullstack_dev_agent
from agents.llm_provider_manager import llm_provider_manager
from agents.meta_agent_creator import meta_agent_creator
from agents.prompt_generator import prompt_generator
from agents.specialist_agents import specialist_agents
from agents.system_optimizer import system_optimizer
from agents.system_supervisor import system_supervisor
from agents.ui_designer import ui_designer_agent

# Centralized agent registry
agent_registry = {
    "agent_maker": agent_maker,
    "ai_research_agent": ai_research_agent,
    "authentication_agent": authentication_agent,
    "auto_deployment_system": auto_deployment_system,
    "autonomous_maintainer": autonomous_maintainer,
    "code_executor": code_executor,
    "credential_manager": credential_manager,
    "cybershell": cybershell_agent,
    "data_sync": data_sync_agent,
    "deploy_manager": deploy_manager,
    "dev_engine": dev_engine_agent,
    "fullstack_dev": fullstack_dev_agent,
    "llm_provider_manager": llm_provider_manager,
    "meta_agent_creator": meta_agent_creator,
    "prompt_generator": prompt_generator,
    "specialist_agents": specialist_agents,
    "system_optimizer": system_optimizer,
    "system_supervisor": system_supervisor,
    "ui_designer": ui_designer_agent,
}

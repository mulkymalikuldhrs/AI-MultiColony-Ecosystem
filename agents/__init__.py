"""
🧠 Agentic AI System - Agents Module
Autonomous Multi-Agent Intelligence System

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

__version__ = "2.0.0"
__author__ = "Mulky Malikul Dhaher"
__description__ = "Autonomous Multi-Agent Intelligence System"

# Import all agents for easy access
from .cybershell import CyberShellAgent
from .ui_designer import UIDesignerAgent  
from .dev_engine import DevEngineAgent
from .agent_maker import AgentMakerAgent
from .data_sync import DataSyncAgent
from .prompt_generator import PromptGeneratorAgent
from .fullstack_dev import FullStackDevAgent
from .backend_dev import BackendDevAgent
from .frontend_dev import FrontendDevAgent
from .agent_watcher import AgentWatcherAgent
from .marketing_bot import MarketingBotAgent
from .voice_agent import VoiceAgent
from .github_agent import GitHubAgent
from .google_agent import GoogleAgent
from .web3_plugin import Web3Agent
from .deploy_manager import DeployManagerAgent

__all__ = [
    'CyberShellAgent',
    'UIDesignerAgent', 
    'DevEngineAgent',
    'AgentMakerAgent',
    'DataSyncAgent',
    'PromptGeneratorAgent',
    'FullStackDevAgent',
    'BackendDevAgent',
    'FrontendDevAgent',
    'AgentWatcherAgent',
    'MarketingBotAgent',
    'VoiceAgent',
    'GitHubAgent',
    'GoogleAgent',
    'Web3Agent',
    'DeployManagerAgent'
]

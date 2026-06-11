"""Agents module for the AI MultiColony Ecosystem.

Exports the AgentRegistry, AgentFactory, and all agent types for
discovery, creation, and management of agents across the colony.
"""

from ai_multicolony.agents.registry import AgentRegistry, AgentFactory
from ai_multicolony.agents.manus.agent import ToolCallAgent, ManusAgent
from ai_multicolony.agents.planner.agent import PlannerAgent
from ai_multicolony.agents.executor.agent import ExecutorAgent
from ai_multicolony.agents.coder.agent import CoderAgent
from ai_multicolony.agents.browser.agent import BrowserAgent
from ai_multicolony.agents.voice.agent import VoiceAgent
from ai_multicolony.agents.security.agent import SecurityAgent
from ai_multicolony.agents.researcher.agent import ResearcherAgent
from ai_multicolony.agents.colony.agent import ColonyAgent

__all__ = [
    "AgentRegistry",
    "AgentFactory",
    "ToolCallAgent",
    "ManusAgent",
    "PlannerAgent",
    "ExecutorAgent",
    "CoderAgent",
    "BrowserAgent",
    "VoiceAgent",
    "SecurityAgent",
    "ResearcherAgent",
    "ColonyAgent",
]

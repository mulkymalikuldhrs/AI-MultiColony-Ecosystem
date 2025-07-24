"""
🧠 Agentic AI System - Core Module
Central Intelligence and Coordination System

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩
"""

from .prompt_master import PromptMasterAgent, prompt_master
from .memory_bus import MemoryBusAgent, memory_bus
from .sync_engine import SyncEngineAgent, sync_engine
from .scheduler import SchedulerAgent, agent_scheduler
from .ai_selector import AISelectorAgent, ai_selector

# Import LLM client with error handling
try:
    from .llm_client import LLMClient, llm_client, LLMResponse
    llm_client_available = True
except ImportError as e:
    LLMClient = None
    llm_client = None
    LLMResponse = None
    llm_client_available = False
    print(f"⚠️  LLM Client not available: {e}")

__all__ = [
    'PromptMasterAgent',
    'prompt_master',
    'MemoryBusAgent', 
    'memory_bus',
    'SyncEngineAgent',
    'sync_engine',
    'SchedulerAgent',
    'agent_scheduler',
    'AISelectorAgent',
    'ai_selector',
    'LLMClient',
    'llm_client',
    'LLMResponse',
    'llm_client_available'
]

print(f"✅ Core module loaded - LLM client: {'available' if llm_client_available else 'unavailable'}")

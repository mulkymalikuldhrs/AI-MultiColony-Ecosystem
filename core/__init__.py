"""
Agentic AI System - Core Module
Central Intelligence and Coordination System

Made with love by Mulky Malikul Dhaher in Indonesia
"""

from .ai_selector import AISelector

# Safe imports - these may fail if optional dependencies are missing
try:
    from .prompt_master import PromptMasterAgent
except ImportError as e:
    PromptMasterAgent = None
    print(f"Warning: PromptMasterAgent not available: {e}")

try:
    from .memory_bus import MemoryBus
except ImportError as e:
    MemoryBus = None
    print(f"Warning: MemoryBus not available: {e}")

try:
    from .sync_engine import SyncEngine
except ImportError as e:
    SyncEngine = None
    print(f"Warning: SyncEngine not available: {e}")

try:
    from .scheduler import AgentScheduler
except ImportError as e:
    AgentScheduler = None
    print(f"Warning: AgentScheduler not available: {e}")

try:
    from .error_recovery import ErrorRecoverySystem
except ImportError:
    ErrorRecoverySystem = None

# New module from cursor/fix integration
try:
    from .llm_client import LLMClient
except ImportError:
    LLMClient = None

__all__ = [
    'PromptMasterAgent',
    'MemoryBus',
    'SyncEngine',
    'AgentScheduler',
    'AISelector',
    'ErrorRecoverySystem',
    'LLMClient'
]

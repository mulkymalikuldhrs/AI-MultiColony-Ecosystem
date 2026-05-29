"""
Agentic AI System - Connectors Module
External service integrations and API gateways

Made with love by Mulky Malikul Dhaher in Indonesia
"""

from .llm_gateway import LLMGateway

# Safe imports - these may fail if optional dependencies are missing
try:
    from .audio_stream import AudioStreamProcessor
except ImportError:
    AudioStreamProcessor = None

try:
    from .google_integration import GoogleIntegration
except ImportError:
    GoogleIntegration = None

try:
    from .github_integration import GitHubIntegration
except ImportError:
    GitHubIntegration = None

try:
    from .web3_plugin import Web3Plugin
except ImportError:
    Web3Plugin = None

__all__ = [
    'LLMGateway',
    'AudioStreamProcessor',
    'GoogleIntegration',
    'GitHubIntegration',
    'Web3Plugin'
]

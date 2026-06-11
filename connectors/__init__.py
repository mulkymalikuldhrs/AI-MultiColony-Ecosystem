"""
Agentic AI System - Connectors Module
External service integrations and API gateways

Made with love by Mulky Malikul Dhaher in Indonesia

.. deprecated::
    This module is deprecated. Use ``src.integrations`` instead.
    The top-level ``connectors/`` package will be removed in a future release.
"""

import warnings

warnings.warn(
    "The top-level 'connectors' package is deprecated. Import from 'src.integrations' instead. "
    "The 'connectors/' directory will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .llm_gateway import LLMGateway

# These connectors are not yet implemented but planned
AudioStreamProcessor = None
GoogleIntegration = None
GitHubIntegration = None
Web3Plugin = None

__all__ = [
    'LLMGateway',
    'AudioStreamProcessor',
    'GoogleIntegration',
    'GitHubIntegration',
    'Web3Plugin'
]

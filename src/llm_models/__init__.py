"""LLM model provider abstractions.

Provides factory-based creation of chat models for various LLM providers
including OpenAI, Claude, vLLM, MindIE, and patched variants.

Consolidated from deer-flow models/.
"""

from src.llm_models.factory import create_chat_model

__all__ = ["create_chat_model"]

"""Coder agent module."""

from ai_multicolony.agents.coder.agent import CoderAgent

# Re-export from the flat coder.py for backward compatibility
try:
    from ai_multicolony.agents.coder import coder as _coder_flat

    CodeArtifact = getattr(_coder_flat, "CodeArtifact", None)
except (ImportError, AttributeError):
    CodeArtifact = None  # type: ignore[misc,assignment]

__all__ = ["CoderAgent"]

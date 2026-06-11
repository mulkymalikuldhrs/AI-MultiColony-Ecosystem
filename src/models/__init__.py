"""Compatibility shim — use src.llm_models instead.

This module re-exports everything from src.llm_models so that existing code
using ``from src.models import ...`` continues to work during the migration.

.. deprecated::
    Import from :mod:`src.llm_models` instead. This shim will be removed in
    a future release.
"""

import sys
import warnings

warnings.warn(
    "src.models is deprecated; import from src.llm_models instead.",
    DeprecationWarning,
    stacklevel=2,
)

try:
    from src.llm_models import *  # noqa: F401,F403

    # Re-export key symbols explicitly for IDE discoverability
    from src.llm_models import create_chat_model  # noqa: F401

    # Register submodules in sys.modules so ``from src.models.assistant_payload_replay import ...``
    # resolves correctly through the compatibility shim.
    _SUBMODULE_MAP = {
        "src.models.factory": "src.llm_models.factory",
        "src.models.assistant_payload_replay": "src.llm_models.assistant_payload_replay",
        "src.models.credential_loader": "src.llm_models.credential_loader",
        "src.models.openai_codex_provider": "src.llm_models.openai_codex_provider",
        "src.models.patched_openai": "src.llm_models.patched_openai",
        "src.models.patched_stepfun": "src.llm_models.patched_stepfun",
        "src.models.patched_deepseek": "src.llm_models.patched_deepseek",
        "src.models.patched_mimo": "src.llm_models.patched_mimo",
        "src.models.patched_minimax": "src.llm_models.patched_minimax",
        "src.models.claude_provider": "src.llm_models.claude_provider",
        "src.models.vllm_provider": "src.llm_models.vllm_provider",
        "src.models.mindie_provider": "src.llm_models.mindie_provider",
    }

    for _alias, _real in _SUBMODULE_MAP.items():
        if _real in sys.modules:
            sys.modules[_alias] = sys.modules[_real]

except ImportError:
    # langchain or other optional deps not available — shim degrades gracefully
    pass

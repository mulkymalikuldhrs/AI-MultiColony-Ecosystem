"""Compatibility shim — use src.df_tools instead.

This module re-exports everything from src.df_tools so that existing code
using ``from src.tools import ...`` continues to work during the migration.

.. deprecated::
    Import from :mod:`src.df_tools` instead. This shim will be removed in
    a future release.
"""

import sys
import warnings

warnings.warn(
    "src.tools is deprecated; import from src.df_tools instead.",
    DeprecationWarning,
    stacklevel=2,
)

try:
    from src.df_tools import *  # noqa: F401,F403

    # Re-export __all__ from df_tools if available
    try:
        from src.df_tools import __all__ as __all__  # noqa: F401
    except ImportError:
        pass

    # Register submodules in sys.modules so ``from src.tools.builtins import ...``
    # resolves correctly through the compatibility shim.
    _SUBMODULE_MAP = {
        "src.tools.sync": "src.df_tools.sync",
        "src.tools.types": "src.df_tools.types",
        "src.tools.mcp_metadata": "src.df_tools.mcp_metadata",
        "src.tools.skill_manage_tool": "src.df_tools.skill_manage_tool",
        "src.tools.builtins": "src.df_tools.builtins",
    }

    # Top-level submodule registration
    for _alias, _real in _SUBMODULE_MAP.items():
        if _real in sys.modules:
            sys.modules[_alias] = sys.modules[_real]

    # Builtins sub-submodule registration (lazy — only if already loaded)
    _BUILTIN_SUBS = [
        "tool_search",
        "task_tool",
        "present_file_tool",
        "view_image_tool",
        "clarification_tool",
        "setup_agent_tool",
        "update_agent_tool",
        "invoke_acp_agent_tool",
    ]
    for _sub in _BUILTIN_SUBS:
        _real_key = f"src.df_tools.builtins.{_sub}"
        _alias_key = f"src.tools.builtins.{_sub}"
        if _real_key in sys.modules:
            sys.modules[_alias_key] = sys.modules[_real_key]

except ImportError:
    # langchain or other optional deps not available — shim degrades gracefully
    pass

"""compat_deps.py
Utility to monkey-patch `sys.modules` with lightweight stubs for heavy optional
third-party libraries that may not be installed in minimal environments.
This allows importing modules that `import psutil`, `redis`, etc. without
raising `ModuleNotFoundError`. Each stub prints a warning on first attribute
access to remind developers to install the real package in production.
"""
from __future__ import annotations

import sys
from types import ModuleType
from typing import Set

# List of optional heavy dependencies
OPTIONAL_DEPS: Set[str] = {
    "psutil",
    "redis",
    "docker",
    "cryptography",
    "cv2",  # opencv-python
    "aiohttp",
    "boto3",
    "transformers",
    "matplotlib",
    "numpy",
    "websockets",
}


class _StubModule(ModuleType):
    """Very lightweight stub that warns on attribute access."""

    __all__ = []

    def __getattr__(self, item):  # noqa: D401, ANN001
        print(f"⚠️  Optional dependency stub accessed: {self.__name__}.{item}. "
              "Install the real package for full functionality.")
        raise AttributeError(f"Stub for optional dependency {self.__name__} has no attribute {item}")


for dep in OPTIONAL_DEPS:
    if dep not in sys.modules:
        sys.modules[dep] = _StubModule(dep)
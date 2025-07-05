"""Automatic bootstrap executed by Python if present on PYTHONPATH.
It imports `src.core.compat_deps` to register stubs for optional heavy
libraries (numpy, psutil, etc.) before any user code imports them.
"""
from importlib import import_module

try:
    import_module("src.core.compat_deps")
except Exception as exc:  # pragma: no cover
    print(f"sitecustomize: unable to load compat_deps: {exc}")
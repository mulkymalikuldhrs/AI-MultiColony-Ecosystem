"""numpy stub (minimal) – allows import numpy as np in environments without numpy.
This stub intentionally raises AttributeError on any attribute use while
providing enough structure for import-time success.
"""
import types
import sys

class _NumpyStub(types.ModuleType):
    def __getattr__(self, item):  # noqa: D401, ANN001
        raise ImportError(
            "Stub numpy module in use – install the real 'numpy' package for full functionality."
        )

sys.modules[__name__] = _NumpyStub(__name__)
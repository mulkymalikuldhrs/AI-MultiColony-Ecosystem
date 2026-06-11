"""Configuration files and templates

.. deprecated::
    This module is deprecated. Use ``src.config`` instead.
    The top-level ``config/`` package will be removed in a future release.
"""

import warnings

warnings.warn(
    "The top-level 'config' package is deprecated. Import from 'src.config' instead. "
    "The 'config/' directory will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

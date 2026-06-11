"""
📊 Database Module - Data Storage and Management
Handles all database operations and configurations

Made with ❤️ by Mulky Malikul Dhaher in Indonesia 🇮🇩

.. deprecated::
    This module is deprecated. Use ``src.persistence`` instead.
    The top-level ``database/`` package will be removed in a future release.
"""

import warnings

warnings.warn(
    "The top-level 'database' package is deprecated. Import from 'src.persistence' instead. "
    "The 'database/' directory will be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)

from .models import *
from .init_db import initialize_database
from .migrations import run_migrations

__all__ = ['initialize_database', 'run_migrations']

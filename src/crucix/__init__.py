"""
Crucix Intelligence Engine — Python port.

Crucix is a multi-source intelligence briefing system that aggregates
OSINT, economic, financial, geopolitical, environmental, and cyber data
from 27+ public APIs, computes deltas between sweeps, and generates
actionable intelligence briefings.

Ported from the original JavaScript/TypeScript implementation at
contrib/crucix/ (Crucix v2.0.0).

Modules:
    briefing: Intelligence briefing generator — the core value of Crucix
    localization: i18n/localization manager with JSON locale files
    gateway: API gateway patterns for serving intelligence data
    data_sources: Data source integration adapters (FRED, GDELT, etc.)
    config: Configuration using pydantic-settings
    delta: Delta engine for computing changes between sweeps
    memory: Hot/cold memory manager for sweep history
"""

__version__ = "2.0.0"
__original__ = "JavaScript/TypeScript — contrib/crucix/"

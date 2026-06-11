"""Browser automation module with stealth capabilities."""

from ai_multicolony.browser.stealth import StealthConfig, StealthBrowser, apply_stealth, get_stealth_script, generate_random_fingerprint
from ai_multicolony.browser.human import HumanBehavior, Mouse, Keyboard, Scroll, human_type, human_click, human_scroll
from ai_multicolony.browser.config import BrowserConfig

__all__ = [
    "StealthConfig", "StealthBrowser", "apply_stealth", "get_stealth_script", "generate_random_fingerprint",
    "HumanBehavior", "Mouse", "Keyboard", "Scroll",
    "human_type", "human_click", "human_scroll",
    "BrowserConfig",
]

"""CloakBrowser stealth integration.

Provides stealth configuration with fingerprint randomization,
anti-detection measures, and proxy support for browser automation.
"""

from __future__ import annotations

import random
import string
from dataclasses import dataclass, field
from typing import Any, Optional

from ai_multicolony.config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class StealthConfig:
    """Configuration for browser stealth mode.

    From CloakBrowser patterns for avoiding bot detection.
    """

    hide_webdriver: bool = True
    mock_languages: list[str] = field(default_factory=lambda: ["en-US", "en"])
    mock_plugins: bool = True
    mock_permissions: bool = True
    randomize_viewport: bool = False
    disable_automation_flags: bool = True
    custom_user_agent: Optional[str] = None
    disable_images: bool = False
    disable_css: bool = False
    extra_headers: dict[str, str] = field(default_factory=dict)

    # Fingerprint randomization
    randomize_canvas: bool = True
    randomize_webgl: bool = True
    randomize_audio: bool = True
    randomize_fonts: bool = True
    randomize_screen: bool = False

    # Anti-detection
    block_webrtc: bool = True
    block_fingerprinting: bool = True
    mask_battery: bool = True
    mask_connection: bool = True

    # Proxy
    proxy_server: Optional[str] = None
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None


# User agents for fingerprint randomization
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

VIEWPORTS = [
    (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
    (1280, 720), (2560, 1440), (1680, 1050), (1280, 800),
]


def generate_random_fingerprint() -> dict[str, Any]:
    """Generate a random browser fingerprint.

    Returns:
        Dictionary with randomized fingerprint data.
    """
    user_agent = random.choice(USER_AGENTS)
    viewport = random.choice(VIEWPORTS)
    platform = "Win32" if "Windows" in user_agent else "MacIntel" if "Mac" in user_agent else "Linux x86_64"

    return {
        "user_agent": user_agent,
        "viewport": {"width": viewport[0], "height": viewport[1]},
        "platform": platform,
        "languages": random.sample(["en-US", "en", "en-GB", "de", "fr", "es", "ja"], k=random.randint(2, 4)),
        "hardware_concurrency": random.choice([2, 4, 8, 12, 16]),
        "device_memory": random.choice([2, 4, 8, 16]),
        "color_depth": random.choice([24, 32]),
        "pixel_ratio": random.choice([1, 1.25, 1.5, 2]),
        "timezone": random.choice([
            "America/New_York", "America/Chicago", "America/Los_Angeles",
            "Europe/London", "Europe/Berlin", "Asia/Tokyo",
        ]),
    }


# JavaScript injection scripts for stealth
STEALTH_SCRIPTS: dict[str, str] = {
    "hide_webdriver": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """,
    "mock_languages": """
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
    """,
    "mock_plugins": """
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
    """,
    "mock_permissions": """
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
    """,
    "disable_automation": """
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
    """,
    "mock_chrome": """
        if (!window.chrome) {
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
        }
    """,
    "block_webrtc": """
        (function() {
            var RTCPeerConnection = window.RTCPeerConnection || window.webkitRTCPeerConnection;
            if (RTCPeerConnection) {
                window.RTCPeerConnection = function() { return null; };
                window.webkitRTCPeerConnection = function() { return null; };
            }
        })();
    """,
    "randomize_canvas": """
        (function() {
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                const context = this.getContext('2d');
                if (context) {
                    const imageData = context.getImageData(0, 0, this.width, this.height);
                    for (let i = 0; i < imageData.data.length; i += 4) {
                        imageData.data[i] += Math.floor(Math.random() * 2) - 1;
                    }
                    context.putImageData(imageData, 0, 0);
                }
                return originalToDataURL.apply(this, arguments);
            };
        })();
    """,
    "randomize_webgl": """
        (function() {
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(param) {
                if (param === 37445) return 'Intel Inc.';
                if (param === 37446) return 'Intel Iris OpenGL Engine';
                return getParameter.apply(this, arguments);
            };
        })();
    """,
    "mask_battery": """
        (function() {
            if (navigator.getBattery) {
                navigator.getBattery = function() {
                    return Promise.resolve({
                        charging: true,
                        chargingTime: 0,
                        dischargingTime: Infinity,
                        level: 1.0,
                        addEventListener: function() {}
                    });
                };
            }
        })();
    """,
    "mask_connection": """
        (function() {
            if (navigator.connection) {
                Object.defineProperty(navigator.connection, 'rtt', { get: () => 50 });
                Object.defineProperty(navigator.connection, 'downlink', { get: () => 10 });
                Object.defineProperty(navigator.connection, 'effectiveType', { get: () => '4g' });
            }
        })();
    """,
}


class StealthBrowser:
    """High-level stealth browser wrapper.

    Combines StealthConfig with Playwright browser management,
    providing a simple API for creating stealth browser sessions
    with fingerprint randomization and anti-detection.
    """

    def __init__(self, config: Optional[StealthConfig] = None) -> None:
        self._config = config or StealthConfig()
        self._fingerprint: Optional[dict[str, Any]] = None
        self._browser: Optional[Any] = None

    async def launch(self, browser_type: str = "chromium") -> Any:
        """Launch a stealth browser instance.

        Args:
            browser_type: Browser type (chromium, firefox, webkit).

        Returns:
            The browser instance.
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ImportError("playwright not installed. Install with: pip install playwright")

        self._fingerprint = generate_random_fingerprint()
        pw = await async_playwright().start()

        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
        ]

        if self._config.block_webrtc:
            launch_args.append("--disable-webrtc")

        launcher = getattr(pw, browser_type)
        kwargs: dict[str, Any] = {
            "headless": True,
            "args": launch_args,
        }

        # Proxy configuration
        if self._config.proxy_server:
            kwargs["proxy"] = {
                "server": self._config.proxy_server,
            }
            if self._config.proxy_username:
                kwargs["proxy"]["username"] = self._config.proxy_username
            if self._config.proxy_password:
                kwargs["proxy"]["password"] = self._config.proxy_password

        self._browser = await launcher.launch(**kwargs)
        return self._browser

    async def new_page(self) -> Any:
        """Create a new stealth page.

        Returns:
            A configured stealth page.
        """
        if not self._browser:
            await self.launch()

        context_kwargs: dict[str, Any] = {}

        if self._fingerprint:
            context_kwargs["user_agent"] = self._fingerprint["user_agent"]
            context_kwargs["viewport"] = self._fingerprint["viewport"]
            context_kwargs["locale"] = self._fingerprint["languages"][0]
            context_kwargs["timezone_id"] = self._fingerprint["timezone"]

        context = await self._browser.new_context(**context_kwargs)
        page = await context.new_page()

        # Apply stealth scripts
        await apply_stealth(page, self._config)

        return page

    async def close(self) -> None:
        """Close the stealth browser."""
        if self._browser:
            await self._browser.close()
            self._browser = None

    @property
    def fingerprint(self) -> Optional[dict[str, Any]]:
        """Get the current fingerprint."""
        return self._fingerprint

    @property
    def config(self) -> StealthConfig:
        """Get the stealth configuration."""
        return self._config


def get_stealth_script(config: Optional[StealthConfig] = None) -> str:
    """Generate a combined stealth injection script.

    Args:
        config: Stealth configuration. Uses defaults if None.

    Returns:
        Combined JavaScript injection script.
    """
    if config is None:
        config = StealthConfig()

    scripts = []

    if config.hide_webdriver:
        scripts.append(STEALTH_SCRIPTS["hide_webdriver"])
    if config.mock_languages:
        scripts.append(STEALTH_SCRIPTS["mock_languages"])
    if config.mock_plugins:
        scripts.append(STEALTH_SCRIPTS["mock_plugins"])
    if config.mock_permissions:
        scripts.append(STEALTH_SCRIPTS["mock_permissions"])
    if config.disable_automation_flags:
        scripts.append(STEALTH_SCRIPTS["disable_automation"])
    scripts.append(STEALTH_SCRIPTS["mock_chrome"])

    if config.block_webrtc:
        scripts.append(STEALTH_SCRIPTS["block_webrtc"])
    if config.randomize_canvas:
        scripts.append(STEALTH_SCRIPTS["randomize_canvas"])
    if config.randomize_webgl:
        scripts.append(STEALTH_SCRIPTS["randomize_webgl"])
    if config.mask_battery:
        scripts.append(STEALTH_SCRIPTS["mask_battery"])
    if config.mask_connection:
        scripts.append(STEALTH_SCRIPTS["mask_connection"])

    return "\n".join(scripts)


async def apply_stealth(page: Any, config: Optional[StealthConfig] = None) -> None:
    """Apply stealth configuration to a Playwright page.

    Args:
        page: The Playwright page object.
        config: Stealth configuration. Uses defaults if None.
    """
    script = get_stealth_script(config)
    await page.add_init_script(script)

    config = config or StealthConfig()

    if config.custom_user_agent:
        await page.set_extra_http_headers({"User-Agent": config.custom_user_agent})

    if config.extra_headers:
        await page.set_extra_http_headers(config.extra_headers)

    if config.disable_images:
        await page.route("**/*.{png,jpg,jpeg,gif,svg,webp}", lambda route: route.abort())

    if config.disable_css:
        await page.route("**/*.css", lambda route: route.abort())

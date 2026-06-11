"""Comprehensive tests for Browser module (stealth, human).

Covers StealthConfig, StealthBrowser, fingerprint randomization,
Mouse, Keyboard, Scroll, and human behavior patterns.
"""

from __future__ import annotations

import asyncio
import random
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_multicolony.browser.stealth import (
    STEALTH_SCRIPTS,
    USER_AGENTS,
    VIEWPORTS,
    StealthBrowser,
    StealthConfig,
    generate_random_fingerprint,
    get_stealth_script,
)
from ai_multicolony.browser.human import (
    HumanBehavior,
    Keyboard,
    Mouse,
    Scroll,
    human_click,
    human_delay,
    human_mouse_move,
    human_scroll,
    human_type,
)


# ============================================================
# StealthConfig Tests
# ============================================================


class TestStealthConfig:
    """Test StealthConfig dataclass."""

    def test_default_values(self):
        config = StealthConfig()
        assert config.hide_webdriver is True
        assert config.mock_languages == ["en-US", "en"]
        assert config.mock_plugins is True
        assert config.mock_permissions is True
        assert config.randomize_viewport is False
        assert config.disable_automation_flags is True
        assert config.custom_user_agent is None
        assert config.disable_images is False
        assert config.disable_css is False

    def test_fingerprint_defaults(self):
        config = StealthConfig()
        assert config.randomize_canvas is True
        assert config.randomize_webgl is True
        assert config.randomize_audio is True
        assert config.randomize_fonts is True
        assert config.randomize_screen is False

    def test_anti_detection_defaults(self):
        config = StealthConfig()
        assert config.block_webrtc is True
        assert config.block_fingerprinting is True
        assert config.mask_battery is True
        assert config.mask_connection is True

    def test_proxy_defaults(self):
        config = StealthConfig()
        assert config.proxy_server is None
        assert config.proxy_username is None
        assert config.proxy_password is None

    def test_custom_proxy(self):
        config = StealthConfig(
            proxy_server="http://proxy:8080",
            proxy_username="user",
            proxy_password="pass",
        )
        assert config.proxy_server == "http://proxy:8080"
        assert config.proxy_username == "user"
        assert config.proxy_password == "pass"

    def test_extra_headers(self):
        config = StealthConfig(extra_headers={"X-Custom": "value"})
        assert config.extra_headers["X-Custom"] == "value"

    def test_custom_user_agent(self):
        config = StealthConfig(custom_user_agent="MyBrowser/1.0")
        assert config.custom_user_agent == "MyBrowser/1.0"

    def test_all_disabled(self):
        config = StealthConfig(
            hide_webdriver=False,
            mock_plugins=False,
            mock_permissions=False,
            randomize_canvas=False,
            randomize_webgl=False,
            randomize_audio=False,
            block_webrtc=False,
            mask_battery=False,
            mask_connection=False,
        )
        assert config.hide_webdriver is False
        assert config.randomize_canvas is False


# ============================================================
# Fingerprint Randomization Tests
# ============================================================


class TestFingerprintRandomization:
    """Test generate_random_fingerprint()."""

    def test_returns_dict(self):
        fp = generate_random_fingerprint()
        assert isinstance(fp, dict)

    def test_has_required_keys(self):
        fp = generate_random_fingerprint()
        required = ["user_agent", "viewport", "platform", "languages",
                     "hardware_concurrency", "device_memory", "color_depth",
                     "pixel_ratio", "timezone"]
        for key in required:
            assert key in fp, f"Missing key: {key}"

    def test_user_agent_from_list(self):
        fp = generate_random_fingerprint()
        assert fp["user_agent"] in USER_AGENTS

    def test_viewport_from_list(self):
        fp = generate_random_fingerprint()
        vp = (fp["viewport"]["width"], fp["viewport"]["height"])
        assert vp in VIEWPORTS

    def test_viewport_structure(self):
        fp = generate_random_fingerprint()
        assert "width" in fp["viewport"]
        assert "height" in fp["viewport"]

    def test_platform_consistency(self):
        """Test that platform matches user agent."""
        fp = generate_random_fingerprint()
        ua = fp["user_agent"]
        if "Windows" in ua:
            assert fp["platform"] == "Win32"
        elif "Mac" in ua:
            assert fp["platform"] == "MacIntel"
        else:
            assert fp["platform"] == "Linux x86_64"

    def test_languages_is_list(self):
        fp = generate_random_fingerprint()
        assert isinstance(fp["languages"], list)
        assert len(fp["languages"]) >= 2

    def test_hardware_concurrency_values(self):
        fp = generate_random_fingerprint()
        assert fp["hardware_concurrency"] in [2, 4, 8, 12, 16]

    def test_device_memory_values(self):
        fp = generate_random_fingerprint()
        assert fp["device_memory"] in [2, 4, 8, 16]

    def test_color_depth_values(self):
        fp = generate_random_fingerprint()
        assert fp["color_depth"] in [24, 32]

    def test_pixel_ratio_values(self):
        fp = generate_random_fingerprint()
        assert fp["pixel_ratio"] in [1, 1.25, 1.5, 2]

    def test_timezone_values(self):
        fp = generate_random_fingerprint()
        valid_timezones = [
            "America/New_York", "America/Chicago", "America/Los_Angeles",
            "Europe/London", "Europe/Berlin", "Asia/Tokyo",
        ]
        assert fp["timezone"] in valid_timezones

    def test_different_fingerprints(self):
        """Verify fingerprints vary across calls (probabilistic)."""
        fps = [generate_random_fingerprint() for _ in range(10)]
        uas = [fp["user_agent"] for fp in fps]
        # With 5 user agents and 10 samples, very likely to have at least 2 different
        assert len(set(uas)) >= 2


class TestConstants:
    """Test module-level constants."""

    def test_user_agents_non_empty(self):
        assert len(USER_AGENTS) > 0

    def test_viewports_non_empty(self):
        assert len(VIEWPORTS) > 0

    def test_stealth_scripts_keys(self):
        expected_keys = {
            "hide_webdriver", "mock_languages", "mock_plugins",
            "mock_permissions", "disable_automation", "mock_chrome",
            "block_webrtc", "randomize_canvas", "randomize_webgl",
            "mask_battery", "mask_connection",
        }
        assert set(STEALTH_SCRIPTS.keys()) == expected_keys

    def test_stealth_scripts_are_strings(self):
        for key, script in STEALTH_SCRIPTS.items():
            assert isinstance(script, str), f"Script {key} is not a string"


# ============================================================
# get_stealth_script Tests
# ============================================================


class TestGetStealthScript:
    """Test get_stealth_script()."""

    def test_default_config_includes_core_scripts(self):
        script = get_stealth_script()
        assert "navigator" in script  # webdriver hiding
        assert "chrome" in script

    def test_no_webdriver_hiding_when_disabled(self):
        config = StealthConfig(hide_webdriver=False)
        script = get_stealth_script(config)
        # Should not contain the webdriver hiding script
        assert "Object.defineProperty(navigator, 'webdriver'" not in script

    def test_includes_webrtc_blocking(self):
        config = StealthConfig(block_webrtc=True)
        script = get_stealth_script(config)
        assert "RTCPeerConnection" in script

    def test_excludes_webrtc_blocking(self):
        config = StealthConfig(block_webrtc=False)
        script = get_stealth_script(config)
        assert "RTCPeerConnection" not in script

    def test_includes_canvas_randomization(self):
        config = StealthConfig(randomize_canvas=True)
        script = get_stealth_script(config)
        assert "toDataURL" in script

    def test_excludes_canvas_randomization(self):
        config = StealthConfig(randomize_canvas=False)
        script = get_stealth_script(config)
        assert "toDataURL" not in script

    def test_includes_webgl_randomization(self):
        config = StealthConfig(randomize_webgl=True)
        script = get_stealth_script(config)
        assert "getParameter" in script

    def test_includes_battery_masking(self):
        config = StealthConfig(mask_battery=True)
        script = get_stealth_script(config)
        assert "getBattery" in script

    def test_includes_connection_masking(self):
        config = StealthConfig(mask_connection=True)
        script = get_stealth_script(config)
        assert "connection" in script

    def test_none_config_uses_defaults(self):
        script = get_stealth_script(None)
        assert "navigator" in script


# ============================================================
# StealthBrowser Tests
# ============================================================


class TestStealthBrowser:
    """Test StealthBrowser (without actually launching browser)."""

    def test_init_default_config(self):
        sb = StealthBrowser()
        assert isinstance(sb._config, StealthConfig)
        assert sb._fingerprint is None
        assert sb._browser is None

    def test_init_custom_config(self):
        config = StealthConfig(disable_images=True, custom_user_agent="Test/1.0")
        sb = StealthBrowser(config=config)
        assert sb._config.disable_images is True
        assert sb._config.custom_user_agent == "Test/1.0"

    def test_fingerprint_property_none(self):
        sb = StealthBrowser()
        assert sb.fingerprint is None

    def test_config_property(self):
        config = StealthConfig(proxy_server="http://proxy:8080")
        sb = StealthBrowser(config=config)
        assert sb.config.proxy_server == "http://proxy:8080"

    def test_is_running_default_false(self):
        sb = StealthBrowser()
        assert sb._browser is None

    async def test_close_without_browser(self):
        sb = StealthBrowser()
        await sb.close()
        assert sb._browser is None

    async def test_close_with_browser(self):
        sb = StealthBrowser()
        mock_browser = AsyncMock()
        sb._browser = mock_browser
        await sb.close()
        mock_browser.close.assert_called_once()
        assert sb._browser is None


# ============================================================
# HumanBehavior Tests
# ============================================================


class TestHumanBehavior:
    """Test HumanBehavior dataclass."""

    def test_defaults(self):
        hb = HumanBehavior()
        assert hb.min_delay == 0.1
        assert hb.max_delay == 0.5
        assert hb.typing_delay_min == 0.05
        assert hb.typing_delay_max == 0.15
        assert hb.scroll_amount_min == 100
        assert hb.scroll_amount_max == 400
        assert hb.mouse_steps_min == 10
        assert hb.mouse_steps_max == 30
        assert hb.click_offset_max == 5

    def test_custom(self):
        hb = HumanBehavior(min_delay=0.2, max_delay=1.0, typing_delay_min=0.1)
        assert hb.min_delay == 0.2
        assert hb.max_delay == 1.0
        assert hb.typing_delay_min == 0.1


# ============================================================
# Mouse Tests
# ============================================================


class TestMouse:
    """Test Mouse class."""

    def test_init(self):
        page = MagicMock()
        mouse = Mouse(page)
        assert mouse._page is page
        assert mouse.position == (0, 0)

    def test_init_with_behavior(self):
        page = MagicMock()
        hb = HumanBehavior(mouse_steps_min=5, mouse_steps_max=10)
        mouse = Mouse(page, behavior=hb)
        assert mouse._behavior.mouse_steps_min == 5

    async def test_move_to_updates_position(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.move = AsyncMock()
        mouse = Mouse(page)
        await mouse.move_to(100, 200, steps=2)
        assert mouse.position == (100, 200)

    async def test_move_to_calls_page_mouse(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.move = AsyncMock()
        mouse = Mouse(page)
        await mouse.move_to(50, 50, steps=3)
        assert page.mouse.move.call_count == 3

    async def test_click_calls_move_and_click(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.move = AsyncMock()
        page.mouse.click = AsyncMock()
        mouse = Mouse(page)
        await mouse.click(100, 200)
        page.mouse.click.assert_called_once()

    async def test_click_with_button(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.move = AsyncMock()
        page.mouse.click = AsyncMock()
        mouse = Mouse(page)
        await mouse.click(100, 200, button="right")
        page.mouse.click.assert_called_with(100, 200, button="right", click_count=1)

    async def test_click_double(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.move = AsyncMock()
        page.mouse.click = AsyncMock()
        mouse = Mouse(page)
        await mouse.click(100, 200, click_count=2)
        page.mouse.click.assert_called_with(100, 200, button="left", click_count=2)

    async def test_click_element_missing(self):
        page = MagicMock()
        page.query_selector = AsyncMock(return_value=None)
        mouse = Mouse(page)
        with pytest.raises(ValueError, match="Element not found"):
            await mouse.click_element(".missing")

    async def test_click_element_no_box(self):
        page = MagicMock()
        element = AsyncMock()
        element.is_visible = AsyncMock(return_value=True)
        element.is_enabled = AsyncMock(return_value=True)
        element.bounding_box = AsyncMock(return_value=None)
        page.query_selector = AsyncMock(return_value=element)
        mouse = Mouse(page)
        with pytest.raises(ValueError, match="bounding box"):
            await mouse.click_element(".no-box")

    async def test_click_element_success(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.move = AsyncMock()
        page.mouse.click = AsyncMock()
        element = AsyncMock()
        element.is_visible = AsyncMock(return_value=True)
        element.is_enabled = AsyncMock(return_value=True)
        element.bounding_box = AsyncMock(return_value={"x": 10, "y": 20, "width": 100, "height": 50})
        page.query_selector = AsyncMock(return_value=element)
        mouse = Mouse(page)
        await mouse.click_element(".btn")
        page.mouse.click.assert_called_once()

    async def test_right_click(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.move = AsyncMock()
        page.mouse.click = AsyncMock()
        mouse = Mouse(page)
        await mouse.right_click(100, 200)
        page.mouse.click.assert_called_with(100, 200, button="right")

    async def test_hover_missing_element(self):
        page = MagicMock()
        page.query_selector = AsyncMock(return_value=None)
        mouse = Mouse(page)
        with pytest.raises(ValueError, match="Element not found"):
            await mouse.hover(".missing")

    async def test_hover_success(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.move = AsyncMock()
        element = AsyncMock()
        element.bounding_box = AsyncMock(return_value={"x": 10, "y": 20, "width": 100, "height": 50})
        page.query_selector = AsyncMock(return_value=element)
        mouse = Mouse(page)
        await mouse.hover(".btn")
        page.mouse.move.assert_called()

    async def test_drag_and_drop_missing_source(self):
        page = MagicMock()
        page.query_selector = AsyncMock(return_value=None)
        mouse = Mouse(page)
        with pytest.raises(ValueError, match="Source or target"):
            await mouse.drag_and_drop(".src", ".tgt")

    async def test_drag_and_drop_success(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.move = AsyncMock()
        page.mouse.down = AsyncMock()
        page.mouse.up = AsyncMock()
        source = AsyncMock()
        source.bounding_box = AsyncMock(return_value={"x": 0, "y": 0, "width": 50, "height": 50})
        target = AsyncMock()
        target.bounding_box = AsyncMock(return_value={"x": 200, "y": 200, "width": 50, "height": 50})
        page.query_selector = AsyncMock(side_effect=[source, target])
        mouse = Mouse(page)
        await mouse.drag_and_drop(".src", ".tgt")
        page.mouse.down.assert_called_once()
        page.mouse.up.assert_called_once()

    async def test_check_actionable_not_visible(self):
        page = MagicMock()
        mouse = Mouse(page)
        element = AsyncMock()
        element.is_visible = AsyncMock(return_value=False)
        with pytest.raises(ValueError, match="not visible"):
            await mouse._check_actionable(element)

    async def test_check_actionable_not_enabled(self):
        page = MagicMock()
        mouse = Mouse(page)
        element = AsyncMock()
        element.is_visible = AsyncMock(return_value=True)
        element.is_enabled = AsyncMock(return_value=False)
        with pytest.raises(ValueError, match="not enabled"):
            await mouse._check_actionable(element)


# ============================================================
# Keyboard Tests
# ============================================================


class TestKeyboard:
    """Test Keyboard class."""

    def test_init(self):
        page = MagicMock()
        kb = Keyboard(page)
        assert kb._page is page

    async def test_type_text_missing_element(self):
        page = MagicMock()
        page.query_selector = AsyncMock(return_value=None)
        kb = Keyboard(page)
        with pytest.raises(ValueError, match="Element not found"):
            await kb.type_text(".input", "hello")

    async def test_type_text_with_clear(self):
        page = MagicMock()
        element = AsyncMock()
        element.click = AsyncMock()
        page.query_selector = AsyncMock(return_value=element)
        page.keyboard = MagicMock()
        page.keyboard.press = AsyncMock()
        page.keyboard.type = AsyncMock()
        kb = Keyboard(page)
        await kb.type_text(".input", "hi", clear=True)
        # Should have pressed Control+a, Backspace, then typed chars
        assert page.keyboard.press.call_count >= 2

    async def test_type_text_without_clear(self):
        page = MagicMock()
        element = AsyncMock()
        element.click = AsyncMock()
        page.query_selector = AsyncMock(return_value=element)
        page.keyboard = MagicMock()
        page.keyboard.press = AsyncMock()
        page.keyboard.type = AsyncMock()
        kb = Keyboard(page)
        await kb.type_text(".input", "hi", clear=False)
        # Should not have pressed Control+a
        assert page.keyboard.press.call_count == 0

    async def test_press_key(self):
        page = MagicMock()
        page.keyboard = MagicMock()
        page.keyboard.press = AsyncMock()
        kb = Keyboard(page)
        await kb.press_key("Enter")
        page.keyboard.press.assert_called_with("Enter")

    async def test_press_shortcut(self):
        page = MagicMock()
        page.keyboard = MagicMock()
        page.keyboard.press = AsyncMock()
        kb = Keyboard(page)
        await kb.press_shortcut("Control", "c")
        page.keyboard.press.assert_called_with("Control+c")

    async def test_type_slowly_missing_element(self):
        page = MagicMock()
        page.query_selector = AsyncMock(return_value=None)
        kb = Keyboard(page)
        with pytest.raises(ValueError, match="Element not found"):
            await kb.type_slowly(".input", "secret")


# ============================================================
# Scroll Tests
# ============================================================


class TestScroll:
    """Test Scroll class."""

    def test_init(self):
        page = MagicMock()
        scroll = Scroll(page)
        assert scroll._page is page

    async def test_down_with_amount(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.wheel = AsyncMock()
        scroll = Scroll(page)
        await scroll.down(200)
        assert page.mouse.wheel.call_count > 0

    async def test_up_with_amount(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.wheel = AsyncMock()
        scroll = Scroll(page)
        await scroll.up(200)
        assert page.mouse.wheel.call_count > 0

    async def test_down_default_amount(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.wheel = AsyncMock()
        scroll = Scroll(page)
        await scroll.down()
        assert page.mouse.wheel.call_count > 0

    async def test_up_default_amount(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.wheel = AsyncMock()
        scroll = Scroll(page)
        await scroll.up()
        assert page.mouse.wheel.call_count > 0

    async def test_to_bottom(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.wheel = AsyncMock()
        scroll = Scroll(page)
        await scroll.to_bottom()
        assert page.mouse.wheel.call_count > 0

    async def test_to_top(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.wheel = AsyncMock()
        scroll = Scroll(page)
        await scroll.to_top()
        assert page.mouse.wheel.call_count > 0

    async def test_to_element(self):
        page = MagicMock()
        element = AsyncMock()
        element.scroll_into_view_if_needed = AsyncMock()
        page.query_selector = AsyncMock(return_value=element)
        scroll = Scroll(page)
        await scroll.to_element(".section")
        element.scroll_into_view_if_needed.assert_called_once()

    async def test_to_element_not_found(self):
        page = MagicMock()
        page.query_selector = AsyncMock(return_value=None)
        scroll = Scroll(page)
        # Should not raise, just skip
        await scroll.to_element(".missing")

    async def test_scroll_incremental(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.wheel = AsyncMock()
        scroll = Scroll(page)
        await scroll._scroll(300, "down")
        # Should have multiple wheel calls (increments)
        assert page.mouse.wheel.call_count >= 2

    async def test_scroll_up_negative_delta(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.wheel = AsyncMock()
        scroll = Scroll(page)
        await scroll._scroll(300, "up")
        # All deltas should be negative for scroll up
        for call in page.mouse.wheel.call_args_list:
            assert call[0][1] <= 0  # second arg is y delta


# ============================================================
# Module-level Function Tests
# ============================================================


class TestModuleFunctions:
    """Test backward-compatible module-level functions."""

    async def test_human_type(self):
        page = MagicMock()
        element = AsyncMock()
        element.click = AsyncMock()
        page.query_selector = AsyncMock(return_value=element)
        page.keyboard = MagicMock()
        page.keyboard.press = AsyncMock()
        page.keyboard.type = AsyncMock()
        await human_type(page, ".input", "hello")

    async def test_human_scroll_down(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.wheel = AsyncMock()
        await human_scroll(page, "down", 200)

    async def test_human_scroll_up(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.wheel = AsyncMock()
        await human_scroll(page, "up", 200)

    async def test_human_click(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.move = AsyncMock()
        page.mouse.click = AsyncMock()
        element = AsyncMock()
        element.is_visible = AsyncMock(return_value=True)
        element.is_enabled = AsyncMock(return_value=True)
        element.bounding_box = AsyncMock(return_value={"x": 10, "y": 20, "width": 100, "height": 50})
        page.query_selector = AsyncMock(return_value=element)
        await human_click(page, ".btn")

    async def test_human_mouse_move(self):
        page = MagicMock()
        page.mouse = MagicMock()
        page.mouse.move = AsyncMock()
        await human_mouse_move(page, 100, 200)

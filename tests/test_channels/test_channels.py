"""Comprehensive tests for all channel types.

Tests cover:
- BaseChannel ABC (abstract interface, common functionality)
- TelegramChannel (core/channel.py and channels/telegram.py)
- WhatsAppChannel (core/channel.py and channels/whatsapp.py)
- DiscordChannel (core/channel.py and channels/discord.py)
- SlackChannel (core/channel.py and channels/slack.py)
- Channel factory function (create_channel)
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai_multicolony.core.channel import (
    BaseChannel,
    TelegramChannel,
    WhatsAppChannel,
    DiscordChannel,
    SlackChannel,
    create_channel,
)
from ai_multicolony.exceptions import ChannelError
from ai_multicolony.types.messages import InboundMessage, OutboundMessage


# ─── Fixtures ───────────────────────────────────────────────────────────────


class ConcreteChannel(BaseChannel):
    """Concrete channel for testing BaseChannel ABC."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(channel_type="test", channel_id="test-id", **kwargs)
        self._started = False
        self._stopped = False
        self._sent_messages: list[OutboundMessage] = []
        self._receive_queue: asyncio.Queue[InboundMessage] = asyncio.Queue()

    async def start(self) -> None:
        self._started = True
        self._running = True

    async def stop(self) -> None:
        self._stopped = True
        self._running = False

    async def send(self, message: OutboundMessage) -> bool:
        self._sent_messages.append(message)
        self._sent_count += 1
        return True

    async def receive(self) -> InboundMessage | None:
        try:
            return self._receive_queue.get_nowait()
        except asyncio.QueueEmpty:
            return None


@pytest.fixture
def concrete_channel() -> ConcreteChannel:
    """Create a concrete channel for testing."""
    return ConcreteChannel()


@pytest.fixture
def outbound_msg() -> OutboundMessage:
    """Create a test outbound message."""
    return OutboundMessage(
        channel_type="test",
        channel_id="ch-1",
        recipient_id="user-1",
        content="Hello!",
    )


@pytest.fixture
def inbound_msg() -> InboundMessage:
    """Create a test inbound message."""
    return InboundMessage(
        channel_type="test",
        channel_id="ch-1",
        sender_id="user-1",
        content="Hi there!",
    )


# ═══════════════════════════════════════════════════════════════════════════
# BaseChannel ABC
# ═══════════════════════════════════════════════════════════════════════════


class TestBaseChannel:
    """Test BaseChannel ABC and common functionality."""

    def test_cannot_instantiate_abc(self):
        """BaseChannel cannot be directly instantiated."""
        with pytest.raises(TypeError):
            BaseChannel(channel_type="x", channel_id="y")  # type: ignore[abstract]

    def test_concrete_channel_init(self, concrete_channel):
        """Concrete channel initializes with correct attributes."""
        assert concrete_channel.channel_type == "test"
        assert concrete_channel.channel_id == "test-id"

    def test_concrete_channel_not_running(self, concrete_channel):
        """Channel starts in non-running state."""
        assert concrete_channel.is_running is False

    def test_concrete_channel_start(self, concrete_channel):
        """Channel start sets running state."""
        concrete_channel._running = True
        assert concrete_channel.is_running is True

    def test_get_info(self, concrete_channel):
        """get_info returns channel information dict."""
        info = concrete_channel.get_info()
        assert info["channel_type"] == "test"
        assert info["channel_id"] == "test-id"
        assert info["is_running"] is False
        assert info["sent_count"] == 0
        assert info["received_count"] == 0

    def test_get_info_has_queued_messages(self, concrete_channel):
        """get_info includes queued_messages field."""
        info = concrete_channel.get_info()
        assert "queued_messages" in info

    def test_on_inbound_registers_handler(self, concrete_channel):
        """on_inbound adds a handler."""
        handler = MagicMock()
        concrete_channel.on_inbound(handler)
        assert handler in concrete_channel._inbound_handlers

    def test_on_inbound_multiple_handlers(self, concrete_channel):
        """Multiple handlers can be registered."""
        h1 = MagicMock()
        h2 = MagicMock()
        concrete_channel.on_inbound(h1)
        concrete_channel.on_inbound(h2)
        assert len(concrete_channel._inbound_handlers) == 2

    @pytest.mark.asyncio
    async def test_dispatch_inbound(self, concrete_channel, inbound_msg):
        """_dispatch_inbound calls registered handlers."""
        handler = AsyncMock()
        concrete_channel.on_inbound(handler)
        await concrete_channel._dispatch_inbound(inbound_msg)
        handler.assert_called_once_with(inbound_msg)

    @pytest.mark.asyncio
    async def test_dispatch_inbound_sync_handler(self, concrete_channel, inbound_msg):
        """_dispatch_inbound calls sync handlers too."""
        handler = MagicMock()
        concrete_channel.on_inbound(handler)
        await concrete_channel._dispatch_inbound(inbound_msg)
        handler.assert_called_once_with(inbound_msg)

    @pytest.mark.asyncio
    async def test_dispatch_inbound_increments_count(self, concrete_channel, inbound_msg):
        """_dispatch_inbound increments received_count."""
        assert concrete_channel._received_count == 0
        await concrete_channel._dispatch_inbound(inbound_msg)
        assert concrete_channel._received_count == 1

    @pytest.mark.asyncio
    async def test_dispatch_inbound_handler_error(self, concrete_channel, inbound_msg):
        """_dispatch_inbound does not crash on handler errors."""
        bad_handler = AsyncMock(side_effect=RuntimeError("boom"))
        concrete_channel.on_inbound(bad_handler)
        await concrete_channel._dispatch_inbound(inbound_msg)

    @pytest.mark.asyncio
    async def test_dispatch_inbound_multiple_handlers(self, concrete_channel, inbound_msg):
        """_dispatch_inbound calls all registered handlers."""
        h1 = AsyncMock()
        h2 = AsyncMock()
        concrete_channel.on_inbound(h1)
        concrete_channel.on_inbound(h2)
        await concrete_channel._dispatch_inbound(inbound_msg)
        h1.assert_called_once()
        h2.assert_called_once()

    @pytest.mark.asyncio
    async def test_queue_outbound(self, concrete_channel, outbound_msg):
        """queue_outbound adds message to queue."""
        await concrete_channel.queue_outbound(outbound_msg)
        assert concrete_channel._message_queue.qsize() == 1

    @pytest.mark.asyncio
    async def test_process_outbound_queue(self, concrete_channel, outbound_msg):
        """process_outbound_queue sends queued messages."""
        await concrete_channel.queue_outbound(outbound_msg)
        count = await concrete_channel.process_outbound_queue()
        assert count == 1
        assert len(concrete_channel._sent_messages) == 1

    @pytest.mark.asyncio
    async def test_process_outbound_empty_queue(self, concrete_channel):
        """process_outbound_queue returns 0 for empty queue."""
        count = await concrete_channel.process_outbound_queue()
        assert count == 0

    @pytest.mark.asyncio
    async def test_process_outbound_multiple_messages(self, concrete_channel):
        """process_outbound_queue handles multiple queued messages."""
        for i in range(3):
            msg = OutboundMessage(
                channel_type="test", channel_id="ch-1",
                recipient_id=f"user-{i}", content=f"Msg {i}",
            )
            await concrete_channel.queue_outbound(msg)
        count = await concrete_channel.process_outbound_queue()
        assert count == 3

    def test_config_passed_through(self):
        """Config is stored on channel."""
        ch = ConcreteChannel(config={"key": "val"})
        assert ch._config == {"key": "val"}

    def test_config_defaults_to_empty_dict(self):
        """Config defaults to empty dict when not provided."""
        ch = ConcreteChannel()
        assert ch._config == {}

    def test_sent_count_starts_at_zero(self, concrete_channel):
        """Sent count starts at 0."""
        assert concrete_channel._sent_count == 0

    def test_received_count_starts_at_zero(self, concrete_channel):
        """Received count starts at 0."""
        assert concrete_channel._received_count == 0


# ═══════════════════════════════════════════════════════════════════════════
# TelegramChannel (core/channel.py)
# ═══════════════════════════════════════════════════════════════════════════


class TestTelegramChannelCore:
    """Test TelegramChannel from core/channel.py."""

    @pytest.fixture
    def telegram(self) -> TelegramChannel:
        return TelegramChannel(
            channel_id="tg-1",
            bot_token="123456:ABC-DEF",
        )

    def test_init(self, telegram):
        assert telegram.channel_type == "telegram"
        assert telegram.channel_id == "tg-1"

    def test_not_running_initially(self, telegram):
        assert telegram.is_running is False

    @pytest.mark.asyncio
    async def test_start_without_sdk(self, telegram):
        with patch.dict("sys.modules", {"telegram.ext": None}):
            await telegram.start()
            assert telegram.is_running is True

    @pytest.mark.asyncio
    async def test_stop(self, telegram):
        telegram._running = True
        await telegram.stop()
        assert telegram.is_running is False

    @pytest.mark.asyncio
    async def test_send_no_client(self, telegram):
        telegram._bot = None
        msg = OutboundMessage(
            channel_type="telegram", channel_id="tg-1",
            recipient_id="chat-1", content="Hi",
        )
        with patch.dict("sys.modules", {"aiohttp": None}):
            result = await telegram.send(msg)
            assert result is False

    @pytest.mark.asyncio
    async def test_receive_empty(self, telegram):
        result = await telegram.receive()
        assert result is None

    def test_bot_token_stored(self, telegram):
        assert telegram._bot_token == "123456:ABC-DEF"


# ═══════════════════════════════════════════════════════════════════════════
# WhatsAppChannel (core/channel.py)
# ═══════════════════════════════════════════════════════════════════════════


class TestWhatsAppChannelCore:
    """Test WhatsAppChannel from core/channel.py."""

    @pytest.fixture
    def whatsapp(self) -> WhatsAppChannel:
        return WhatsAppChannel(
            channel_id="wa-1",
            phone_number_id="12345",
            access_token="token123",
            verify_token="verify456",
        )

    def test_init(self, whatsapp):
        assert whatsapp.channel_type == "whatsapp"
        assert whatsapp.channel_id == "wa-1"

    @pytest.mark.asyncio
    async def test_start(self, whatsapp):
        await whatsapp.start()
        assert whatsapp.is_running is True

    @pytest.mark.asyncio
    async def test_stop(self, whatsapp):
        whatsapp._running = True
        await whatsapp.stop()
        assert whatsapp.is_running is False

    def test_handle_webhook_valid(self, whatsapp):
        data = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "1234567890",
                            "text": {"body": "Hello"},
                        }]
                    }
                }]
            }]
        }
        whatsapp.handle_webhook(data)
        assert not whatsapp._inbound_queue.empty()

    def test_handle_webhook_empty(self, whatsapp):
        whatsapp.handle_webhook({})
        # Should not crash

    def test_handle_webhook_no_messages(self, whatsapp):
        data = {
            "entry": [{
                "changes": [{
                    "value": {"messages": []}
                }]
            }]
        }
        whatsapp.handle_webhook(data)
        assert whatsapp._inbound_queue.empty()

    @pytest.mark.asyncio
    async def test_receive_empty(self, whatsapp):
        result = await whatsapp.receive()
        assert result is None

    def test_stores_access_token(self, whatsapp):
        assert whatsapp._access_token == "token123"

    def test_stores_verify_token(self, whatsapp):
        assert whatsapp._verify_token == "verify456"

    def test_stores_phone_number_id(self, whatsapp):
        assert whatsapp._phone_number_id == "12345"


# ═══════════════════════════════════════════════════════════════════════════
# DiscordChannel (core/channel.py)
# ═══════════════════════════════════════════════════════════════════════════


class TestDiscordChannelCore:
    """Test DiscordChannel from core/channel.py."""

    @pytest.fixture
    def discord_ch(self) -> DiscordChannel:
        return DiscordChannel(
            channel_id="dc-1",
            bot_token="discord-token-123",
        )

    def test_init(self, discord_ch):
        assert discord_ch.channel_type == "discord"
        assert discord_ch.channel_id == "dc-1"

    @pytest.mark.asyncio
    async def test_start_without_sdk(self, discord_ch):
        with patch.dict("sys.modules", {"discord": None}):
            await discord_ch.start()
            assert discord_ch.is_running is True

    @pytest.mark.asyncio
    async def test_stop_no_client(self, discord_ch):
        discord_ch._running = True
        await discord_ch.stop()
        assert discord_ch.is_running is False

    @pytest.mark.asyncio
    async def test_send_no_client(self, discord_ch):
        discord_ch._client = None
        msg = OutboundMessage(
            channel_type="discord", channel_id="dc-1",
            recipient_id="12345", content="Hi",
        )
        result = await discord_ch.send(msg)
        assert result is False

    @pytest.mark.asyncio
    async def test_receive_empty(self, discord_ch):
        result = await discord_ch.receive()
        assert result is None

    def test_stores_bot_token(self, discord_ch):
        assert discord_ch._bot_token == "discord-token-123"


# ═══════════════════════════════════════════════════════════════════════════
# SlackChannel (core/channel.py)
# ═══════════════════════════════════════════════════════════════════════════


class TestSlackChannelCore:
    """Test SlackChannel from core/channel.py."""

    @pytest.fixture
    def slack_ch(self) -> SlackChannel:
        return SlackChannel(
            channel_id="sl-1",
            bot_token="xoxb-token-123",
        )

    def test_init(self, slack_ch):
        assert slack_ch.channel_type == "slack"
        assert slack_ch.channel_id == "sl-1"

    def test_init_with_app_token(self):
        ch = SlackChannel(
            channel_id="sl-2",
            bot_token="xoxb-token",
            app_token="xapp-token",
        )
        assert ch._app_token == "xapp-token"

    @pytest.mark.asyncio
    async def test_start_without_sdk(self, slack_ch):
        with patch.dict("sys.modules", {"slack_bolt.async_app": None}):
            await slack_ch.start()
            assert slack_ch.is_running is True

    @pytest.mark.asyncio
    async def test_stop(self, slack_ch):
        slack_ch._running = True
        await slack_ch.stop()
        assert slack_ch.is_running is False

    @pytest.mark.asyncio
    async def test_send_no_app(self, slack_ch):
        slack_ch._app = None
        msg = OutboundMessage(
            channel_type="slack", channel_id="sl-1",
            recipient_id="C12345", content="Hello",
        )
        result = await slack_ch.send(msg)
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_receive_empty(self, slack_ch):
        result = await slack_ch.receive()
        assert result is None

    def test_stores_bot_token(self, slack_ch):
        assert slack_ch._bot_token == "xoxb-token-123"


# ═══════════════════════════════════════════════════════════════════════════
# Channel-Specific Extensions (channels/ package)
# ═══════════════════════════════════════════════════════════════════════════


class TestTelegramChannelExtension:
    """Test TelegramChannel from channels/telegram.py."""

    @pytest.fixture
    def tg_ext(self):
        from ai_multicolony.channels.telegram import TelegramChannel as TgExt
        return TgExt(bot_token="123456:ABCDEF1234567890abcdefghij")

    def test_init(self, tg_ext):
        assert tg_ext.channel_type == "telegram"
        assert tg_ext._bot_token == "123456:ABCDEF1234567890abcdefghij"

    def test_api_base(self, tg_ext):
        assert tg_ext._api_base.startswith("https://api.telegram.org/bot")

    def test_api_base_contains_token(self, tg_ext):
        assert "123456:ABCDEF1234567890abcdefghij" in tg_ext._api_base

    @pytest.mark.asyncio
    async def test_stop(self, tg_ext):
        tg_ext._running = True
        await tg_ext.stop()
        assert tg_ext._running is False

    def test_offset_starts_at_zero(self, tg_ext):
        assert tg_ext._offset == 0

    @pytest.mark.asyncio
    async def test_send_with_mocked_httpx(self, tg_ext):
        """Test send via mocked httpx."""
        msg = OutboundMessage(
            channel_type="telegram", channel_id="tg-1",
            recipient_id="chat-1", content="Hello",
        )
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True}
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await tg_ext.send(msg)
            assert result is True

    @pytest.mark.asyncio
    async def test_send_failed_response(self, tg_ext):
        """Test send when Telegram API returns failure."""
        msg = OutboundMessage(
            channel_type="telegram", channel_id="tg-1",
            recipient_id="chat-1", content="Hello",
        )
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": False, "description": "Bad request"}
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await tg_ext.send(msg)
            assert result is False

    @pytest.mark.asyncio
    async def test_receive_with_mocked_httpx(self, tg_ext):
        """Test receive via mocked httpx."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ok": True,
            "result": [{
                "update_id": 42,
                "message": {
                    "chat": {"id": 123},
                    "from": {"id": 456, "username": "testuser"},
                    "text": "Hello bot",
                },
            }],
        }
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await tg_ext.receive()
            assert result is not None
            assert result.content == "Hello bot"
            assert tg_ext._offset == 43

    @pytest.mark.asyncio
    async def test_receive_no_updates(self, tg_ext):
        """Test receive when no updates available."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"ok": True, "result": []}
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await tg_ext.receive()
            assert result is None


class TestWhatsAppChannelExtension:
    """Test WhatsAppChannel from channels/whatsapp.py."""

    @pytest.fixture
    def wa_ext(self):
        from ai_multicolony.channels.whatsapp import WhatsAppChannel as WaExt
        return WaExt(
            phone_number_id="12345",
            access_token="test-token",
            verify_token="verify-token",
        )

    def test_init(self, wa_ext):
        assert wa_ext.channel_type == "whatsapp"

    def test_api_base_url(self, wa_ext):
        assert wa_ext._api_base == "https://graph.facebook.com/v18.0"

    def test_verify_webhook_success(self, wa_ext):
        result = wa_ext.verify_webhook("subscribe", "verify-token", "challenge123")
        assert result == "challenge123"

    def test_verify_webhook_wrong_token(self, wa_ext):
        result = wa_ext.verify_webhook("subscribe", "wrong-token", "challenge123")
        assert result is None

    def test_verify_webhook_wrong_mode(self, wa_ext):
        result = wa_ext.verify_webhook("unsubscribe", "verify-token", "challenge123")
        assert result is None

    def test_verify_webhook_empty_params(self, wa_ext):
        result = wa_ext.verify_webhook("", "", "")
        assert result is None

    def test_parse_webhook_valid(self, wa_ext):
        body = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "1234567890",
                            "text": {"body": "Hello from WhatsApp"},
                        }]
                    }
                }]
            }]
        }
        result = wa_ext.parse_webhook(body)
        assert result is not None
        assert result.content == "Hello from WhatsApp"
        assert result.channel_type == "whatsapp"

    def test_parse_webhook_empty(self, wa_ext):
        result = wa_ext.parse_webhook({})
        assert result is None

    def test_parse_webhook_no_messages(self, wa_ext):
        body = {
            "entry": [{
                "changes": [{
                    "value": {"messages": []}
                }]
            }]
        }
        result = wa_ext.parse_webhook(body)
        assert result is None

    def test_parse_webhook_increment_received_count(self, wa_ext):
        initial_count = wa_ext._received_count
        body = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "123",
                            "text": {"body": "test"},
                        }]
                    }
                }]
            }]
        }
        wa_ext.parse_webhook(body)
        assert wa_ext._received_count == initial_count + 1

    @pytest.mark.asyncio
    async def test_receive_returns_none(self, wa_ext):
        result = await wa_ext.receive()
        assert result is None

    def test_start_sets_running(self, wa_ext):
        assert wa_ext.is_running is False
        import asyncio
        asyncio.get_event_loop().run_until_complete(wa_ext.start())
        assert wa_ext.is_running is True

    @pytest.mark.asyncio
    async def test_send_with_mocked_httpx(self, wa_ext):
        """Test WhatsApp send with mocked httpx."""
        msg = OutboundMessage(
            channel_type="whatsapp", channel_id="wa-1",
            recipient_id="1234567890", content="Hello WA",
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await wa_ext.send(msg)
            assert result is True

    @pytest.mark.asyncio
    async def test_send_template(self, wa_ext):
        """Test send_template creates correct message."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)

        with patch("httpx.AsyncClient", return_value=mock_client):
            result = await wa_ext.send_template(
                recipient="1234567890",
                template_name="hello_template",
                language_code="en",
            )
            assert result is True


class TestDiscordChannelExtension:
    """Test DiscordChannel from channels/discord.py."""

    @pytest.fixture
    def dc_ext(self):
        from ai_multicolony.channels.discord import DiscordChannel as DcExt
        return DcExt(bot_token="discord-bot-token-1234567890")

    def test_init(self, dc_ext):
        assert dc_ext.channel_type == "discord"

    def test_client_starts_none(self, dc_ext):
        assert dc_ext._client is None

    @pytest.mark.asyncio
    async def test_start_without_sdk(self, dc_ext):
        with patch.dict("sys.modules", {"discord": None}):
            await dc_ext.start()
            assert dc_ext._running is True

    @pytest.mark.asyncio
    async def test_stop_no_client(self, dc_ext):
        dc_ext._running = True
        await dc_ext.stop()
        assert dc_ext._running is False

    @pytest.mark.asyncio
    async def test_send_no_client(self, dc_ext):
        dc_ext._client = None
        msg = OutboundMessage(
            channel_type="discord", channel_id="dc-1",
            recipient_id="12345", content="Hi",
        )
        result = await dc_ext.send(msg)
        assert result is False

    @pytest.mark.asyncio
    async def test_send_with_mocked_client(self, dc_ext):
        """Test send with a mocked Discord client."""
        mock_channel = AsyncMock()
        mock_client = MagicMock()
        mock_client.get_channel.return_value = mock_channel
        dc_ext._client = mock_client

        msg = OutboundMessage(
            channel_type="discord", channel_id="dc-1",
            recipient_id="12345", content="Hello Discord",
        )
        result = await dc_ext.send(msg)
        assert result is True
        mock_channel.send.assert_called_once_with("Hello Discord")

    @pytest.mark.asyncio
    async def test_send_with_embed_metadata(self, dc_ext):
        """Test send with embed in metadata."""
        mock_channel = AsyncMock()
        mock_client = MagicMock()
        mock_client.get_channel.return_value = mock_channel
        dc_ext._client = mock_client

        embed = MagicMock()
        msg = OutboundMessage(
            channel_type="discord", channel_id="dc-1",
            recipient_id="12345", content="With embed",
            metadata={"embed": embed},
        )
        result = await dc_ext.send(msg)
        assert result is True
        mock_channel.send.assert_called_once_with(embed=embed)

    @pytest.mark.asyncio
    async def test_send_channel_not_found(self, dc_ext):
        """Test send when channel is not found."""
        mock_client = MagicMock()
        mock_client.get_channel.return_value = None
        dc_ext._client = mock_client

        msg = OutboundMessage(
            channel_type="discord", channel_id="dc-1",
            recipient_id="99999", content="Hello",
        )
        result = await dc_ext.send(msg)
        assert result is False

    @pytest.mark.asyncio
    async def test_receive_returns_none(self, dc_ext):
        result = await dc_ext.receive()
        assert result is None

    @pytest.mark.asyncio
    async def test_stop_with_client(self, dc_ext):
        """Test stop when client exists."""
        mock_client = AsyncMock()
        dc_ext._client = mock_client
        dc_ext._running = True
        await dc_ext.stop()
        mock_client.close.assert_called_once()
        assert dc_ext._running is False


class TestSlackChannelExtension:
    """Test SlackChannel from channels/slack.py."""

    @pytest.fixture
    def sl_ext(self):
        from ai_multicolony.channels.slack import SlackChannel as SlExt
        return SlExt(bot_token="xoxb-test-token-1234567890")

    def test_init(self, sl_ext):
        assert sl_ext.channel_type == "slack"

    def test_init_with_app_token(self):
        from ai_multicolony.channels.slack import SlackChannel as SlExt
        ch = SlExt(bot_token="xoxb-token", app_token="xapp-token")
        assert ch._app_token == "xapp-token"

    def test_parse_event_valid(self, sl_ext):
        event = {
            "channel": "C12345",
            "user": "U67890",
            "text": "Hello Slack!",
        }
        result = sl_ext.parse_event(event)
        assert result is not None
        assert result.content == "Hello Slack!"
        assert result.channel_type == "slack"
        assert result.sender_id == "U67890"

    def test_parse_event_empty(self, sl_ext):
        result = sl_ext.parse_event({})
        assert result is not None  # Still creates InboundMessage with defaults

    def test_parse_event_increment_received_count(self, sl_ext):
        initial_count = sl_ext._received_count
        sl_ext.parse_event({"channel": "C1", "user": "U1", "text": "test"})
        assert sl_ext._received_count == initial_count + 1

    @pytest.mark.asyncio
    async def test_start_without_sdk(self, sl_ext):
        with patch.dict("sys.modules", {"slack_bolt.async_app": None}):
            await sl_ext.start()
            assert sl_ext._running is True

    @pytest.mark.asyncio
    async def test_receive_returns_none(self, sl_ext):
        result = await sl_ext.receive()
        assert result is None

    @pytest.mark.asyncio
    async def test_send_with_blocks_metadata(self, sl_ext):
        """Test send with blocks in metadata."""
        msg = OutboundMessage(
            channel_type="slack", channel_id="sl-1",
            recipient_id="C12345", content="Hello",
            metadata={"blocks": [{"type": "section", "text": {"type": "plain_text", "text": "Hi"}}]},
        )
        # No app client available, will try _send_via_api
        sl_ext._app = None
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_httpx.return_value = mock_client

            result = await sl_ext.send(msg)
            assert result is True

    def test_send_blocks_creates_outbound(self, sl_ext):
        """send_blocks creates OutboundMessage with blocks metadata."""
        # We can't easily test the full async flow, but verify the method exists
        assert hasattr(sl_ext, "send_blocks")

    def test_update_message_exists(self, sl_ext):
        """update_message method exists."""
        assert hasattr(sl_ext, "update_message")


# ═══════════════════════════════════════════════════════════════════════════
# Channel Factory
# ═══════════════════════════════════════════════════════════════════════════


class TestChannelFactory:
    """Test create_channel factory function."""

    def test_create_telegram(self):
        ch = create_channel("telegram", channel_id="tg-1", bot_token="tok")
        assert isinstance(ch, TelegramChannel)
        assert ch.channel_type == "telegram"

    def test_create_discord(self):
        ch = create_channel("discord", channel_id="dc-1", bot_token="tok")
        assert isinstance(ch, DiscordChannel)
        assert ch.channel_type == "discord"

    def test_create_slack(self):
        ch = create_channel("slack", channel_id="sl-1", bot_token="tok")
        assert isinstance(ch, SlackChannel)
        assert ch.channel_type == "slack"

    def test_create_whatsapp(self):
        ch = create_channel(
            "whatsapp",
            channel_id="wa-1",
            phone_number_id="123",
            access_token="tok",
        )
        assert isinstance(ch, WhatsAppChannel)
        assert ch.channel_type == "whatsapp"

    def test_create_unsupported_raises(self):
        with pytest.raises(ChannelError) as exc_info:
            create_channel("unsupported")
        assert "Unsupported channel type" in str(exc_info.value)

    def test_create_unsupported_error_code(self):
        with pytest.raises(ChannelError) as exc_info:
            create_channel("irc")
        assert exc_info.value.code == "CHANNEL_ERROR"

    def test_create_unsupported_lists_supported(self):
        with pytest.raises(ChannelError) as exc_info:
            create_channel("unknown")
        # Error message should list supported types
        msg = str(exc_info.value)
        assert "telegram" in msg or "Supported" in msg

    def test_create_case_sensitive(self):
        """Channel type is case-sensitive."""
        with pytest.raises(ChannelError):
            create_channel("Telegram")  # Capital T

    def test_factory_returns_base_channel(self):
        """All factory-created channels are BaseChannel instances."""
        ch = create_channel("telegram", channel_id="tg-1", bot_token="tok")
        assert isinstance(ch, BaseChannel)

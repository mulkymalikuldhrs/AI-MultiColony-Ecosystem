"""Telegram channel implementation.

Provides Telegram bot integration with Bot API for
the AI MultiColony Ecosystem.
"""

from __future__ import annotations

from typing import Any, Optional

from ai_multicolony.config.logging_config import get_logger
from ai_multicolony.core.channel import BaseChannel
from ai_multicolony.exceptions import ChannelError
from ai_multicolony.types.messages import InboundMessage, OutboundMessage

logger = get_logger(__name__)


class TelegramChannel(BaseChannel):
    """Telegram bot channel.

    Features:
    - Send and receive messages via Telegram Bot API
    - Handle commands and callbacks
    - Support inline keyboards
    - Group chat support
    - Webhook and polling modes
    """

    def __init__(self, bot_token: str, config: Optional[dict[str, Any]] = None) -> None:
        super().__init__(channel_type="telegram", channel_id=bot_token[:10], config=config)
        self._bot_token = bot_token
        self._api_base = f"https://api.telegram.org/bot{bot_token}"
        self._offset = 0

    async def start(self) -> None:
        """Start the Telegram bot."""
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self._api_base}/getMe")
                data = response.json()
                if not data.get("ok"):
                    raise ChannelError("Telegram bot authentication failed", channel_type="telegram")
                bot_info = data.get("result", {})
                logger.info("telegram_bot_started", bot_name=bot_info.get("username", "unknown"))
        except ImportError:
            logger.warning("httpx_not_installed", message="pip install httpx")
        except ChannelError:
            raise
        except Exception as e:
            raise ChannelError(f"Failed to start Telegram bot: {e}", channel_type="telegram")

        self._running = True

    async def stop(self) -> None:
        """Stop the Telegram bot."""
        self._running = False
        logger.info("telegram_bot_stopped")

    async def send(self, message: OutboundMessage) -> bool:
        """Send a message via Telegram.

        Args:
            message: The outbound message.

        Returns:
            True if sent successfully.
        """
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30) as client:
                payload: dict[str, Any] = {
                    "chat_id": message.recipient_id,
                    "text": message.content,
                    "parse_mode": "Markdown",
                }
                # Add reply markup if present
                if message.metadata.get("reply_markup"):
                    payload["reply_markup"] = message.metadata["reply_markup"]

                response = await client.post(f"{self._api_base}/sendMessage", json=payload)
                data = response.json()
                if data.get("ok"):
                    self._sent_count += 1
                    return True
                logger.warning("telegram_send_failed", error=data.get("description"))
                return False
        except Exception as e:
            logger.error("telegram_send_error", error=str(e))
            return False

    async def receive(self) -> Optional[InboundMessage]:
        """Receive the next message from Telegram via long polling.

        Returns:
            The inbound message, or None.
        """
        try:
            import httpx
            async with httpx.AsyncClient(timeout=35) as client:
                response = await client.get(
                    f"{self._api_base}/getUpdates",
                    params={"offset": self._offset, "timeout": 30},
                )
                data = response.json()

                if not data.get("ok") or not data.get("result"):
                    return None

                update = data["result"][0]
                self._offset = update["update_id"] + 1

                msg = update.get("message", {})
                if not msg:
                    return None

                self._received_count += 1
                return InboundMessage(
                    channel_type="telegram",
                    channel_id=str(msg.get("chat", {}).get("id", "")),
                    sender_id=str(msg.get("from", {}).get("id", "")),
                    sender_name=msg.get("from", {}).get("username", ""),
                    content=msg.get("text", ""),
                )
        except Exception as e:
            logger.error("telegram_receive_error", error=str(e))
            return None

    async def set_webhook(self, url: str) -> bool:
        """Set a webhook for the Telegram bot.

        Args:
            url: The webhook URL.

        Returns:
            True if set successfully.
        """
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"{self._api_base}/setWebhook",
                    json={"url": url},
                )
                return response.json().get("ok", False)
        except Exception:
            return False

    async def send_photo(self, chat_id: str, photo_url: str, caption: str = "") -> bool:
        """Send a photo via Telegram.

        Args:
            chat_id: Target chat ID.
            photo_url: URL of the photo.
            caption: Optional caption.

        Returns:
            True if sent successfully.
        """
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30) as client:
                payload = {"chat_id": chat_id, "photo": photo_url}
                if caption:
                    payload["caption"] = caption
                response = await client.post(f"{self._api_base}/sendPhoto", json=payload)
                return response.json().get("ok", False)
        except Exception:
            return False

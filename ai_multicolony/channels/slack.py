"""Slack channel implementation.

Provides Slack integration via the Bolt SDK for
the AI MultiColony Ecosystem.
"""

from __future__ import annotations

from typing import Any, Optional

from ai_multicolony.config.logging_config import get_logger
from ai_multicolony.core.channel import BaseChannel
from ai_multicolony.exceptions import ChannelError
from ai_multicolony.types.messages import InboundMessage, OutboundMessage

logger = get_logger(__name__)


class SlackChannel(BaseChannel):
    """Slack bot channel.

    Features:
    - Send and receive messages via Slack
    - Slash command support
    - Channel and DM support
    - Block Kit support
    - Thread support
    """

    def __init__(
        self,
        bot_token: str,
        app_token: Optional[str] = None,
        config: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(channel_type="slack", channel_id=bot_token[:10], config=config)
        self._bot_token = bot_token
        self._app_token = app_token
        self._app: Optional[Any] = None

    async def start(self) -> None:
        """Start the Slack channel."""
        try:
            from slack_bolt.async_app import AsyncApp

            self._app = AsyncApp(token=self._bot_token)

            @self._app.event("message")
            async def handle_message(event: dict, say: Any) -> None:
                inbound = InboundMessage(
                    channel_type="slack",
                    channel_id=event.get("channel", ""),
                    sender_id=event.get("user", ""),
                    content=event.get("text", ""),
                )
                await self._dispatch_inbound(inbound)

            # Start Socket Mode if app token provided
            if self._app_token:
                try:
                    from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
                    import asyncio
                    handler = AsyncSocketModeHandler(self._app, self._app_token)
                    asyncio.ensure_future(handler.start_async())
                except ImportError:
                    logger.warning("slack_socket_mode_not_available")

            self._running = True
            logger.info("slack_channel_started")

        except ImportError:
            logger.warning("slack_sdk_not_installed", message="pip install slack-bolt")
            self._running = True

    async def stop(self) -> None:
        """Stop the Slack channel."""
        self._running = False

    async def send(self, message: OutboundMessage) -> bool:
        """Send a message via Slack.

        Args:
            message: The outbound message.

        Returns:
            True if sent successfully.
        """
        try:
            if self._app and self._app.client:
                kwargs: dict[str, Any] = {
                    "channel": message.recipient_id,
                    "text": message.content,
                }

                # Support Block Kit
                if message.metadata.get("blocks"):
                    kwargs["blocks"] = message.metadata["blocks"]

                # Support threads
                if message.metadata.get("thread_ts"):
                    kwargs["thread_ts"] = message.metadata["thread_ts"]

                # Support reply broadcasting
                if message.metadata.get("reply_broadcast"):
                    kwargs["reply_broadcast"] = True

                response = self._app.client.chat_postMessage(**kwargs)
                if response.get("ok"):
                    self._sent_count += 1
                    return True
            else:
                return await self._send_via_api(message)
        except Exception as e:
            logger.error("slack_send_error", error=str(e))
            return False
        return False

    async def _send_via_api(self, message: OutboundMessage) -> bool:
        """Send via Slack Web API as fallback."""
        try:
            import httpx
            url = "https://slack.com/api/chat.postMessage"
            headers = {"Authorization": f"Bearer {self._bot_token}"}
            payload: dict[str, Any] = {
                "channel": message.recipient_id,
                "text": message.content,
            }
            if message.metadata.get("blocks"):
                payload["blocks"] = message.metadata["blocks"]

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        self._sent_count += 1
                        return True
            return False
        except Exception:
            return False

    async def receive(self) -> Optional[InboundMessage]:
        """Receive is handled via Slack events."""
        return None

    def parse_event(self, event: dict[str, Any]) -> Optional[InboundMessage]:
        """Parse a Slack event.

        Args:
            event: The Slack event data.

        Returns:
            Parsed InboundMessage, or None.
        """
        try:
            self._received_count += 1
            return InboundMessage(
                channel_type="slack",
                channel_id=event.get("channel", ""),
                sender_id=event.get("user", ""),
                content=event.get("text", ""),
            )
        except Exception as e:
            logger.error("slack_event_parse_error", error=str(e))
            return None

    async def send_blocks(
        self,
        channel: str,
        blocks: list[dict[str, Any]],
        fallback_text: str = "",
    ) -> bool:
        """Send a Block Kit message.

        Args:
            channel: Slack channel ID.
            blocks: Block Kit blocks.
            fallback_text: Fallback text for notifications.

        Returns:
            True if sent successfully.
        """
        msg = OutboundMessage(
            channel_type="slack",
            channel_id=self.channel_id,
            recipient_id=channel,
            content=fallback_text,
            metadata={"blocks": blocks},
        )
        return await self.send(msg)

    async def update_message(
        self,
        channel: str,
        ts: str,
        text: str,
        blocks: Optional[list[dict[str, Any]]] = None,
    ) -> bool:
        """Update an existing message.

        Args:
            channel: Channel ID.
            ts: Message timestamp.
            text: New text.
            blocks: Optional new blocks.

        Returns:
            True if updated successfully.
        """
        try:
            if self._app and self._app.client:
                kwargs: dict[str, Any] = {
                    "channel": channel,
                    "ts": ts,
                    "text": text,
                }
                if blocks:
                    kwargs["blocks"] = blocks
                response = self._app.client.chat_update(**kwargs)
                return response.get("ok", False)
        except Exception as e:
            logger.error("slack_update_error", error=str(e))
        return False

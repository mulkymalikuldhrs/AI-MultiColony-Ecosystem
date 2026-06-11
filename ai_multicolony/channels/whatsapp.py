"""WhatsApp channel implementation.

Provides WhatsApp integration via the WhatsApp Business API
with Web.js pattern for the AI MultiColony Ecosystem.
"""

from __future__ import annotations

from typing import Any, Optional

from ai_multicolony.config.logging_config import get_logger
from ai_multicolony.core.channel import BaseChannel
from ai_multicolony.exceptions import ChannelError
from ai_multicolony.types.messages import InboundMessage, OutboundMessage

logger = get_logger(__name__)


class WhatsAppChannel(BaseChannel):
    """WhatsApp Business API channel.

    Features:
    - Send messages via WhatsApp Business API
    - Receive webhook messages
    - Template message support
    - Media message support
    - Interactive message support
    """

    def __init__(
        self,
        phone_number_id: str,
        access_token: str,
        verify_token: Optional[str] = None,
        config: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(channel_type="whatsapp", channel_id=phone_number_id, config=config)
        self._phone_number_id = phone_number_id
        self._access_token = access_token
        self._verify_token = verify_token
        self._api_base = "https://graph.facebook.com/v18.0"

    async def start(self) -> None:
        """Start the WhatsApp channel."""
        self._running = True
        logger.info("whatsapp_channel_started")

    async def stop(self) -> None:
        """Stop the WhatsApp channel."""
        self._running = False

    async def send(self, message: OutboundMessage) -> bool:
        """Send a message via WhatsApp.

        Args:
            message: The outbound message.

        Returns:
            True if sent successfully.
        """
        try:
            import httpx
            async with httpx.AsyncClient(timeout=30) as client:
                url = f"{self._api_base}/{self._phone_number_id}/messages"
                headers = {
                    "Authorization": f"Bearer {self._access_token}",
                    "Content-Type": "application/json",
                }

                # Determine message type
                content_type = message.metadata.get("whatsapp_type", "text")

                if content_type == "template":
                    payload = {
                        "messaging_product": "whatsapp",
                        "to": message.recipient_id,
                        "type": "template",
                        "template": message.metadata.get("template", {}),
                    }
                elif content_type == "interactive":
                    payload = {
                        "messaging_product": "whatsapp",
                        "to": message.recipient_id,
                        "type": "interactive",
                        "interactive": message.metadata.get("interactive", {}),
                    }
                else:
                    payload = {
                        "messaging_product": "whatsapp",
                        "to": message.recipient_id,
                        "type": "text",
                        "text": {"body": message.content},
                    }

                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    self._sent_count += 1
                    return True
                logger.warning("whatsapp_send_failed", status=response.status_code)
                return False
        except Exception as e:
            logger.error("whatsapp_send_error", error=str(e))
            return False

    async def receive(self) -> Optional[InboundMessage]:
        """Receive is handled via webhooks for WhatsApp."""
        return None

    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify a WhatsApp webhook.

        Args:
            mode: Webhook mode.
            token: Verify token.
            challenge: Challenge string.

        Returns:
            Challenge string if verified, None otherwise.
        """
        if mode == "subscribe" and token == self._verify_token:
            return challenge
        return None

    def parse_webhook(self, body: dict[str, Any]) -> Optional[InboundMessage]:
        """Parse a WhatsApp webhook body.

        Args:
            body: The webhook request body.

        Returns:
            Parsed InboundMessage, or None.
        """
        try:
            entry = body.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])
            if not messages or not messages[0]:
                return None

            msg = messages[0]
            self._received_count += 1
            return InboundMessage(
                channel_type="whatsapp",
                channel_id=self._phone_number_id,
                sender_id=msg.get("from", ""),
                content=msg.get("text", {}).get("body", ""),
                content_type="text",
            )
        except (IndexError, KeyError) as e:
            logger.error("whatsapp_webhook_parse_error", error=str(e))
            return None

    async def send_template(
        self,
        recipient: str,
        template_name: str,
        language_code: str = "en",
        parameters: Optional[list[str]] = None,
    ) -> bool:
        """Send a template message.

        Args:
            recipient: Recipient phone number.
            template_name: Template name.
            language_code: Language code.
            parameters: Optional template parameters.

        Returns:
            True if sent successfully.
        """
        components = []
        if parameters:
            components.append({
                "type": "body",
                "parameters": [{"type": "text", "text": p} for p in parameters],
            })

        msg = OutboundMessage(
            channel_type="whatsapp",
            channel_id=self._phone_number_id,
            recipient_id=recipient,
            content="",
            metadata={
                "whatsapp_type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": language_code},
                    "components": components,
                },
            },
        )
        return await self.send(msg)

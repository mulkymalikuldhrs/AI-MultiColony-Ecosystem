"""Discord channel implementation.

Provides Discord bot integration with Bot API for
the AI MultiColony Ecosystem.
"""

from __future__ import annotations

from typing import Any, Optional

from ai_multicolony.config.logging_config import get_logger
from ai_multicolony.core.channel import BaseChannel
from ai_multicolony.exceptions import ChannelError
from ai_multicolony.types.messages import InboundMessage, OutboundMessage

logger = get_logger(__name__)


class DiscordChannel(BaseChannel):
    """Discord bot channel.

    Features:
    - Send and receive messages via Discord
    - Slash command support
    - Channel and DM support
    - Embed support
    - Reaction support
    """

    def __init__(self, bot_token: str, config: Optional[dict[str, Any]] = None) -> None:
        super().__init__(channel_type="discord", channel_id=bot_token[:10], config=config)
        self._bot_token = bot_token
        self._client: Optional[Any] = None

    async def start(self) -> None:
        """Start the Discord bot."""
        try:
            import discord

            intents = discord.Intents.default()
            intents.message_content = True
            self._client = discord.Client(intents=intents)

            @self._client.event
            async def on_ready() -> None:
                logger.info(
                    "discord_bot_ready",
                    bot_name=self._client.user.name if self._client.user else "unknown",
                )

            @self._client.event
            async def on_message(message: discord.Message) -> None:
                if message.author.bot:
                    return
                inbound = InboundMessage(
                    channel_type="discord",
                    channel_id=str(message.channel.id),
                    sender_id=str(message.author.id),
                    sender_name=message.author.name,
                    content=message.content,
                )
                await self._dispatch_inbound(inbound)

            # Start the client in background
            import asyncio
            asyncio.ensure_future(self._client.start(self._bot_token))
            self._running = True
            logger.info("discord_channel_started")

        except ImportError:
            logger.warning("discord_sdk_not_installed", message="pip install discord.py")
            self._running = True

    async def stop(self) -> None:
        """Stop the Discord bot."""
        if hasattr(self, "_client") and self._client:
            try:
                await self._client.close()
            except Exception as e:
                logger.warning("discord_stop_error", error=str(e))
        self._running = False

    async def send(self, message: OutboundMessage) -> bool:
        """Send a message via Discord.

        Args:
            message: The outbound message.

        Returns:
            True if sent successfully.
        """
        try:
            if hasattr(self, "_client") and self._client:
                channel = self._client.get_channel(int(message.recipient_id))
                if channel:
                    # Support embeds
                    if message.metadata.get("embed"):
                        await channel.send(embed=message.metadata["embed"])
                    else:
                        await channel.send(message.content)
                    self._sent_count += 1
                    return True
            return False
        except Exception as e:
            logger.error("discord_send_error", error=str(e))
            return False

    async def receive(self) -> Optional[InboundMessage]:
        """Receive is handled via Discord events."""
        return None

    async def send_embed(
        self,
        channel_id: str,
        title: str,
        description: str = "",
        color: int = 0x00FF00,
        fields: Optional[list[dict[str, str]]] = None,
    ) -> bool:
        """Send an embed message.

        Args:
            channel_id: Discord channel ID.
            title: Embed title.
            description: Embed description.
            color: Embed color.
            fields: Optional embed fields.

        Returns:
            True if sent successfully.
        """
        try:
            import discord

            if self._client:
                channel = self._client.get_channel(int(channel_id))
                if channel:
                    embed = discord.Embed(title=title, description=description, color=color)
                    if fields:
                        for field in fields:
                            embed.add_field(
                                name=field.get("name", ""),
                                value=field.get("value", ""),
                                inline=field.get("inline", False),
                            )
                    await channel.send(embed=embed)
                    return True
        except Exception as e:
            logger.error("discord_embed_error", error=str(e))
        return False

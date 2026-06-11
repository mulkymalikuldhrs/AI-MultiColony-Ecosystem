"""Communication channels module.

Self-contained channel implementations for multi-platform communication.
"""

from ai_multicolony.channels.base import BaseChannel
from ai_multicolony.channels.telegram import TelegramChannel
from ai_multicolony.channels.whatsapp import WhatsAppChannel
from ai_multicolony.channels.discord import DiscordChannel
from ai_multicolony.channels.slack import SlackChannel

__all__ = ["BaseChannel", "TelegramChannel", "WhatsAppChannel", "DiscordChannel", "SlackChannel"]

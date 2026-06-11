"""IM Channel integration for DeerFlow.

Provides a pluggable channel system that connects external messaging platforms
(Feishu/Lark, Slack, Telegram, Discord, WeChat, DingTalk, WeCom) to the agent
ecosystem via the ChannelManager and MessageBus.

Consolidated from deer-flow backend/app/channels/.
"""

from src.channels.base import Channel
from src.channels.message_bus import InboundMessage, MessageBus, OutboundMessage

__all__ = [
    "Channel",
    "InboundMessage",
    "MessageBus",
    "OutboundMessage",
]

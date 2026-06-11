"""WebSocket API routes for real-time communication."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from ai_multicolony.config.logging_config import get_logger
from ai_multicolony.core.event_bus import EventBus

logger = get_logger(__name__)


def create_router() -> Any:
    """Create the WebSocket router."""
    from fastapi import APIRouter, WebSocket, WebSocketDisconnect

    router = APIRouter(tags=["websocket"])

    # Track connected clients
    connected_clients: list[WebSocket] = []

    @router.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        """WebSocket endpoint for real-time events."""
        await websocket.accept()
        event_bus = EventBus.get_instance()
        connected_clients.append(websocket)

        async def event_handler(event: Any) -> None:
            """Handle events from the event bus and send to WebSocket."""
            try:
                await websocket.send_json(event.model_dump())
            except Exception:
                pass

        # Subscribe to all events
        event_bus.subscribe("*", event_handler)

        try:
            while True:
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    # Process incoming messages
                    msg_type = message.get("type", "")

                    if msg_type == "ping":
                        await websocket.send_json({"type": "pong"})
                    elif msg_type == "subscribe":
                        channel = message.get("channel", "*")
                        event_bus.subscribe(channel, event_handler)
                        await websocket.send_json({"type": "subscribed", "channel": channel})
                    elif msg_type == "unsubscribe":
                        channel = message.get("channel", "*")
                        event_bus.unsubscribe(channel, event_handler)
                        await websocket.send_json({"type": "unsubscribed", "channel": channel})
                    else:
                        # Broadcast to event bus
                        await event_bus.broadcast(
                            sender="ws_client",
                            channel=message.get("channel", "websocket"),
                            content=message,
                        )
                except json.JSONDecodeError:
                    await websocket.send_json({"type": "error", "message": "Invalid JSON"})
        except WebSocketDisconnect:
            event_bus.unsubscribe("*", event_handler)
            if websocket in connected_clients:
                connected_clients.remove(websocket)
            logger.info("websocket_disconnected")

    @router.get("/ws/status")
    async def ws_status() -> dict[str, Any]:
        """Get WebSocket connection status."""
        return {
            "connected_clients": len(connected_clients),
            "status": "active" if connected_clients else "idle",
        }

    return router

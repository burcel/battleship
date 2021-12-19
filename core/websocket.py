from typing import Any, Dict

from fastapi import WebSocket


class WebsocketManager:

    def __init__(self) -> None:
        self.active_connections: Dict[int, WebSocket] = {}

    def add_connection(self, user_id: int, websocket: WebSocket) -> None:
        """Add given websocket to connection dict"""
        self.active_connections[user_id] = websocket

    def remove_connection(self, user_id: int) -> None:
        """Remove user id from connection dict"""
        self.active_connections.pop(user_id, None)

    async def send(self, user_id: int, message: Dict) -> None:
        """Fetch websocket related to user id and send message"""
        websocket = self.active_connections.get(user_id)
        if websocket is None:
            raise KeyError
        await websocket.send_json(message)


websocket_manager = WebsocketManager()

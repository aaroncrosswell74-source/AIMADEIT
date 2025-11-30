# app/ws.py
from fastapi import WebSocket
from typing import Dict, List
import json
from app.logger import logger

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.admin_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, user_id: str = None, is_admin: bool = False):
        await websocket.accept()
        if user_id:
            self.active_connections[user_id] = websocket
        if is_admin:
            self.admin_connections.append(websocket)
        logger.info(f"WebSocket connected: {user_id} (admin: {is_admin})")

    def disconnect(self, websocket: WebSocket):
        # Remove from active connections
        for user_id, ws in list(self.active_connections.items()):
            if ws == websocket:
                del self.active_connections[user_id]
                break
        # Remove from admin connections
        if websocket in self.admin_connections:
            self.admin_connections.remove(websocket)

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(json.dumps(message))

    async def broadcast_to_admins(self, message: dict):
        text = json.dumps(message)
        for connection in self.admin_connections:
            await connection.send_text(text)

    async def broadcast_to_user(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(json.dumps(message))

manager = ConnectionManager()
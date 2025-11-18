# app/websocket/manager.py
from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # room_id -> [WebSocket, WebSocket, ...]
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, room_id: int, websocket: WebSocket):
        # 연결 수락
        await websocket.accept()
        self.active_connections.setdefault(room_id, []).append(websocket)
        print(f"[WS] Connected to room {room_id}. Now {len(self.active_connections[room_id])} clients.")

    def disconnect(self, room_id: int, websocket: WebSocket):
        conns = self.active_connections.get(room_id)
        if not conns:
            return
        if websocket in conns:
            conns.remove(websocket)
            print(f"[WS] Disconnected from room {room_id}. Left {len(conns)} clients.")
        if not conns:
            self.active_connections.pop(room_id, None)

    async def broadcast(self, room_id: int, message: dict):
        conns = self.active_connections.get(room_id, [])
        # 에러 방지용으로 한 번 복사본 iteration
        for ws in list(conns):
            try:
                await ws.send_json(message)
            except Exception as e:
                print(f"[WS] broadcast error: {e}")
                self.disconnect(room_id, ws)

manager = ConnectionManager()

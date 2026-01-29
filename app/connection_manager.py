from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = {}

    def connect(self, user_id: str, websocket: WebSocket):
        if user_id not in self._connections:
            self._connections[user_id] = []
        self._connections[user_id].append(websocket)

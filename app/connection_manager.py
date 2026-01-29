from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.connections: dict[str, list[WebSocket]] = {}

    def connect(self, user_id: str, websocket: WebSocket) -> None:
        if user_id not in self.connections:
            self.connections[user_id] = []
        self.connections[user_id].append(websocket)

    def disconnect(self, user_id, websocket: WebSocket) -> None:
        if user_id in self.connections:
            self.connections[user_id].remove(websocket)
            if len(self.connections[user_id]) == 0:
                del self.connections[user_id]

    @property
    def sockets(self) -> list[WebSocket]:
        results: list[WebSocket] = []
        for ws_list in self.connections.values():
            results.extend(ws_list)
        return results

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = {}

    def connect(self, user_id: str, websocket: WebSocket) -> None:
        if user_id not in self._connections:
            self._connections[user_id] = []
        self._connections[user_id].append(websocket)

    def disconnect(self, user_id, websocket: WebSocket) -> None:
        if user_id in self._connections:
            self._connections[user_id].remove(websocket)
            if len(self._connections[user_id]) == 0:
                del self._connections[user_id]

    @property
    def connections(self):
        return self._connections

    @property
    def sockets(self) -> list[WebSocket]:
        results: list[WebSocket] = []
        for ws_list in self._connections.values():
            results.extend(ws_list)
        return results

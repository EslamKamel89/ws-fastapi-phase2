from fastapi import FastAPI, WebSocket

app = FastAPI(title="Phase 2 websocket course")

active_connections: dict[str, list[WebSocket]] = {}


@app.get("/")
async def home():
    connections = [
        {"user_id": user_id, "connections_count": len(sockets)}
        for user_id, sockets in active_connections.items()
    ]
    return {"status": "ok", "connections": connections}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    secret = websocket.query_params.get("token")
    print("secret", secret)
    if secret != "password":
        print("invalid token")
        await websocket.close(1008, reason="invalid token")
        return
    user_id = "user_1"
    await websocket.accept()
    if user_id not in active_connections:
        active_connections[user_id] = []
    active_connections[user_id].append(websocket)
    try:
        while True:
            print("start while loop")
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
            print("end while loop")
    finally:
        active_connections[user_id].remove(websocket)
        if len(active_connections[user_id]) == 0:
            del active_connections[user_id]

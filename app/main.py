import asyncio
import json
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI, WebSocket

from .types import *

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
REDIS_CHANNEL = "ws:messages"
active_connections: dict[str, list[WebSocket]] = {}


async def redis_listener():
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(REDIS_CHANNEL)
    async for message in pubsub.listen():
        if message["type"] != "message":
            continue
        data: Message = json.loads(message["data"])
        payload = data["payload"]
        sender = data["sender"]
        message_type = data["type"]
        if message_type == "broadcast":
            for sockets in active_connections.values():
                for ws in sockets:
                    await ws.send_text(payload)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(redis_listener())
    try:
        yield
    finally:
        task.cancel()


app = FastAPI(title="Phase 2 websocket course", lifespan=lifespan)


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
            # await websocket.send_text(f"Echo: {data}")
            message: Message = {
                "type": "broadcast",
                "sender": user_id,
                "payload": f"Echo: {data}",
            }
            await redis_client.publish(REDIS_CHANNEL, json.dumps(message))
            print("end while loop")
    finally:
        active_connections[user_id].remove(websocket)
        if len(active_connections[user_id]) == 0:
            del active_connections[user_id]

import asyncio
import json
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI, WebSocket

from .connection_manager import ConnectionManager
from .types import *

connection_manager = ConnectionManager()
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
REDIS_CHANNEL = "ws:messages"
PRESENCE_TTL = 30  # seconds
USERS: list[User] = [
    {"password": "123", "id": "user_1", "name": "alice"},
    {"password": "456", "id": "user_2", "name": "pop"},
    {"password": "789", "id": "user_3", "name": "eslam"},
]


async def redis_listener():
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(REDIS_CHANNEL)
    async for message in pubsub.listen():
        if message["type"] != "message":
            continue
        data: Message = json.loads(message["data"])
        sender = get_user_by_id(data["sender"])
        payload = f"{sender['name']}: {data['payload']}" if sender else data["payload"]
        message_type = data["type"]
        if message_type == "broadcast":
            for sockets in connection_manager.connections.values():
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
        {
            "user": get_user_by_id(user_id),
            "connections_count_local_to_this_worker": len(sockets),
            "is_online": bool(await redis_client.exists(f"presence:user:{user_id}")),
        }
        for user_id, sockets in connection_manager.connections.items()
    ]
    return {"status": "ok", "connections": connections}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    name = websocket.query_params.get("name")
    password = websocket.query_params.get("password")
    print("name", name)
    print("password", password)

    user_id = get_user_id(name, password)
    if not user_id:
        print("invalid credentials")
        await websocket.close(1008, reason="invalid credentials")
        return
    await websocket.accept()
    await set_user_online(user_id)
    if user_id not in connection_manager.connections:
        connection_manager.connections[user_id] = []
    connection_manager.connections[user_id].append(websocket)
    try:
        while True:
            print("start while loop")
            data = await websocket.receive_text()
            # await websocket.send_text(f"Echo: {data}")
            await set_user_online(user_id)
            message: Message = {
                "type": "broadcast",
                "sender": user_id,
                "payload": f"Echo: {data}",
            }
            await redis_client.publish(REDIS_CHANNEL, json.dumps(message))
            print("end while loop")
    finally:
        connection_manager.connections[user_id].remove(websocket)
        if len(connection_manager.connections[user_id]) == 0:
            del connection_manager.connections[user_id]


def get_user_id(name: str | None, password: str | None) -> str | None:
    if not name or not password:
        return None
    current_user: User | None = None
    for user in USERS:
        if user["name"] == name and user["password"] == password:
            current_user = user
            break
    return current_user["id"] if current_user else None


def get_user_by_id(user_id: str) -> User | None:
    for user in USERS:
        if user["id"] == user_id:
            return user
    return None


async def set_user_online(user_id: str) -> None:
    key = f"presence:user:{user_id}"
    await redis_client.set(key, "online", ex=PRESENCE_TTL)

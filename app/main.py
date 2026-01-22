from fastapi import FastAPI, WebSocket

app = FastAPI(title="Phase 2 websocket course")


@app.get("/")
async def home():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    secret = websocket.query_params.get("token")
    print("secret", secret)
    if secret != "password":
        print("invalid token")
        await websocket.close(1008, reason="invalid token")
        return
    await websocket.accept()
    while True:
        print("start while loop")
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")
        print("end while loop")

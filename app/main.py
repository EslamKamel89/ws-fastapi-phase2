from fastapi import FastAPI, WebSocket

app = FastAPI(title="Phase 2 websocket course")


@app.get("/")
async def home():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        print("start while loop")
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")
        print("end while loop")

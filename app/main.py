from fastapi import FastAPI, WebSocket

app = FastAPI(title="Phase 2 websocket course")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

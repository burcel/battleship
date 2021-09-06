from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"You wrote: {data}")
    except WebSocketDisconnect:
        # manager.disconnect(websocket)
        # await manager.broadcast(f"Client #{client_id} left the chat")
        print("bye")

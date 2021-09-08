from core.security import decode_access_token
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from jwt.exceptions import PyJWTError
from schemas.user import UserBaseLogin

router = APIRouter()


def authenticate_socket(token: str) -> UserBaseLogin:
    pass


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # Token authenticate
        token = await websocket.receive_text()
        user = decode_access_token(token)
        await websocket.send_text(f"You are: {user.username}")
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"You wrote: {data}")
    except PyJWTError:
        await websocket.send_text("Invalid token!")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except WebSocketDisconnect:
        # manager.disconnect(websocket)
        # await manager.broadcast(f"Client #{client_id} left the chat")
        print("bye")

from core.security import decode_access_token
from data.user import user_data
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from jwt.exceptions import PyJWTError
from schemas.user import UserBaseLogin, UserStateEnum, UserBaseDatabase

router = APIRouter()


def authenticate_socket(token: str) -> UserBaseDatabase:
    """Authenticate websocket using generated JWT"""
    user: UserBaseLogin = decode_access_token(token)
    user_session = user_data.get_user(user.username)
    if user_session is None:
        raise PyJWTError
    # Move user to lobby
    user_session.state = UserStateEnum.LOBBY
    return user_session


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user = None
    try:
        # Token authenticate
        token = await websocket.receive_text()
        user = authenticate_socket(token)
        # Send lobby information
        await websocket.send_json(user_data.return_lobby())
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"You wrote: {data}")
    except PyJWTError:
        await websocket.send_text("Invalid token!")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except WebSocketDisconnect:
        if user is None:
            return None
        user_data.remove_username(user.username)
        # TODO: if user is in lobby -> Broadcast as left

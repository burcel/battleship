from core.security import decode_access_token
from data.user import user_data
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from jwt.exceptions import PyJWTError
from schemas.user import UserBaseDatabase, UserBaseLogin, UserStateEnum
from schemas.websocket import WebsocketResponse, WebsocketResponseEnum, User

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
        user.websocket = websocket
        # Send user info to lobby
        response = WebsocketResponse(type=WebsocketResponseEnum.LOBBY_USER_IN, data=User(username=user.username))
        await user_data.broadcast(user.username, UserStateEnum.LOBBY, response)
        # Send lobby information to user
        await websocket.send_json(user_data.return_lobby().dict())
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"You wrote: {data}")
    except PyJWTError:
        await websocket.send_text("Invalid token!")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except WebSocketDisconnect:
        if user is None:
            return None
        if user.state == UserStateEnum.LOBBY:
            # Send user info to lobby
            response = WebsocketResponse(type=WebsocketResponseEnum.LOBBY_USER_OUT, data=User(username=user.username))
            await user_data.broadcast(user.username, UserStateEnum.LOBBY, response)
        user_data.remove_username(user.username)

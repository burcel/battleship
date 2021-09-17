from json.decoder import JSONDecodeError

from core.security import decode_access_token
from data.user import user_data
from data.game import game_date
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from fastapi.logger import logger
from jwt.exceptions import PyJWTError
from schemas.user import UserBaseDatabase, UserBaseLogin, UserStateEnum
from schemas.websocket import WebsocketBase, WebsocketResponseEnum, WebsocketToken, WebsocketUser, WebsocketGame

router = APIRouter()


def authenticate_socket(request: WebsocketToken) -> UserBaseDatabase:
    """Authenticate websocket using generated JWT"""
    # Check if token exists
    if request.type != WebsocketResponseEnum.TOKEN:
        raise PyJWTError
    user: UserBaseLogin = decode_access_token(request.token)
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
        user = authenticate_socket(WebsocketToken(**await websocket.receive_json()))
        # Valid user -> Save websocket
        user.websocket = websocket
        # Send user info to lobby
        response = WebsocketUser(type=WebsocketResponseEnum.LOBBY_USER_IN, username=user.username)
        await user_data.broadcast(user.username, UserStateEnum.LOBBY, response)
        # Send lobby information to user
        await user_data.send_lobby(user)
        while True:
            request = WebsocketBase(**await websocket.receive_json())
            if request.type == WebsocketResponseEnum.GAME_CREATE and user.state == UserStateEnum.LOBBY:
                game_id = game_date.register_game(user.username)
                user.state = UserStateEnum.GAME
                await websocket.send_json(WebsocketGame(type=WebsocketResponseEnum.GAME_CREATE, game_id=game_id).dict())
            elif request.type == WebsocketResponseEnum.GAME_LEAVE:
                pass
            else:
                await websocket.send_json(WebsocketBase(type=WebsocketResponseEnum.INVALID).dict())
    except (PyJWTError, JSONDecodeError, TypeError):
        await websocket.send_json(WebsocketBase(type=WebsocketResponseEnum.INVALID).dict())
    except WebSocketDisconnect:
        pass
    finally:
        if user is None:
            return None
        if user.state == UserStateEnum.LOBBY:
            # Send user info to lobby as left
            response = WebsocketUser(type=WebsocketResponseEnum.LOBBY_USER_OUT, username=user.username)
            await user_data.broadcast(user.username, UserStateEnum.LOBBY, response)
        user_data.remove_username(user.username)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

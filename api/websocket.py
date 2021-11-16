from json.decoder import JSONDecodeError

from core.security import Security
from data.user import user_data
from data.game import game_data
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
    user: UserBaseLogin = Security.decode_token(request.token)
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
        await user_data.broadcast(user.username, UserStateEnum.LOBBY, WebsocketUser(type=WebsocketResponseEnum.LOBBY_USER_IN, username=user.username))
        # Send lobby information to user
        await user_data.send_lobby(user)
        while True:
            request = await websocket.receive_json()
            request_base = WebsocketBase(**request)
            if request_base.type == WebsocketResponseEnum.GAME_CREATE:
                game_id = None if "game_id" not in request else WebsocketGame(**request).game_id
                game = game_data.register_game(user, game_id)
                response_game = WebsocketGame(type=WebsocketResponseEnum.GAME_CREATE, game_id=game.game_id)
                await websocket.send_json(response_game.dict())
                await user_data.broadcast(None, UserStateEnum.LOBBY, response_game)
                # Check if user entered a game or created one
                if game.users[0].username != user.username:
                    # Send message to game creator
                    await user_data.send(game.users[0].username, WebsocketUser(type=WebsocketResponseEnum.GAME_CREATE, username=user.username))
            elif request_base.type == WebsocketResponseEnum.GAME_LEAVE:
                request_game = WebsocketGame(**request)
                game = game_data.remove_game(user, request_game.game_id)
                response = WebsocketGame(type=WebsocketResponseEnum.GAME_LEAVE, game_id=response_game.game_id)
                await user_data.broadcast(None, UserStateEnum.LOBBY, response)
                # Check if user left the game of somebody else
                if game.users[0].username != user.username:
                    # Send message to game creator
                    await user_data.send(game.users[0].username, WebsocketUser(type=WebsocketResponseEnum.GAME_LEAVE, username=user.username))
            else:
                raise TypeError
    except (PyJWTError, JSONDecodeError, TypeError, KeyError, ValueError):
        await websocket.send_json(WebsocketBase(type=WebsocketResponseEnum.INVALID).dict())
    except WebSocketDisconnect:
        pass
    finally:
        if user is None:
            return None
        if user.state == UserStateEnum.LOBBY:
            # Send user info to lobby as left
            response_user = WebsocketUser(type=WebsocketResponseEnum.LOBBY_USER_OUT, username=user.username)
            await user_data.broadcast(user.username, UserStateEnum.LOBBY, response_user)
        user_data.remove_username(user.username)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

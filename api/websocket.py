from typing import Optional

from controllers.game import ControllerGame
from core.auth import TokenValidator
from core.db import get_session
from core.websocket import websocket_manager
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from models.games import Games
from schemas.user import UserBaseSession
from schemas.websocket import WebsocketBase, WebsocketResponse, WebsocketResponseEnum, WebsocketToken, WebsocketMessage
from sqlalchemy.orm import Session

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session: Session = Depends(get_session)):
    user: Optional[UserBaseSession] = None
    game: Optional[Games] = None
    await websocket.accept()
    try:
        authenticated = False
        while True:
            request = await websocket.receive_json()
            request_base = WebsocketBase(**request)
            if request_base.type == WebsocketResponseEnum.TOKEN and authenticated is False:
                # Check if token is valid
                user = TokenValidator.authorize_socket(WebsocketToken(**request))
                TokenValidator.check_token(session, user.id)
                # Check if user is in a game
                game = ControllerGame.get_by_user_id(session, user.id)
                if game is None:
                    raise ValueError
                await websocket.send_json(WebsocketResponse(type=request_base.type, status=status.HTTP_200_OK).dict())
                authenticated = True
                websocket_manager.add_connection(user.id, websocket)
            elif request_base.type == WebsocketResponseEnum.MESSAGE and authenticated is True:
                message = WebsocketMessage(**request)
                user_id = ControllerGame.get_other_user_id(game, user.id)  # type: ignore
                if user_id is not None:
                    websocket_manager.send(user_id, message.dict())
                await websocket.send_json(WebsocketResponse(type=request_base.type, status=status.HTTP_200_OK).dict())
            else:
                await websocket.send_json(WebsocketResponse(type=request_base.type, status=status.HTTP_400_BAD_REQUEST).dict())
                break
    except (ValueError, TypeError):
        await websocket.send_json(WebsocketResponse(type=WebsocketResponseEnum.INVALID, status=status.HTTP_400_BAD_REQUEST).dict())
    except HTTPException:
        await websocket.send_json(WebsocketResponse(type=request_base.type, status=status.HTTP_400_BAD_REQUEST).dict())
    except WebSocketDisconnect:
        ...
    finally:
        if user is not None:
            websocket_manager.remove_connection(user.id)
        await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)

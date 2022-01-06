from core.db import get_session
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from process.websocket import WebsocketProcessor
from schemas.websocket import WebsocketBase, WebsocketMessage, WebsocketResponse, WebsocketResponseEnum, WebsocketToken
from sqlalchemy.orm import Session

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session: Session = Depends(get_session)):
    websocket_processor = WebsocketProcessor(websocket, session)
    await websocket.accept()
    try:
        while True:
            request = await websocket.receive_json()
            request_base = WebsocketBase(**request)
            if request_base.type == WebsocketResponseEnum.TOKEN and websocket_processor.authenticated is False:
                websocket_processor.authorize_user(WebsocketToken(**request))
            elif request_base.type == WebsocketResponseEnum.MESSAGE and websocket_processor.authenticated is True:
                websocket_processor.message(WebsocketMessage(**request))
            elif request_base.type == WebsocketResponseEnum.READY and websocket_processor.authenticated is True:
                websocket_processor.ready()
            else:
                await websocket_processor.default()
                break
    except (ValueError, TypeError, KeyError):
        await websocket.send_json(WebsocketResponse(type=WebsocketResponseEnum.INVALID, status=status.HTTP_400_BAD_REQUEST).dict())
    except HTTPException:
        await websocket.send_json(WebsocketResponse(type=request_base.type, status=status.HTTP_400_BAD_REQUEST).dict())
    except WebSocketDisconnect:
        ...
    finally:
        websocket_processor.disconnect()
        await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)

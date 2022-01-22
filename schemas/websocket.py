from enum import Enum
from typing import Optional

from pydantic import BaseModel


class WebsocketResponseEnum(str, Enum):
    INVALID = "INVALID"
    TOKEN = "TOKEN"
    MESSAGE = "MESSAGE"
    USER_IN = "USER_IN"
    USER_OUT = "USER_OUT"
    READY = "READY"
    BOARD = "BOARD"
    TURN = "TURN"
    RESULT = "RESULT"


class WebsocketBase(BaseModel):
    type: WebsocketResponseEnum


class WebsocketResponse(WebsocketBase):
    status: int


class WebsocketToken(WebsocketBase):
    token: str


class WebsocketMessage(WebsocketBase):
    message: str


class WebsocketUser(WebsocketBase):
    username: str


class WebsocketBoard(WebsocketBase):
    self_board: str
    opponent_board: str


class WebsocketTurn(WebsocketBase):
    x: int
    y: int


class WebsocketTurnResponse(WebsocketResponse):
    hit: bool
    x: int
    y: int


class WebsocketResultResponse(WebsocketResponse):
    win: bool

from enum import IntEnum
from typing import Optional

from fastapi import WebSocket
from pydantic import BaseModel, constr


class UserBaseLogin(BaseModel):
    username: constr(min_length=2, max_length=20)  # type: ignore


class UserBaseLoginResponse(BaseModel):
    token: str


class UserStateEnum(IntEnum):
    LOGGED = 0
    LOBBY = 1
    GAME = 2


class UserBaseDatabase(BaseModel):
    username: constr(min_length=2, max_length=20)  # type: ignore
    websocket: Optional[WebSocket] = None
    state: UserStateEnum = UserStateEnum.LOGGED

    class Config:
        arbitrary_types_allowed = True


class Message(BaseModel):
    message: str

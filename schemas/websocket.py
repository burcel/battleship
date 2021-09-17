from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel


class WebsocketResponseEnum(str, Enum):
    INVALID = "INVALID"
    TOKEN = "TOKEN"
    LOBBY_INIT = "LOBBY_INIT"
    LOBBY_USER_IN = "LOBBY_USER_IN"
    LOBBY_USER_OUT = "LOBBY_USER_OUT"
    LOBBY_GAME_IN = "LOBBY_GAME_IN"
    LOBBY_GAME_OUT = "LOBBY_GAME_OUT"


class WebsocketBase(BaseModel):
    type: WebsocketResponseEnum


class WebsocketToken(WebsocketBase):
    token: str


class WebsocketUser(WebsocketBase):
    username: str


class WebsocketLobby(WebsocketBase):
    user_list: List[str]
    game_list: List[str]

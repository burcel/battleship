from enum import Enum
from typing import List, Union

from pydantic import BaseModel


class WebsocketResponseEnum(str, Enum):
    LOBBY_INIT = "LOBBY_INIT"
    LOBBY_USER_IN = "LOBBY_USER_IN"
    LOBBY_USER_OUT = "LOBBY_USER_OUT"
    LOBBY_GAME_IN = "LOBBY_GAME_IN"
    LOBBY_GAME_OUT = "LOBBY_GAME_OUT"


class User(BaseModel):
    username: str


class Game(BaseModel):
    game_name: str
    username: str


class Lobby(BaseModel):
    user_list: List[str]
    game_list: List[str]


class WebsocketResponse(BaseModel):
    type: WebsocketResponseEnum
    data: Union[User, Game, Lobby]

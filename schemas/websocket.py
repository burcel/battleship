from enum import Enum

from pydantic import BaseModel


class WebsocketResponseEnum(str, Enum):
    INVALID = "INVALID"
    TOKEN = "TOKEN"
    MESSAGE = "MESSAGE"
    USER_IN = "USER_IN"
    USER_OUT = "USER_OUT"


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

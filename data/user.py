from typing import Dict, List, Optional

from schemas.user import UserBaseDatabase, UserStateEnum
from schemas.websocket import Lobby, WebsocketResponse, WebsocketResponseEnum


class UserData:

    def __init__(self) -> None:
        self._username_dict: Dict[str, UserBaseDatabase] = dict()

    def check_username(self, username: str) -> bool:
        """Check if username exists and return true or false"""
        return username in self._username_dict

    def register_user(self, user: UserBaseDatabase) -> None:
        """Register username to user database"""
        self._username_dict[user.username] = user

    def get_user(self, username: str) -> Optional[UserBaseDatabase]:
        """Return user database object from username"""
        return self._username_dict.get(username)

    def remove_username(self, username: str) -> None:
        """Remove username from user database"""
        self._username_dict.pop(username)

    def return_lobby(self) -> WebsocketResponse:
        """Return list of username"""
        user_list: List[str] = []
        for username, user in self._username_dict.items():
            if user.state == UserStateEnum.LOBBY:
                user_list.append(username)
        game_list: List[str] = []
        return WebsocketResponse(type=WebsocketResponseEnum.LOBBY_INIT, data=Lobby(user_list=user_list, game_list=game_list))

    async def broadcast(self, subject_username: str, user_state: UserStateEnum, response: WebsocketResponse) -> None:
        """Broadcast the response to users with given state other than subject"""
        for username, user in self._username_dict.items():
            if username != subject_username and user.state == user_state and user.websocket is not None:
                await user.websocket.send_json(response.dict())


user_data = UserData()

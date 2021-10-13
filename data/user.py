from typing import Dict, List, Optional, Union

from fastapi import WebSocketDisconnect
from schemas.user import UserBaseDatabase, UserStateEnum
from schemas.websocket import WebsocketGame, WebsocketLobby, WebsocketResponseEnum, WebsocketUser

from data.game import game_data


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

    async def send(self, username: str, response: Union[WebsocketUser]) -> None:
        """Send message to username"""
        user = self.get_user(username)
        if user is None or user.websocket is None:
            raise KeyError
        await user.websocket.send_json(response.dict())

    async def send_lobby(self, user: UserBaseDatabase) -> None:
        """Return lobby information"""
        if user.websocket is None:
            raise WebSocketDisconnect
        # Create user list
        user_list: List[str] = []
        for username, user_session in self._username_dict.items():
            if user_session.state == UserStateEnum.LOBBY:
                user_list.append(username)
        # Create game list
        game_list: List[int] = game_data.return_game_id_list()
        response = WebsocketLobby(type=WebsocketResponseEnum.LOBBY_INIT, user_list=user_list, game_list=game_list)
        await user.websocket.send_json(response.dict())

    async def broadcast(self, subject_username: Optional[str], user_state: UserStateEnum, response: Union[WebsocketUser, WebsocketGame]) -> None:
        """Broadcast the response to users with given state, if subject_username is given; skip that subject subject"""
        for username, user in self._username_dict.items():
            if username != subject_username and user.state == user_state and user.websocket is not None:
                await user.websocket.send_json(response.dict())


user_data = UserData()

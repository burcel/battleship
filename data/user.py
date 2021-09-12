from typing import Dict, List, Optional

from schemas.user import UserBaseDatabase, UserStateEnum


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

    def return_lobby(self) -> List[str]:
        """Return list of username"""
        lobby_list: List[str] = []
        for username, user in self._username_dict.items():
            if user.state == UserStateEnum.LOBBY:
                lobby_list.append(username)
        return lobby_list

    async def broadcast_lobby(self, subject_username: str) -> None:
        """Broadcast lobby info to other users who are in the lobby"""
        for username, user in self._username_dict.items():
            if username != subject_username and user.state == UserStateEnum.LOBBY and user.websocket is not None:
                await user.websocket.send_json(subject_username)


user_data = UserData()

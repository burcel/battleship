from typing import Dict, Union

from fastapi import WebSocket


class UserData:

    def __init__(self) -> None:
        self._username_dict: Dict[str, Union[None, WebSocket]] = {}

    def check_username(self, username: str) -> bool:
        """Check if username exists"""
        return username in self._username_dict

    def register_user(self, username: str) -> None:
        """Register username to user database"""
        self._username_dict[username] = None

    def remove_username(self, username: str) -> None:
        """Remove username from user database"""
        self._username_dict.pop(username)


user_data = UserData()

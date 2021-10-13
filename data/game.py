from secrets import randbelow
from typing import Dict, Optional, List, Tuple

from fastapi import WebSocket
from schemas.game import GameBase
from schemas.user import UserBaseDatabase, UserStateEnum


class GameData:
    def __init__(self) -> None:
        self._game_dict: Dict[int, GameBase] = {}

    def return_game_id_list(self) -> List[int]:
        """Return game ids as list"""
        return list(self._game_dict.keys())

    def check_game_id(self, game_id: int) -> bool:
        """Check if game id exists and return true or false"""
        return game_id in self._game_dict

    def get_game(self, game_id: int) -> Optional[GameBase]:
        """Return game object with respect to the game id"""
        return self._game_dict.get(game_id)

    def register_game(self, user: UserBaseDatabase, game_id: Optional[int] = None) -> GameBase:
        """Open a new game and return its GameBase object, if game_id is given; add user to that game"""
        if user.state != UserStateEnum.LOBBY:
            raise ValueError
        if game_id is not None:  # Add user to game
            game = self._game_dict[game_id]
            game.users = (game.users[0], user)
        else:  # Create new game
            # Gerenate id
            while True:
                game_id = randbelow(999999)
                if self.check_game_id(game_id) is False:
                    break
            self._game_dict[game_id] = GameBase(game_id=game_id, users=(user, None))
        # Move user to game status
        user.state = UserStateEnum.GAME
        return self._game_dict[game_id]

    def remove_game(self, user: UserBaseDatabase, game_id: int) -> GameBase:
        """Remove game from game database, return the second user websocket if the remover is host"""
        if user.state != UserStateEnum.GAME:
            raise ValueError
        game = self.get_game(game_id)
        if game is None:
            raise KeyError
        if game.users[0].username == user.username:
            # Game host
            user.state = UserStateEnum.LOBBY
            if game.users[1] is not None:
                game.users[1].state = UserStateEnum.LOBBY
            self._game_dict.pop(game_id)
        elif game.users[1] is not None and game.users[1].username == user.username:
            # Game attendee
            user.state = UserStateEnum.LOBBY
            game.users = (game.users[0], None)
        else:
            # This user is not associated with this game
            raise ValueError
        return game


game_data = GameData()

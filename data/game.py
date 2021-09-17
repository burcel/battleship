from typing import Dict, Optional
from secrets import randbelow
from schemas.game import GameBase


class GameData:
    def __init__(self) -> None:
        self._game_dict: Dict[int, GameBase] = {}

    def check_game_id(self, game_id: int) -> bool:
        """Check if game id exists and return true or false"""
        return game_id in self._game_dict

    def register_game(self, username: str, game_id: Optional[int] = None) -> int:
        """Open a new game and return its id, if game_id is given; add username to that game"""
        if game_id is not None:  # Add user to game
            game = self._game_dict[game_id]
            game.users = (game.users[0], username)
        else:  # Create new game
            # Gerenate id
            while True:
                game_id = randbelow(999999)
                if self.check_game_id(game_id) is False:
                    break
            self._game_dict[game_id] = GameBase(users=(username, None))
        return game_id

    def remove_game(self, game_id: int) -> None:
        """Remove game from game database"""
        self._game_dict.pop(game_id)


game_date = GameData()

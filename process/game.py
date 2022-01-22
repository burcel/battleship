from typing import Dict, Optional

from process.board import Board


class GameManager:
    ACTIVE_GAMES: Dict[int, Board] = {}

    @classmethod
    def add_board(cls, user_id: int, board: Board) -> None:
        """Add given websocket to connection dict"""
        cls.ACTIVE_GAMES[user_id] = board

    @classmethod
    def get_board(cls, user_id: int) -> Optional[Board]:
        """Return board related to user id"""
        return cls.ACTIVE_GAMES.get(user_id, None)

    @classmethod
    def remove_board(cls, user_id: int) -> None:
        """Remove user id from connection dict"""
        cls.ACTIVE_GAMES.pop(user_id, None)

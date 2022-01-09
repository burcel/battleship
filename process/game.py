from typing import Dict, Tuple

from process.board import Board


class GameProcessor:

    def __init__(self) -> None:
        self.creator_board = Board()
        self.second_board = Board()

    def initialize(self) -> None:
        """Initialize boards for both players"""
        self.creator_board.populate()
        self.second_board.populate()

    def return_boards_str(self) -> Tuple[str, str]:
        """Return string representations of the board"""
        return self.creator_board.serialize(), self.second_board.serialize()

from board import Board
import pytest


class TestBoard:

    def test_populate(self) -> None:
        """
        Populate function of the board
        """
        board = Board()
        board.populate()

        # Check if coordinate size list length equals to total ship part count
        assert len(board.return_ship_coordinate_list()) == sum(board.SHIP_SIZE_LIST)
        # Check if cell for each ship part is correct
        ship_coordinate_list = board.return_ship_coordinate_list()
        for x in range(Board.BOARD_DIM):
            for y in range(Board.BOARD_DIM):
                if (x, y) in ship_coordinate_list:
                    assert board.return_cell(x, y) == Board.SHIP
                else:
                    assert board.return_cell(x, y) == Board.EMPTY

    def test_hit(self) -> None:
        """
        Test hit function
        Empty -> Miss
        Ship -> Hit
        """
        board = Board()
        board.populate()
        ship_coordinate_list = board.return_ship_coordinate_list()
        for x in range(Board.BOARD_DIM):
            for y in range(Board.BOARD_DIM):
                result = board.hit(x, y)
                if (x, y) in ship_coordinate_list:
                    # There is a ship on this coordinate
                    assert result is True
                    assert board.return_cell(x, y) == Board.HIT
                else:
                    # There is no ship on this coordinate
                    assert result is False
                    assert board.return_cell(x, y) == Board.MISS

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

    def test_hit_boundaries(self) -> None:
        """
        Test boundaries for hit function
        """
        board = Board()
        board.populate()
        # Valid
        board.hit(0, 0)
        board.hit(2, 3)
        board.hit(1, 4)
        board.hit(Board.BOARD_DIM - 1, Board.BOARD_DIM - 1)
        board.hit(0, Board.BOARD_DIM - 1)
        # Invalid
        board = Board()
        board.populate()
        with pytest.raises(Exception):
            board.hit(Board.BOARD_DIM, Board.BOARD_DIM)
        with pytest.raises(Exception):
            board.hit(Board.BOARD_DIM + 1, Board.BOARD_DIM * 3)
        with pytest.raises(Exception):
            board.hit(-1, -1)
        with pytest.raises(Exception):
            board.hit(-4, -26)
        with pytest.raises(Exception):
            board.hit(Board.BOARD_DIM - 1, Board.BOARD_DIM + 1)
        with pytest.raises(Exception):
            board.hit(0, 777)
        with pytest.raises(Exception):
            board.hit(12345, 0)

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
        assert board.return_status() is True

    def test_record_boundaries(self) -> None:
        """
        Test boundaries for hit and record functions
        """
        board = Board()
        # Valid
        board.record(0, 0, Board.HIT)
        board.record(0, 0, Board.MISS)
        board.record(2, 4, Board.MISS)
        board.record(Board.BOARD_DIM - 1, Board.BOARD_DIM - 1, Board.HIT)
        # Invalid
        board = Board()
        with pytest.raises(Exception):
            board.record(0, 0, "Audiomachine")
        with pytest.raises(Exception):
            board.record(0, 0, Board.HIT + "-_-")
        with pytest.raises(Exception):
            board.record(-1, -1, Board.HIT)
        with pytest.raises(Exception):
            board.record(-4, -26, Board.MISS)
        with pytest.raises(Exception):
            board.record(1, 245, Board.HIT)
        with pytest.raises(Exception):
            board.record(2345, 0, Board.HIT)

    def test_record(self) -> None:
        """
        Test record
        """
        board = Board()
        hit_count = 0
        for x in range(Board.BOARD_DIM):
            for y in range(Board.BOARD_DIM):
                if y % 2 == 0:
                    board.record(x, y, Board.HIT)
                    assert board.return_cell(x, y) == Board.HIT
                    hit_count += 1
                else:
                    board.record(x, y, Board.MISS)
                    assert board.return_cell(x, y) == Board.MISS
                # Status control
                if hit_count == Board.SHIP_PART_COUNT:
                    assert board.return_status() is True
                    break
                else:
                    assert board.return_status() is False

            if board.return_status() is True:
                # All ships are sunk, exit
                break

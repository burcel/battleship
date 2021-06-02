from typing import List, Tuple
import secrets


class Board:
    BOARD_DIM = 10
    # Cell representation
    EMPTY = ' '
    HIT = 'X'
    MISS = 'O'
    SHIP = 'S'
    # Total ship count with respect to sizes
    SHIP_SIZE_LIST = [2, 3, 3, 4, 5]
    SHIP_PART_COUNT = sum(SHIP_SIZE_LIST)
    # Ship direction for randomized placement
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    MOVEMENT_LIST = [UP, DOWN, LEFT, RIGHT]

    def __init__(self):
        self._board = None
        self._ship_coordinate_list: List[Tuple[int, int]] = []
        self._finished = False
        self._init_board()

    def __str__(self) -> str:
        """
        Return string representation of the board
        """
        board_str = self._return_row_line()
        # Prepare column index
        board_str += "| * "
        for column_index in range(self.BOARD_DIM):
            board_str += "| {} ".format(column_index)
        board_str += "|\n"
        board_str += self._return_row_line()
        # Prepare board content along with row index
        for row_index, rows in enumerate(self._board, start=0):
            board_str += "| {} ".format(row_index)
            for cell in rows:
                board_str += "| {} ".format(cell)
            board_str += "|\n"
        return board_str

    def _return_row_line(self) -> str:
        """
        Return line strips each row
        """
        line_str = ""
        for index in range((self.BOARD_DIM + 1) * 5 - self.BOARD_DIM):
            line_str += "-"
        return line_str + "\n"

    def _init_board(self) -> None:
        """
        Initialize the board with empty cells
        """
        self._board = []
        for i in range(self.BOARD_DIM):
            row = []
            for j in range(self.BOARD_DIM):
                row.append(self.EMPTY)
            self._board.append(row)

    def check_boundaries(self, x: int, y: int):
        """
        Check whether given boundaries are valid
        """
        if not 0 <= x < self.BOARD_DIM:
            raise Exception("Invalid x value for board!")
        if not 0 <= y < self.BOARD_DIM:
            raise Exception("Invalid y value for board!")

    def return_board(self) -> List[List[str]]:
        """
        Return board representation as 2d list
        """
        return self._board

    def populate(self) -> None:
        """
        Randomly populate the board
        """

        for ship_size in self.SHIP_SIZE_LIST:
            while True:
                # Get random coordinates
                x = secrets.randbelow(self.BOARD_DIM)
                y = secrets.randbelow(self.BOARD_DIM)
                # Get random directions
                direction = secrets.randbelow(len(self.MOVEMENT_LIST))
                coordinate_list = self._return_coordinates(x, y, direction, ship_size)
                if len(coordinate_list) == 0:
                    # Invalid coordinates -> Try again
                    continue
                else:
                    # Every ship part can be properly placed
                    for x, y in coordinate_list:
                        self._board[x][y] = self.SHIP
                        self._ship_coordinate_list.append((x, y))
                break

    def _return_coordinates(self, x: int, y: int, direction: int, ship_size: int) -> List[Tuple[int, int]]:
        """
        Return coordinates of the ship as a list
        If the returned list is empty, it means that given coordinates and direction are invalid for a proper ship
        """
        coordinate_list = []
        for ship_index in range(ship_size):
            _x = x
            _y = y
            # Decide coordinate with respect to direction
            if direction == self.UP:
                _y += ship_index
            elif direction == self.DOWN:
                _y -= ship_index
            elif direction == self.LEFT:
                _x -= ship_index
            else:
                _x += ship_index
            # Check coordinate for validity -> Cell must be empty and must be inside board boundaries
            if not 0 <= _x < self.BOARD_DIM or not 0 <= _y < self.BOARD_DIM or self._board[_x][_y] != self.EMPTY:
                # Invalid placement -> Start over for this ship
                coordinate_list.clear()
                break
            else:
                # This ship part is fine, continue to the next part
                coordinate_list.append((_x, _y))

        return coordinate_list

    def _check_game_status(self) -> None:
        """
        Check game status and update finished variable
        """
        sunk_ship_part_count = 0
        for x, y in self._ship_coordinate_list:
            if self._board[x][y] != self.HIT:
                break
            else:
                sunk_ship_part_count += 1
        self._finished = sunk_ship_part_count == self.SHIP_PART_COUNT

    def return_cell(self, x: int, y: int) -> str:
        """
        Return cell content
        """
        return self._board[x][y]

    def return_ship_coordinate_list(self) -> List[Tuple[int, int]]:
        """
        Return coordination of ship parts as a list
        """
        return self._ship_coordinate_list

    def return_status(self) -> bool:
        """
        Return board status as boolean
        True -> All ship parts are hit and the game is finished
        False -> There are still remaining ship parts
        """
        return self._finished

    def hit(self, x: int, y: int) -> bool:
        """
        Hit given x, y coordinates and return True if hit is successful
        If cell is empty -> Miss
        IF cell is not empty -> Hit
        """
        self.check_boundaries(x, y)
        is_hit = False
        if self._board[x][y] == self.EMPTY:
            self._board[x][y] = self.MISS
        elif self._board[x][y] == self.SHIP:
            self._board[x][y] = self.HIT
            is_hit = True
            self._check_game_status()
        return is_hit

    def record(self, x: int, y: int, status: str) -> None:
        """
        Record given cell status (Used for reconnaissance when ship locations are not known)
        status: Union[HIT, MISS]
        """
        self.check_boundaries(x, y)
        if status != self.HIT and status != self.MISS:
            raise Exception("Status can only be Hit or Miss value!")

        self._board[x][y] = status
        if status == self.HIT:
            self._ship_coordinate_list.append((x, y))
            self._check_game_status()

    def record_ship_info(self, ship_coordinate_list: List[Tuple[int, int]]) -> None:
        """
        Save ship part coordinate info and record them to board
        """
        self._ship_coordinate_list = ship_coordinate_list
        for x, y in self._ship_coordinate_list:
            self._board[x][y] = self.SHIP

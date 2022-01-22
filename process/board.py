from secrets import randbelow
from typing import List, Tuple


class Board:
    BOARD_DIM = 10
    # Cell representation
    EMPTY = 0
    SHIP = 1
    HIT = 2
    MISS = 3
    # Total ship count with respect to sizes
    SHIP_SIZE_LIST = [2, 3, 3, 4, 5]
    SHIP_PART_COUNT = sum(SHIP_SIZE_LIST)
    # Ship direction for randomized placement

    def __init__(self) -> None:
        self.board: List[List[int]] = [[self.EMPTY] * self.BOARD_DIM for _ in range(self.BOARD_DIM)]
        self.ship_coordinate_list: List[Tuple[int, int]] = []
        self.ship_hit_list: List[Tuple[int, int]] = []
        self.ship_miss_list: List[Tuple[int, int]] = []
        self.finished = False
        self.populate()

    def __str__(self) -> str:
        """Return string representation of the board"""

        def return_row_line() -> str:
            """Return line strips each row"""
            line_str = ""
            for _ in range((self.BOARD_DIM + 1) * 5 - self.BOARD_DIM):
                line_str += "-"
            return line_str + "\n"

        cell_str_dict = {
            self.EMPTY: ' ',
            self.SHIP: 'S',
            self.HIT: 'X',
            self.MISS: '0'
        }
        board_str = return_row_line()
        # Prepare column index
        board_str += "| * "
        for column_index in range(self.BOARD_DIM):
            board_str += "| {} ".format(column_index)
        board_str += "|\n"
        board_str += return_row_line()
        # Prepare board content along with row index
        for row_index, rows in enumerate(self.board, start=0):
            board_str += "| {} ".format(row_index)
            for cell in rows:
                board_str += "| {} ".format(cell_str_dict.get(cell))
            board_str += "|\n"
        return board_str

    @classmethod
    def check_boundaries(cls, x: int, y: int):
        """Check whether given boundaries are valid"""
        if not 0 <= x < cls.BOARD_DIM:
            raise ValueError("Invalid x value for board!")
        if not 0 <= y < cls.BOARD_DIM:
            raise ValueError("Invalid y value for board!")

    def populate(self) -> None:
        """Randomly populate the board"""
        up = 0
        down = 1
        left = 2
        right = 3
        move_list = [up, down, left, right]

        def return_coordinates(x: int, y: int, direction: int, ship_size: int) -> List[Tuple[int, int]]:
            """Return coordinates of the ship as a list, if the returned list is empty, it means that given coordinates and direction are invalid for a proper ship"""
            coordinate_list: List[Tuple[int, int]] = []
            for ship_index in range(ship_size):
                _x = x
                _y = y
                # Decide coordinate with respect to direction
                if direction == up:
                    _y += ship_index
                elif direction == down:
                    _y -= ship_index
                elif direction == left:
                    _x -= ship_index
                else:
                    _x += ship_index
                # Check coordinate for validity -> Cell must be empty and must be inside board boundaries
                if not 0 <= _x < self.BOARD_DIM or not 0 <= _y < self.BOARD_DIM or self.board[_x][_y] != self.EMPTY:
                    # Invalid placement -> Start over for this ship
                    coordinate_list.clear()
                    break
                else:
                    # This ship part is fine, continue to the next part
                    coordinate_list.append((_x, _y))

            return coordinate_list

        if len(self.ship_coordinate_list) > 0:
            return None

        for ship_size in self.SHIP_SIZE_LIST:
            while True:
                # Get random coordinates
                x = randbelow(self.BOARD_DIM)
                y = randbelow(self.BOARD_DIM)
                # Get random directions
                direction = randbelow(len(move_list))
                coordinate_list = return_coordinates(x, y, direction, ship_size)
                if len(coordinate_list) == 0:
                    # Invalid coordinates -> Try again
                    continue
                else:
                    # Every ship part can be properly placed -> Record the cells
                    for x, y in coordinate_list:
                        self.board[x][y] = self.SHIP
                        self.ship_coordinate_list.append((x, y))
                # This ship is placed -> Move to the next one
                break

    def serialize(self, hide_ships: bool = False) -> str:
        """Serialize board into string"""
        serialized_str = ""
        for x in range(self.BOARD_DIM):
            for y in range(self.BOARD_DIM):
                if hide_ships is True and self.board[x][y] == self.SHIP:
                    serialized_str += str(self.EMPTY)
                else:
                    serialized_str += str(self.board[x][y])
        return serialized_str

    def deserialize(self, serialized_str: str) -> None:
        """Deserialize board from string into Board object"""
        for x in range(self.BOARD_DIM):
            for y in range(self.BOARD_DIM):
                # Populate board
                self.board[x][y] = int(serialized_str[x * self.BOARD_DIM + y])
                # Populate lists
                if self.board[x][y] == self.SHIP:
                    self.ship_coordinate_list.append((x, y))
                elif self.board[x][y] == self.HIT:
                    self.ship_hit_list.append((x, y))
                elif self.board[x][y] == self.MISS:
                    self.ship_miss_list.append((x, y))

    def hit(self, x: int, y: int) -> bool:
        """Register given x-y coordinates as hit; If cell is empty -> Miss, If cell is not empty -> Hit"""
        self.check_boundaries(x, y)
        is_hit = False
        if self.board[x][y] == self.EMPTY:
            self.board[x][y] = self.MISS
            self.ship_miss_list.append((x, y))
        elif self.board[x][y] == self.SHIP:
            self.board[x][y] = self.HIT
            self.ship_hit_list.append((x, y))
            is_hit = True
            self.update_game_status()
        else:
            raise ValueError("Only EMPTY or SHIP values can be hit!")
        return is_hit

    def update_game_status(self) -> None:
        """Check game status and update finished variable"""
        sunk_ship_part_count = 0
        for x, y in self.ship_coordinate_list:
            if self.board[x][y] != self.HIT:
                break
            else:
                sunk_ship_part_count += 1
        self.finished = sunk_ship_part_count == self.SHIP_PART_COUNT

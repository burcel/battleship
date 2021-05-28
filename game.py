from board import Board
from typing import Union, Tuple


class Game:
    def __init__(self):
        self._board = Board()
        self._board.populate()
        self._opponent_board = Board()

    def print_state(self) -> None:
        """
        Print the boards of player and opponent
        """
        print("--> Board")
        print(self._board)
        print("--> Opponent Board")
        print(self._opponent_board)

    def _validate_input(self, user_input: str) -> Union[Tuple[bool, str], Tuple[bool, int, int]]:
        """
        Validate the input for board indexes and return either:
        False, Reason for invalidation as str
        True, x, y
        """
        if len(user_input) != 2:
            return False, "Input should be like: 00"

        x = user_input[0]
        if x.isdecimal() is False:
            return False, "x value should be decimal"
        x = int(x)
        if not 0 <= x < Board.BOARD_DIM:
            return False, "x value must be between 0 and {}".format(Board.BOARD_DIM)

        y = user_input[1]
        if y.isdecimal() is False:
            return False, "y value should be decimal"
        y = int(y)
        if not 0 <= y < Board.BOARD_DIM:
            return False, "y value must be between 0 and {}".format(Board.BOARD_DIM)

        return True, x, y

    def take_input(self) -> Tuple[int, int]:
        """
        Take coordinates from the user as input and return x & y as integers
        """
        while True:
            user_input = input("xy?")
            validate_return = self._validate_input(user_input)
            if validate_return[0] is True:
                x = validate_return[1]
                y = validate_return[2]
                break
            else:
                print(validate_return[1])

        return x, y

    def take_action(self):
        pass

    def receive_action(self):
        pass
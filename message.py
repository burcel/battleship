class Message:
    OK = "OK"
    MOVE = "MOVE"  # Indicates the client to make a move
    WAIT = "WAIT"  # Indicates the client to wait for the opponent to make a move
    SHIP = "SHIP"  # Information concerning ship parts
    WIN = "WIN"  # Client won
    LOSE = "LOSE"  # Client lost
    ENTER_USERNAME = "Please enter a username."
    ENTER_VALID_USERNAME = "Please enter a valid username."
    TAKEN_USERNAME = "That username is taken. Please enter another username."
    GAME_NOT_READY = "There are currently not enough players inside the lobby to initiate a game."
    GAME_READY = "Game is found with user: {}"

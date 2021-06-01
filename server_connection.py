import threading
import traceback
from message import Message


class ServerConnection(threading.Thread):
    BUFFER_SIZE = 1024

    def __init__(self, server, conn, address):
        super().__init__()
        self._server = server
        self._conn = conn
        self._address = address
        self._username = None
        self._in_game = False
        self._game_key = None

    def run(self) -> None:
        """
        Start server listener thread for particular client
        """
        self._register()
        # A new user has entered the lobby -> Notify others
        self._server.broadcast_lobby()
        # Try to find a game for user
        self._initiate_game()
        try:
            self._play_game()
        except ConnectionResetError as e:
            print("Closed connection.")
            # TODO: clean client info from server
            # TODO: broadcast when somebody leaves
        except Exception:
            print(traceback.format_exc())

    def _play_game(self) -> None:
        """
        Listen for incoming messages
        """
        while True:
            message = self.receive()
            print(message)

    def send(self, message: str) -> None:
        """
        Send message through socket
        """
        self._conn.sendall(message.encode("UTF-8"))

    def receive(self) -> str:
        """
        Receive message from socket
        """
        message = self._conn.recv(self.BUFFER_SIZE).decode("UTF-8")
        return message

    def close(self) -> None:
        """
        Close socket
        """
        self._conn.close()

    def _register(self) -> None:
        """
        Register user into the lobby
        """
        message = Message.ENTER_USERNAME
        while True:
            self.send(message)
            received_message = self.receive()
            if len(received_message) > 0:
                if self._server.check_username(received_message) is True:
                    message = Message.TAKEN_USERNAME
                else:
                    self._username = received_message
                    self._server.add_client(self._username, self)
                    self.send(Message.OK)
                    break
            else:
                message = Message.ENTER_VALID_USERNAME

    def return_game_status(self) -> bool:
        """
        Return game status
        True: User is currently in game
        False: User is not in any game
        """
        return self._in_game

    def change_game_statue(self) -> None:
        """
        Switch game status
        """
        self._in_game = not self._in_game

    def _initiate_game(self) -> None:
        """
        Initialize game process
        """
        game_found, game_key = self._server.find_game(self._username)
        if game_found is False:
            self.send(Message.GAME_NOT_READY)
        else:
            self._game_key = game_key


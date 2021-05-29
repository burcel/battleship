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

    def run(self) -> None:
        """
        Start server listener thread for particular client
        """
        self._register()

        try:
            self.listen()
        except Exception:
            print(traceback.format_exc())

    def listen(self) -> None:
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

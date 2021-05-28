import threading
import traceback


class ServerConnection(threading.Thread):
    BUFFER_SIZE = 1024

    def __init__(self, server, conn, address):
        super().__init__()
        self._server = server
        self._conn = conn
        self._address = address

    def run(self) -> None:
        """
        Start server listener thread for particular client
        """
        try:
            self.listen()
        except Exception:
            print(traceback.format_exc())

    def listen(self) -> None:
        """
        Listen for incoming messages
        """
        while True:
            message = self.receive().decode("UTF-8")
            print(message)

    def send(self, message: bytes) -> None:
        """
        Send message through socket
        """
        self._conn.sendall(message)

    def receive(self) -> bytes:
        """
        Receive message from socket
        """
        message = self._conn.recv(self.BUFFER_SIZE)
        return message


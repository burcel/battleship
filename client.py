import traceback
import socket
from config_parser import ConfigParser
from message import Message


class Client:
    BUFFER_SIZE = 1024

    def __init__(self):
        self._sock = None
        self._username = None
        self.config_parser = ConfigParser()

    def start(self) -> None:
        """
        Start client and open socket to server
        """
        try:
            self._connect()
            self._register()
            self._wait_server()
        except KeyboardInterrupt:
            print("Shutting down the client... Bye!")
        except Exception:
            print(traceback.format_exc())
        finally:
            if self._sock is not None:
                self._sock.close()

    def _connect(self) -> None:
        """
        Create socket connection and start conversation
        """
        print("Trying to connect server...")
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.connect((self.config_parser.server_ip, self.config_parser.server_port))
        print("Connected to server.")
        # TODO: Server not open case

    def _send(self, message: str) -> None:
        """
        Send message through socket
        """
        self._sock.sendall(message.encode("UTF-8"))

    def _receive(self) -> bytes:
        """
        Receive message from socket
        """
        message = self._sock.recv(self.BUFFER_SIZE).decode("UTF-8")
        return message

    def _close(self) -> None:
        """
        Close socket
        """
        self._sock.close()

    def _register(self):
        """
        Register to the server in order to enter the lobby
        """
        while True:
            message = self._receive()
            if message == Message.OK:
                break
            print(message)
            while True:
                self._username = input("Username: ")
                if len(self._username) > 0:
                    self._send(self._username)
                    break
                else:
                    print(Message.ENTER_VALID_USERNAME)

    def _wait_server(self) -> None:
        """
        Initialize game process
        """
        while True:
            message = self._receive()
            print(message)


if __name__ == '__main__':
    client = Client()
    client.start()

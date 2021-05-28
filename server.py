import socket
from config_parser import ConfigParser
from server_connection import ServerConnection


class Server:
    def __init__(self):
        self.config_parser = ConfigParser()

    def start(self) -> None:
        """
        Start server and get ready for accepting new requests
        """
        print("Server is being initiated...")
        try:
            self.listen()
        except KeyboardInterrupt:
            print("Shutting down the server... Bye!")

    def listen(self) -> None:
        """
        Listen for incoming connections
        """
        # Create server socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.config_parser.server_ip, self.config_parser.server_port))
        sock.listen(5)
        print("Listening at {}:{}".format(self.config_parser.server_ip, self.config_parser.server_port))
        while True:
            # Accept new connections
            conn, address = sock.accept()
            print("Incoming connection from: {}".format(conn.getpeername()))
            # Create thread for connection
            server_connection = ServerConnection(self, conn, address)
            server_connection.start()


if __name__ == '__main__':
    server = Server()
    server.start()

import socket
from prettytable import PrettyTable
from config_parser import ConfigParser
from server_connection import ServerConnection
from typing import Dict, List, Tuple


class Server:
    def __init__(self):
        self.config_parser = ConfigParser()
        self._client_dict: Dict[str, ServerConnection] = {}
        self._game_dict: Dict[Tuple[str, str], None] = {}

    def start(self) -> None:
        """
        Start server and get ready for accepting new requests
        """
        print("Server is being initiated...")
        try:
            self._listen()
        except KeyboardInterrupt:
            print("Shutting down the server... Bye!")

    def _listen(self) -> None:
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

    def add_client(self, username: str, server_connection: ServerConnection) -> None:
        """
        Add connected client to the lobby
        """
        self._client_dict[username] = server_connection

    def remove_client(self, username: str) -> None:
        """
        Remove connected client from the lobby
        """
        server_connection = self._client_dict[username]
        server_connection.close()

    def check_username(self, username: str) -> bool:
        """
        Check if username exists in server; return True if it is, False otherwise
        """
        return username in self._client_dict

    def _return_lobby(self) -> str:
        """
        Return lobby information as str
        """
        pt = PrettyTable()
        pt.field_names = ["Username", "Available"]
        for username, server_connection in self._client_dict.items():
            game_status = "Yes" if server_connection.return_game_status() is False else "No"
            pt.add_row([username, game_status])
        return pt.get_string()

    def broadcast_lobby(self) -> None:
        """
        Broadcast lobby information to other clients who are not on a game
        """
        for username, server_connection in self._client_dict.items():
            if server_connection.return_game_status() is False:
                server_connection.send(self._return_lobby())

    def find_game(self, username: str) -> bool:
        """
        Find game for given username and return result as boolean
        True: Game is found
        False: Could not find any game
        """
        game_found = False
        for client_username, server_connection in self._client_dict.items():
            if client_username == username:
                continue
            if server_connection.return_game_status() is False:
                self._client_dict[username].change_game_statue()
                server_connection.change_game_statue()
                self._game_dict[(username, client_username)] = None
                game_found = True
                break
        return game_found


if __name__ == '__main__':
    server = Server()
    server.start()

from typing import Dict, Optional

from controllers.game import ControllerGame
from core.auth import TokenValidator
from fastapi import WebSocket, status
from models.games import Games
from process.board import Board
from schemas.user import UserBaseSession
from schemas.websocket import (WebsocketMessage, WebsocketResponse,
                               WebsocketResponseEnum, WebsocketToken,
                               WebsocketUser, WebsocketBoard, WebsocketTurn)
from sqlalchemy.orm import Session

from process.game import GameProcessor


class WebsocketManager:
    ACTIVE_CONNECTIONS: Dict[int, WebSocket] = {}

    @classmethod
    def add_connection(cls, user_id: int, websocket: WebSocket) -> None:
        """Add given websocket to connection dict"""
        cls.ACTIVE_CONNECTIONS[user_id] = websocket

    @classmethod
    def remove_connection(cls, user_id: int) -> None:
        """Remove user id from connection dict"""
        cls.ACTIVE_CONNECTIONS.pop(user_id, None)

    @classmethod
    async def send(cls, user_id: int, message: Dict) -> None:
        """Fetch websocket related to user id and send message"""
        websocket = cls.ACTIVE_CONNECTIONS.get(user_id, None)
        if websocket is None:
            raise KeyError
        await websocket.send_json(message)


class WebsocketProcessor:

    def __init__(self, websocket: WebSocket, session: Session) -> None:
        self.websocket: WebSocket = websocket
        self.session: Session = session
        self.user: Optional[UserBaseSession] = None
        self.game: Optional[Games] = None
        self.game_processor = GameProcessor()
        self.authenticated = False

    async def authorize_user(self, token: WebsocketToken) -> None:
        """Authorize user to websocket connection -> This must be the first action in websocket"""
        # Check if token is valid
        self.user = TokenValidator.authorize_socket(token)
        TokenValidator.check_token(self.session, self.user.id)
        # Check if user is in a game
        self.game = ControllerGame.get_by_user_id(self.session, self.user.id)
        if self.game is None:
            raise KeyError(f"User({self.user.id}) is not in a game.")
        WebsocketManager.add_connection(self.user.id, self.websocket)
        self.authenticated = True
        # Check if user is secondary player -> Notify game creator
        if self.game.second_user_id == self.user.id:
            user_in = WebsocketUser(type=WebsocketResponseEnum.USER_IN, username=self.game.second_user.username)
            await WebsocketManager.send(self.game.creator_user_id, user_in.dict())  # type: ignore
        # Return response that authentication is successful
        response = WebsocketResponse(type=WebsocketResponseEnum.TOKEN, status=status.HTTP_200_OK)
        await WebsocketManager.send(self.user.id, response.dict())

    async def message(self, message: WebsocketMessage) -> None:
        """Process incoming messages from users"""
        self.session.refresh(self.game)
        user_id = ControllerGame.get_other_user_id(self.game, self.user.id)  # type: ignore
        if user_id is not None:
            await WebsocketManager.send(user_id, message.dict())
        response = WebsocketResponse(type=WebsocketResponseEnum.MESSAGE, status=status.HTTP_200_OK)
        await WebsocketManager.send(self.user.id, response.dict())  # type: ignore

    async def ready(self) -> None:
        """Process ready message"""
        self.session.refresh(self.game)
        # Save ready flags
        if self.game.creator_user_id == self.user.id:
            self.game.creator_user_ready = not self.game.creator_user_ready
        else:
            self.game.second_user_ready = not self.game.second_user_ready
        response = WebsocketResponse(type=WebsocketResponseEnum.READY, status=status.HTTP_200_OK)
        await WebsocketManager.send(self.user.id, response.dict())  # type: ignore
        # Check ready flags -> Start game if every user is ready
        if self.game.creator_user_ready is True and self.game.second_user_ready is True:
            # Game is ready -> Initiate boards and send them to users
            self.game_processor.initialize()
            self.game.creator_user_board, self.game.second_user_board = self.game_processor.return_boards_str()
            # Send board to creator
            creator_board = WebsocketBoard(type=WebsocketResponseEnum.BOARD, board=self.game.creator_user_board)
            await WebsocketManager.send(self.game.creator_user_id, creator_board.dict())  # type: ignore
            # Send board to second user
            second_board = WebsocketBoard(type=WebsocketResponseEnum.BOARD, board=self.game.second_user_board)
            await WebsocketManager.send(self.game.second_user_id, second_board.dict())  # type: ignore
            # Send turn to the creator
            response = WebsocketResponse(type=WebsocketResponseEnum.TURN, status=status.HTTP_200_OK)
            await WebsocketManager.send(self.game.creator_user_id, response.dict())  # type: ignore

    async def turn(self, turn: WebsocketTurn) -> None:
        """Process turn info"""
        self.session.refresh(self.game)
        # TODO: check turn
        # TODO: hit and return responses to creator and second user
        # TODO: change turns

    async def default(self) -> None:
        """Send default response to user"""
        response = WebsocketResponse(type=WebsocketResponseEnum.INVALID, status=status.HTTP_400_BAD_REQUEST)
        await WebsocketManager.send(self.user.id, response.dict())  # type: ignore

    def disconnect(self) -> None:
        """Process websocket disconnect case"""
        if self.user is not None:
            WebsocketManager.remove_connection(self.user.id)

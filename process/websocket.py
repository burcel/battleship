from typing import Dict, Optional

from controllers.game import ControllerGame
from core.auth import TokenValidator
from fastapi import WebSocket, status
from models.games import Games
from schemas.user import UserBaseSession
from schemas.websocket import (WebsocketBoard, WebsocketMessage,
                               WebsocketResponse, WebsocketResponseEnum,
                               WebsocketToken, WebsocketTurn,
                               WebsocketTurnResponse, WebsocketUser)
from sqlalchemy.orm import Session

from process.board import Board
from process.game import GameManager


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
            await WebsocketManager.send(self.game.creator_user_id, user_in.dict())
        # Return token response that authentication is successful
        await WebsocketManager.send(self.user.id, WebsocketResponse(type=WebsocketResponseEnum.TOKEN, status=status.HTTP_200_OK).dict())

    async def message(self, message: WebsocketMessage) -> None:
        """Process incoming messages from users"""
        self.session.refresh(self.game)
        other_user_id = ControllerGame.get_other_user_id(self.game, self.user.id)
        if other_user_id is not None:
            await WebsocketManager.send(other_user_id, message.dict())
        await WebsocketManager.send(self.user.id, WebsocketResponse(type=WebsocketResponseEnum.MESSAGE, status=status.HTTP_200_OK).dict())

    async def ready(self) -> None:
        """Process ready message coming from users"""
        self.session.refresh(self.game)
        if self.game.creator_user_ready is True and self.game.second_user_ready is True:
            # Game is already started -> Cannot send ready again
            await WebsocketManager.send(self.user.id, WebsocketResponse(type=WebsocketResponseEnum.INVALID, status=status.HTTP_400_BAD_REQUEST).dict())
            return
        # Save ready flags
        if self.game.creator_user_id == self.user.id:
            self.game.creator_user_ready = not self.game.creator_user_ready
        else:
            self.game.second_user_ready = not self.game.second_user_ready
        # Send ready flag response
        await WebsocketManager.send(self.user.id, WebsocketResponse(type=WebsocketResponseEnum.READY, status=status.HTTP_200_OK).dict())
        # TODO: Maybe notify other user of readiness
        # Check ready flags -> Start game if every user is ready
        if self.game.creator_user_ready is True and self.game.second_user_ready is True:
            # Game is ready -> Initiate boards and send them to users
            GameManager.add_board(self.game.creator_user_id, Board())
            GameManager.add_board(self.game.second_user_id, Board())
            await self.send_boards(self.game.creator_user_id, self.game.second_user_id)
            await self.send_turn(self.game.creator_user_id)
        self.session.commit()

    async def turn(self, turn: WebsocketTurn) -> None:
        """Process turn info"""
        self.session.refresh(self.game)
        # Check if it is user's turn to act
        if self.game.turn != self.user.id:
            # Turn is not on this user
            await WebsocketManager.send(self.user.id, WebsocketResponse(type=WebsocketResponseEnum.INVALID, status=status.HTTP_400_BAD_REQUEST).dict())
            return
        # Fetch boards of users
        other_user_id = ControllerGame.get_other_user_id(self.game, self.user.id)
        self_board = GameManager.get_board(self.user.id)
        other_board = GameManager.get_board(other_user_id)
        if self_board is None or other_board is None:
            raise KeyError
        # Record hit
        response = WebsocketTurnResponse(
            type=WebsocketResponseEnum.TURN,
            status=status.HTTP_200_OK,
            hit=other_board.hit(turn.x, turn.y),
            x=turn.x,
            y=turn.y
        )
        await WebsocketManager.send(self.user.id, response.dict())
        await WebsocketManager.send(other_user_id, response.dict())
        # Change turn
        await self.send_turn(other_user_id)
        self.session.commit()

    async def send_boards(self, first_user_id: int, second_user_id: int) -> None:
        """Send board representations to users -> Opponent must not see the ships"""
        response = WebsocketBoard(
            type=WebsocketResponseEnum.BOARD,
            self_board=GameManager.get_board(first_user_id).serialize(),
            opponent_board=GameManager.get_board(second_user_id).serialize(hide_ships=True)
        )
        await WebsocketManager.send(first_user_id, response.dict())
        response = WebsocketBoard(
            type=WebsocketResponseEnum.BOARD,
            self_board=GameManager.get_board(second_user_id).serialize(),
            opponent_board=GameManager.get_board(first_user_id).serialize(hide_ships=True)
        )
        await WebsocketManager.send(second_user_id, response.dict())

    async def send_turn(self, user_id: int) -> None:
        """Change turn information and send it to the user"""
        self.game.turn = user_id
        self.game.move_number += 1
        await WebsocketManager.send(user_id, WebsocketResponse(type=WebsocketResponseEnum.TURN, status=status.HTTP_200_OK).dict())

    async def default(self) -> None:
        """Send default response to user"""
        response = WebsocketResponse(type=WebsocketResponseEnum.INVALID, status=status.HTTP_400_BAD_REQUEST)
        await WebsocketManager.send(self.user.id, response.dict())

    def disconnect(self) -> None:
        """Process websocket disconnect case"""
        if self.user is not None:
            WebsocketManager.remove_connection(self.user.id)

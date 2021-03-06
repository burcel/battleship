from typing import Any, List

from controllers.game import ControllerGame
from core.auth import JWTBearer, TokenValidator
from core.db import get_session
from core.security import Security
from fastapi import APIRouter, Depends, status, Path
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from models.games import Games
from schemas.game import GameBase, GameBaseCreate, GameBaseCreateResponse, GameBaseJoin, GameBaseList, GameBaseResponse
from schemas.message import Message
from schemas.user import UserBaseSession
from sqlalchemy.orm import Session

token_auth_scheme = HTTPBearer()

router = APIRouter()


@router.get(
    "/list",
    response_model=List[GameBaseResponse],
    responses={
        status.HTTP_200_OK: {"model": List[GameBaseList]},
        status.HTTP_401_UNAUTHORIZED: {"model": Message},
        status.HTTP_403_FORBIDDEN: {"model": Message}
    }
)
async def list(
    game_params: GameBaseList,
    session: Session = Depends(get_session),
    user: UserBaseSession = Depends(JWTBearer())
) -> List[Games]:
    """List games"""
    TokenValidator.check_token(session, user.id)
    game_list = ControllerGame.list(session, game_params)
    for game in game_list:
        if game.password is None:
            game.with_password = False
        else:
            game.with_password = True
    return game_list


@router.post(
    "/create",
    response_model=GameBaseCreateResponse,
    responses={
        status.HTTP_200_OK: {"model": GameBaseCreateResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": Message},
        status.HTTP_403_FORBIDDEN: {"model": Message}
    }
)
async def create(
    game: GameBaseCreate,
    session: Session = Depends(get_session),
    user: UserBaseSession = Depends(JWTBearer())
) -> GameBaseCreateResponse:
    """Create game request"""
    TokenValidator.check_token(session, user.id)
    # Check if user is in another game
    db_game = ControllerGame.get_by_username(session, user.username)
    if db_game is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is in another game.")
    if game.name is None:
        game.name = f"{user.username}'s Game"
    if game.password is not None:
        game.password = Security.get_pwd_hash(game.password)
    db_game = ControllerGame.create(session, game, user.id)
    return GameBaseCreateResponse(id=db_game.id)


@router.post(
    "/join",
    response_model=Message,
    responses={
        status.HTTP_200_OK: {"model": Message},
        status.HTTP_401_UNAUTHORIZED: {"model": Message},
        status.HTTP_403_FORBIDDEN: {"model": Message},
        status.HTTP_404_NOT_FOUND: {"model": Message}
    }
)
async def join(
    game: GameBaseJoin,
    session: Session = Depends(get_session),
    user: UserBaseSession = Depends(JWTBearer())
) -> Message:
    """Join game request"""
    TokenValidator.check_token(session, user.id)
    # Check if user is in another game
    db_game = ControllerGame.get_by_username(session, user.username)
    if db_game is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is in another game.")
    # Fetch game object
    db_game = ControllerGame.get_by_id(session, game.id)
    # Check if given game id is valid
    if db_game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid game id.")
    # Check if game has open place for joining
    if db_game.second_user_id is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Game is full.")
    # Check if game has password -> Verify password
    if db_game.password is not None:
        if game.password is None or Security.verify_pwd(game.password, db_game.password) is False:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password.")
    ControllerGame.join(session, game.id, user.id)
    return Message(detail="Joining is successful.")


@router.get(
    "/{game_id}",
    response_model=GameBase,
    responses={
        status.HTTP_200_OK: {"model": GameBase},
        status.HTTP_401_UNAUTHORIZED: {"model": Message},
        status.HTTP_403_FORBIDDEN: {"model": Message}
    }
)
async def get(
    game_id: int = Path(..., ge=0),
    session: Session = Depends(get_session),
    user: UserBaseSession = Depends(JWTBearer())
) -> Any:
    """Get info on given game"""
    TokenValidator.check_token(session, user.id)
    return ControllerGame.get(session, game_id)

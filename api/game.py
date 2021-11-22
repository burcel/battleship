from typing import List

from controllers.game import ControllerGame
from core.auth import JWTBearer
from core.db import get_session
from core.security import Security
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from schemas.game import GameBaseCreate, GameBaseCreateResponse
from schemas.message import Message
from schemas.user import UserBaseSession
from sqlalchemy.orm import Session

token_auth_scheme = HTTPBearer()

router = APIRouter()


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
    # Check if user is in another game
    db_game = ControllerGame.get_by_username(session, user.username)
    if db_game is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is in another game.")
    if game.name is None:
        game.name = f"{user.username}'s Game"
    if game.password is not None:
        game.password = Security.get_pwd_hash(game.password)
    db_game = ControllerGame.create(session, game, user.id)
    return GameBaseCreateResponse(game_id=db_game.id)


# /list
# /join
# /{id}

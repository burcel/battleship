from typing import Optional

from core.security import Security
from models.games import Games
from schemas.game import GameBaseCreate
from sqlalchemy.orm import Session
from controllers.user import ControllerUser


class ControllerGame:

    @staticmethod
    def get_by_id(session: Session, game_id: int) -> Optional[Games]:
        return session.query(Games).filter(Games.id == game_id).first()

    @staticmethod
    def get_by_username(session: Session, username: str) -> Optional[Games]:
        user = ControllerUser.get_by_username(session, username)
        if user is None:
            return None
        return session.query(Games).filter((Games.creator_user_id == user.id) | (Games.second_user_id == user.id)).first()

    @staticmethod
    def create(session: Session, game: GameBaseCreate, user_id: int) -> Games:
        db_game = Games(**game.dict())
        db_game.creator_user_id = user_id
        session.add(db_game)
        session.commit()
        session.refresh(db_game)
        return db_game

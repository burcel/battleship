from typing import List, Optional

from models.games import Games
from models.users import Users
from schemas.game import GameBaseCreate, GameBaseList
from sqlalchemy import desc
from sqlalchemy.orm import Session, aliased

from controllers.user import ControllerUser


class ControllerGame:
    LIMIT = 10

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

    @classmethod
    def list(cls, session: Session, game_param: GameBaseList) -> List[Games]:
        creator_user = aliased(Users)
        second_user = aliased(Users)
        query = session.query(Games)\
            .join(creator_user, Games.creator_user_id == creator_user.id, isouter=True)\
            .join(second_user, Games.second_user_id == second_user.id, isouter=True)

        if game_param.name is not None:
            query = query.filter(Games.name.contains(game_param.name) | (creator_user.username.contains(game_param.name)) | (second_user.username.contains(game_param.name)))

        return query.order_by(desc(Games.id)).offset(game_param.page).limit(cls.LIMIT).all()

    @staticmethod
    def join(session: Session, game_id: int, user_id: int) -> None:
        session.query(Games).where(Games.id == game_id).update({Games.second_user_id: user_id})

    @staticmethod
    def get(session: Session, game_id: int) -> Optional[Games]:
        creator_user = aliased(Users)
        second_user = aliased(Users)
        return session.query(Games)\
            .join(creator_user, Games.creator_user_id == creator_user.id, isouter=True)\
            .join(second_user, Games.second_user_id == second_user.id, isouter=True)\
            .filter(Games.id == game_id)\
            .first()

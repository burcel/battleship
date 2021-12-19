from typing import List, Optional

from sqlalchemy.sql.functions import user

from models.games import Games
from models.users import Users
from schemas.game import GameBaseCreate, GameBaseList
from sqlalchemy import desc
from sqlalchemy.orm import Session, aliased

from controllers.user import ControllerUser


class ControllerGame:
    LIMIT = 10

    @staticmethod
    def get_other_user_id(game: Games, user_id: int) -> Optional[int]:
        """Given game and user id, return the other user id in the game"""
        other_user_id = None
        if game.creator_user_id == user_id:
            other_user_id = game.second_user_id  # Might ne None
        elif game.second_user_id == user_id:
            other_user_id = game.creator_user_id  # Cannot be None
        return other_user_id

    @staticmethod
    def get_by_id(session: Session, game_id: int) -> Optional[Games]:
        return session.query(Games).filter(Games.id == game_id).first()

    @staticmethod
    def get_by_user_id(session: Session, user_id: int) -> Optional[Games]:
        return session.query(Games).filter((Games.creator_user_id == user_id) | (Games.second_user_id == user_id)).first()

    @classmethod
    def get_by_username(cls, session: Session, username: str) -> Optional[Games]:
        user = ControllerUser.get_by_username(session, username)
        if user is None:
            return None
        return cls.get_by_user_id(session, user.id)

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
        session.commit()

    @staticmethod
    def get(session: Session, game_id: int) -> Optional[Games]:
        creator_user = aliased(Users)
        second_user = aliased(Users)
        return session.query(Games)\
            .join(creator_user, Games.creator_user_id == creator_user.id, isouter=True)\
            .join(second_user, Games.second_user_id == second_user.id, isouter=True)\
            .filter(Games.id == game_id)\
            .first()

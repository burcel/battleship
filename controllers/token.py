from typing import Optional

from sqlalchemy.sql.functions import user

from models.tokens import Tokens
from sqlalchemy import func
from sqlalchemy.orm import Session


class ControllerToken:

    @staticmethod
    def get_by_user_id(session: Session, user_id: int) -> Optional[Tokens]:
        return session.query(Tokens).filter(Tokens.user_id == user_id).first()

    @staticmethod
    def get_by_token(session: Session, token: str) -> Optional[Tokens]:
        return session.query(Tokens).filter(Tokens.token == token).first()

    @staticmethod
    def save_token(session: Session, token: str, user_id: int) -> Tokens:
        db_token = Tokens(user_id=user_id, token=token, valid=True)
        session.add(db_token)
        session.commit()
        session.refresh(db_token)
        return db_token

    @staticmethod
    def update_token(session: Session, token_id: int, token: str) -> None:
        session.query(Tokens).where(Tokens.id == token_id).update({Tokens.token: token, Tokens.valid: True, Tokens.create_date: func.now()})
        session.commit()

    @staticmethod
    def invalidate_token(session: Session, token_id: int) -> None:
        session.query(Tokens).where(Tokens.id == token_id).update({Tokens.valid: False})
        session.commit()

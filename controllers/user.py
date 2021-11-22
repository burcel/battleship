from typing import Optional

from core.security import Security
from models.users import Users
from schemas.user import UserBaseCreate
from sqlalchemy.orm import Session


class ControllerUser:

    @staticmethod
    def get_by_id(session: Session, user_id: int) -> Optional[Users]:
        return session.query(Users).filter(Users.id == user_id).first()

    @staticmethod
    def get_by_username(session: Session, username: str) -> Optional[Users]:
        return session.query(Users).filter(Users.username == username).first()

    @staticmethod
    def get_by_email(session: Session, email: str) -> Optional[Users]:
        return session.query(Users).filter(Users.email == email).first()

    @classmethod
    def create(cls, session: Session, user: UserBaseCreate) -> Users:
        db_user = Users(**user.dict())
        db_user.password = Security.get_pwd_hash(user.password)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

    @classmethod
    def authenticate(cls, session: Session, username: str, password: str) -> Optional[Users]:
        user = cls.get_by_username(session, username)
        if user is not None and Security.verify_pwd(password, user.password) is True:
            return user
        else:
            return None

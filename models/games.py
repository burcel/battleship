from core.db import Base
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        func)
from sqlalchemy.orm import relationship

from models.users import Users


class Games(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True)
    name = Column(String(length=200), nullable=False)
    password = Column(String(length=200))
    create_date = Column(DateTime, default=func.now())
    creator_user_id = Column(Integer, ForeignKey(Users.id), unique=True)
    second_user_id = Column(Integer, ForeignKey(Users.id), unique=True)
    creator_user_ready = Column(Boolean, default=False)
    second_user_ready = Column(Boolean, default=False)
    creator_user_board = Column(String(length=100))
    second_user_board = Column(String(length=100))
    turn = Column(Integer, default=0)
    move_number = Column(Integer, default=0)
    finished = Column(Boolean, default=False)

    creator_user = relationship(Users, foreign_keys=[creator_user_id], uselist=False)
    second_user = relationship(Users, foreign_keys=[second_user_id], uselist=False)

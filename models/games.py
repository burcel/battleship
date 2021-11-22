from core.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
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

    creator_user = relationship(Users, foreign_keys=[creator_user_id], uselist=False)
    second_user = relationship(Users, foreign_keys=[second_user_id], uselist=False)

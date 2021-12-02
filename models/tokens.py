from core.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import relationship
from models.users import Users


class Tokens(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(Users.id), unique=True, nullable=False)
    token = Column(String(length=3000), nullable=False)
    valid = Column(Boolean, default=False)
    create_date = Column(DateTime, default=func.now())

    user = relationship(Users, foreign_keys=[user_id], uselist=False)

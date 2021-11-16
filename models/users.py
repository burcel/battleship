from core.db import Base
from sqlalchemy import Column, Integer, String


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(length=50), unique=True, index=True, nullable=False)
    password = Column(String(length=200), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

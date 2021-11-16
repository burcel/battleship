import secrets
from datetime import datetime, timedelta

import jwt
from jwt.exceptions import DecodeError
from passlib.context import CryptContext
from schemas.user import UserBaseLogin

from core.settings import settings


class Security:
    KEY = secrets.token_urlsafe(32)
    ALGORITHM = "HS256"
    PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def create_token(cls, user: UserBaseLogin) -> str:
        """Create access token for login and return it"""
        data = {
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(minutes=settings.token_expire_min),
        }
        encoded_jwt = jwt.encode(data, cls.KEY, algorithm=cls.ALGORITHM)
        return encoded_jwt

    @classmethod
    def decode_token(cls, token: str) -> UserBaseLogin:
        """Decode access token and return user"""
        data = jwt.decode(token, cls.KEY, algorithm=[cls.ALGORITHM])
        if data.get("username") is None:
            raise DecodeError
        return UserBaseLogin(username=data.get("username"))

    @classmethod
    def get_pwd_hash(cls, password: str) -> str:
        """Return hashed password"""
        return cls.PWD_CONTEXT.hash(password)

    @classmethod
    def verify_pwd(cls, plain_password: str, hashed_password: str) -> bool:
        """Verify given plaintext with hashed password and return the comparison"""
        return cls.PWD_CONTEXT.verify(plain_password, hashed_password)

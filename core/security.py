import secrets
from datetime import datetime, timedelta

import jwt
from jwt.exceptions import PyJWTError, ExpiredSignatureError
from fastapi import HTTPException, status
from models.users import Users
from passlib.context import CryptContext
from schemas.user import UserBaseSession

from core.settings import settings


class Security:
    KEY = secrets.token_urlsafe(32)
    ALGORITHM = "HS256"
    PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def create_token(cls, user: Users) -> str:
        """Create access token with respect to user data and return it"""
        data = {
            "id": user.id,
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(minutes=settings.token_expire_min),
        }
        encoded_jwt = jwt.encode(data, cls.KEY, algorithm=cls.ALGORITHM)
        return encoded_jwt

    @classmethod
    def decode_token(cls, token: str) -> UserBaseSession:
        """Decode access token and return user session object"""
        try:
            data = jwt.decode(token, cls.KEY, algorithm=[cls.ALGORITHM])
        except ExpiredSignatureError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token is expired.")
        except PyJWTError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token.")

        if data.get("id") is None or data.get("username") is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token.")
        return UserBaseSession(id=data.get("id"), username=data.get("username"))

    @classmethod
    def get_pwd_hash(cls, password: str) -> str:
        """Return hashed password"""
        return cls.PWD_CONTEXT.hash(password)

    @classmethod
    def verify_pwd(cls, plain_password: str, hashed_password: str) -> bool:
        """Verify given plaintext with hashed password and return the comparison"""
        return cls.PWD_CONTEXT.verify(plain_password, hashed_password)

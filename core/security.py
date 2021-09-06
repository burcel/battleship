from datetime import datetime, timedelta
from typing import Any

import jwt
from jwt.exceptions import DecodeError
from schemas.user import UserBaseLogin

from core.settings import settings


def create_access_token(user: UserBaseLogin) -> str:
    """ Create access token for login and return it"""
    data = {
        "username": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINS),
    }
    encoded_jwt = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.SECRET_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> UserBaseLogin:
    """Decode access token and return user"""
    data = jwt.decode(token, settings.SECRET_KEY, algorithm=[settings.SECRET_ALGORITHM])
    if data.get("username") is None:
        raise DecodeError
    return UserBaseLogin(username=data.get("username"))

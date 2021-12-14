from typing import Optional

from controllers.token import ControllerToken
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from models.tokens import Tokens
from schemas.user import UserBaseSession
from sqlalchemy.orm import Session
from schemas.websocket import WebsocketToken

from core.security import Security


class JWTBearer(HTTPBearer):

    def __init__(self, auto_error: bool = True) -> None:
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> UserBaseSession:
        credentials: Optional[HTTPAuthorizationCredentials] = await super(JWTBearer, self).__call__(request)
        if credentials is not None:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication scheme.")
            return Security.decode_token(credentials.credentials)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authorization code.")


class TokenValidator:

    @staticmethod
    def check_token(session: Session, user_id: int) -> Tokens:
        """Check token in database given user id and control its validity"""
        db_token = ControllerToken.get_by_user_id(session, user_id)
        if db_token is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token error.")
        elif db_token.valid is False:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authorization code.")
        return db_token

    @staticmethod
    def authorize_socket(token: WebsocketToken) -> UserBaseSession:
        """Authorize token coming"""
        return Security.decode_token(token.token)

from typing import Any

from controllers.user import ControllerUser
from controllers.token import ControllerToken
from core.auth import JWTBearer
from core.db import get_session
from core.security import Security
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from schemas.message import Message
from schemas.user import UserBaseCreate, UserBaseLogin, UserBaseLoginResponse, UserBaseResponse, UserBaseSession
from sqlalchemy.orm import Session

router = APIRouter()


@router.post(
    "/login",
    response_model=UserBaseLoginResponse,
    responses={
        status.HTTP_200_OK: {"model": UserBaseLoginResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": Message}
    }
)
async def login(user: UserBaseLogin, session: Session = Depends(get_session)) -> UserBaseLoginResponse:
    """Login request"""
    db_user = ControllerUser.authenticate(session, user.username, user.password)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    # Check token
    db_token = ControllerToken.get_by_user_id(session, db_user.id)
    if db_token is None:
        # User is not logged in before
        access_token = Security.create_token(db_user)
        ControllerToken.save_token(session, access_token, db_user.id)
    elif db_token.valid is True:
        # User is already logged in
        access_token = db_token.token
    else:
        # User is logged out -> Give new token
        access_token = Security.create_token(db_user)
        ControllerToken.update_token(session, db_token.id, access_token)
    return UserBaseLoginResponse(token=access_token)


@router.post(
    "/logout",
    response_model=Message,
    responses={
        status.HTTP_200_OK: {"model": Message},
        status.HTTP_401_UNAUTHORIZED: {"model": Message},
    }
)
async def logout(session: Session = Depends(get_session), user: UserBaseSession = Depends(JWTBearer())) -> Message:
    """Logout request"""
    db_token = ControllerToken.get_by_user_id(session, user.id)
    if db_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User cannot be logged out.")
    elif db_token.valid is False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is already logged out.")
    ControllerToken.invalidate_token(session, db_token.id)
    return Message(detail="Logout is successful.")


@router.post(
    "/create",
    response_model=Message,
    responses={
        status.HTTP_200_OK: {"model": Message},
        status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
    }
)
async def create(user: UserBaseCreate, session: Session = Depends(get_session)) -> Any:
    """Create user request"""
    db_user = ControllerUser.get_by_username(session, user.username)
    if db_user is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username is taken.")
    db_user = ControllerUser.get_by_email(session, user.email)
    if db_user is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email is taken.")
    ControllerUser.create(session, user=user)
    return Message(detail="User is created.")


@router.get(
    "/{user_id}",
    response_model=UserBaseResponse,
    responses={
        status.HTTP_200_OK: {"model": UserBaseResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": Message},
        status.HTTP_403_FORBIDDEN: {"model": Message}
    }
)
async def get(
    user_id: int,
    session: Session = Depends(get_session),
    user: UserBaseSession = Depends(JWTBearer())
) -> Any:
    """Get info on given user"""
    return ControllerUser.get_by_id(session, user_id=user_id)

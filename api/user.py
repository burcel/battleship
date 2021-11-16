from typing import Any

from controllers.user import ControllerUser
from core.db import get_session
from core.security import Security
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from jwt.exceptions import PyJWTError
from models.users import Users
from schemas.message import Message
from schemas.user import UserBaseLogin, UserBaseLoginResponse, UserBaseCreate
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
    db_user = ControllerUser.authenticate(session, username=user.username, password=user.password)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    access_token = Security.create_token(user)
    return UserBaseLoginResponse(token=access_token)


@router.post(
    "/logout",
    response_model=Message,
    responses={
        status.HTTP_200_OK: {"model": Message},
        status.HTTP_401_UNAUTHORIZED: {"model": Message},
    }
)
async def logout(user: UserBaseLoginResponse) -> Any:
    """Logout request"""
    return {"TBD"}


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
    db_user = ControllerUser.get_by_username(session, username=user.username)
    if db_user is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    ControllerUser.create(session, user=user)
    return Message(message="User is created.")

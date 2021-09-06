from typing import Any

from core.security import create_access_token, decode_access_token
from data.user import user_data
from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import PyJWTError
from schemas.user import Message, UserBaseLogin, UserBaseLoginResponse

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/login", response_model=UserBaseLoginResponse, responses={
    status.HTTP_200_OK: {"model": UserBaseLoginResponse},
    status.HTTP_406_NOT_ACCEPTABLE: {"model": Message},
})
async def login(user: UserBaseLogin) -> UserBaseLoginResponse:
    """Login request"""
    username_exists = user_data.check_username(user.username)
    if username_exists is True:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Username is already registered.")
    user_data.register_user(user.username)
    access_token = create_access_token(user)
    return UserBaseLoginResponse(token=access_token)


@router.post("/logout", response_model=Message, responses={
    status.HTTP_200_OK: {"model": Message},
    status.HTTP_401_UNAUTHORIZED: {"model": Message},
})
async def logout(user: UserBaseLoginResponse) -> Message:
    """Logout request"""
    try:
        decoded_user = decode_access_token(user.token)
    except PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials!")
    user_data.remove_username(decoded_user.username)
    return Message(message="Successfully logged out.")
